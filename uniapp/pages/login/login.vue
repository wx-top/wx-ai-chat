<template>
	<view class="login-container">
		<!-- 左侧品牌区域 -->
		<view class="brand-section">
			<view class="brand-content">
				<view class="brand-logo">
					<view class="logo-icon"></view>
					<text class="brand-name">{{ VUE_APP_NAME }}</text>
				</view>
				<view class="brand-description">
					<text class="description-text">{{ VUE_APP_DESCRIPTION }}</text>
				</view>
			</view>
			<view class="decorative-elements">
				<view class="floating-shape shape-1"></view>
				<view class="floating-shape shape-2"></view>
				<view class="floating-shape shape-3"></view>
			</view>
		</view>

		<!-- 右侧登录区域 -->
		<view class="login-section">
			<view class="login-content">
				<view class="login-header">
					<text class="login-title">欢迎回来</text>
					<text class="login-subtitle">请登录您的账户</text>
				</view>

				<!-- #ifdef MP-WEIXIN -->
				<view class="wx-login-area">
					<button class="wx-login-btn" @click="handleWxLogin">
						<view class="wx-icon"></view>
						<text>微信一键登录</text>
					</button>
				</view>
				<!-- #endif -->

				<!-- #ifndef MP-WEIXIN -->
				<view class="form-area">
					<view class="input-container">
						<view class="input-wrapper">
							<view class="input-icon user-icon"></view>
							<input class="form-input" type="text" v-model="username" placeholder="请输入用户名" />
						</view>
					</view>
					<view class="input-container">
						<view class="input-wrapper">
							<view class="input-icon lock-icon"></view>
							<input class="form-input" type="password" v-model="password" placeholder="请输入密码" />
						</view>
					</view>
					<button class="submit-btn" @click="handleAccountLogin">
						<text>立即登录</text>
					</button>
					<view class="form-footer">
						<text class="register-text">还没有账户？</text>
						<text @click="goToRegister" class="register-link">立即注册</text>
					</view>
				</view>
				<!-- #endif -->
			</view>
		</view>

		<!-- #ifdef MP-WEIXIN -->
		<zero-privacy :onNeed='false'></zero-privacy>
		<!-- #endif -->
	</view>
</template>

<script setup>
	import {
		useUserStore
	} from '@/store/user.js'
	import {
		onMounted,
		ref,
		computed
	} from 'vue'
	import {
		login,
		wxlogin
	} from '@/api'
	import APP_CONFIG from '@/config/app.js'
	const userStore = useUserStore()

	// 应用配置
	const VUE_APP_NAME = computed(() => APP_CONFIG.NAME)
	const VUE_APP_DESCRIPTION = computed(() => APP_CONFIG.DESCRIPTION)

	// #ifndef MP-WEIXIN
	// 账号登录表单数据
	const username = ref('')
	const password = ref('')
	// #endif

	// 微信小程序登录
	const handleWxLogin = async () => {
		try {
			// 获取微信登录 code
			const loginRes = await uni.login({
				provider: 'weixin'
			})

			// 调用微信登录接口
			const result = await wxlogin(loginRes.code)

			console.log(result)

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

	// #ifndef MP-WEIXIN
	// 账号登录
	const handleAccountLogin = async () => {
		try {
			// 验证表单
			if (!username.value.trim()) {
				uni.showToast({
					title: '请输入用户名',
					icon: 'none'
				})
				return
			}
			if (!password.value.trim()) {
				uni.showToast({
					title: '请输入密码',
					icon: 'none'
				})
				return
			}

			// 调用账号登录接口
			const result = await login(username.value, password.value)

			console.log(result)

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
				// 跳转到聊天页面
				uni.switchTab({
					url: '/pages/index/index'
				})
			}, 1000)
		} catch (err) {
			console.error('登录失败', err)
			uni.showToast({
				title: err.message || '登录失败，请重试',
				icon: 'none'
			})
		}
	}

	// 跳转到注册页面
	const goToRegister = () => {
		uni.navigateTo({
			url: '/pages/register/register'
		})
	}
	// #endif
</script>

