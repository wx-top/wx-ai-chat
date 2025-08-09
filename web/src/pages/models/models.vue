<template>
  <view class="container">
    <view class="header">
      <view class="title">选择模型</view>
    </view>

    <view class="model-list">
      <view 
        v-for="model in models" 
        :key="model.id"
        class="model-item"
        :class="{ 'selected': model.id === selectedModel?.id }"
        @click="selectModel(model)"
      >
        <view class="model-info">
          <view class="model-title">{{ model.description }}</view>
          <view class="model-name">{{ model.name }}</view>
        </view>
        <view class="model-status">
          <text v-if="model.id === selectedModel?.id" class="selected-icon">✓</text>
        </view>
      </view>
    </view>

    <view class="btn-container">
      <view class="confirm-btn" @click="confirmSelection" :class="{ 'disabled': !selectedModel }">
        <text>确认选择</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useModelStore } from '@/store/model.js'
import { storeToRefs } from 'pinia'

const modelStore = useModelStore()
const { models, selectedModel } = storeToRefs(modelStore)

// 选择模型
const selectModel = (model) => {
  modelStore.selectModel(model)
}

// 确认选择
const confirmSelection = () => {
  if (!selectedModel.value) return
  
  // 返回上一页
  uni.navigateBack()
}

// 页面加载时获取模型列表
onMounted(async () => {
  try {
    console.log('开始获取模型列表')
    await modelStore.fetchModels()
    console.log('模型列表:', models.value)
  } catch (error) {
    console.error('获取模型列表失败:', error)
    uni.showToast({
      title: '加载模型列表失败',
      icon: 'none'
    })
  }
})

// 监听模型列表变化
watch(models, (newModels) => {
  console.log('模型列表更新:', newModels)
}, { deep: true })
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 24rpx;
  box-sizing: border-box;
}

.header {
  text-align: center;
  margin-bottom: 48rpx;
  
  .title {
    font-size: 40rpx;
    font-weight: 700;
    color: #333;
    letter-spacing: 1rpx;
  }
}

.model-list {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
  border-radius: 24rpx;
  padding: 24rpx;
  margin-bottom: 48rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.08);
  border: 1rpx solid rgba(255, 255, 255, 0.8);
}

.model-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32rpx 24rpx;
  border-radius: 16rpx;
  margin-bottom: 16rpx;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  &:hover {
    background: rgba(0, 122, 255, 0.05);
    transform: translateY(-2rpx);
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
  }
  
  &.selected {
    background: linear-gradient(135deg, rgba(0, 122, 255, 0.1) 0%, rgba(0, 122, 255, 0.05) 100%);
    border: 2rpx solid rgba(0, 122, 255, 0.2);
    box-shadow: 0 4rpx 16rpx rgba(0, 122, 255, 0.15);
  }
}

.model-info {
  flex: 1;
  
  .model-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 8rpx;
    line-height: 1.4;
  }
  
  .model-name {
    font-size: 26rpx;
    color: #666;
    line-height: 1.3;
  }
}

.model-status {
  width: 60rpx;
  text-align: center;
  
  .selected-icon {
    color: #007AFF;
    font-size: 40rpx;
    font-weight: bold;
    text-shadow: 0 2rpx 4rpx rgba(0, 122, 255, 0.2);
  }
}

.btn-container {
  padding: 0 24rpx;
  
  .confirm-btn {
    width: 100%;
    height: 80rpx;
    background: linear-gradient(135deg, #007AFF 0%, #0056CC 100%);
    border-radius: 16rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 30rpx;
    font-weight: 600;
    box-shadow: 0 6rpx 20rpx rgba(0, 122, 255, 0.25);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    
    &:hover {
      background: linear-gradient(135deg, #0056CC 0%, #003d99 100%);
      transform: translateY(-2rpx);
      box-shadow: 0 8rpx 25rpx rgba(0, 122, 255, 0.35);
    }
    
    &:active {
      transform: translateY(0) scale(0.98);
      box-shadow: 0 4rpx 15rpx rgba(0, 122, 255, 0.2);
    }
    
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
      transition: left 0.5s;
    }
    
    &:hover::before {
      left: 100%;
    }
    
    &.disabled {
      background: linear-gradient(135deg, #cccccc 0%, #999999 100%);
      pointer-events: none;
      transform: none;
      box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
      
      &::before {
        display: none;
      }
    }
  }
}
</style>