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
  background-color: #f8f8f8;
  padding: 20rpx;
}

.header {
  text-align: center;
  margin-bottom: 40rpx;
  
  .title {
    font-size: 36rpx;
    font-weight: bold;
    color: #333;
  }
}

.model-list {
  background-color: #fff;
  border-radius: 20rpx;
  padding: 20rpx;
  margin-bottom: 40rpx;
}

.model-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
  
  &:last-child {
    border-bottom: none;
  }
  
  &.selected {
    background-color: #f8f8f8;
  }
}

.model-info {
  flex: 1;
  
  .model-title {
    font-size: 32rpx;
    color: #333;
    margin-bottom: 10rpx;
  }
  
  .model-name {
    font-size: 26rpx;
    color: #666;
  }
}

.model-status {
  width: 60rpx;
  text-align: center;
  
  .selected-icon {
    color: #07C160;
    font-size: 36rpx;
  }
}

.btn-container {
  padding: 0 40rpx;
  
  .confirm-btn {
    width: 100%;
    height: 88rpx;
    background: linear-gradient(135deg, #07C160, #1AAD19);
    border-radius: 44rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 32rpx;
    font-weight: 500;
    
    &.disabled {
      background: #ccc;
      pointer-events: none;
    }
  }
}
</style> 