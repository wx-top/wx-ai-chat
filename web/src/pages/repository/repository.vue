<template>
	<view class="container">
		<!-- 顶部操作栏：搜索框和创建按钮 -->
		<view class="header">
			<up-search placeholder="搜索知识库" v-model="keyword" :clearabled="true" :showAction="false"></up-search>
			<button class="add-btn" type="primary" @click="addDialogToggle"><text class="button-text">添加</text></button>
		</view>

		<up-popup ref="addDialog" v-model:show="showAddDialog" mode="center" :round="10">
			<view class="dialog-content">
				<view class="dialog-title">添加知识库</view>
				<up-input v-model="addRepositoryName" placeholder="请输入知识库名字" class="dialog-input"></up-input>
				<view class="dialog-buttons">
					<up-button @click="showAddDialog = false" size="small" type="info" text="取消"></up-button>
					<up-button @click="dialogAddConfirm" size="small" type="primary" text="确定"></up-button>
				</view>
			</view>
		</up-popup>

		<!-- 修改知识库弹窗 -->
		<up-popup ref="editDialog" v-model:show="showEditDialog" mode="center" :round="10">
			<view class="dialog-content">
				<view class="dialog-title">修改知识库</view>
				<up-input v-model="editRepositoryName" placeholder="请输入知识库名字" class="dialog-input"></up-input>
				<view class="dialog-buttons">
					<up-button @click="showEditDialog = false" size="small" type="info" text="取消"></up-button>
					<up-button @click="dialogEditConfirm" size="small" type="primary" text="确定"></up-button>
				</view>
			</view>
		</up-popup>
		<up-list>
			<up-list-item v-for="(item, index) in repositoryList" :key="index">
				<up-cell :title="item.title">
					<template #title>
						<view class="list-item-title">
							<up-text type="primary" :text="item.name"></up-text>
							<!-- <up-text type="info" size="14" :text="formatTime(item.created_at)"></up-text> -->
						</view>
					</template>
					<template #right-icon>
						<view class="list-item-btns">
							<up-button type="success" @click="toDetail(item.id)" size="mini" text="详情"></up-button>
							<up-button type="primary" @click="editRep(item.id)" size="mini" text="修改"></up-button>
							<up-button type="error" @click="deleteRep(item.id)" size="mini" text="删除"></up-button>
						</view>
					</template>
				</up-cell>
			</up-list-item>
		</up-list>
	</view>
</template>

<script setup>
	import {
		ref,
		onMounted,
		watch
	} from 'vue'
	import {
		addRepository,
		getRepositories,
		updateRepository,
		deleteRepository
	} from '@/api/repository'
	const keyword = ref('')
