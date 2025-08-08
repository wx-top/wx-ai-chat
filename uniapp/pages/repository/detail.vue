<template>
	<view class="repository-detail">
		<!-- 顶部操作栏：搜索框和添加文件按钮 -->
		<view class="header">
			<up-search placeholder="搜索文件" v-model="keyword" :clearabled="true" :showAction="false" @change="onSearchChange" @clear="onSearchChange"></up-search>
			<button class="add-btn" type="primary" @click="showFilePicker">
				<text class="button-text">添加</text>
			</button>
		</view>

		<!-- 文件选择弹窗 -->
		<up-popup v-model:show="filePickerPopup" mode="bottom">
			<view class="file-picker-popup">
				<view class="popup-title">选择文件</view>
				<uni-file-picker v-model="selectedFiles" file-mediatype="all" :limit="1" :auto-upload="false"
					@select="selectFile"></uni-file-picker>
				<view class="popup-buttons">
					<button class="cancel-btn" @click="closeFilePicker">取消</button>
					<button class="confirm-btn" @click="confirmUpload">确定</button>
				</view>
			</view>
		</up-popup>
		<up-list>
			<up-list-item v-for="(item, index) in filteredFileList" :key="index">
				<up-cell :title="item.title">
					<template #title>
						<view class="list-item-title">
							<up-text type="primary" :text="item.name"></up-text>
							<up-text type="info" size="14" :text="formatFileSize(item.size)"></up-text>
						</view>
					</template>
					<template #right-icon>
						<view class="list-item-btns">
							<up-button type="success" @click="toDetail(item.id)" size="mini" text="详情"></up-button>
							<up-button type="error" @click="deleteFileById(item.id)" size="mini" text="删除"></up-button>
						</view>
					</template>
				</up-cell>
			</up-list-item>
		</up-list>
	</view>
</template>

<script setup>
import { onLoad } from '@dcloudio/uni-app'
import { ref, onMounted } from 'vue'
import { getRepositoryFilesById, uploadFile, deleteFile } from '@/api/repository'
import { config } from '@/utils/http'

const repositoryId = ref(null)
const keyword = ref('')
const fileList = ref([])
const filteredFileList = ref([])
const selectedFiles = ref([])
const currentFile = ref(null)
const filePickerPopup = ref(false)

onLoad((option) => {
	repositoryId.value = option.id
	if (!repositoryId.value) {
		uni.showToast({
			title: '未传递参数id',
			icon: 'none',
			duration: 1500
		});
		uni.navigateBack()
	}
})

const showFilePicker = () => {
	filePickerPopup.value = true
}

const closeFilePicker = () => {
	filePickerPopup.value = false
	selectedFiles.value = []
	currentFile.value = null
}

const selectFile = (e) => {
	console.log('选择文件：', e)
	if (e.tempFiles && e.tempFiles.length > 0) {
		currentFile.value = e.tempFiles[0]
		console.log('当前选择的文件：', currentFile.value)
	}
}

const confirmUpload = async () => {
	if (!currentFile.value) {
		uni.showToast({
			title: '请选择文件',
			icon: 'none'
		})
		return
	}

	// 检查文件路径
	const filePath = currentFile.value.path || currentFile.value.url
	if (!filePath) {
		uni.showToast({
			title: '文件路径无效',
			icon: 'none'
		})
		return
	}

	try {
		uni.showLoading({
			title: '上传中...'
		})
		
		// 使用正确的文件路径和名称
		const fileName = currentFile.value.name || currentFile.value.file?.name || '未知文件'
		console.log('准备上传文件：', { filePath, fileName })
		
		await uploadFile(repositoryId.value, { path: filePath }, fileName)
		uni.hideLoading()
		uni.showToast({
			title: '上传成功',
			icon: 'success'
		})
		closeFilePicker()
		loadFileList()
	} catch (error) {
		uni.hideLoading()
		console.log('上传失败：', error)
		uni.showToast({
			title: `上传失败: ${error.message || error}`,
			icon: 'error'
		})
	}
}
const toDetail = (id) => {
	const file = fileList.value.find(item => item.id === id)
	if (!file) return

	uni.showLoading({
		title: '加载中...'
	})

	// 构建完整的文件URL
	const fileUrl = config.baseURL + file.file

	// 下载文件
	uni.downloadFile({
		url: fileUrl,
		success: function (res) {
			if (res.statusCode === 200) {
				// 打开文档
				uni.openDocument({
					filePath: res.tempFilePath,
					showMenu: true,
					success: function () {
						console.log('打开文档成功')
					},
					fail: function (error) {
						console.error('打开文档失败：', error)
						uni.showToast({
							title: '打开文档失败',
							icon: 'error'
						})
					}
				})
			} else {
				uni.showToast({
					title: '下载文件失败',
					icon: 'error'
				})
			}
		},
		fail: function (error) {
			console.error('下载文件失败：', error)
			uni.showToast({
				title: '下载文件失败',
				icon: 'error'
			})
		},
		complete: function () {
			uni.hideLoading()
		}
	})
}


