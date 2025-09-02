export function isWechat() {   
     var ua = navigator.userAgent.toLowerCase()

        var isWXWork = ua.match(/wxwork/i) == 'wxwork'

        var isWeixin = !isWXWork && ua.match(/MicroMessenger/i) == 'micromessenger'
  
  return isWeixin

}

// 判断是否是移动设备
export function isMobile() {
  const ua = navigator.userAgent.toLowerCase()
  
  // 检测移动设备的关键词
  const mobileKeywords = [
    'mobile', 'android', 'iphone', 'ipad', 'ipod', 
    'blackberry', 'windows phone', 'opera mini', 
    'iemobile', 'webos', 'palm'
  ]
  
  // 检查是否包含移动设备关键词
  const hasMobileKeyword = mobileKeywords.some(keyword => ua.includes(keyword))
  
  // 检查屏幕宽度（作为辅助判断）
  const hasSmallScreen = window.screen && window.screen.width <= 768
  
  // 检查触摸支持
  const hasTouchSupport = 'ontouchstart' in window || navigator.maxTouchPoints > 0
  
  return hasMobileKeyword || (hasSmallScreen && hasTouchSupport)
}

// 判断是否是平板设备
export function isTablet() {
  const ua = navigator.userAgent.toLowerCase()
  
  // iPad 检测
  if (ua.includes('ipad')) {
    return true
  }
  
  // Android 平板检测（通常不包含 'mobile' 关键词）
  if (ua.includes('android') && !ua.includes('mobile')) {
    return true
  }
  
  // 屏幕尺寸判断（平板通常在 768px - 1024px 之间）
  if (window.screen && window.screen.width >= 768 && window.screen.width <= 1024) {
    return true
  }
  
  return false
}

// 获取设备类型
export function getDeviceType() {
  if (isTablet()) {
    return 'tablet'
  } else if (isWechat()) {
    return 'wechat'
  } else if (isMobile()) {
    return 'mobile'
  } else {
    return 'desktop'
  }
}