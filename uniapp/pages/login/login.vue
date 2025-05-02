<template>
	<view class="login-container">
		<view class="background">
			<view class="circle circle-1"></view>
			<view class="circle circle-2"></view>
			<view class="circle circle-3"></view>
		</view>

		<view class="content">
			<view class="logo-area">
				<text class="app-name">AI聊天助手</text>
			</view>

			<view class="login-area">
				<view class="welcome-text">
					<text class="title">欢迎使用</text>
					<text class="subtitle">AI智能助手，让沟通更简单</text>
				</view>

				<button class="login-btn" @click="checkPrivacy">
					<text>一键登录</text>
				</button>

				<view class="agreement">
					<text>登录即代表同意</text>
					<text class="link">《用户协议》</text>
					<text>和</text>
					<text class="link">《隐私政策》</text>
				</view>
			</view>
		</view>
		
		<!-- 隐私协议弹窗 -->
		<privacy-popup ref="privacyPopup" @agree="handleLogin" @reject="handleReject" />
	</view>
</template>

<script setup>
import {
	useUserStore
} from '@/store/user.js'
import { login } from '@/api'
import PrivacyPopup from '@/components/privacy-popup/privacy-popup.vue'

const userStore = useUserStore()
const privacyPopup = ref(null)

// 检查隐私协议
const checkPrivacy = () => {
	// #ifdef MP-WEIXIN
	// 检查是否已同意隐私协议
	const privacySetting = uni.getPrivacySetting()
	if (privacySetting.needAuthorization) {
		privacyPopup.value.showPrivacy = true
		privacyPopup.value.$refs.popup.open('bottom')
	} else {
		// 已同意隐私协议，直接登录
		handleLogin()
	}
	// #endif
	
	// #ifndef MP-WEIXIN
	// 非微信小程序环境直接登录
	handleLogin()
	// #endif
}

// 处理拒绝隐私协议
const handleReject = () => {
	uni.showToast({
		title: '需要同意隐私协议才能继续使用',
		icon: 'none'
	})
}

// 处理获取用户信息
const handleLogin = async () => {
	try {
		// 获取微信登录 code
		const loginRes = await uni.login({
			provider: 'weixin'
		})

		// 调用登录接口
		const result = await login(loginRes.code)

		// 更新用户状态
		userStore.setAccessToken(result.access_token)
		userStore.setRefreshToken(result.refresh_token)
		userStore.setUserInfo(result.user)
		userStore.setLoginStatus(true)
		// 登录成功提示
		uni.showToast({
			title: '登录成功',
			icon: 'success'
		})
		setTimeout(() => {
			// 如果用户信息不完整，去个人中心页面完善
			if (!result.user.nickname || !result.user.avatar) {
				uni.switchTab({
					url: '/pages/mine/mine'
				})
			} else {
				// 跳转到聊天页面
				uni.switchTab({
					url: '/pages/index/index'
				})
			}
		}, 1000)
	} catch (err) {
		console.error('登录失败', err)
		uni.showToast({
			title: err.message || '登录失败，请重试',
			icon: 'none'
		})
	}
}

</script>

<style>
.login-container {
	position: relative;
	height: 100vh;
	background-color: #f8f8f8;
	overflow: hidden;
}

.background {
	position: absolute;
	width: 100%;
	height: 100%;
	z-index: 0;
}

.circle {
	position: absolute;
	border-radius: 50%;
	background: linear-gradient(135deg, #07C160, #1AAD19);
	opacity: 0.1;
}

.circle-1 {
	width: 600rpx;
	height: 600rpx;
	top: -200rpx;
	right: -200rpx;
}

.circle-2 {
	width: 400rpx;
	height: 400rpx;
	bottom: -100rpx;
	left: -100rpx;
}

.circle-3 {
	width: 300rpx;
	height: 300rpx;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
}

.content {
	position: relative;
	z-index: 1;
	height: 100%;
	display: flex;
	flex-direction: column;
}

.logo-area {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding-top: 100rpx;
}

.app-name {
	font-size: 48rpx;
	font-weight: bold;
	color: #333333;
	letter-spacing: 2rpx;
	animation: float 3s ease-in-out infinite;
}

@keyframes float {
	0% {
		transform: translateY(0);
	}

	50% {
		transform: translateY(-20rpx);
	}

	100% {
		transform: translateY(0);
	}
}

.login-area {
	flex: 1;
	padding: 0 60rpx;
	display: flex;
	flex-direction: column;
	justify-content: center;
}

.welcome-text {
	margin-bottom: 80rpx;
	text-align: center;
}

.title {
	font-size: 48rpx;
	font-weight: bold;
	color: #333333;
	display: block;
	margin-bottom: 20rpx;
	letter-spacing: 2rpx;
}

.subtitle {
	font-size: 28rpx;
	color: #666666;
	letter-spacing: 1rpx;
}

.login-btn {
	display: flex;
	align-items: center;
	justify-content: center;
	background-color: #07C160;
	color: #ffffff;
	height: 88rpx;
	border-radius: 44rpx;
	font-size: 32rpx;
	margin-bottom: 40rpx;
	box-shadow: 0 8rpx 16rpx rgba(7, 193, 96, 0.2);
	transition: all 0.3s ease;
}

.login-btn:active {
	transform: scale(0.98);
	box-shadow: 0 4rpx 8rpx rgba(7, 193, 96, 0.2);
}

.agreement {
	text-align: center;
	font-size: 24rpx;
	color: #999999;
	line-height: 1.6;
}

.link {
	color: #07C160;
	position: relative;
}

.link::after {
	content: '';
	position: absolute;
	bottom: -2rpx;
	left: 0;
	width: 100%;
	height: 2rpx;
	background-color: #07C160;
	opacity: 0;
	transition: opacity 0.3s ease;
}

.link:active::after {
	opacity: 1;
}
</style>