import { defineStore } from 'pinia'
import { refreshToken, logout } from '@/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    access_token: null,
    refresh_token: null,
    userInfo: null,
    isLogin: false
  }),

  getters: {
    // 获取用户信息
    getUserInfo: (state) => state.userInfo,
    // 获取登录状态
    getLoginStatus: (state) => state.isLogin,
    // 获取 access_token
    getAccessToken: (state) => state.access_token
  },

  actions: {
    // 设置登录状态
    setLoginStatus(status) {
      this.isLogin = status
      this.saveToStorage()
    },

    // 设置用户信息
    setUserInfo(info) {
      this.userInfo = info
      this.saveToStorage()
    },

    // 设置 access_token
    setAccessToken(token) {
      this.access_token = token
      this.saveToStorage()
    },

    // 设置刷新令牌
    setRefreshToken(token) {
      this.refresh_token = token
      this.saveToStorage()
    },

    // 保存到本地存储
    saveToStorage() {
      try {
        uni.setStorageSync('user_info', JSON.stringify(this.userInfo))
        uni.setStorageSync('access_token', this.access_token)
        uni.setStorageSync('refresh_token', this.refresh_token)
        uni.setStorageSync('user_login_status', this.isLogin)
      } catch (e) {
        console.error('保存用户数据失败', e)
      }
    },

    // 从本地存储加载
    loadFromStorage() {
      try {
        const userInfoStr = uni.getStorageSync('user_info')
        if (userInfoStr) {
          this.userInfo = JSON.parse(userInfoStr)
        }
        
        const accessToken = uni.getStorageSync('access_token')
        if (accessToken) {
          this.access_token = accessToken
        }
        
        const refreshToken = uni.getStorageSync('refresh_token')
        if (refreshToken) {
          this.refresh_token = refreshToken
        }
        
        const loginStatus = uni.getStorageSync('user_login_status')
        if (loginStatus) {
          this.isLogin = loginStatus
        }
      } catch (e) {
        console.error('加载用户数据失败', e)
      }
    },

    // 刷新 token
    async refreshToken() {
      try {
        if (!this.refresh_token) {
          throw new Error('刷新令牌不存在')
        }
        
        const result = await refreshToken(this.refresh_token)
        this.setAccessToken(result.access_token)
        return result.access_token
      } catch (error) {
        console.error('刷新令牌失败', error)
        this.clearUserInfo()
        throw error
      }
    },

    // 登出
    async handleLogout() {
      try {
        if (this.access_token) {
          await logout()
        }
      } catch (error) {
        console.error('登出失败', error)
      } finally {
        this.clearUserInfo()
      }
    },

    // 清除用户信息
    clearUserInfo() {
      this.access_token = null
      this.refresh_token = null
      this.userInfo = null
      this.isLogin = false
      
      try {
        uni.removeStorageSync('user_info')
        uni.removeStorageSync('access_token')
        uni.removeStorageSync('refresh_token')
        uni.removeStorageSync('user_login_status')
      } catch (e) {
        console.error('清除用户数据失败', e)
      }
    }
  }
}) 