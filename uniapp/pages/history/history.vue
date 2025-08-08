<template>
	<view class="history-container">
		<!-- 会话列表 -->
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

<style scoped>
	.history-container {
		padding: 32rpx 24rpx 180rpx;
		height: 100vh;
		background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
		box-sizing: border-box;
	}

	/* H5平台样式修复 */
	/* #ifdef H5 */
	.history-container {
		height: 100vh;
		max-height: 100vh;
		overflow-y: auto;
		box-sizing: border-box;
		padding: 32rpx 24rpx 180rpx;
	}
	/* #endif */

	.list-item-title {
		display: flex;
		flex-direction: column;
		gap: 8rpx;
	}

	.list-item-btns {
		display: flex;
		gap: 12rpx;
		align-items: center;
	}

	/* 自定义搜索框样式 */
	:deep(.u-search) {
		margin-bottom: 32rpx;
		border-radius: 16rpx;
		box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
		background: #ffffff;
		border: 1rpx solid rgba(255, 255, 255, 0.8);
	}

	:deep(.u-search__content) {
		border-radius: 16rpx;
		background: #ffffff;
		border: none;
		box-shadow: inset 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
	}

	/* 自定义列表样式 */
	:deep(.u-list-item) {
		margin-bottom: 20rpx;
		border-radius: 16rpx;
		background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
		box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
		border: 1rpx solid rgba(255, 255, 255, 0.8);
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		overflow: hidden;
	}

	:deep(.u-list-item:hover) {
		transform: translateY(-2rpx);
		box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.12);
	}

	:deep(.u-cell) {
		padding: 24rpx;
		background: transparent;
		border: none;
	}

	/* 自定义按钮样式 */
	:deep(.u-button--success) {
		background: linear-gradient(135deg, #007AFF 0%, #0056CC 100%);
		border: none;
		border-radius: 12rpx;
		box-shadow: 0 4rpx 12rpx rgba(0, 122, 255, 0.25);
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		font-weight: 600;
	}

	:deep(.u-button--success:hover) {
		background: linear-gradient(135deg, #0056CC 0%, #003d99 100%);
		transform: translateY(-1rpx);
		box-shadow: 0 6rpx 16rpx rgba(0, 122, 255, 0.35);
	}

	:deep(.u-button--error) {
		background: linear-gradient(135deg, #ff4757 0%, #ff3742 100%);
		border: none;
		border-radius: 12rpx;
		box-shadow: 0 4rpx 12rpx rgba(255, 71, 87, 0.25);
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		font-weight: 600;
	}

	:deep(.u-button--error:hover) {
		background: linear-gradient(135deg, #ff3742 0%, #ff1e2d 100%);
		transform: translateY(-1rpx);
		box-shadow: 0 6rpx 16rpx rgba(255, 71, 87, 0.35);
	}

	:deep(.u-button--mini) {
		height: 56rpx;
		min-width: 80rpx;
		font-size: 24rpx;
		padding: 0 16rpx;
	}

	/* 文本样式优化 */
	:deep(.u-text--primary) {
		font-weight: 600;
		font-size: 30rpx;
		color: #333333;
	}

	:deep(.u-text--info) {
		color: #999999;
		font-size: 24rpx;
	}
</style>