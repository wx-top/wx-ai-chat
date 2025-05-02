import http from '../utils/http.js'

// 获取模型列表
export const getModels = async () => {
  try {
    console.log('发送模型列表请求')
    const response = await http.get('/api/model/models')
    console.log('模型列表响应:', response)
    if (Array.isArray(response)) {
      return response
    }
    throw new Error('获取模型列表失败：响应数据格式错误')
  } catch (error) {
    console.error('获取模型列表失败', error)
    throw error
  }
}

// 创建模型
export const createModel = (data) => {
  return http.post('/api/model/models', data)
}

// 更新模型
export const updateModel = (modelId, data) => {
  return http.put(`/api/model/models/${modelId}`, data)
} 