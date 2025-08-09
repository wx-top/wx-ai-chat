<template>
	<view class="container">
		<view class="header">
			<view class="title">{{ userInfo?.nickname ? '编辑个人信息' : '完善个人信息' }}</view>
			<view class="subtitle">{{ userInfo?.nickname ? '修改您的个人信息' : '请设置您的个人信息' }}</view>
		</view>

		<view class="form-container">
			<!-- #ifdef MP-WEIXIN -->
			<view class="avatar-section">
				<view class="section-title">头像</view>
				<button type="balanced" open-type="chooseAvatar" @chooseavatar="onChooseavatar" class="avatar-btn">
					<image :src="getFullAvatarUrl(avatarUrl || userInfo?.avatar) || '/static/default-avatar.png'" class="avatar"></image>
					<view class="avatar-tip">点击更换头像</view>
				</button>
			</view>
			<!-- #endif -->

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
	// #ifdef MP-WEIXIN
	if (!avatarUrl.value) {
		uni.showToast({
			title: '请选择头像',
			icon: 'none'
		})
		return
	}
	// #endif

	isLoading.value = true
	try {

		// 上传头像
		// #ifdef MP-WEIXIN
		let avatar = userInfo.value?.avatar
		if (avatarUrl.value !== userInfo.value?.avatar) {
			const uploadResult = await uploadAvatar(avatarUrl.value)
			avatar = uploadResult.avatar
		}
		// #endif

		// 更新用户信息
		await updateProfile({
			nickname: userName.value,
			// #ifdef MP-WEIXIN
			avatar: avatarUrl.value
			// #endif
		})

		// 更新用户信息
		userStore.setUserInfo({
			...userInfo.value,
			// #ifdef MP-WEIXIN
			avatar,
			// #endif
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
				uni.removeStorageSync('access_token')
				uni.removeStorageSync('refresh_token')
				uni.removeStorageSync('user_info')
				uni.removeStorageSync('user_info')
				uni.removeStorageSync('user_login_status')
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

/* H5平台样式修复 */
/* #ifdef H5 */
.container {
	height: 100vh;
	max-height: 100vh;
	overflow-y: auto;
	box-sizing: border-box;
}
/* #endif */

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
	background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
	border-radius: 24rpx;
	padding: 48rpx;
	box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.08);
	border: 1rpx solid rgba(255, 255, 255, 0.8);
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
			border: 6rpx solid #ffffff;
			box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.12), 0 0 0 2rpx rgba(0, 122, 255, 0.1);
			transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
		height: 80rpx;
		background: #ffffff;
		border: none;
		border-radius: 16rpx;
		padding: 0 24rpx;
		font-size: 28rpx;
		color: #333;
		box-shadow: inset 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
		transition: all 0.3s ease;
		box-sizing: border-box;
		
		&:focus {
			box-shadow: inset 0 2rpx 8rpx rgba(0, 0, 0, 0.06), 0 0 0 3rpx rgba(0, 122, 255, 0.1);
			transform: translateY(-1rpx);
		}
		
		&::placeholder {
			color: #999;
			font-size: 26rpx;
		}
	}
}

.btn-container {
	margin-top: 60rpx;
	padding: 0 40rpx;
	
	.submit-btn {
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
		
		&.loading {
			opacity: 0.8;
			pointer-events: none;
		}
		
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

	.logout-btn {
		width: 100%;
		height: 80rpx;
		background: linear-gradient(135deg, #ff4757 0%, #ff3742 100%);
		border-radius: 16rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		color: #fff;
		font-size: 30rpx;
		font-weight: 600;
		margin-top: 32rpx;
		box-shadow: 0 6rpx 20rpx rgba(255, 71, 87, 0.25);
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		position: relative;
		overflow: hidden;

		&:hover {
			background: linear-gradient(135deg, #ff3742 0%, #ff1e2d 100%);
			transform: translateY(-2rpx);
			box-shadow: 0 8rpx 25rpx rgba(255, 71, 87, 0.35);
		}

		&:active {
			transform: translateY(0) scale(0.98);
			box-shadow: 0 4rpx 15rpx rgba(255, 71, 87, 0.2);
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
</style>
