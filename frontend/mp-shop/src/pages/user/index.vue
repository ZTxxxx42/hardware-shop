<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { memberApi } from '@/api/member'
import { getErrorMessage } from '@/api/http'
import { useUserStore } from '@/store/user'
import { useCartStore } from '@/store/cart'
import type { AccountDeletion, Level, Profile } from '@/types/shop'
import LegalLinks from '@/components/LegalLinks.vue'

const userStore = useUserStore()
const cartStore = useCartStore()
const profile = ref<Profile | null>(null)
const level = ref<Level | null>(null)
const deletion = ref<AccountDeletion | null>(null)
const loading = ref(false)
const deleting = ref(false)
const error = ref('')

function deletionKey(userId: number): string {
  return `hengtai_account_deletion_${userId}`
}

function restoreDeletion(userId: number) {
  const cached = uni.getStorageSync(deletionKey(userId)) as AccountDeletion | ''
  deletion.value = cached && cached.deletion_status === 'PENDING' ? cached : null
}

function formatDate(value: string): string {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString('zh-CN', { hour12: false })
}

async function loadProfile() {
  if (!userStore.isLoggedIn) {
    profile.value = null
    deletion.value = null
    return
  }
  loading.value = true
  error.value = ''
  try {
    const [profileData, levelData] = await Promise.all([memberApi.profile(), memberApi.level()])
    profile.value = profileData
    level.value = levelData
    restoreDeletion(profileData.user_id)
  } catch (requestError) {
    error.value = getErrorMessage(requestError, '会员信息加载失败')
  } finally {
    loading.value = false
  }
}

function goLogin() {
  uni.navigateTo({ url: '/pages/login/index' })
}

function goOrders() {
  if (!userStore.isLoggedIn) {
    goLogin()
    return
  }
  uni.navigateTo({ url: '/pages/orders/index' })
}

function goAddresses() {
  if (!userStore.isLoggedIn) {
    goLogin()
    return
  }
  uni.navigateTo({ url: '/pages/address/index' })
}

function goCart() {
  uni.switchTab({ url: '/pages/cart/index' })
}

async function requestAccountDeletion() {
  const currentProfile = profile.value
  if (!currentProfile || deleting.value) return
  if (deletion.value?.deletion_status === 'PENDING') {
    uni.showToast({ title: '注销申请已提交，正在等待处理', icon: 'none' })
    return
  }
  const confirmed = await new Promise<boolean>((resolve) => {
    uni.showModal({
      title: '申请账号注销',
      content: '提交后仅生成注销申请，账号不会立即删除。平台将按流程核验并处理，确定继续吗？',
      confirmText: '提交申请',
      confirmColor: '#c8521f',
      cancelText: '再想想',
      success: (result) => resolve(result.confirm),
      fail: () => resolve(false),
    })
  })
  if (!confirmed) return
  deleting.value = true
  try {
    const result = await memberApi.requestAccountDeletion()
    deletion.value = result
    uni.setStorageSync(deletionKey(currentProfile.user_id), result)
    uni.showToast({ title: '注销申请已提交', icon: 'success' })
  } catch (requestError) {
    uni.showToast({ title: getErrorMessage(requestError, '注销申请提交失败，请稍后重试'), icon: 'none' })
  } finally {
    deleting.value = false
  }
}

function logout() {
  userStore.logout()
  cartStore.clear()
  profile.value = null
  level.value = null
  deletion.value = null
  uni.showToast({ title: '已退出登录', icon: 'success' })
}

onShow(loadProfile)
</script>

