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
      <image class="request-state__empty-mark" src="/static/brand/logo.png" mode="aspectFit" />
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
  color: var(--muted);
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
  border: 5rpx solid var(--surface-deep);
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
  color: var(--muted);
  font-size: 26rpx;
}

.request-state__retry {
  min-height: 68rpx;
  padding: 0 30rpx;
  font-size: 24rpx;
}

.request-state__empty-mark {
  width: 88rpx;
  height: 88rpx;
}
</style>
