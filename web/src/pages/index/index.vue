<template>
	<view class="chat-page" :style="{ height: getChatPageHeight() }">
		<!-- 顶部区域 -->
		<view class="header">
			<view class="header-left">
				<up-cell @click="modelPickerShow = true" :title="selectedModel ? '' : '选择模型'" isLink>
					<template #value>
						<view v-if="selectedModel">
							{{ selectedModel.description }}
						</view>
					</template>
				</up-cell>
				<up-picker v-model:show="modelPickerShow" :columns="[modelStore.models]" keyName="description"
					valueName="id" @confirm="modelPickerConfirm"></up-picker>
			</view>
			<view class="header-right">
<!--				<view class="repository-selector">-->
<!--					<view class="repository-btn" @click="repoPickerShow = true">-->
<!--						<uni-icons type="folder-add" size="24" color="#007AFF"></uni-icons>-->
<!--						<text v-if="currentRepository" class="repository-name">{{ currentRepository.name }}</text>-->
<!--					</view>-->
<!--					<view v-if="currentRepository" class="repository-cancel" @click="cancelRepositorySelect">-->
<!--						<uni-icons type="closeempty" size="16" color="#999"></uni-icons>-->
<!--					</view>-->
<!--					<up-picker v-model:show="repoPickerShow" :columns="[repositories]" keyName="name"-->
<!--						valueName="id" @confirm="repoPickerConfirm"></up-picker>-->
<!--				</view>-->
				<view class="new-chat-btn" @click="createNewChat">
					<text>新对话</text>
				</view>
			</view>
		</view>

		<!-- 中间消息区域 -->
		<view class="content">
			<scroll-view class="message-container" scroll-y="true" :scroll-into-view="scrollIntoView" scroll-with-animation>
				<view class="message-list">
					<view v-for="(message, index) in currentMessages" :key="index"
						:id="index === currentMessages.length - 1 ? 'bottom-message' : ''"
						:class="['message-item', message.role === 'user' ? 'user-message' : 'ai-message']">
						<view class="message-bubble">
							<text>{{ message.content || '正在思考...' }}</text>
						</view>
					</view>
					<!-- 滚动锚点 -->
					<view id="scroll-bottom" class="scroll-anchor"></view>
				</view>
			</scroll-view>
		</view>

		<!-- 底部输入区域 -->
		<view class="footer">
			<view class="input-container">
				<textarea class="input-field" v-model="inputMessage" placeholder="请输入消息..." :disabled="loading"
					auto-height @keydown.enter.prevent="sendMessage" @focus="handleKeyboardShow" @blur="handleKeyboardHide" />
				<button class="send-button" :disabled="!inputMessage.trim() || loading" @click="sendMessage">
					<uni-icons type="paperplane-filled" size="18" color="#ffffff"></uni-icons>
				</button>
			</view>
		</view>
	</view>
</template>

<script setup>
import {
	ref,
	nextTick,
	watch,
	onMounted,
} from 'vue'
import { useAppStore } from '@/store/app.js'
import {
	useChatStore
} from '@/store/chat.js'
import {
	useModelStore
} from '@/store/model.js'
import {
	storeToRefs
} from 'pinia'
import {
	onShow
} from "@dcloudio/uni-app"
import {
	getRepositories
} from '@/api/repository'
import {
	debounce
} from '@/utils/debounce.js'

const chatStore = useChatStore()
const modelStore = useModelStore()
const appStore = useAppStore()
const inputMessage = ref('')
const scrollIntoView = ref('')
const repositories = ref([])

const currentModel = ref(null)
const modelPickerShow = ref(false)
const repoPickerShow = ref(false)

// 当前选择的模型
const {
	selectedModel
} = storeToRefs(modelStore)
const {
	chats,
	loading,
	currentMessages,
	currentChatId,
	currentRepository
} = storeToRefs(chatStore)
const {
	isWechat: isWechatEnv
} = storeToRefs(appStore)

const modelPickerConfirm = (e) => {
	console.log("选择", e)
	selectedModel.value = e.value[0]
}

const repoPickerConfirm = (e) => {
	currentRepository.value = e.value[0]
}

// 创建新对话
const createNewChat = async () => {
	try {
		// 如果没有选择模型，跳转到模型选择页
		if (!modelStore.selectedModel) {
			goToModelSelect()
			return
		}

		// 创建新聊天
		const chat = await chatStore.newChat('新对话')
		// 获取新聊天的消息
		await chatStore.fetchMessages(chat.id)
		// 清空输入
		inputMessage.value = ''
	} catch (error) {
		uni.showToast({
			title: error.message || '创建对话失败',
			icon: 'none'
		})
	}
}

