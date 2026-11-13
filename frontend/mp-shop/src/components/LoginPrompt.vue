<script setup lang="ts">
import { goLogin } from '@/utils/auth'

withDefaults(
  defineProps<{ title: string; description?: string; redirect?: string }>(),
  { description: '', redirect: '' },
)
</script>

<template>
  <view class="login-prompt">
    <image class="login-prompt__mark" src="/static/brand/logo.png" mode="aspectFit" />
    <text class="login-prompt__title">{{ title }}</text>
    <text v-if="description" class="login-prompt__desc">{{ description }}</text>
    <button class="btn btn-primary login-prompt__btn" @tap="goLogin(redirect)">去登录/注册</button>
  </view>
</template>

<style scoped>
.login-prompt {
  display: flex;
  min-height: 560rpx;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20rpx;
  padding: 24rpx;
  text-align: center;
}

.login-prompt__mark {
  width: 110rpx;
  height: 110rpx;
}

.login-prompt__title {
  color: var(--ink-soft);
  font-size: 28rpx;
  font-weight: 650;
}

.login-prompt__desc {
  color: var(--muted);
  font-size: 24rpx;
  line-height: 1.7;
}

.login-prompt__btn {
  min-height: 76rpx;
  margin-top: 10rpx;
  padding: 0 44rpx;
}
</style>
