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

export const sendMessageStream = async (chatId, content, modelId, onChunkReceived, repositoryId) => {
  try {
    const userStore = useUserStore()
    const token = userStore.getAccessToken

    const response = await http.post(`/api/chat/chats/${chatId}/messages/stream`, {
      content,
      model_id: modelId,
      repository_id: repositoryId
    }, {
      header: {
        'Authorization': `Bearer ${token}`
      }
    })

    // 由于微信小程序限制，这里可能无法实现真正的流式
    // 我们返回完整的响应，让前端模拟流式效果
    if (onChunkReceived && typeof onChunkReceived === 'function') {
      // 模拟流式效果，逐字符显示
      const text = response.content || response
      for (let i = 0; i < text.length; i++) {
        onChunkReceived(text[i])
        // 添加小延迟模拟流式效果
        await new Promise(resolve => setTimeout(resolve, 10))
      }
    }

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
