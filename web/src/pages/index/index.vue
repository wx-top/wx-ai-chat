<template>
	<view class="page-container">
		<!-- 固定顶部区域 -->
		<view class="header-fixed">
			<view class="model-selector">
				<up-cell @click="modelPickerShow = true" :title="selectedModel ? '': '选择模型'" isLink>
					<template #value>
						<view v-if="selectedModel">
							{{selectedModel.description}}
						</view>
					</template>
				</up-cell>
				<up-picker v-model:show="modelPickerShow" :columns="[modelStore.models]" keyName="description"
					valueName="id" @confirm="modelPickerConfirm"></up-picker>
			</view>
			<view class="header-buttons">
				<view class="repository-container">
					<view class="repository-btn" @click="repoPickerShow = true">
						<uni-icons type="folder-add" size="24" color="#007AFF"></uni-icons>
						<text v-if="currentRepository" class="repository-name">{{ currentRepository.name }}</text>
					</view>
					<view v-if="currentRepository" class="repository-cancel" @click="cancelRepositorySelect">
						<uni-icons type="closeempty" size="16" color="#999"></uni-icons>
					</view>
					<up-picker v-model:show="repoPickerShow" :columns="[repositories]" keyName="name"
						valueName="id" @confirm="repoPickerConfirm"></up-picker>
				</view>
				<view class="new-chat-btn" @click="createNewChat">
					<text>新对话</text>
				</view>
			</view>
		</view>

		<!-- 聊天消息区域 -->
		<view class="chat-content">
			<scroll-view class="message-scroll" scroll-y="true" :scroll-top="scrollTop" :scroll-into-view="scrollIntoView" scroll-with-animation>
			<view class="message-list">
				<view v-for="(message, index) in currentMessages" :key="index"
					:id="index === currentMessages.length - 1 ? 'bottom-message' : ''"
					:class="['message', message.role === 'user' ? 'message-user' : 'message-ai']">
					<view class="message-content">
						<text>{{ message.content || '正在思考...' }}</text>
					</view>
				</view>
				<!-- 底部锚点 -->
				<view id="scroll-bottom" style="height: 1px;"></view>
			</view>
		</scroll-view>
		</view>

		<!-- 固定底部输入区域 -->
		<view class="input-fixed">
			<view class="input-wrapper">
				<textarea class="message-input" v-model="inputMessage" placeholder="请输入消息..." :disabled="loading"
				auto-height @keydown.enter.prevent="sendMessage" @focus="handleKeyboardShow" @blur="handleKeyboardHide" />
				<button class="send-btn" :disabled="!inputMessage.trim() || loading" @click="sendMessage">
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
	const inputMessage = ref('')
	const scrollTop = ref(0)
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

	// 取消选择知识库
	const cancelRepositorySelect = () => {
		chatStore.setCurrentRepository(null)
	}
</script>

