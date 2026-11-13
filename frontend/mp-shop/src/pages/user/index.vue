<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { memberApi } from '@/api/member'
import { getErrorMessage } from '@/api/http'
import { useUserStore } from '@/store/user'
import { useCartStore } from '@/store/cart'
import type { Level, Profile } from '@/types/shop'

const userStore = useUserStore()
const cartStore = useCartStore()
const profile = ref<Profile | null>(null)
const level = ref<Level | null>(null)
const loading = ref(false)
const error = ref('')

async function loadProfile() {
  if (!userStore.isLoggedIn) return
  loading.value = true
  error.value = ''
  try {
    const [profileData, levelData] = await Promise.all([memberApi.profile(), memberApi.level()])
    profile.value = profileData
    level.value = levelData
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

function logout() {
  userStore.logout()
  cartStore.clear()
  profile.value = null
  level.value = null
  uni.showToast({ title: '已退出登录', icon: 'success' })
}

onShow(loadProfile)
</script>

<template>
  <view class="page-pad">
    <view v-if="!userStore.isLoggedIn" class="guest-card card">
      <view class="guest-card__avatar">恒</view>
      <view class="guest-card__title">欢迎来到恒泰五金</view>
      <view class="guest-card__subtitle">登录后查看会员价格、管理购物车与订单</view>
      <button class="btn btn-primary guest-card__btn" @tap="goLogin">立即登录</button>
    </view>

    <template v-else>
      <view v-if="loading" class="profile-loading">正在加载会员信息...</view>
      <view v-else-if="error" class="profile-error" @tap="loadProfile">{{ error }}，点击重试</view>
      <template v-else-if="profile">
        <view class="profile-card card">
          <view class="profile-card__avatar">{{ profile.username.slice(0, 1).toUpperCase() }}</view>
          <view class="profile-card__info">
            <view class="profile-card__name">{{ profile.username }}</view>
            <view class="profile-card__tags">
              <text class="level-tag">{{ profile.level_name ?? '普通会员' }}</text>
              <text v-if="level" class="level-tag level-tag--ghost">{{ level.name }}</text>
            </view>
            <text class="profile-card__id">客户编号：{{ profile.user_id }}</text>
          </view>
          <button class="profile-card__logout" @tap="logout">退出登录</button>
        </view>

        <view class="profile-grid">
          <view class="profile-item card">
            <text class="profile-item__label">手机号码</text>
            <text class="profile-item__value">{{ profile.phone || '未填写' }}</text>
          </view>
          <view class="profile-item card">
            <text class="profile-item__label">客户等级</text>
            <text class="profile-item__value">{{ profile.level_name ?? '普通会员' }}</text>
          </view>
          <view class="profile-item card">
            <text class="profile-item__label">联系人</text>
            <text class="profile-item__value">{{ profile.real_name || '未填写' }}</text>
          </view>
          <view class="profile-item card">
            <text class="profile-item__label">登录账号</text>
            <text class="profile-item__value">{{ profile.username }}</text>
          </view>
        </view>
      </template>
    </template>

    <view class="quick-links">
      <view class="quick-link card" @tap="goOrders">
        <text class="quick-link__mark">单</text>
        <text class="quick-link__label">我的订单</text>
      </view>
      <view class="quick-link card" @tap="goAddresses">
        <text class="quick-link__mark">址</text>
        <text class="quick-link__label">收货地址</text>
      </view>
      <view class="quick-link card" @tap="goCart">
        <text class="quick-link__mark">购</text>
        <text class="quick-link__label">购物车</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.guest-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14rpx;
  padding: 70rpx 40rpx;
  text-align: center;
}

.guest-card__avatar {
  display: flex;
  width: 128rpx;
  height: 128rpx;
  align-items: center; justify-content: center;
  border-radius: 40rpx;
  color: #ffffff;
  background: linear-gradient(135deg, #0c56ad, #2b96e9);
  font-size: 56rpx;
  font-weight: 700;
}

.guest-card__title {
  margin-top: 12rpx;
  font-size: 34rpx;
  font-weight: 700;
}

.guest-card__subtitle {
  color: #7b8998;
  font-size: 24rpx;
}

.guest-card__btn {
  min-height: 80rpx;
  margin-top: 20rpx;
  padding: 0 60rpx;
}

.profile-loading,
.profile-error {
  padding: 80rpx 0;
  color: #8b97a4;
  font-size: 24rpx;
  text-align: center;
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 32rpx 28rpx;
}

.profile-card__avatar {
  display: flex;
  width: 120rpx;
  height: 120rpx;
  flex: 0 0 auto;
  align-items: center; justify-content: center;
  border-radius: 36rpx;
  color: #ffffff;
  background: linear-gradient(135deg, #0c56ad, #2b96e9);
  font-size: 52rpx;
  font-weight: 700;
}

.profile-card__info {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
  gap: 8rpx;
}

.profile-card__name {
  font-size: 36rpx;
  font-weight: 750;
}

.profile-card__tags {
  display: flex;
  gap: 10rpx;
}

.level-tag {
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
  color: #1559ab;
  background: #eaf3ff;
  font-size: 20rpx;
}

.level-tag--ghost {
  color: #718094;
  background: #f0f3f7;
}

.profile-card__id {
  color: #8a97a5;
  font-size: 22rpx;
}

.profile-card__logout {
  flex: 0 0 auto;
  padding: 14rpx 24rpx;
  border: 1rpx solid #e0e7ef;
  border-radius: 12rpx;
  color: #64768a;
  background: #ffffff;
  font-size: 24rpx;
}

.profile-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-top: 24rpx;
}

.profile-item {
  display: flex;
  width: calc(50% - 10rpx);
  flex-direction: column;
  gap: 8rpx;
  margin-bottom: 20rpx;
  padding: 26rpx 28rpx;
}

.profile-item__label {
  color: #95a2af;
  font-size: 21rpx;
}

.profile-item__value {
  color: #3c4e61;
  font-size: 28rpx;
  font-weight: 600;
}

.quick-links {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-top: 24rpx;
}

.quick-link {
  display: flex;
  width: calc(33.33% - 14rpx);
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  padding: 34rpx 10rpx;
}

.quick-link__mark {
  display: flex;
  width: 76rpx;
  height: 76rpx;
  align-items: center; justify-content: center;
  border-radius: 24rpx;
  color: var(--brand);
  background: var(--brand-light);
  font-size: 32rpx;
  font-weight: 700;
}

.quick-link__label {
  color: #4e6073;
  font-size: 24rpx;
  font-weight: 600;
}
</style>
