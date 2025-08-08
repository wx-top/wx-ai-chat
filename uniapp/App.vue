<script>
import { useUserStore } from './store/user.js'

export default {
	onLaunch: function () {
		console.log('App Launch')
		// 确保应用启动时加载存储的状态
		const userStore = useUserStore()
		userStore.loadFromStorage()
		// 如果用户未登录，跳转到登录页面
		if (!userStore.isLogin) {
			uni.navigateTo({ url: '/pages/login/login' })
		}

	},
		onShow: function () {
			console.log('App Show')
		},
		onHide: function () {
			console.log('App Hide')
		}
	}
</script>

<style lang="scss">
	@import "@/uni_modules/uview-plus/index.scss";

	/* H5平台全局样式修复 */
	/* #ifdef H5 */
	html {
		height: 100%;
		margin: 0;
		padding: 0;
		overflow: hidden;
		-webkit-overflow-scrolling: touch;
	}

	body {
		height: 100%;
		margin: 0;
		padding: 0;
		overflow: hidden;
		-webkit-user-select: none;
		user-select: none;
		-webkit-touch-callout: none;
		-webkit-tap-highlight-color: transparent;
		position: fixed;
		width: 100%;
	}

	#app {
		height: 100vh;
		width: 100vw;
		overflow: hidden;
		position: relative;
	}

	/* 彻底隐藏所有滚动条 */
	* {
		scrollbar-width: none !important;
		-ms-overflow-style: none !important;
	}

	*::-webkit-scrollbar {
		width: 0 !important;
		height: 0 !important;
		display: none !important;
	}

	/* 确保页面内容不会超出视口 */
	.uni-page-body {
		height: 100vh !important;
		overflow: hidden !important;
	}

	/* 修复输入框在H5中的显示问题 */
	textarea, input {
		-webkit-appearance: none;
		border-radius: 0;
		outline: none;
	}
	/* #endif */
</style>