const repositoryList = ref([])
const addDialog = ref(null)
const editDialog = ref(null)
const currentRepository = ref(null)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const addRepositoryName = ref('')
const editRepositoryName = ref('')

	const addDialogToggle = () => {
		addRepositoryName.value = ''
		showAddDialog.value = true
	}

	const toDetail = (id) => {
		uni.navigateTo({
			url: `/pages/repository/detail?id=${id}`
		})
	}

	const editRep = (id) => {
		const repository = repositoryList.value.find(item => item.id === id)
		if (repository) {
			currentRepository.value = repository
			editRepositoryName.value = repository.name
			showEditDialog.value = true
		}
	}
	const deleteRep = (id) => {
		uni.showModal({
			title: '提示',
			content: '确定要删除该知识库吗？删除后无法恢复。',
			confirmColor: '#FF0000',
			success: async (res) => {
				if (res.confirm) {
					try {
						await deleteRepository(id)
						uni.showToast({
							title: '删除成功',
							icon: 'success'
						})
						loadRepositoryList()
					} catch (error) {
						console.log("删除知识库失败", error)
						uni.showToast({
							title: '删除失败',
							icon: 'error'
						})
					}
				}
			}
		})
	}

	const dialogAddConfirm = async () => {
		if (!addRepositoryName.value.trim()) {
			uni.showToast({
				title: "请输入知识库名称",
				icon: "none"
			})
			return
		}
		try {
			console.log("创建知识库", addRepositoryName.value)
			await addRepository({
				name: addRepositoryName.value
			})
			uni.showToast({
				title: "创建成功",
				icon: "success"
			})
			showAddDialog.value = false
			loadRepositoryList()
		} catch (error) {
			console.log("创建知识库失败", error)
			uni.showToast({
				title: "创建知识库失败",
				icon: "error"
			})
		}
	}

	const dialogEditConfirm = async () => {
		if (!editRepositoryName.value.trim()) {
			uni.showToast({
				title: "请输入知识库名称",
				icon: "none"
			})
			return
		}
		try {
			if (!currentRepository.value) return
			console.log("修改知识库", editRepositoryName.value)
			await updateRepository(currentRepository.value.id, {
				name: editRepositoryName.value
			})
			uni.showToast({
				title: "修改成功",
				icon: "success"
			})
			showEditDialog.value = false
			loadRepositoryList()
		} catch (error) {
			console.log("修改知识库失败", error)
			uni.showToast({
				title: "修改知识库失败",
				icon: "error"
			})
		}
	}

	const loadRepositoryList = async (searchKeyword = '') => {
		try {
			repositoryList.value = await getRepositories(searchKeyword) || []
			console.log("获取知识库", repositoryList.value)
		} catch (error) {
			console.log("获取知识库失败", error)
			uni.showToast({
				title: "获取知识库失败",
				icon: "error"
			})
		}
	}

	// 监听搜索关键字变化
	watch(keyword, (newKeyword) => {
		loadRepositoryList(newKeyword.trim())
	})

	onMounted(() => {
		loadRepositoryList()
	})
</script>

