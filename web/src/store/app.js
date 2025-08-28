import { defineStore } from 'pinia'
import { getDeviceType } from '@/utils/wx'

export const useAppStore = defineStore('app', {
  state: () => ({
    deviceType: getDeviceType()
  }),

  getters: {
  },

  actions: {
    // 刷新设备信息（在窗口大小改变时可能需要）
    refreshDeviceInfo() {
      this.deviceType = getDeviceType()
    }
  }
})