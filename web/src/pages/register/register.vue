<template>
	<view class="register-container">
		<!-- 左侧品牌区域 -->
		<view class="brand-section">
			<view class="brand-content">
				<view class="logo-container">
					<view class="logo-icon"></view>
					<text class="brand-name">{{ VUE_APP_DESCRIPTION }}</text>
				</view>
				<text class="description-text">创建您的账户，开启智能对话之旅</text>
			</view>
			
			<!-- 装饰性浮动形状 -->
			<view class="floating-shapes">
				<view class="shape shape-1"></view>
				<view class="shape shape-2"></view>
				<view class="shape shape-3"></view>
			</view>
		</view>

		<!-- 右侧注册区域 -->
		<view class="register-section">
			<view class="register-content">
				<view class="register-header">
					<text class="register-title">创建账户</text>
					<text class="register-subtitle">请填写以下信息完成注册</text>
				</view>

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

					<view class="input-container">
						<view class="input-wrapper">
							<view class="input-icon lock-icon"></view>
							<input class="form-input" type="password" v-model="passwordConfirm" placeholder="请确认密码" />
						</view>
					</view>

					<button class="submit-btn" @click="handleRegister">
						创建账户
					</button>

					<view class="form-footer">
						<text class="login-text">已有账户？</text>
						<text class="login-link" @click="goToLogin">立即登录</text>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
	import {
		ref,
		computed
	} from 'vue'
	import {
		register
	} from '@/api'
	// 应用配置
	const VUE_APP_DESCRIPTION = computed(() => import.meta.env.VITE_APP_DESCRIPTION || '采育镇助手，让沟通更简单')

	// 表单数据
	const username = ref('')
	const password = ref('')
	const passwordConfirm = ref('')

	// 注册处理
	const handleRegister = async () => {
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
			if (!passwordConfirm.value.trim()) {
				uni.showToast({
					title: '请确认密码',
					icon: 'none'
				})
				return
			}
			if (password.value !== passwordConfirm.value) {
				uni.showToast({
					title: '两次密码输入不一致',
					icon: 'none'
				})
				return
			}
			if (password.value.length < 6) {
				uni.showToast({
					title: '密码长度不能少于6位',
					icon: 'none'
				})
				return
			}

			// 调用注册接口
			const result = await register(username.value, password.value, passwordConfirm.value)

			console.log(result)

			// 注册成功提示
			uni.showToast({
				title: '注册成功',
				icon: 'success'
			})
			setTimeout(() => {
				// 跳转到登录页面
				uni.navigateBack()
			}, 1000)
		} catch (err) {
			console.error('注册失败', err)
			uni.showToast({
				title: err.message || '注册失败，请重试',
				icon: 'none'
			})
		}
	}

	// 跳转到登录页面
	const goToLogin = () => {
		uni.navigateBack()
	}
</script>

<style scoped>
	.register-container {
		display: flex;
		flex-direction: column;
		height: 100vh;
		overflow: hidden;
	}

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
		overflow: hidden;
	}

	.brand-content {
		text-align: center;
		z-index: 2;
		position: relative;
	}

	.logo-container {
		margin-bottom: 30rpx;
	}

	.logo-icon {
		width: 80rpx;
		height: 80rpx;
		background: rgba(255, 255, 255, 0.2);
		border-radius: 16rpx;
		margin: 0 auto 20rpx;
		position: relative;
		backdrop-filter: blur(20px);
		border: 2rpx solid rgba(255, 255, 255, 0.3);
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
		border-radius: 12rpx;
	}

	.brand-name {
		font-size: 36rpx;
		font-weight: 700;
		color: white;
		display: block;
		letter-spacing: 1rpx;
		text-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.2);
	}

	.description-text {
		font-size: 26rpx;
		color: rgba(255, 255, 255, 0.9);
		line-height: 1.4;
		max-width: 350rpx;
		margin: 0 auto;
		text-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.1);
	}

	.floating-shapes {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		pointer-events: none;
	}

	.shape {
		position: absolute;
		border-radius: 50%;
		background: rgba(255, 255, 255, 0.1);
		animation: float 15s ease-in-out infinite;
	}

	.shape-1 {
		width: 200rpx;
		height: 200rpx;
		top: 10%;
		right: 10%;
		animation-delay: 0s;
	}

	.shape-2 {
		width: 120rpx;
		height: 120rpx;
		bottom: 20%;
		left: 15%;
		animation-delay: 5s;
	}

	.shape-3 {
		width: 80rpx;
		height: 80rpx;
		top: 60%;
		right: 25%;
		animation-delay: 10s;
	}

	@keyframes float {
		0%, 100% {
			transform: translateY(0) rotate(0deg);
			opacity: 0.7;
		}
		50% {
			transform: translateY(-30rpx) rotate(180deg);
			opacity: 1;
		}
	}

	/* 下方注册区域 */
	.register-section {
		flex: 1;
		background: white;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 40rpx;
		box-sizing: border-box;
	}

	.register-content {
		width: 100%;
		max-width: 480rpx;
	}

	.register-header {
		text-align: center;
		margin-bottom: 80rpx;
	}

	.register-title {
		font-size: 48rpx;
		font-weight: 700;
		color: #333333;
		display: block;
		margin-bottom: 20rpx;
		letter-spacing: 1rpx;
	}

	.register-subtitle {
		font-size: 28rpx;
		color: #666666;
		line-height: 1.5;
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

	.login-text {
		font-size: 28rpx;
		color: #6c757d;
		margin-right: 8rpx;
	}

	.login-link {
		font-size: 28rpx;
		color: #2196F3;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.3s ease;
		position: relative;
	}

	.login-link::after {
		content: '';
		position: absolute;
		bottom: -2rpx;
		left: 0;
		width: 0;
		height: 2rpx;
		background: #2196F3;
		transition: width 0.3s ease;
	}

	.login-link:active::after {
		width: 100%;
	}

	/* 响应式设计 */
	@media (max-width: 768px) {
		.register-container {
			flex-direction: column;
		}

		.brand-section {
			flex: none;
			height: 40vh;
			padding: 40rpx;
		}

		.register-section {
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

		.register-title {
			font-size: 36rpx;
		}
	}
</style>