<template>
  <view class="page-pad user-page">
    <view v-if="!userStore.isLoggedIn" class="guest-card">
      <view class="guest-card__avatar">恒</view>
      <text class="eyebrow">HENGTAI / MEMBER</text>
      <view class="guest-card__title">采购服务，从登录开始</view>
      <text class="guest-card__subtitle">查看会员价格，管理购物车、订单与收货地址</text>
      <button class="btn btn-primary guest-card__btn" @tap="goLogin">立即登录</button>
    </view>

    <template v-else>
      <view v-if="loading" class="profile-loading"><view class="profile-loading__line" />正在加载会员信息...</view>
      <view v-else-if="error" class="profile-error" @tap="loadProfile">{{ error }}，点击重试</view>
      <template v-else-if="profile">
        <view class="profile-card">
          <view class="profile-card__avatar">{{ profile.username.slice(0, 1).toUpperCase() }}</view>
          <view class="profile-card__info">
            <view class="profile-card__name">{{ profile.username }}</view>
            <view class="profile-card__tags">
              <text class="level-tag">{{ profile.level_name ?? '普通会员' }}</text>
              <text v-if="level" class="level-tag level-tag--ghost">{{ level.name }}</text>
            </view>
            <text class="profile-card__id">客户编号 / {{ profile.user_id }}</text>
          </view>
          <button class="profile-card__logout" @tap="logout">退出</button>
        </view>

        <view class="profile-grid">
          <view class="profile-item card"><text class="profile-item__label">手机号码</text><text class="profile-item__value">{{ profile.phone || '未填写' }}</text></view>
          <view class="profile-item card"><text class="profile-item__label">客户等级</text><text class="profile-item__value">{{ profile.level_name ?? '普通会员' }}</text></view>
          <view class="profile-item card"><text class="profile-item__label">联系人</text><text class="profile-item__value">{{ profile.real_name || '未填写' }}</text></view>
          <view class="profile-item card"><text class="profile-item__label">登录账号</text><text class="profile-item__value">{{ profile.username }}</text></view>
        </view>
      </template>
    </template>

    <view class="quick-links">
      <view class="quick-link card" @tap="goOrders"><text class="quick-link__mark">单</text><text class="quick-link__label">我的订单</text><text class="quick-link__hint">进度查询</text></view>
      <view class="quick-link card" @tap="goAddresses"><text class="quick-link__mark">址</text><text class="quick-link__label">收货地址</text><text class="quick-link__hint">配送管理</text></view>
      <view class="quick-link card" @tap="goCart"><text class="quick-link__mark">购</text><text class="quick-link__label">购物车</text><text class="quick-link__hint">继续采购</text></view>
    </view>

    <view v-if="userStore.isLoggedIn && profile" class="account-panel card">
      <view class="account-panel__heading">账号与安全</view>
      <view v-if="deletion" class="deletion-status">
        <view class="deletion-status__top"><text>注销申请状态</text><text class="deletion-status__tag">{{ deletion.deletion_status }}</text></view>
        <text class="deletion-status__time">申请时间：{{ formatDate(deletion.deletion_requested_at) }}</text>
        <text class="deletion-status__note">申请已受理，账号尚未删除，请等待平台处理。</text>
      </view>
      <button class="account-row" :disabled="deleting" @tap="requestAccountDeletion">
        <view class="account-row__body">
          <text class="account-row__title">{{ deleting ? '正在提交注销申请...' : '账号注销' }}</text>
          <text class="account-row__desc">提交注销申请，不会在客户端即时删除账号</text>
        </view>
        <text class="account-row__arrow">›</text>
      </button>
    </view>

    <view class="user-legal">
      <LegalLinks quiet />
      <text>恒泰五金 · 工业供应</text>
    </view>
  </view>
</template>

