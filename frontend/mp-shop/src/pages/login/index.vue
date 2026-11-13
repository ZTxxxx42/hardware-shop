<script setup lang="ts">
import { reactive, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { authApi } from '@/api/auth'
import { getErrorMessage } from '@/api/http'
import { useUserStore } from '@/store/user'
import { useCartStore } from '@/store/cart'

const userStore = useUserStore()
const cartStore = useCartStore()
const form = reactive({ username: '', password: '' })
const loading = ref(false)
const redirect = ref('')

const tabPages = ['/pages/index/index', '/pages/category/index', '/pages/cart/index', '/pages/user/index']

function navigateAfterLogin() {
  if (!redirect.value) {
    uni.switchTab({ url: '/pages/user/index' })
    return
  }
  if (tabPages.includes(redirect.value)) {
    uni.switchTab({ url: redirect.value })
  } else {
    uni.redirectTo({ url: redirect.value })
  }
}

async function submit() {
  const username = form.username.trim()
  const password = form.password
  if (!username) {
    uni.showToast({ title: '请输入会员账号', icon: 'none' })
    return
  }
  if (!password) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }
  loading.value = true
  try {
    const session = await authApi.login({ username, password })
    userStore.setSession(session.access_token, session.user)
    void cartStore.load().catch(() => {})
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(navigateAfterLogin, 500)
  } catch (error) {
    uni.showToast({ title: getErrorMessage(error, '登录失败，请检查账号密码'), icon: 'none' })
  } finally {
    loading.value = false
  }
}

onLoad((options) => {
  const raw = options?.redirect
  redirect.value = typeof raw === 'string' ? raw : ''
})
</script>

<template>
  <view class="page-pad login-page">
    <view class="login-card card">
      <view class="login-card__heading">
        <text class="eyebrow">MEMBER LOGIN</text>
        <view class="login-card__title">会员登录</view>
        <text class="login-card__subtitle">登录后可查看会员价格、管理购物车并提交订单</text>
      </view>

      <view class="login-form">
        <view class="form-field">
          <text class="form-field__label">会员账号</text>
          <input
            v-model="form.username"
            class="form-field__input"
            type="text"
            placeholder="请输入会员账号"
            placeholder-class="form-field__placeholder"
          />
        </view>
        <view class="form-field">
          <text class="form-field__label">登录密码</text>
          <input
            v-model="form.password"
            class="form-field__input"
            password
            placeholder="请输入密码"
            placeholder-class="form-field__placeholder"
            @confirm="submit"
          />
        </view>
        <button class="btn btn-primary login-form__submit" :disabled="loading" @tap="submit">登录</button>
      </view>

      <view class="login-card__tip">
        <text>测试会员账号：member / member123</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.login-page {
  padding-top: 60rpx;
}

.login-card {
  padding: 48rpx 40rpx 40rpx;
}

.login-card__heading {
  text-align: center;
}

.login-card__title {
  margin-top: 8rpx;
  font-size: 44rpx;
  font-weight: 750;
}

.login-card__subtitle {
  display: block;
  margin-top: 12rpx;
  color: #7b8998;
  font-size: 24rpx;
}

.login-form {
  margin-top: 40rpx;
}

.form-field {
  margin-bottom: 26rpx;
}

.form-field__label {
  display: block;
  margin-bottom: 12rpx;
  color: #46586b;
  font-size: 25rpx;
}

.form-field__input {
  height: 92rpx;
  padding: 0 26rpx;
  border: 1rpx solid #e0e7ef;
  border-radius: 14rpx;
  background: #f8fafc;
  font-size: 28rpx;
}

.form-field__placeholder {
  color: #a0abb7;
}

.login-form__submit {
  width: 100%;
  min-height: 92rpx;
  margin-top: 12rpx;
  border-radius: 14rpx;
}

.login-card__tip {
  margin-top: 32rpx;
  padding-top: 26rpx;
  border-top: 1rpx dashed #e2e9f0;
  color: #a0abb7;
  font-size: 22rpx;
  text-align: center;
}
</style>
