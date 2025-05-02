<template>
	<view class="container">
		<view class="header">
			<view class="title">{{ userInfo?.nickname ? '编辑个人信息' : '完善个人信息' }}</view>
			<view class="subtitle">{{ userInfo?.nickname ? '修改您的头像和昵称' : '请设置您的头像和昵称' }}</view>
		</view>

		<view class="form-container">
			<view class="avatar-section">
				<view class="section-title">头像</view>
				<button type="balanced" open-type="chooseAvatar" @chooseavatar="onChooseavatar" class="avatar-btn">
					<image :src="getFullAvatarUrl(avatarUrl || userInfo?.avatar) || '/static/default-avatar.png'" class="avatar"></image>
					<view class="avatar-tip">点击更换头像</view>
				</button>
			</view>

			<view class="nickname-section">
				<view class="section-title">昵称</view>
				<input 
					type="nickname" 
					class="nickname-input" 
					:value="userName || userInfo?.nickname" 
					@blur="bindblur" 
					placeholder="请输入您的昵称"
					@input="bindinput" 
				/>
			</view>
		</view>

		<view class="btn-container">
			<view class="submit-btn" @click="onSubmit" :class="{ 'loading': isLoading }">
				<text v-if="!isLoading">保存信息</text>
				<text v-else>保存中...</text>
			</view>
			<view class="logout-btn" @click="onLogout">
				<text>退出登录</text>
			</view>
		</view>
	</view>
</template>

<script setup>
import { useUserStore } from '@/store/user.js'
import { ref, onMounted } from 'vue'
import { getProfile, updateProfile, uploadAvatar } from '@/api'
import { config } from '@/utils/http'

const userStore = useUserStore()
const userInfo = ref(null)
const avatarUrl = ref('')
const userName = ref('')
const isLoading = ref(false)

// 获取完整的头像URL
const getFullAvatarUrl = (url) => {
	if (!url) return ''
	if (url.startsWith('http')) return url
	return config.baseURL + url
}

// 页面加载时获取用户信息
onMounted(async () => {
	try {
		const data = await getProfile()
		userInfo.value = data
		avatarUrl.value = data.avatar
		userName.value = data.nickname
	} catch (error) {
		console.error('获取用户信息失败', error)
		uni.showToast({
			title: '获取用户信息失败',
			icon: 'none'
		})
	}
})

// 处理昵称输入
const bindblur = (e) => {
	userName.value = e.detail.value
}

const bindinput = (e) => {
	userName.value = e.detail.value
}

// 处理头像选择
const onChooseavatar = (e) => {
	const { avatarUrl: newAvatarUrl } = e.detail
	avatarUrl.value = newAvatarUrl
}

// 提交表单
const onSubmit = async () => {
	if (isLoading.value) return
	
	// 验证表单
	if (!userName.value) {
		uni.showToast({
			title: '请输入昵称',
			icon: 'none'
		})
		return
	}

	if (!avatarUrl.value) {
		uni.showToast({
			title: '请选择头像',
			icon: 'none'
		})
		return
	}

	isLoading.value = true
	try {
		// 上传头像
		let avatar = userInfo.value?.avatar
		if (avatarUrl.value !== userInfo.value?.avatar) {
			const uploadResult = await uploadAvatar(avatarUrl.value)
			avatar = uploadResult.avatar
		}

		// 更新用户信息
		const updateResult = await updateProfile({
			nickname: userName.value,
			avatar: avatarUrl.value
		})

		// 更新用户信息
		userStore.setUserInfo({
			...userInfo.value,
			avatar,
			nickname: userName.value
		})

		uni.showToast({
			title: '保存成功',
			icon: 'success'
		})

		// 返回上一页
		setTimeout(() => {
			uni.navigateBack()
		}, 1500)
	} catch (error) {
		console.error('保存失败', error)
		uni.showToast({
			title: error.message || '保存失败',
			icon: 'none',
			duration: 2000
		})
	} finally {
		isLoading.value = false
	}
}

// 退出登录
const onLogout = () => {
	uni.showModal({
		title: '提示',
		content: '确定要退出登录吗？',
		success: (res) => {
			if (res.confirm) {
				// 清除用户信息
				userStore.setUserInfo(null)
				// 清除token
				uni.removeStorageSync('token')
				// 跳转到登录页
				uni.reLaunch({
					url: '/pages/login/login'
				})
			}
		}
	})
}
</script>

<style lang="scss" scoped>
.container {
	min-height: 100vh;
	background-color: #f8f8f8;
	padding: 40rpx;
}

.header {
	text-align: center;
	margin-bottom: 60rpx;
	
	.title {
		font-size: 40rpx;
		font-weight: bold;
		color: #333;
		margin-bottom: 20rpx;
	}
	
	.subtitle {
		font-size: 28rpx;
		color: #666;
	}
}

.form-container {
	background-color: #fff;
	border-radius: 20rpx;
	padding: 40rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.avatar-section {
	margin-bottom: 40rpx;
	
	.section-title {
		font-size: 32rpx;
		color: #333;
		margin-bottom: 30rpx;
	}
	
	.avatar-btn {
		display: flex;
		flex-direction: column;
		align-items: center;
		background: none;
		padding: 0;
		margin: 0;
		width: auto;
		line-height: 1;
		
		&::after {
			border: none;
		}
		
		.avatar {
			width: 160rpx;
			height: 160rpx;
			border-radius: 50%;
			background-color: #f0f0f0;
			margin-bottom: 20rpx;
			border: 4rpx solid #fff;
			box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
		}
		
		.avatar-tip {
			font-size: 24rpx;
			color: #999;
		}
	}
}

.nickname-section {
	.section-title {
		font-size: 32rpx;
		color: #333;
		margin-bottom: 30rpx;
	}
	
	.nickname-input {
		width: 100%;
		height: 88rpx;
		background-color: #f8f8f8;
		border-radius: 44rpx;
		padding: 0 40rpx;
		font-size: 28rpx;
		color: #333;
		
		&::placeholder {
			color: #999;
		}
	}
}

.btn-container {
	margin-top: 60rpx;
	padding: 0 40rpx;
	
	.submit-btn {
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
		box-shadow: 0 8rpx 16rpx rgba(7, 193, 96, 0.2);
		transition: all 0.3s ease;
		
		&.loading {
			opacity: 0.8;
			pointer-events: none;
		}
		
		&:active {
			transform: scale(0.98);
			box-shadow: 0 4rpx 8rpx rgba(7, 193, 96, 0.2);
		}
	}

	.logout-btn {
		width: 100%;
		height: 88rpx;
		background: #ff4d4f;
		border-radius: 44rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		color: #fff;
		font-size: 32rpx;
		font-weight: 500;
		margin-top: 40rpx;
		box-shadow: 0 8rpx 16rpx rgba(255, 77, 79, 0.15);
		transition: all 0.3s ease;

		&:active {
			transform: scale(0.98);
			box-shadow: 0 4rpx 8rpx rgba(255, 77, 79, 0.15);
		}
	}
}
</style>
