<template>
	<view class="repository-detail">
		<!-- 顶部操作栏：搜索框和添加文件按钮 -->
		<view class="header">
			<uni-search-bar :focus="true" v-model="keyword">
			</uni-search-bar>
			<button class="add-btn" type="primary" @click="showFilePicker">
				<text class="button-text">添加</text>
			</button>
		</view>

		<!-- 文件选择弹窗 -->
		<uni-popup ref="filePickerPopup" type="center">
			<view class="file-picker-popup">
				<view class="popup-title">选择文件</view>
				<uni-file-picker 
					v-model="selectedFiles"
					file-mediatype="all"
					:limit="1"
					:auto-upload="false"
					@select="selectFile"
				></uni-file-picker>
				<view class="popup-buttons">
					<button class="cancel-btn" @click="closeFilePicker">取消</button>
					<button class="confirm-btn" @click="confirmUpload">确定</button>
				</view>
			</view>
		</uni-popup>

		<!-- 文件列表 -->
		<uni-swipe-action>
			<uni-swipe-action-item v-for="item in fileList" :right-options="options" @click="onClick($event, item.id)">
				<view class="file-item">
					<text class="file-name">{{ item.name }}</text>
					<text class="file-size">{{ formatFileSize(item.size) }}</text>
				</view>
			</uni-swipe-action-item>
		</uni-swipe-action>
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
const filePickerPopup = ref(null)
const selectedFiles = ref([])
const currentFile = ref(null)

const options = ref([
	{
		text: '详情',
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
	filePickerPopup.value.open()
}

const closeFilePicker = () => {
	filePickerPopup.value.close()
	selectedFiles.value = []
	currentFile.value = null
}

const selectFile = (e) => {
	console.log('选择文件：', e)
	currentFile.value = e.tempFiles[0]
}

const confirmUpload = async () => {
	if (!currentFile.value) {
		uni.showToast({
			title: '请选择文件',
			icon: 'none'
		})
		return
	}

	try {
		uni.showLoading({
			title: '上传中...'
		})
		await uploadFile(repositoryId.value, currentFile.value, currentFile.value.name)
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
			title: '上传失败',
			icon: 'error'
		})
	}
}

const onClick = ({index}, id) => {
	if (index === 0) {
		// 详情 - 打开文档
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
	} else if (index === 1) {
		// 删除
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
	} catch (error) {
		console.log("获取文件列表失败", error)
		uni.showToast({
			title: '获取文件列表失败',
			icon: 'error'
		})
	}
}

onMounted(() => {
	loadFileList()
})
</script>

<style lang="scss" scoped>
.repository-detail {
	height: 100vh;
	padding: 20rpx 30rpx;
	background-color: #f8f9fa;

	.header {
		display: flex;
		align-items: center;
		gap: 20rpx;
		margin-bottom: 30rpx;

		.add-btn {
			height: 52rpx;
			background: linear-gradient(135deg, #4CAF50, #45a049);
			font-size: 28rpx;
			display: flex;
			align-items: center;
			justify-content: center;
			padding: 0 40rpx;
			border-radius: 26rpx;
			color: #ffffff;
			box-shadow: 0 4rpx 12rpx rgba(76, 175, 80, 0.2);
			transition: all 0.3s ease;

			&:active {
				transform: scale(0.98);
				box-shadow: 0 2rpx 8rpx rgba(76, 175, 80, 0.2);
			}
		}
	}

	.file-picker-popup {
		background-color: #ffffff;
		border-radius: 12rpx;
		padding: 30rpx;
		width: 600rpx;

		.popup-title {
			font-size: 32rpx;
			font-weight: bold;
			text-align: center;
			margin-bottom: 30rpx;
		}

		.popup-buttons {
			display: flex;
			justify-content: space-between;
			margin-top: 30rpx;
			gap: 20rpx;

			button {
				flex: 1;
				height: 80rpx;
				line-height: 80rpx;
				text-align: center;
				border-radius: 40rpx;
				font-size: 28rpx;
			}

			.cancel-btn {
				background-color: #f5f5f5;
				color: #666;
			}

			.confirm-btn {
				background: linear-gradient(135deg, #4CAF50, #45a049);
				color: #ffffff;
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
</style>
