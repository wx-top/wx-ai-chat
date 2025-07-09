<template>
	<view class="history-container">
		<!-- 会话列表 -->
		<up-search placeholder="搜索会话" v-model="keyword" :clearabled="true"></up-search>
		<up-list>
			<up-list-item v-for="(item, index) in chats" :key="index">
				<up-cell :title="item.title">
					<template #title>
						<view class="list-item-title">
							<up-text type="primary" :text="item.title"></up-text>
							<up-text type="info" size="14" :text="formatTime(item.created_at)"></up-text>
						</view>
					</template>
					<template #right-icon>
						<view class="list-item-btns">
							<up-button type="success" @click="goToChat(item.id)" text="聊天" size="mini"></up-button>
							<up-button type="error" @click="deleteChat(item.id)" text="删除" size="mini"></up-button>
						</view>
					</template>
				</up-cell>
			</up-list-item>
		</up-list>
	</view>
</template>

<script setup>
	import {
		onMounted
	} from 'vue'
	import {
		useChatStore
	} from '@/store/chat'
	import {
		storeToRefs
	} from 'pinia'


	const chatStore = useChatStore()
	const {
		chats,
		loading,
		currentChatId
	} = storeToRefs(chatStore)
	const {
		removeChat,
		fetchChats
	} = chatStore

	// 格式化时间
	const formatTime = (timestamp) => {
		if (!timestamp) return ''

		const date = new Date(timestamp)
		const year = date.getFullYear()
		const month = (date.getMonth() + 1).toString().padStart(2, '0')
		const day = date.getDate().toString().padStart(2, '0')
		const hours = date.getHours().toString().padStart(2, '0')
		const minutes = date.getMinutes().toString().padStart(2, '0')

		return `${year}-${month}-${day} ${hours}:${minutes}`
	}

	// 跳转到聊天页面
	const goToChat = (chatId) => {
		currentChatId.value = chatId
		console.log('跳转聊天页面', chatId)
		uni.switchTab({
			url: '/pages/index/index'
		})
	}

	// 删除会话
	const deleteChat = async (chatId) => {
		try {
			const res = await uni.showModal({
				title: '确认删除',
				content: '确定要删除这个会话吗？',
				confirmText: '删除',
				confirmColor: '#ff3b30'
			})

			if (res.confirm) {
				await removeChat(chatId)
				uni.showToast({
					title: '删除成功',
					icon: 'success'
				})
			}
		} catch (error) {
			console.error('删除会话失败', error)
			uni.showToast({
				title: '删除失败',
				icon: 'none'
			})
		}
	}

	// 页面加载时获取聊天列表
	onMounted(async () => {
		try {
			await fetchChats()
		} catch (error) {
			uni.showToast({
				title: '加载失败',
				icon: 'none'
			})
		}
	})
</script>

<style>
	.history-container {
		padding: 20rpx;
		height: 100vh;
		background-color: #f0f0f0;
	}

	.list-item-btns {
		display: flex;
		gap: 5rpx;
	}
</style>