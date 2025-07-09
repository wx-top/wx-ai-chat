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
</style>