<style scoped>
	/* 页面容器 - 考虑tabbar高度 */
	.page-container {
		position: relative;
		width: 100%;
		height: calc(100vh - var(--window-bottom));
		background-color: #f5f5f5;
		overflow: hidden;
		display: flex;
		flex-direction: column;
	}

	/* 固定顶部区域 */
	.header-fixed {
		flex-shrink: 0;
		background-color: white;
		border-bottom: 2rpx solid #e0e0e0;
		padding: 20rpx 30rpx;
		display: flex;
		justify-content: space-between;
		align-items: center;
		box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
		z-index: 100;
	}

	/* 聊天内容区域 */
	.chat-content {
		flex: 1;
		padding: 0 30rpx;
		overflow: hidden;
		position: relative;
	}

	/* 消息滚动区域 */
	.message-scroll {
		height: 100%;
		width: 100%;
		overflow-y: auto;
		overflow-x: hidden;
	}

	/* 固定底部输入区域 */
	.input-fixed {
		flex-shrink: 0;
		background-color: white;
		border-top: 2rpx solid #dcd6d6;
		/* padding: 12rpx 12rpx; */
		padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
		box-shadow: 0 -2rpx 8rpx rgba(0, 0, 0, 0.1);
		/* z-index: 100; */
		position: relative;
		min-height: 220rpx;
		display: block;
	}

	.input-wrapper {
		display: flex;
		align-items: flex-end;
		gap: 12rpx;
		background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
		border-radius: 20rpx;
		padding: 16rpx;
		box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.08);
		min-height: 48rpx;
		width: 100%;
		box-sizing: border-box;
	}

	/* 模型选择器 */
	.model-selector {
		font-size: 28rpx;
	}

	/* 头部按钮组 */
	.header-buttons {
		display: flex;
		align-items: center;
		gap: 20rpx;
	}

	.new-chat-btn {
		color: #007AFF;
		font-size: 28rpx;
		padding: 12rpx 24rpx;
		border: 2rpx solid #007AFF;
		border-radius: 20rpx;
		background-color: transparent;
	}

	/* 知识库选择 */
	.repository-container {
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

	/* 消息列表 */
	.message-list {
		display: flex;
		flex-direction: column;
		gap: 24rpx;
		padding: 30rpx 0 60rpx 0;
		min-height: 100%;
	}

	.message {
		max-width: 75%;
		border-radius: 24rpx;
		padding: 20rpx 24rpx;
		position: relative;
		word-break: break-word;
		line-height: 1.5;
	}

	.message-user {
		align-self: flex-end;
		background-color: #007AFF;
		color: white;
		margin-right: 20rpx;
	}

	.message-ai {
		align-self: flex-start;
		background-color: white;
		color: #333;
		border: 2rpx solid #e0e0e0;
		margin-left: 20rpx;
		box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
	}

	.message-content {
		font-size: 28rpx;
		line-height: 1.6;
	}

	/* 输入框样式 */
	.message-input {
		flex: 1;
		border: none;
		border-radius: 16rpx;
		padding: 16rpx 20rpx;
		max-height: 120rpx;
		min-height: 64rpx;
		font-size: 28rpx;
		background: #ffffff;
		resize: none;
		line-height: 1.4;
		box-sizing: border-box;
		color: #333333;
		box-shadow: inset 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
		transition: all 0.3s ease;
	}

	.message-input:focus {
		outline: none;
		background: #ffffff;
		box-shadow: inset 0 2rpx 8rpx rgba(0, 0, 0, 0.06), 0 0 0 3rpx rgba(0, 122, 255, 0.1);
		transform: translateY(-1rpx);
	}

	.message-input::placeholder {
		color: #999999;
		font-size: 26rpx;
	}

	.send-btn {
		background: linear-gradient(135deg, #007AFF 0%, #0056CC 100%);
		color: white;
		border-radius: 16rpx;
		height: 64rpx;
		width: 64rpx;
		font-size: 28rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0;
		border: none;
		box-shadow: 0 4rpx 16rpx rgba(0, 122, 255, 0.25);
		flex-shrink: 0;
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		position: relative;
		overflow: hidden;
	}

	.send-btn:disabled {
		background: linear-gradient(135deg, #cccccc 0%, #999999 100%);
		box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
		cursor: not-allowed;
		transform: none;
		opacity: 0.6;
	}

	.send-btn:not(:disabled):hover {
		background: linear-gradient(135deg, #0056CC 0%, #003d99 100%);
		transform: translateY(-2rpx) scale(1.02);
		box-shadow: 0 8rpx 25rpx rgba(0, 122, 255, 0.35);
	}

	.send-btn:not(:disabled):active {
		transform: translateY(0) scale(0.98);
		box-shadow: 0 4rpx 15rpx rgba(0, 122, 255, 0.2);
	}

	.send-btn::before {
		content: '';
		position: absolute;
		top: 0;
		left: -100%;
		width: 100%;
		height: 100%;
		background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
		transition: left 0.5s;
	}

	.send-btn:not(:disabled):hover::before {
		left: 100%;
	}

	/* H5平台特殊适配 */
	/* #ifdef H5 */
	.page-container {
		height: calc(100vh - 50px); /* 为tabbar留出空间 */
	}

	/* 确保输入框在H5中完全可见 */
	.input-wrapper {
		margin: 12rpx;
		padding: 12rpx;
	}

	.input-fixed {
		padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
	}

	.message-input {
		max-height: 100rpx !important;
		font-size: 26rpx !important;
		min-height: 56rpx !important;
	}

	.send-btn {
		height: 56rpx !important;
		width: 56rpx !important;
	}

	/* PC端适配 - 减少输入框区域高度 */
	@media (min-width: 768px) {
		.input-fixed {
			min-height: 120rpx !important;
			padding: 16rpx 24rpx !important;
		}
		
		.input-wrapper {
			margin: 0 !important;
			padding: 12rpx 16rpx !important;
		}
	}
	/* #endif */

	/* 隐藏滚动条但保持滚动功能 */
	.message-scroll {
		scrollbar-width: none; /* Firefox */
		-ms-overflow-style: none; /* IE and Edge */
	}

	.message-scroll::-webkit-scrollbar {
		display: none; /* Webkit */
	}

	/* 移除不需要的样式 */
	.chat-list,
	.chat-item,
	.chat-title {
		display: none;
	}

	/* 弹窗相关样式保持不变 */
	.repository-popup {
		background-color: white;
		border-radius: 40rpx 40rpx 0 0;
		padding: 40rpx;
		max-height: 60vh;
	}

	.popup-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 40rpx;
	}

	.popup-title {
		font-size: 32rpx;
		font-weight: bold;
	}

	.close-btn {
		font-size: 48rpx;
		color: #999;
		padding: 0 20rpx;
	}

	.repository-list {
		max-height: calc(60vh - 120rpx);
	}

	.repository-item {
		padding: 30rpx;
		border-bottom: 2rpx solid #f0f0f0;
	}

	.repository-remark {
		font-size: 24rpx;
		color: #999;
	}

	.repository-item-selected {
		background-color: #e6f7ff;
		border-radius: 16rpx;
		box-shadow: 0 4rpx 16rpx rgba(0, 122, 255, 0.1);
	}

	.repository-tag {
		display: flex;
		align-items: center;
		gap: 8rpx;
	}
</style>