<style scoped>
	.login-container {
		display: flex;
		flex-direction: column;
		height: 100vh;
		overflow: hidden;
	}

	/* H5平台样式修复 */
	/* #ifdef H5 */
	.login-container {
		height: 100vh;
		max-height: 100vh;
		overflow: hidden;
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
	}
	/* #endif */

	/* 上方品牌区域 */
	.brand-section {
		height: 400rpx;
		min-height: 400rpx;
		max-height: 400rpx;
		background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
		position: relative;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 20rpx;
		box-sizing: border-box;
	}

	.brand-content {
		position: relative;
		z-index: 2;
		text-align: center;
		color: white;
	}

	.brand-logo {
		margin-bottom: 30rpx;
	}

	.logo-icon {
		width: 80rpx;
		height: 80rpx;
		background: rgba(255, 255, 255, 0.2);
		border-radius: 50%;
		margin: 0 auto 20rpx;
		position: relative;
		backdrop-filter: blur(10px);
	}

	.logo-icon::before {
		content: '';
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 60rpx;
		height: 60rpx;
		background: white;
		border-radius: 50%;
	}

	.brand-name {
		font-size: 36rpx;
		font-weight: 700;
		color: white;
		letter-spacing: 1rpx;
	}

	.brand-description {
		max-width: 350rpx;
		margin: 0 auto;
	}

	.description-text {
		font-size: 26rpx;
		color: rgba(255, 255, 255, 0.9);
		line-height: 1.4;
		max-width: 350rpx;
		margin: 0 auto;
		text-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.1);
	}

	.decorative-elements {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		z-index: 1;
		pointer-events: none;
	}

	.floating-shape {
		position: absolute;
		background: rgba(255, 255, 255, 0.1);
		border-radius: 50%;
		animation: float 8s ease-in-out infinite;
	}

	.shape-1 {
		width: 200rpx;
		height: 200rpx;
		top: 10%;
		right: 10%;
		animation-delay: 0s;
	}

	.shape-2 {
		width: 150rpx;
		height: 150rpx;
		bottom: 20%;
		left: 15%;
		animation-delay: 2s;
	}

	.shape-3 {
		width: 100rpx;
		height: 100rpx;
		top: 60%;
		right: 20%;
		animation-delay: 4s;
	}

	@keyframes float {
		0%, 100% {
			transform: translateY(0) scale(1);
			opacity: 0.7;
		}
		50% {
			transform: translateY(-20rpx) scale(1.1);
			opacity: 1;
		}
	}

	/* 下方登录区域 */
	.login-section {
		flex: 1;
		background: #ffffff;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 40rpx;
		box-sizing: border-box;
	}

	.login-content {
		width: 100%;
		max-width: 480rpx;
	}

	.login-header {
		text-align: center;
		margin-bottom: 60rpx;
	}

	.login-title {
		display: block;
		font-size: 42rpx;
		font-weight: 700;
		color: #333333;
		margin-bottom: 16rpx;
		letter-spacing: 1rpx;
	}

	.login-subtitle {
		display: block;
		font-size: 28rpx;
		color: #666666;
		line-height: 1.4;
	}

	/* 微信登录区域 */
	.wx-login-area {
		width: 100%;
	}

	.wx-login-btn {
		width: 100%;
		height: 80rpx;
		background: #07C160;
		border-radius: 16rpx;
		border: none;
		display: flex;
		align-items: center;
		justify-content: center;
		color: white;
		font-size: 30rpx;
		font-weight: 500;
		box-shadow: 0 6rpx 20rpx rgba(7, 193, 96, 0.25);
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		position: relative;
		overflow: hidden;
	}

	.wx-login-btn:hover {
		background: #06A952;
		transform: translateY(-2rpx);
		box-shadow: 0 8rpx 25rpx rgba(7, 193, 96, 0.35);
	}

	.wx-login-btn:active {
		transform: translateY(0) scale(0.98);
		box-shadow: 0 4rpx 15rpx rgba(7, 193, 96, 0.2);
	}

	.wx-login-btn::before {
		content: '';
		position: absolute;
		top: 0;
		left: -100%;
		width: 100%;
		height: 100%;
		background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
		transition: left 0.5s;
	}

	.wx-login-btn:hover::before {
		left: 100%;
	}

	.wx-icon {
		width: 40rpx;
		height: 40rpx;
		background: white;
		border-radius: 50%;
		margin-right: 20rpx;
		position: relative;
	}

	.wx-icon::before {
		content: '';
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 24rpx;
		height: 24rpx;
		background: #07C160;
		border-radius: 4rpx;
	}

	/* 表单区域 */
	.form-area {
		width: 100%;
	}

	.input-container {
		margin-bottom: 24rpx;
	}

	.input-wrapper {
		position: relative;
		display: flex;
		align-items: center;
		background: #ffffff;
		border: none;
		border-radius: 16rpx;
		box-shadow: inset 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
		transition: all 0.3s ease;
	}

	.input-wrapper:focus-within {
		background: #ffffff;
		box-shadow: inset 0 2rpx 8rpx rgba(0, 0, 0, 0.06), 0 0 0 3rpx rgba(33, 150, 243, 0.1);
		transform: translateY(-1rpx);
	}

	.input-icon {
		width: 36rpx;
		height: 36rpx;
		margin: 0 20rpx 0 24rpx;
		background: #f0f0f0;
		border-radius: 50%;
		position: relative;
		flex-shrink: 0;
		transition: all 0.3s ease;
	}

	.user-icon::before {
		content: '';
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 20rpx;
		height: 20rpx;
		background: #6c757d;
		border-radius: 50%;
	}

	.lock-icon::before {
		content: '';
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 16rpx;
		height: 20rpx;
		border: 3rpx solid #6c757d;
		border-radius: 4rpx 4rpx 0 0;
		background: transparent;
	}

	.lock-icon::after {
		content: '';
		position: absolute;
		top: 60%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 20rpx;
		height: 12rpx;
		background: #6c757d;
		border-radius: 0 0 4rpx 4rpx;
	}

	.form-input {
		flex: 1;
		height: 80rpx;
		border: none;
		outline: none;
		background: transparent;
		font-size: 28rpx;
		color: #333333;
		padding-right: 24rpx;
		line-height: 1.4;
	}

	.form-input::placeholder {
		color: #999999;
		font-weight: 400;
		font-size: 26rpx;
	}

	.submit-btn {
		width: 100%;
		height: 80rpx;
		background: linear-gradient(135deg, #007AFF 0%, #0056CC 100%);
		border: none;
		border-radius: 16rpx;
		color: white;
		font-size: 30rpx;
		font-weight: 600;
		margin: 32rpx 0 24rpx;
		box-shadow: 0 6rpx 20rpx rgba(0, 122, 255, 0.25);
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		cursor: pointer;
		position: relative;
		overflow: hidden;
	}

	.submit-btn:hover {
		background: linear-gradient(135deg, #0056CC 0%, #003d99 100%);
		transform: translateY(-2rpx);
		box-shadow: 0 8rpx 25rpx rgba(0, 122, 255, 0.35);
	}

	.submit-btn:active {
		transform: translateY(0) scale(0.98);
		box-shadow: 0 4rpx 15rpx rgba(0, 122, 255, 0.2);
	}

	.submit-btn::before {
		content: '';
		position: absolute;
		top: 0;
		left: -100%;
		width: 100%;
		height: 100%;
		background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
		transition: left 0.5s;
	}

	.submit-btn:hover::before {
		left: 100%;
	}

	.form-footer {
		text-align: center;
		margin-top: 40rpx;
	}

	.register-text {
		font-size: 28rpx;
		color: #6c757d;
		margin-right: 8rpx;
	}

	.register-link {
		font-size: 28rpx;
		color: #2196F3;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.3s ease;
		position: relative;
	}

	.register-link::after {
		content: '';
		position: absolute;
		bottom: -2rpx;
		left: 0;
		width: 0;
		height: 2rpx;
		background: #2196F3;
		transition: width 0.3s ease;
	}

	.register-link:active::after {
		width: 100%;
	}

	/* 响应式设计 */
	@media (max-width: 768px) {
		.login-container {
			flex-direction: column;
		}

		.brand-section {
			flex: none;
			height: 40vh;
			padding: 40rpx;
		}

		.login-section {
			flex: none;
			height: 60vh;
			padding: 40rpx;
		}

		.brand-name {
			font-size: 36rpx;
		}

		.description-text {
			font-size: 28rpx;
		}

		.login-title {
			font-size: 36rpx;
		}
	}
</style>