const deleteFileById = (id) => {
	uni.showModal({
		title: '提示',
		content: '确定要删除该文件吗？',
		success: async (res) => {
			if (res.confirm) {
				try {
					await deleteFile(repositoryId.value, id)
					uni.showToast({
						title: '删除成功',
						icon: 'success'
					})
					loadFileList()
				} catch (error) {
					console.log('删除失败：', error)
					uni.showToast({
						title: '删除失败',
						icon: 'error'
					})
				}
			}
		}
	})
}

const formatFileSize = (size) => {
	if (!size) return '0 B'
	const units = ['B', 'KB', 'MB', 'GB']
	let index = 0
	while (size >= 1024 && index < units.length - 1) {
		size /= 1024
		index++
	}
	return `${size.toFixed(2)} ${units[index]}`
}

const loadFileList = async () => {
	try {
		fileList.value = await getRepositoryFilesById(repositoryId.value) || []
		filterFileList()
	} catch (error) {
		console.log("获取文件列表失败", error)
		uni.showToast({
			title: '获取文件列表失败',
			icon: 'error'
		})
	}
}

// 文件搜索过滤
const filterFileList = () => {
	if (!keyword.value.trim()) {
		filteredFileList.value = fileList.value
	} else {
		filteredFileList.value = fileList.value.filter(file => 
			file.name.toLowerCase().includes(keyword.value.toLowerCase())
		)
	}
}

// 监听搜索关键词变化
const onSearchChange = () => {
	filterFileList()
}

onMounted(() => {
	loadFileList()
})
</script>

<style lang="scss" scoped>
.repository-detail {
	height: 100vh;
	padding: 24rpx;
	background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
	box-sizing: border-box;

	.header {
		display: flex;
		align-items: center;
		gap: 24rpx;
		margin-bottom: 32rpx;

		.add-btn {
			height: 80rpx;
			background: linear-gradient(135deg, #007AFF 0%, #0056CC 100%);
			font-size: 30rpx;
			font-weight: 600;
			display: flex;
			align-items: center;
			justify-content: center;
			padding: 0 32rpx;
			border-radius: 16rpx;
			color: #ffffff;
			box-shadow: 0 8rpx 24rpx rgba(0, 122, 255, 0.3);
			transition: all 0.3s ease;
			position: relative;
			overflow: hidden;

			&::before {
				content: '';
				position: absolute;
				top: 0;
				left: -100%;
				width: 100%;
				height: 100%;
				background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
				transition: left 0.6s ease;
			}

			&:hover {
				transform: translateY(-2rpx);
				box-shadow: 0 12rpx 32rpx rgba(0, 122, 255, 0.4);

				&::before {
					left: 100%;
				}
			}

			&:active {
				transform: scale(0.98);
				box-shadow: 0 4rpx 16rpx rgba(0, 122, 255, 0.3);
			}
		}
	}

	.file-picker-popup {
		background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
		border-radius: 24rpx;
		padding: 48rpx;
		width: 600rpx;
		box-shadow: 0 16rpx 48rpx rgba(0, 0, 0, 0.15);
		border: 2rpx solid rgba(255, 255, 255, 0.8);

		.popup-title {
			font-size: 36rpx;
			font-weight: 700;
			text-align: center;
			margin-bottom: 40rpx;
			color: #333333;
			letter-spacing: 1rpx;
		}

		.popup-buttons {
			display: flex;
			justify-content: space-between;
			margin-top: 40rpx;
			gap: 24rpx;

			button {
				flex: 1;
				height: 80rpx;
				line-height: 80rpx;
				text-align: center;
				border-radius: 16rpx;
				font-size: 30rpx;
				font-weight: 600;
				transition: all 0.3s ease;
				position: relative;
				overflow: hidden;

				&::before {
					content: '';
					position: absolute;
					top: 0;
					left: -100%;
					width: 100%;
					height: 100%;
					background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
					transition: left 0.6s ease;
				}

				&:hover {
					transform: translateY(-2rpx);

					&::before {
						left: 100%;
					}
				}

				&:active {
					transform: scale(0.98);
				}
			}

			.cancel-btn {
				background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
				color: #666666;
				box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);

				&:hover {
					box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.15);
				}
			}

			.confirm-btn {
				background: linear-gradient(135deg, #007AFF 0%, #0056CC 100%);
				color: #ffffff;
				box-shadow: 0 8rpx 24rpx rgba(0, 122, 255, 0.3);

				&:hover {
					box-shadow: 0 12rpx 32rpx rgba(0, 122, 255, 0.4);
				}
			}
		}
	}

	.file-item {
		height: 80rpx;
		line-height: 80rpx;
		display: flex;
		justify-content: space-between;
		align-items: center;

		.file-name {
			font-size: 28rpx;
			color: #333;
		}

		.file-size {
			font-size: 24rpx;
			color: #999;
		}
	}
}

