// 移动设备检测使用示例
import { useAppStore } from '@/store/app'
import { isMobile, isTablet, getDeviceType } from '@/utils/wx'

// 方法1: 直接使用工具函数
export function directDeviceDetection() {
  console.log('是否是移动设备:', isMobile())
  console.log('是否是平板设备:', isTablet())
  console.log('设备类型:', getDeviceType())
}

// 方法2: 在Vue组件中使用store
export function useDeviceDetectionInComponent() {
  // 在Vue组件的setup()函数中使用
  const appStore = useAppStore()
  
  return {
    // 基础检测
    isMobile: appStore.isMobile,
    isTablet: appStore.isTablet,
    isWechat: appStore.isWechat,
    deviceType: appStore.deviceType,
    
    // 组合检测
    isMobileDevice: appStore.isMobileDevice, // 手机或平板
    isDesktop: appStore.isDesktop,
    
    // 刷新设备信息的方法
    refreshDeviceInfo: appStore.refreshDeviceInfo
  }
}

// 方法3: 响应式布局示例
export function getResponsiveStyles() {
  const deviceType = getDeviceType()
  
  const styles = {
    mobile: {
      fontSize: '14px',
      padding: '10px',
      maxWidth: '100%'
    },
    tablet: {
      fontSize: '16px',
      padding: '15px',
      maxWidth: '768px'
    },
    desktop: {
      fontSize: '18px',
      padding: '20px',
      maxWidth: '1200px'
    }
  }
  
  return styles[deviceType] || styles.desktop
}

// 方法4: 条件渲染示例
export function shouldShowMobileUI() {
  return isMobile()
}

export function shouldShowTabletUI() {
  return isTablet()
}

export function shouldShowDesktopUI() {
  return getDeviceType() === 'desktop'
}

// 方法5: 动态类名生成
export function getDeviceClass() {
  const deviceType = getDeviceType()
  return `device-${deviceType}`
}

// 方法6: 媒体查询补充检测
export function enhancedMobileDetection() {
  const basicDetection = isMobile()
  
  // 结合CSS媒体查询进行更精确的检测
  const mediaQuery = window.matchMedia('(max-width: 768px)')
  const isSmallScreen = mediaQuery.matches
  
  return basicDetection || isSmallScreen
}

// 使用示例说明
/*
在Vue组件中的使用方法:

<template>
  <div :class="getDeviceClass()">
    <div v-if="isMobile">移动端内容</div>
    <div v-else-if="isTablet">平板端内容</div>
    <div v-else>桌面端内容</div>
  </div>
</template>

<script setup>
import { useAppStore } from '@/store/app'
import { storeToRefs } from 'pinia'

const appStore = useAppStore()
const { isMobile, isTablet, deviceType } = storeToRefs(appStore)

// 监听窗口大小变化
window.addEventListener('resize', () => {
  appStore.refreshDeviceInfo()
})
</script>

<style scoped>
.device-mobile {
  font-size: 14px;
}

.device-tablet {
  font-size: 16px;
}

.device-desktop {
  font-size: 18px;
}
</style>
*/