// 跳转到模型选择页面
const goToModelSelect = () => {
	uni.navigateTo({
		url: '/pages/models/models'
	})
}

// 发送消息
const sendMessage = async () => {
	if (!inputMessage.value.trim() || chatStore.loading) return

	const content = inputMessage.value.trim()
	inputMessage.value = ''

	try {
		// 如果没有当前聊天，创建新聊天
		if (!currentChatId.value) {
			await createNewChat()
		}

		// 发送消息到服务器
		await chatStore.sendChatMessage(content)

		// 自动滚动到底部
		await scrollToBottom()
	} catch (error) {
		uni.showToast({
			title: error.message || '发送消息失败',
			icon: 'none'
		})
	}
}

// 滚动到底部
const scrollToBottom = async () => {
	await nextTick()
	// 使用scroll-into-view滚动到底部锚点
	scrollIntoView.value = 'scroll-bottom'
	// 清空scroll-into-view以便下次使用
	setTimeout(() => {
		scrollIntoView.value = ''
	}, 100)
}

// 防抖滚动到底部
const debouncedScrollToBottom = debounce(scrollToBottom, 300)

// 键盘弹出处理
const handleKeyboardShow = () => {
	setTimeout(() => {
		debouncedScrollToBottom()
	}, 600) // 增加延迟确保键盘完全弹出
}

// 键盘收起处理
const handleKeyboardHide = () => {
	setTimeout(() => {
		debouncedScrollToBottom()
	}, 100)
}

// 监听消息变化，自动滚动到底部
watch(() => currentMessages.value.length, async () => {
	await nextTick()
	debouncedScrollToBottom()
})

// 监听消息内容变化（仅在消息数量不变时触发，避免重复滚动）
let lastMessageCount = 0
watch(() => currentMessages.value, async () => {
	if (currentMessages.value.length === lastMessageCount) {
		// 消息数量没变，说明是内容更新（如AI正在输出）
		await nextTick()
		debouncedScrollToBottom()
	}
	lastMessageCount = currentMessages.value.length
}, { deep: true })

// 监听流式响应状态，确保接收完消息后滚动到底部
watch(() => chatStore.streaming, async (newVal, oldVal) => {
	// 当流式响应结束时（从true变为false），确保滚动到底部
	if (oldVal === true && newVal === false) {
		await nextTick()
		// 使用直接滚动而不是防抖，确保消息接收完成后立即滚动
		scrollToBottom()
	}
})

// 页面加载时获取聊天列表和模型列表
onMounted(async () => {
})

onShow(async () => {
	console.log("index page on show")
	// 获取模型列表
	await modelStore.fetchModels()
	// 默认值为第一个模型
	if (modelStore.models.length > 0) {
		currentModel.value = modelStore.models[0]
	}
	
	repositories.value = await getRepositories()
	console.log(repositories.value)
	
	// 获取聊天列表
	await chatStore.fetchChats()

	// 如果没有选择的模型，则选择第一个模型
	if (!modelStore.selectedModel && modelStore.models.length > 0) {
		modelStore.selectModel(modelStore.models[0])
	}

	// 如果有当前聊天ID，直接加载该聊天的消息
	if (currentChatId.value) {
		await chatStore.fetchMessages(currentChatId.value)
	} else if (chats.value?.length > 0) {
		// 如果没有当前聊天ID但有聊天记录，加载第一个聊天的消息
		await chatStore.fetchMessages(chats.value[0].id)
	} else if (modelStore.selectedModel) {
		// 如果没有聊天记录但有选择的模型，创建新聊天
		const chat = await chatStore.newChat('新对话')
		await chatStore.fetchMessages(chat.id)
	} else {
		// 如果没有模型，跳转到模型选择页
		goToModelSelect()
	}
})

// 获取聊天页面高度
const getChatPageHeight = () => {
	const deviceType = appStore.deviceType
	console.log("deviceType", deviceType)
	switch (deviceType) {
		case 'wechat':
			return 'calc(100vh - 100rpx)'
		case 'mobile':
			return 'calc(100vh - 205rpx)'
		case 'tablet':
			return 'calc(100vh - 100rpx)'
		case 'desktop':
			return 'calc(100vh - 100rpx)'
		default:
			return 'calc(100vh - 100rpx)'
	}

}

// 取消选择知识库
const cancelRepositorySelect = () => {
	chatStore.setCurrentRepository(null)
}
</script>

<style scoped>
/* 页面主容器 */
.chat-page {
	display: flex;
	flex-direction: column;
	background-color: #f5f5f5;
	overflow: hidden;
}

