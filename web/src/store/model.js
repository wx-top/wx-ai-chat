import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getModels, createModel, updateModel } from '@/api/model'

export const useModelStore = defineStore('model', () => {
  // 模型列表
  const models = ref([])
  // 加载状态
  const loading = ref(false)
  // 当前选择的模型
  const selectedModel = ref(null)

  // 获取模型列表
  const fetchModels = async () => {
    try {
      loading.value = true
      console.log('开始请求模型列表')
      const data = await getModels()
      console.log('获取到的模型数据:', data)
      if (data) {
        models.value = data
        console.log('更新后的模型列表:', models.value)
      }
    } catch (error) {
      console.error('获取模型列表失败', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建模型
  const newModel = async (name, description, isActive = true) => {
    try {
      loading.value = true
      const data = await createModel({
        name,
        description,
        is_active: isActive
      })
      models.value.push(data)
      return data
    } catch (error) {
      console.error('创建模型失败', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新模型
  const updateModelInfo = async (modelId, updates) => {
    try {
      loading.value = true
      const data = await updateModel(modelId, updates)
      // 更新模型列表中的对应模型
      const index = models.value.findIndex(m => m.id === modelId)
      if (index !== -1) {
        models.value[index] = { ...models.value[index], ...data }
      }
      return data
    } catch (error) {
      console.error('更新模型失败', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 选择模型
  const selectModel = (model) => {
    selectedModel.value = model
  }

  // 清空选择的模型
  const clearSelectedModel = () => {
    selectedModel.value = null
  }

  return {
    models,
    loading,
    selectedModel,
    fetchModels,
    newModel,
    updateModelInfo,
    selectModel,
    clearSelectedModel
  }
}) 