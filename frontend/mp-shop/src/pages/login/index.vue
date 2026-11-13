<script setup lang="ts">
import { reactive, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { authApi } from '@/api/auth'
import { ApiRequestError, getErrorMessage } from '@/api/http'
import { useUserStore } from '@/store/user'
import { useCartStore } from '@/store/cart'
import type { TokenResponse } from '@/types/shop'
import LegalLinks from '@/components/LegalLinks.vue'

const userStore = useUserStore()
const cartStore = useCartStore()
const form = reactive({ username: '', password: '' })
const accountLoading = ref(false)
const wechatLoading = ref(false)
const agreed = ref(false)
const redirect = ref('')
const tabPages = ['/pages/index/index', '/pages/category/index', '/pages/cart/index', '/pages/user/index']

function navigateAfterLogin() {
  if (!redirect.value) {
    uni.switchTab({ url: '/pages/user/index' })
    return
  }
  if (tabPages.includes(redirect.value)) uni.switchTab({ url: redirect.value })
  else uni.redirectTo({ url: redirect.value })
}

function ensureAgreement(): boolean {
  if (agreed.value) return true
  uni.showToast({ title: '请先阅读并同意隐私政策与用户协议', icon: 'none' })
  return false
}

async function completeLogin(session: TokenResponse) {
  userStore.setSession(session.access_token, session.user)
  void cartStore.load().catch(() => {})
  uni.showToast({ title: '登录成功', icon: 'success' })
  setTimeout(navigateAfterLogin, 500)
}

async function submit() {
  if (!ensureAgreement()) return
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
  accountLoading.value = true
  try {
    await completeLogin(await authApi.login({ username, password }))
  } catch (error) {
    uni.showToast({ title: getErrorMessage(error, '登录失败，请检查账号密码'), icon: 'none' })
  } finally {
    accountLoading.value = false
  }
}

function getWechatCode(): Promise<string> {
  return new Promise((resolve, reject) => {
    uni.login({
      provider: 'weixin',
      success: (result) => {
        if (result.code) resolve(result.code)
        else reject(new Error('未获取到微信登录凭证'))
      },
      fail: () => reject(new Error('微信登录已取消或暂不可用')),
    })
  })
}

function wechatErrorMessage(error: unknown): string {
  if (error instanceof ApiRequestError && (error.status === 503 || error.code === 'WECHAT_SERVICE_UNAVAILABLE')) {
    return '微信登录暂未开通'
  }
  return getErrorMessage(error, '微信登录失败，请使用账号密码登录')
}

async function submitWechat() {
  if (!ensureAgreement()) return
  // #ifndef MP-WEIXIN
  uni.showToast({ title: '请在微信小程序中使用微信登录', icon: 'none' })
  return
  // #endif
  // #ifdef MP-WEIXIN
  wechatLoading.value = true
  try {
    const code = await getWechatCode()
    await completeLogin(await authApi.wechatLogin({ code }))
  } catch (error) {
    uni.showToast({ title: wechatErrorMessage(error), icon: 'none' })
  } finally {
    wechatLoading.value = false
  }
  // #endif
}

onLoad((options) => {
  const raw = options?.redirect
  redirect.value = typeof raw === 'string' ? raw : ''
})
</script>

<template>
  <view class="page-pad login-page">
    <view class="login-brand">
      <view class="login-brand__mark">
        <image src="/static/brand/logo.png" mode="aspectFit" />
      </view>
      <text class="login-brand__eyebrow">HENGTAI / MEMBER ACCESS</text>
      <view class="login-brand__title">恒泰五金</view>
      <text class="login-brand__subtitle">登录采购账号，查看等级价格并管理订单</text>
    </view>

    <view class="login-card">
      <button class="btn btn-primary login-wechat" :disabled="accountLoading || wechatLoading" @tap="submitWechat">
        <text class="login-wechat__mark">微</text>
        <text>{{ wechatLoading ? '正在登录...' : '微信快捷登录' }}</text>
      </button>
      <text class="login-wechat__tip">仅获取登录凭证，不保存微信会话密钥</text>

      <view class="login-divider"><text>或使用会员账号</text></view>

      <view class="login-form">
        <view class="form-field">
          <text class="form-field__label">会员账号</text>
          <input v-model="form.username" class="form-field__input" type="text" placeholder="请输入会员账号" placeholder-class="form-field__placeholder" />
        </view>
        <view class="form-field">
          <text class="form-field__label">登录密码</text>
          <input v-model="form.password" class="form-field__input" password placeholder="请输入密码" placeholder-class="form-field__placeholder" @confirm="submit" />
        </view>
        <button class="btn login-form__submit" :disabled="accountLoading || wechatLoading" @tap="submit">
          {{ accountLoading ? '正在登录...' : '账号密码登录' }}
        </button>
      </view>

      <view class="login-consent" @tap="agreed = !agreed">
        <view class="login-consent__box" :class="{ 'is-checked': agreed }"><text v-if="agreed">✓</text></view>
        <text>我已阅读并同意隐私政策与用户协议</text>
      </view>
      <LegalLinks class="login-legal" />
    </view>
    <text class="login-page__foot">工业供应 · 品质可查 · 采购可追踪</text>
  </view>
</template>

<style scoped>
.login-page { padding-top: 44rpx; }
.login-brand { position: relative; padding: 38rpx 36rpx 42rpx; overflow: hidden; border-radius: var(--radius-lg) var(--radius-lg) 0 0; color: var(--white); background: var(--brand-deep); }
.login-brand::after { content: ''; position: absolute; right: -30rpx; bottom: 0; width: 160rpx; height: 10rpx; background: var(--brand); }
.login-brand__mark { width: 82rpx; height: 90rpx; margin-bottom: 28rpx; }
.login-brand__mark image { width: 100%; height: 100%; }
.login-brand__eyebrow { display: block; color: #b9c9d8; font-family: Arial, sans-serif; font-size: 20rpx; letter-spacing: 0.14em; }
.login-brand__title { margin-top: 10rpx; font-size: 52rpx; font-weight: 800; letter-spacing: 0.06em; }
.login-brand__subtitle { display: block; margin-top: 14rpx; color: #b9c9d8; font-size: 24rpx; }
.login-card { padding: 36rpx; border: 1rpx solid var(--line); border-top: 0; border-radius: 0 0 var(--radius-lg) var(--radius-lg); background: var(--white); }
.login-wechat { width: 100%; min-height: 92rpx; }
.login-wechat__mark { display: inline-flex; width: 40rpx; height: 40rpx; align-items: center; justify-content: center; border: 1rpx solid rgb(255 255 255 / 55%); border-radius: 50%; font-size: 21rpx; }
.login-wechat__tip { display: block; margin-top: 12rpx; color: var(--muted); font-size: 20rpx; text-align: center; }
.login-divider { display: flex; align-items: center; gap: 20rpx; margin: 34rpx 0; color: var(--muted); font-size: 22rpx; }
.login-divider::before, .login-divider::after { content: ''; height: 1rpx; flex: 1; background: var(--line); }
.form-field { margin-bottom: 24rpx; }
.form-field__label { display: block; margin-bottom: 10rpx; color: var(--ink-soft); font-size: 24rpx; font-weight: 600; }
.form-field__input { height: 88rpx; padding: 0 24rpx; border: 1rpx solid var(--line-dark); border-radius: var(--radius-sm); background: var(--surface); font-size: 28rpx; }
.form-field__placeholder { color: var(--placeholder); }
.login-form__submit { width: 100%; min-height: 88rpx; margin-top: 8rpx; border: 1rpx solid var(--brand-deep); color: var(--brand-deep); background: transparent; }
.login-consent { display: flex; align-items: flex-start; gap: 14rpx; margin-top: 28rpx; color: var(--muted); font-size: 22rpx; line-height: 1.7; }
.login-consent__box { display: flex; width: 30rpx; height: 30rpx; flex: 0 0 auto; align-items: center; justify-content: center; margin-top: 3rpx; border: 2rpx solid var(--line-dark); border-radius: 6rpx; color: var(--white); font-size: 21rpx; }
.login-consent__box.is-checked { border-color: var(--brand); background: var(--brand); }
.login-legal { margin-top: 10rpx; }
.login-page__foot { display: block; padding: 32rpx 0 16rpx; color: var(--muted); font-size: 21rpx; letter-spacing: 0.08em; text-align: center; }
</style>
