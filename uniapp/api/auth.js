import http from '../utils/http.js'

// 微信登录
export const login = (code) => {
  return http.post('/api/auth/login', { code })
}

// 刷新令牌
export const refreshToken = (refreshToken) => {
  return http.post('/api/auth/refresh', null, {
    header: {
      'Authorization': `Bearer ${refreshToken}`
    }
  })
}

// 登出
export const logout = () => {
  return http.post('/api/auth/logout')
}
