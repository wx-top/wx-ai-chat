<template>
	<view class="chat-container">
		<!-- 顶部模型选择 -->
		<view class="header">
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

		<!-- 聊天记录 -->
		<scroll-view class="chat-messages" scroll-y="true" :scroll-top="scrollTop" scroll-with-animation>
			<view class="message-list">
				<view v-for="(message, index) in currentMessages" :key="index"
					:class="['message', message.role === 'user' ? 'message-user' : 'message-ai']">
					<view class="message-content">
						<text>{{ message.content || '正在思考...' }}</text>
					</view>
				</view>
			</view>
		</scroll-view>

		<!-- 输入区域 -->
		<view class="input-area">
			<textarea class="message-input" v-model="inputMessage" placeholder="请输入消息..." :disabled="loading"
				auto-height @keydown.enter.prevent="sendMessage" />
			<button class="send-btn" :disabled="!inputMessage.trim() || loading" @click="sendMessage">
				发送
			</button>
		</view>
	</view>
</template>

<script setup>
	import {
		ref,
		computed,
		nextTick,
		watch,
		onMounted,
		toRef
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

	const chatStore = useChatStore()
	const modelStore = useModelStore()
	const inputMessage = ref('')
	const scrollTop = ref(0)
	const repositoryPopup = ref(null)
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
		// currentModel.value = e.value[0]
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

	// 格式化时间
	const formatTime = (timestamp) => {
		if (!timestamp) return ''

		const date = new Date(timestamp)
		const hours = date.getHours().toString().padStart(2, '0')
		const minutes = date.getMinutes().toString().padStart(2, '0')

		return `${hours}:${minutes}`
	}

	// 滚动到底部
	const scrollToBottom = async () => {
		await nextTick()
		scrollTop.value = Math.random() * 10000
	}

	// 监听消息变化，自动滚动到底部
	watch(() => currentMessages.value.length, async () => {
		await scrollToBottom()
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

<style>
	.chat-container {
		display: flex;
		flex-direction: column;
		height: 100vh;
		padding: 0 15px;
	}

	.header {
		display: flex;
		justify-content: space-between;
		padding: 10px 0;
		background-color: white;
		border-bottom: 1px solid #e0e0e0;
	}

	.model-selector {
		display: flex;
		align-items: center;
		font-size: 14px;
	}

	.icon {
		margin-left: 5px;
		font-size: 12px;
	}

	.new-chat-btn {
		color: #007AFF;
		font-size: 14px;
		padding: 6px 10px;
	}

	.chat-messages {
		flex: 1;
		padding: 10px 0;
		background-color: #f5f5f5;
		overflow-y: auto;
		/* 隐藏滚动条 */
		scrollbar-width: none;
		/* Firefox */
		-ms-overflow-style: none;
		/* IE and Edge */
	}

	/* 隐藏 Webkit 浏览器的滚动条 */
	.chat-messages::-webkit-scrollbar {
		display: none;
	}

	.message-list {
		display: flex;
		flex-direction: column;
		gap: 12px;
		padding-bottom: 10px;
	}

	.message {
		max-width: 75%;
		border-radius: 12px;
		padding: 8px 12px;
		position: relative;
		word-break: break-word;
	}

	.message-user {
		align-self: flex-end;
		background-color: #007AFF;
		color: white;
		margin-right: 10px;
	}

	.message-ai {
		align-self: flex-start;
		background-color: white;
		color: #333;
		border: 1px solid #e0e0e0;
		margin-left: 10px;
	}

	.message-content {
		line-height: 1.4;
		font-size: 14px;
	}

	.input-area {
		background-color: white;
		border-top: 1px solid #e0e0e0;
		padding: 10px 0;
		display: flex;
		align-items: flex-end;
	}

	.message-input {
		flex: 1;
		border: 1px solid #e0e0e0;
		border-radius: 18px;
		padding: 8px 12px;
		max-height: 100px;
		min-height: 36px;
		margin-right: 8px;
	}

	.send-btn {
		background-color: #007AFF;
		color: white;
		border-radius: 18px;
		height: 36px;
		width: 70px;
		font-size: 14px;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0;
	}

	.send-btn:disabled {
		background-color: #ccc;
	}

	/* 移除 chat-list 相关样式 */
	.chat-list,
	.chat-item,
	.chat-title {
		display: none;
	}

	.header-buttons {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.repository-container {
		display: flex;
		align-items: center;
		gap: 4px;
	}

	.repository-btn {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 4px 8px;
		background-color: #f0f0f0;
		border-radius: 15px;
		font-size: 14px;
	}

	.repository-name {
		color: #007AFF;
		font-size: 14px;
	}

	.repository-cancel {
		padding: 4px;
		cursor: pointer;
	}

	.repository-popup {
		background-color: white;
		border-radius: 20px 20px 0 0;
		padding: 20px;
		max-height: 60vh;
	}

	.popup-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 20px;
	}

	.popup-title {
		font-size: 16px;
		font-weight: bold;
	}

	.close-btn {
		font-size: 24px;
		color: #999;
		padding: 0 10px;
	}

	.repository-list {
		max-height: calc(60vh - 60px);
	}

	.repository-item {
		padding: 15px;
		border-bottom: 1px solid #f0f0f0;
	}

	.repository-remark {
		font-size: 12px;
		color: #999;
	}

	.repository-item-selected {
		background-color: #e6f7ff;
		border-radius: 8px;
		box-shadow: 0 2px 8px rgba(0, 122, 255, 0.1);
	}


	.repository-tag {
		display: flex;
		align-items: center;
		gap: 4px;
	}
</style>