<style lang="scss" scoped>
	.container {
		height: 100vh;
		padding: 120rpx 24rpx 180rpx;
		background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
		box-sizing: border-box;
	}

	/* H5平台样式修复 */
	/* #ifdef H5 */
	.container {
		height: 100vh;
		max-height: 100vh;
		overflow-y: auto;
		box-sizing: border-box;
		padding: 120rpx 24rpx 180rpx;
	}
	/* #endif */

	.header {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 999;
		display: flex;
		align-items: center;
		gap: 16rpx;
		padding: 32rpx 24rpx;
		background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
		box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
		border-bottom: 1rpx solid rgba(0, 0, 0, 0.05);
		backdrop-filter: blur(10rpx);

		.add-btn {
			height: 64rpx;
			background: linear-gradient(135deg, #007AFF 0%, #0056CC 100%);
			font-size: 28rpx;
			display: flex;
			align-items: center;
			justify-content: center;
			padding: 0 32rpx;
			border-radius: 16rpx;
			color: #ffffff;
			box-shadow: 0 6rpx 20rpx rgba(0, 122, 255, 0.25);
			transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
			position: relative;
			overflow: hidden;
			border: none;
			font-weight: 600;

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
		}
	}

	.list-item-btns {
		display: flex;
		gap: 12rpx;
		align-items: center;
	}

	.dialog-content {
		padding: 48rpx;
		background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
		border-radius: 24rpx;
		min-width: 500rpx;
		box-shadow: 0 12rpx 40rpx rgba(0, 0, 0, 0.15);
		border: 1rpx solid rgba(255, 255, 255, 0.8);

		.dialog-title {
			font-size: 36rpx;
			font-weight: 700;
			text-align: center;
			margin-bottom: 32rpx;
			color: #333;
			letter-spacing: 1rpx;
		}

		.dialog-input {
			margin-bottom: 32rpx;
		}

		.dialog-buttons {
			display: flex;
			justify-content: space-between;
			gap: 24rpx;
		}
	}

	/* 自定义搜索框样式 */
	:deep(.u-search) {
		flex: 1;
		border-radius: 16rpx;
		box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
		background: #ffffff;
		border: 1rpx solid rgba(255, 255, 255, 0.8);
	}

	:deep(.u-search__content) {
		border-radius: 16rpx;
		background: #ffffff;
		border: none;
		box-shadow: inset 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
		height: 64rpx;
	}

	/* 自定义列表样式 */
	:deep(.u-list-item) {
		margin-bottom: 20rpx;
		border-radius: 16rpx;
		background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
		box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
		border: 1rpx solid rgba(255, 255, 255, 0.8);
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		overflow: hidden;
	}

	:deep(.u-list-item:hover) {
		transform: translateY(-2rpx);
		box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.12);
	}

	:deep(.u-cell) {
		padding: 24rpx;
		background: transparent;
		border: none;
	}

	/* 自定义按钮样式 */
	:deep(.u-button--success) {
		background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
		border: none;
		border-radius: 12rpx;
		box-shadow: 0 4rpx 12rpx rgba(82, 196, 26, 0.25);
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		font-weight: 600;
	}

	:deep(.u-button--success:hover) {
		background: linear-gradient(135deg, #389e0d 0%, #237804 100%);
		transform: translateY(-1rpx);
		box-shadow: 0 6rpx 16rpx rgba(82, 196, 26, 0.35);
	}

	:deep(.u-button--primary) {
		background: linear-gradient(135deg, #007AFF 0%, #0056CC 100%);
		border: none;
		border-radius: 12rpx;
		box-shadow: 0 4rpx 12rpx rgba(0, 122, 255, 0.25);
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		font-weight: 600;
	}

	:deep(.u-button--primary:hover) {
		background: linear-gradient(135deg, #0056CC 0%, #003d99 100%);
		transform: translateY(-1rpx);
		box-shadow: 0 6rpx 16rpx rgba(0, 122, 255, 0.35);
	}

	:deep(.u-button--error) {
		background: linear-gradient(135deg, #ff4757 0%, #ff3742 100%);
		border: none;
		border-radius: 12rpx;
		box-shadow: 0 4rpx 12rpx rgba(255, 71, 87, 0.25);
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		font-weight: 600;
	}

	:deep(.u-button--error:hover) {
		background: linear-gradient(135deg, #ff3742 0%, #ff1e2d 100%);
		transform: translateY(-1rpx);
		box-shadow: 0 6rpx 16rpx rgba(255, 71, 87, 0.35);
	}

	:deep(.u-button--info) {
		background: linear-gradient(135deg, #909399 0%, #73767a 100%);
		border: none;
		border-radius: 12rpx;
		box-shadow: 0 4rpx 12rpx rgba(144, 147, 153, 0.25);
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		font-weight: 600;
	}

	:deep(.u-button--info:hover) {
		background: linear-gradient(135deg, #73767a 0%, #606266 100%);
		transform: translateY(-1rpx);
		box-shadow: 0 6rpx 16rpx rgba(144, 147, 153, 0.35);
	}

	:deep(.u-button--mini) {
		height: 56rpx;
		min-width: 80rpx;
		font-size: 24rpx;
		padding: 0 16rpx;
	}

	:deep(.u-button--small) {
		height: 64rpx;
		min-width: 120rpx;
		font-size: 28rpx;
		padding: 0 24rpx;
		border-radius: 16rpx;
	}

	/* 文本样式优化 */
	:deep(.u-text--primary) {
		font-weight: 600;
		font-size: 30rpx;
		color: #333333;
	}

	/* 输入框样式优化 */
	:deep(.u-input) {
		background: #ffffff;
		border: none;
		border-radius: 16rpx;
		box-shadow: inset 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
		transition: all 0.3s ease;
		height: 80rpx;
		padding: 0 24rpx;
		font-size: 28rpx;
	}

	:deep(.u-input:focus) {
		box-shadow: inset 0 2rpx 8rpx rgba(0, 0, 0, 0.06), 0 0 0 3rpx rgba(0, 122, 255, 0.1);
		transform: translateY(-1rpx);
	}
</style>