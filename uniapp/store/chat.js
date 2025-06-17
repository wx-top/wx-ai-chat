import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getChats, createChat, getMessages, sendMessage, deleteChat } from '@/api/chat'
import { useModelStore } from './model'

export const useChatStore = defineStore('chat', () => {
  // 聊天列表
  const chats = ref([])
  // 当前聊天ID
  const currentChatId = ref(null)
  // 当前聊天消息
  const currentMessages = ref([])
  // 当前知识库信息
  const currentRepository = ref(null)
  // 加载状态
  const loading = ref(false)
  // 流式响应状态
  const streaming = ref(false)

  const modelStore = useModelStore()

  // 获取聊天列表
  const fetchChats = async () => {
    try {
      const data = await getChats()
      chats.value = data
    } catch (error) {
      console.error('获取聊天列表失败', error)
      throw error
    }
  }

  // 创建新聊天
  const newChat = async (title) => {
    try {
      loading.value = true
      const data = await createChat({ title })
      chats.value.unshift(data)
      return data
    } catch (error) {
      console.error('创建聊天失败', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取聊天消息
  const fetchMessages = async (chatId) => {
    try {
      loading.value = true
      currentChatId.value = chatId
      const data = await getMessages(chatId)
      currentMessages.value = data
    } catch (error) {
      console.error('获取聊天消息失败：', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 发送消息
  const sendChatMessage = async (content, onChunkReceived) => {
    if (!currentChatId.value) {
      throw new Error('没有当前聊天')
    }
    if (!modelStore.selectedModel) {
      throw new Error('请先选择模型')
    }

    try {
      loading.value = true
      streaming.value = true
      
      // 立即添加用户消息到列表
      const userMessage = {
        role: 'user',
        content: content,
        created_at: new Date().toISOString()
      }
      currentMessages.value.push(userMessage)

      // 添加一个空的 AI 消息用于流式显示
      const aiMessage = {
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString()
      }
      currentMessages.value.push(aiMessage)

      // 发送消息到服务器
      const response = await sendMessage(
        currentChatId.value,
        content,
        modelStore.selectedModel.id,
        (chunk) => {
          // 更新 AI 消息内容
          aiMessage.content += chunk
          // 强制更新视图
          currentMessages.value = [...currentMessages.value]
        },
        currentRepository.value?.id
      )
      
      // 更新 AI 消息的完整内容
      aiMessage.content = response.content
      return response
    } catch (error) {
      console.error('发送消息失败', error)
      // 移除空的 AI 消息
      currentMessages.value.pop()
      throw error
    } finally {
      loading.value = false
      streaming.value = false
    }
  }

  // 清空当前聊天
  const clearCurrentChat = () => {
    currentChatId.value = null
    currentMessages.value = []
    currentRepository.value = null
  }

  // 删除聊天
  const removeChat = async (chatId) => {
    try {
      loading.value = true
      await deleteChat(chatId)
      // 从列表中移除
      chats.value = chats.value.filter(chat => chat.id !== chatId)
      // 如果删除的是当前聊天，清空当前聊天
      if (currentChatId.value === chatId) {
        clearCurrentChat()
      }
    } catch (error) {
      console.error('删除聊天失败', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 添加消息
  const addMessage = (message) => {
    if (!currentChatId.value) {
      throw new Error('没有当前聊天')
    }
    currentMessages.value.push(message)
  }

  // 设置当前知识库
  const setCurrentRepository = (repository) => {
    currentRepository.value = repository
  }

  return {
    chats,
    currentChatId,
    currentMessages,
    currentRepository,
    loading,
    streaming,
    fetchChats,
    newChat,
    fetchMessages,
    sendChatMessage,
    clearCurrentChat,
    removeChat,
    addMessage,
    setCurrentRepository
  }
})