/* 自定义搜索框样式 */
:deep(.u-search) {
	flex: 1;
	border-radius: 16rpx;
	box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
	background: #ffffff;
	border: 2rpx solid rgba(0, 122, 255, 0.1);
	transition: all 0.3s ease;
}

:deep(.u-search__content) {
	border-radius: 16rpx;
	background: #ffffff;
	border: none;
}

/* 自定义列表项样式 */
:deep(.u-list-item) {
	margin-bottom: 16rpx;
	border-radius: 16rpx;
	background: #ffffff;
	box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
	border: 2rpx solid rgba(0, 122, 255, 0.05);
	transition: all 0.3s ease;
	overflow: hidden;
}

:deep(.u-list-item:hover) {
	transform: translateY(-2rpx);
	box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.12);
	border-color: rgba(0, 122, 255, 0.2);
}

:deep(.u-cell) {
	padding: 24rpx;
	background: transparent;
	border-bottom: none;
}

/* 自定义按钮样式 */
:deep(.u-button--success) {
	background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
	border: none !important;
	border-radius: 12rpx !important;
	box-shadow: 0 4rpx 12rpx rgba(40, 167, 69, 0.3) !important;
	transition: all 0.3s ease !important;
	font-weight: 600 !important;
}

:deep(.u-button--success:hover) {
	transform: translateY(-1rpx) !important;
	box-shadow: 0 6rpx 16rpx rgba(40, 167, 69, 0.4) !important;
}

:deep(.u-button--error) {
	background: linear-gradient(135deg, #dc3545 0%, #e74c3c 100%) !important;
	border: none !important;
	border-radius: 12rpx !important;
	box-shadow: 0 4rpx 12rpx rgba(220, 53, 69, 0.3) !important;
	transition: all 0.3s ease !important;
	font-weight: 600 !important;
}

:deep(.u-button--error:hover) {
	transform: translateY(-1rpx) !important;
	box-shadow: 0 6rpx 16rpx rgba(220, 53, 69, 0.4) !important;
}

:deep(.u-button--mini) {
	height: 56rpx !important;
	min-width: 80rpx !important;
	font-size: 24rpx !important;
	padding: 0 16rpx !important;
}

/* 文本样式 */
:deep(.u-text--primary) {
	font-weight: 600 !important;
	font-size: 30rpx !important;
	color: #333333 !important;
}

:deep(.u-text--info) {
	color: #999999 !important;
	font-size: 24rpx !important;
}

.list-item-title {
	display: flex;
	flex-direction: column;
	gap: 8rpx;
	align-items: flex-start;
}

.list-item-btns {
	display: flex;
	gap: 12rpx;
	align-items: center;
}
</style>
