import {http} from '../utils/http.js'

// 微信登录
export const wxlogin = (code) => {
  return http.post('/auth/wxlogin', { code })
}

// 账号登录
export const login = (username, password) => {
	return http.post('/auth/login', { username, password })
}

// 用户注册
export const register = (username, password, password_confirm) => {
	return http.post('/auth/register', { username, password, password_confirm })
}

// 刷新令牌
export const refreshToken = (refreshToken) => {
  return http.post('/auth/refresh', null, {
    header: {
      'Authorization': `Bearer ${refreshToken}`
    }
  })
}

// 登出
export const logout = () => {
  return http.post('/auth/logout')
}
