<template>
	<uni-popup 
		v-show="showPrivacy" 
		ref="popup" 
		:is-mask-click="false"
		mask-background-color="rgba(0,0,0,0.4)">
		<view class="popup-content">
			<view><text class="title">{{privacyTitle}}</text></view>
			<view class="desc">
				<text>{{privacyDescStart}}: \n</text>
				<text class="desc-link" @click="openPrivacyContract">{{privacyContractName}}</text> 
				<text>\n{{privacyDescEnd}}</text>
			</view>
			<view class="flex">
				<button class="btn flex-item" type="default" @click="reject" id="reject-btn">拒绝</button>
				<button class="btn flex-item" type="primary" id="agree-btn" 
					open-type="agreePrivacyAuthorization"
					style="margin-left: 28rpx;"
					@agreeprivacyauthorization="agreeAuth">同意</button>
			</view>
		</view>
	</uni-popup>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'

const popup = ref(null)
const showPrivacy = ref(false)
const privacyTitle = ref('用户隐私保护提示')
const privacyContractName = ref('《查看隐私协议》')
const privacyDescStart = ref('在你使用AI聊天助手服务之前，请仔细阅读')
const privacyDescEnd = ref('如你同意该指引，请点击"同意"开始使用本小程序。')

// 检查隐私协议
const checkPrivacy = () => {
	console.log('开始检查隐私协议')
	wx.getPrivacySetting({
		success: res => {
			console.log('隐私协议检查结果：', res)
			privacyContractName.value = res?.privacyContractName || '《查看隐私协议》'
			if (res.needAuthorization) {
				console.log('需要授权隐私协议')
				showPrivacy.value = true
				uni.setStorage({key: 'showPrivacy', data: true})
				nextTick(() => {
					console.log('打开弹窗')
					popup.value?.open('bottom')
				})
			} else {
				console.log('不需要授权隐私协议')
				hidePrivacy()
			}
		},
		fail: (err) => {
			console.error('隐私协议检查失败：', err)
		},
		complete: () => {
			console.log('隐私协议检查完成')
		}
	})
}

// 同意隐私协议
const agreeAuth = (e) => { 
	console.log('同意隐私协议事件：', e)
	if (e?.detail?.errMsg === 'agreePrivacyAuthorization:ok') {
		console.log('用户同意隐私协议')
		emit('agree')
	} else {
		console.log('用户未同意隐私协议')
	}
	hidePrivacy()
}

// 打开隐私协议
const openPrivacyContract = () => {
	console.log('打开隐私协议页面')
	wx.openPrivacyContract({
		success: () => {
			console.log('成功打开隐私协议页面')
		},
		fail: (err) => {
			console.error('打开隐私协议页面失败：', err)
		},
		complete: () => {
			console.log('打开隐私协议页面操作完成')
		}
	})
}

// 拒绝隐私协议
const reject = () => {
	console.log('用户拒绝隐私协议')
	hidePrivacy()
	emit('reject')
	// 退出小程序
	uni.exitMiniProgram({
		success: () => {
			console.log('成功退出小程序')
		},
		fail: (err) => {
			console.error('退出小程序失败：', err)
		}
	})
}

// 隐藏隐私协议弹窗
const hidePrivacy = () => {
	console.log('隐藏隐私协议弹窗')
	showPrivacy.value = false
	nextTick(() => {
		popup.value?.close()
	})
}

// 定义事件
const emit = defineEmits(['agree', 'reject'])

// 组件挂载后检查隐私协议
onMounted(() => {
	console.log('隐私弹窗组件已挂载')
	checkPrivacy()
})
</script>

<style>
.popup-content {
	background-color: #fff;
	padding: 40rpx;
	border-radius: 20rpx;
}

.title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
	text-align: center;
	margin-bottom: 30rpx;
}

.desc {
	font-size: 28rpx;
	color: #666;
	line-height: 1.6;
	margin-bottom: 40rpx;
}

.desc-link {
	color: #07C160;
}

.flex {
	display: flex;
	justify-content: space-between;
}

.flex-item {
	flex: 1;
}

.btn {
	height: 80rpx;
	line-height: 80rpx;
	font-size: 28rpx;
	border-radius: 40rpx;
}

#reject-btn {
	background-color: #f5f5f5;
	color: #666;
}

#agree-btn {
	background-color: #07C160;
	color: #fff;
}
</style> 