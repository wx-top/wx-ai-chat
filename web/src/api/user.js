import {http} from '../utils/http.js'
import { useUserStore } from '../store/user.js'

// 获取用户信息
export const getProfile = () => {
  return http.get('/user/profile')
}

// 更新用户信息
export const updateProfile = (data) => {
  return http.put('/user/profile', data)
}

// 上传头像
export const uploadAvatar = (filePath) => {
  return http.upload('/user/avatar', filePath, {
    header: {
      'Authorization': `Bearer ${useUserStore().getAccessToken}`
    }
  }).catch(error => {
    // 处理特定错误码
    if (error.message.includes('400')) {
      throw new Error('请选择正确的图片文件（支持png、jpg、jpeg、gif格式）')
    } else if (error.message.includes('401')) {
      throw new Error('登录已过期，请重新登录')
    } else if (error.message.includes('404')) {
      throw new Error('用户不存在')
    }
    throw error
  })
} 