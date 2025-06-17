<template>
	<view class="container">
		<!-- 顶部操作栏：搜索框和创建按钮 -->
		<view class="header">
			<uni-search-bar :focus="true" v-model="keyword">
			</uni-search-bar>
			<button class="add-btn" type="primary" @click="addDialogToggle"><text class="button-text">添加</text></button>
		</view>

		<uni-popup ref="addDialog" type="dialog">
			<uni-popup-dialog mode="input" title="添加知识库" placeholder="请输入知识库名字"
				@confirm="dialogAddConfirm"></uni-popup-dialog>
		</uni-popup>

		<!-- 修改知识库弹窗 -->
		<uni-popup ref="editDialog" type="dialog">
			<uni-popup-dialog mode="input" title="修改知识库" placeholder="请输入知识库名字" :value="currentRepository?.name"
				@confirm="dialogEditConfirm"></uni-popup-dialog>
		</uni-popup>

		<uni-swipe-action>
			<uni-swipe-action-item v-for="item in repositoryList" :right-options="options"
				@click="onClick($event, item.id)">
				<view style="height: 80rpx; line-height: 80rpx;">{{ item.name }}</view>
			</uni-swipe-action-item>
		</uni-swipe-action>
	</view>
</template>

<script setup>
	import {
		ref,
		onMounted
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
	const options = ref([{
			text: '详情',
			style: {
				backgroundColor: '#007AFF'
			}
		},
		{
			text: '编辑',
			style: {
				backgroundColor: '#007AFF'
			}
		},
		{
			text: '删除',
			style: {
				backgroundColor: '#FF0000'
			}
		}
	])

	const addDialogToggle = () => {
		addDialog.value.open()
	}


	const onClick = ({
		index
	}, id) => {
		console.log('onClick', index)
		if (index === 0) {
			// 详情
			uni.navigateTo({
				url: `/pages/repository/detail?id=${id}`
			})
		} else if (index === 1) {
			// 编辑
			const repository = repositoryList.value.find(item => item.id === id)
			if (repository) {
				currentRepository.value = repository
				editDialog.value.open()
			}
		} else if (index === 2) {
			// 删除
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
	}

	const dialogAddConfirm = async (name) => {
		try {
			console.log("创建知识库", name)
			await addRepository({
				name
			})
			uni.showToast({
				title: "创建成功",
				icon: "success"
			})
			loadRepositoryList()
		} catch (error) {
			console.log("创建知识库失败", error)
			uni.showToast({
				title: "创建知识库失败",
				icon: "error"
			})
		}
	}

	const dialogEditConfirm = async (name) => {
		try {
			if (!currentRepository.value) return
			console.log("修改知识库", name)
			await updateRepository(currentRepository.value.id, {
				name
			})
			uni.showToast({
				title: "修改成功",
				icon: "success"
			})
			loadRepositoryList()
		} catch (error) {
			console.log("修改知识库失败", error)
			uni.showToast({
				title: "修改知识库失败",
				icon: "error"
			})
		}
	}

	const loadRepositoryList = async () => {
		try {
			repositoryList.value = await getRepositories() || []
			console.log("获取知识库", repositoryList.value)
		} catch (error) {
			console.log("获取知识库失败", error)
			uni.showToast({
				title: "获取知识库失败",
				icon: "error"
			})
		}
	}

	onMounted(() => {
		loadRepositoryList()
	})
</script>

<style lang="scss" scoped>
	.container {
		height: 100vh;
		padding: 20rpx 30rpx;
		background-color: #f8f9fa;

		.header {
			display: flex;
			align-items: center;
			gap: 20rpx;
			margin-bottom: 30rpx;

			.search {
				flex: 1;
				height: 72rpx;
				padding: 0 30rpx;
				border-radius: 36rpx;
				background-color: #ffffff;
				box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
				font-size: 28rpx;
				border: none;

				&::placeholder {
					color: #999;
				}
			}

			.add-btn {
				height: 52rpx;
				background: linear-gradient(135deg, #4CAF50, #45a049);
				font-size: 28rpx;
				display: flex;
				align-items: center;
				justify-content: center;
				padding: 0 40rpx;
				border-radius: 36rpx;
				color: #ffffff;
				box-shadow: 0 4rpx 12rpx rgba(76, 175, 80, 0.2);
				transition: all 0.3s ease;

				&:active {
					transform: scale(0.98);
					box-shadow: 0 2rpx 8rpx rgba(76, 175, 80, 0.2);
				}
			}
		}
	}
</style>