import {http} from '../utils/http.js'
import { useUserStore } from '../store/user.js'

// 获取聊天列表
export const getChats = () => {
  return http.get('/api/chat/chats')
}

// 创建聊天
export const createChat = (data) => {
  return http.post('/api/chat/chats', data)
}

// 获取聊天消息
export const getMessages = (chatId) => {
  return http.get(`/api/chat/chats/${chatId}/messages`)
}

// 发送消息
export const sendMessage = async (chatId, content, modelId, onChunkReceived, repositoryId) => {
  try {
    const userStore = useUserStore()
    const token = userStore.getAccessToken

    const response = await http.post(`/api/chat/chats/${chatId}/messages`, {
      content,
      model_id: modelId,
      repository_id: repositoryId
    }, {
      header: {
        'Authorization': `Bearer ${token}`
      }
    })

    // 直接返回响应数据，因为 http.js 已经处理了响应拦截
    return response
  } catch (error) {
    console.error('发送消息失败', error)
    throw error
  }
}

// 删除聊天
export const deleteChat = (chatId) => {
  return http.delete(`/api/chat/chats/${chatId}`)
} 
