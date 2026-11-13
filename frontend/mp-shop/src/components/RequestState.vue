<script setup lang="ts">
withDefaults(
  defineProps<{ loading?: boolean; error?: string; empty?: boolean; loadingText?: string; emptyText?: string }>(),
  { loading: false, error: '', empty: false, loadingText: '正在加载...', emptyText: '暂无数据' },
)
</script>

<template>
  <view class="request-state">
    <view v-if="loading" class="request-state__row" role="status">
      <view class="spinner" />
      <text>{{ loadingText }}</text>
    </view>
    <view v-else-if="error" class="request-state__error" role="alert">
      <text class="request-state__error-text">{{ error }}</text>
      <button class="btn btn-ghost request-state__retry" @tap="$emit('retry')">重新加载</button>
    </view>
    <view v-else-if="empty" class="request-state__empty">
      <view class="request-state__empty-mark">恒</view>
      <text>{{ emptyText }}</text>
    </view>
  </view>
</template>

<style scoped>
.request-state {
  display: flex;
  min-height: 260rpx;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20rpx;
  color: #7b8998;
  font-size: 26rpx;
}

.request-state__row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.spinner {
  width: 40rpx;
  height: 40rpx;
  border: 5rpx solid #dbe9f8;
  border-top-color: var(--brand);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.request-state__error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
  padding: 24rpx;
  text-align: center;
}

.request-state__error-text {
  color: #7a8795;
  font-size: 26rpx;
}

.request-state__retry {
  min-height: 68rpx;
  padding: 0 30rpx;
  font-size: 24rpx;
}

.request-state__empty-mark {
  display: flex;
  width: 88rpx;
  height: 88rpx;
  align-items: center; justify-content: center;
  border-radius: 26rpx;
  color: var(--brand);
  background: var(--brand-light);
  font-size: 40rpx;
  font-weight: 700;
}
</style>