/* 顶部区域 */
.header {
	flex-shrink: 0;
	height: 120rpx;
	background-color: #ffffff;
	border-bottom: 1px solid #e5e5e5;
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 0 30rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
	z-index: 100;
}

.header-left {
	flex: 0 0 auto;
	max-width: 60%;
	font-size: 28rpx;
}

.header-right {
	display: flex;
	align-items: center;
	gap: 20rpx;
	flex: 0 0 auto;
	max-width: 40%;
}

.repository-selector {
	display: flex;
	align-items: center;
	gap: 8rpx;
}

.repository-btn {
	display: flex;
	align-items: center;
	gap: 16rpx;
	padding: 8rpx 16rpx;
	background-color: #f0f0f0;
	border-radius: 30rpx;
	font-size: 28rpx;
}

.repository-name {
	color: #007AFF;
	font-size: 28rpx;
}

.repository-cancel {
	padding: 8rpx;
	cursor: pointer;
}

.new-chat-btn {
	color: #007AFF;
	font-size: 28rpx;
	padding: 12rpx 24rpx;
	border: 2rpx solid #007AFF;
	border-radius: 20rpx;
	background-color: transparent;
}

/* 中间内容区域 */
.content {
	flex: 1;
	overflow: hidden;
	position: relative;
}

.message-container {
	height: 100%;
	width: 100%;
	padding: 0 30rpx;
	box-sizing: border-box;
}

.message-list {
	display: flex;
	flex-direction: column;
	gap: 24rpx;
	padding: 30rpx 0 60rpx 0;
	min-height: 100%;
}

.message-item {
	max-width: 85%;
	display: flex;
	width: 100%;
}

.user-message {
	justify-content: flex-end;
	align-self: flex-end;
}

.ai-message {
	justify-content: flex-start;
	align-self: flex-start;
}

.message-bubble {
	border-radius: 24rpx;
	padding: 20rpx 24rpx;
	word-break: break-word;
	line-height: 1.5;
	font-size: 28rpx;
}

.user-message .message-bubble {
	background-color: #007AFF;
	color: white;
}

.ai-message .message-bubble {
	background-color: white;
	color: #333;
	border: 2rpx solid #e0e0e0;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.scroll-anchor {
	height: 1px;
	width: 100%;
}

/* 底部输入区域 */
.footer {
	flex-shrink: 0;
	background-color: #ffffff;
	border-top: 1px solid #e5e5e5;
	padding: 20rpx 30rpx;
	padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
	box-shadow: 0 -2rpx 8rpx rgba(0, 0, 0, 0.1);
}

.input-container {
	display: flex;
	align-items: flex-end;
	gap: 16rpx;
	background: #f8f9fa;
	border-radius: 24rpx;
	padding: 16rpx 20rpx;
	min-height: 80rpx;
	box-sizing: border-box;
}

.input-field {
	flex: 1;
	border: none;
	background: transparent;
	font-size: 28rpx;
	line-height: 1.4;
	max-height: 120rpx;
	min-height: 48rpx;
	resize: none;
	outline: none;
	color: #333;
}

.input-field::placeholder {
	color: #999;
}

.send-button {
	width: 64rpx;
	height: 64rpx;
	border-radius: 50%;
	background: linear-gradient(135deg, #007AFF 0%, #0056CC 100%);
	border: none;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 4rpx 16rpx rgba(0, 122, 255, 0.25);
	transition: all 0.3s ease;
	flex-shrink: 0;
}

.send-button:disabled {
	background: #ccc;
	box-shadow: none;
	opacity: 0.6;
}

.send-button:not(:disabled):active {
	transform: scale(0.95);
}

/* 隐藏滚动条 */
.message-container {
	scrollbar-width: none;
	-ms-overflow-style: none;
}

.message-container::-webkit-scrollbar {
	display: none;
}

/* 多端适配 */
/* #ifdef H5 */

.input-container {
	padding: 12rpx 16rpx;
}

.input-field {
	font-size: 26rpx;
	max-height: 100rpx;
	min-height: 44rpx;
}

.send-button {
	width: 56rpx;
	height: 56rpx;
}

/* PC端适配 */
@media (min-width: 768px) {
	.footer {
		padding: 16rpx 24rpx;
	}
	
	.input-container {
		padding: 12rpx 16rpx;
	}
	
	.message-item {
		max-width: 70%;
	}
}
/* #endif */

/* #ifdef MP-WEIXIN */
.chat-page {
	height: calc(100vh - var(--window-bottom));
}
/* #endif */
</style>