<style scoped>
.user-page { padding-top: 32rpx; }
.guest-card { display: flex; flex-direction: column; align-items: flex-start; padding: 44rpx 36rpx; border-top: 6rpx solid var(--brand); background: var(--brand-deep); color: var(--white); }
.guest-card .eyebrow { color: #d6d1c7; }
.guest-card__avatar { display: flex; width: 112rpx; height: 112rpx; align-items: center; justify-content: center; margin-bottom: 28rpx; border-radius: 28rpx; color: var(--brand-deep); background: var(--brand); font-size: 48rpx; font-weight: 800; }
.guest-card__title { margin-top: 12rpx; font-size: 38rpx; font-weight: 750; }
.guest-card__subtitle { margin-top: 12rpx; color: #d6d1c7; font-size: 24rpx; }
.guest-card__btn { min-height: 80rpx; margin-top: 30rpx; padding: 0 44rpx; }
.profile-loading, .profile-error { padding: 80rpx 0; color: var(--muted); font-size: 24rpx; text-align: center; }
.profile-loading__line { width: 56rpx; height: 5rpx; margin: 0 auto 18rpx; background: var(--brand); }
.profile-card { display: flex; align-items: center; gap: 24rpx; padding: 34rpx 28rpx; border-top: 5rpx solid var(--brand); color: var(--white); background: var(--brand-deep); }
.profile-card__avatar { display: flex; width: 108rpx; height: 108rpx; flex: 0 0 auto; align-items: center; justify-content: center; border: 1rpx solid #625d54; border-radius: 26rpx; color: var(--white); background: #353630; font-size: 46rpx; font-weight: 700; }
.profile-card__info { display: flex; min-width: 0; flex: 1; flex-direction: column; gap: 8rpx; }
.profile-card__name { overflow: hidden; font-size: 34rpx; font-weight: 750; text-overflow: ellipsis; white-space: nowrap; }
.profile-card__tags { display: flex; flex-wrap: wrap; gap: 10rpx; }
.level-tag { padding: 5rpx 14rpx; border-radius: 8rpx; color: #ffddc7; background: #5a3b29; font-size: 20rpx; }
.level-tag--ghost { color: #ded9d0; background: #454640; }
.profile-card__id { color: #bdb8af; font-family: Arial, sans-serif; font-size: 21rpx; }
.profile-card__logout { flex: 0 0 auto; padding: 12rpx 18rpx; border: 1rpx solid #625d54; border-radius: 10rpx; color: #ded9d0; font-size: 22rpx; }
.profile-grid { display: flex; flex-wrap: wrap; justify-content: space-between; margin-top: 20rpx; }
.profile-item { display: flex; width: calc(50% - 10rpx); flex-direction: column; gap: 8rpx; margin-bottom: 20rpx; padding: 24rpx; }
.profile-item__label { color: var(--muted); font-size: 21rpx; }
.profile-item__value { overflow: hidden; color: var(--ink-soft); font-size: 26rpx; font-weight: 600; text-overflow: ellipsis; white-space: nowrap; }
.quick-links { display: flex; flex-wrap: wrap; justify-content: space-between; margin-top: 8rpx; }
.quick-link { display: flex; width: calc(33.33% - 14rpx); flex-direction: column; align-items: center; padding: 28rpx 8rpx; }
.quick-link__mark { display: flex; width: 68rpx; height: 68rpx; align-items: center; justify-content: center; border-radius: 18rpx; color: var(--brand-dark); background: var(--brand-light); font-size: 29rpx; font-weight: 700; }
.quick-link__label { margin-top: 14rpx; color: var(--ink-soft); font-size: 24rpx; font-weight: 600; }
.quick-link__hint { margin-top: 4rpx; color: var(--muted); font-size: 19rpx; }
.account-panel { margin-top: 24rpx; padding: 28rpx; }
.account-panel__heading { padding-bottom: 18rpx; border-bottom: 1rpx solid var(--line); font-size: 28rpx; font-weight: 700; }
.account-row { display: flex; width: 100%; align-items: center; gap: 20rpx; padding-top: 24rpx; text-align: left; }
.account-row__body { display: flex; min-width: 0; flex: 1; flex-direction: column; gap: 6rpx; }
.account-row__title { color: var(--danger); font-size: 26rpx; font-weight: 600; }
.account-row__desc { color: var(--muted); font-size: 21rpx; }
.account-row__arrow { color: var(--muted); font-size: 36rpx; }
.deletion-status { margin-top: 22rpx; padding: 20rpx; border-left: 5rpx solid var(--warning); background: var(--warning-light); }
.deletion-status__top { display: flex; align-items: center; justify-content: space-between; color: var(--ink-soft); font-size: 24rpx; }
.deletion-status__tag { color: var(--warning); font-family: Arial, sans-serif; font-size: 21rpx; font-weight: 700; }
.deletion-status__time, .deletion-status__note { display: block; margin-top: 8rpx; color: var(--muted); font-size: 20rpx; }
.user-legal { display: flex; flex-direction: column; align-items: center; gap: 12rpx; padding: 36rpx 0 10rpx; color: var(--muted); font-size: 20rpx; }
</style>
