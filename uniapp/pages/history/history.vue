<template>
  <view class="history-container">
    <!-- 会话列表 -->
    <scroll-view class="chat-list" scroll-y="true">
      <view v-if="loading" class="loading">
        <text>加载中...</text>
      </view>
      <view v-else-if="chats.length === 0" class="empty">
        <text>暂无历史会话</text>
      </view>
      <view v-else class="chat-item" v-for="chat in chats" :key="chat.id">
        <view class="chat-info" @click="goToChat(chat.id)">
          <view class="chat-title">{{ chat.title }}</view>
          <view class="chat-meta">
            <text class="time">{{ formatTime(chat.created_at) }}</text>
          </view>
        </view>
        <view class="chat-actions">
          <button class="delete-btn" @click="deleteChat(chat.id)">删除</button>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { onMounted } from 'vue'
import { useChatStore } from '@/store/chat'
import { storeToRefs } from 'pinia'
 

const chatStore = useChatStore()
const { chats, loading, currentChatId, removeChat, fetchChats } = storeToRefs(chatStore)

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
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.chat-list {
  flex: 1;
  padding: 10px 0;
  /* 隐藏滚动条 */
  scrollbar-width: none;
  -ms-overflow-style: none;
}

/* 隐藏滚动条 */
.chat-list ::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
  color: transparent;
}

.loading, .empty {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
  color: #999;
}

.chat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: white;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chat-info {
  flex: 1;
  margin-right: 10px;
}

.chat-title {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 5px;
}

.chat-meta {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #999;
}

.chat-actions {
  display: flex;
  align-items: center;
}

.delete-btn {
  background-color: transparent;
  color: #ff3b30;
  font-size: 14px;
  padding: 5px 10px;
  border: none;
}

.delete-btn::after {
  border: none;
}
</style> 