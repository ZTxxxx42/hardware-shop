<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  carrier?: string | null
  trackingNo?: string | null
  shippedAt?: string | null
}>(), { carrier: null, trackingNo: null, shippedAt: null })

const hasLogistics = computed(() => Boolean(props.carrier || props.trackingNo || props.shippedAt))
const shippedAtText = computed(() => {
  if (!props.shippedAt) return ''
  const date = new Date(props.shippedAt)
  return Number.isNaN(date.getTime()) ? props.shippedAt : date.toLocaleString('zh-CN', { hour12: false })
})

function copyTrackingNo() {
  if (!props.trackingNo) return
  uni.setClipboardData({
    data: props.trackingNo,
    success: () => uni.showToast({ title: '物流单号已复制', icon: 'success' }),
  })
}
</script>

<template>
  <view class="logistics-card card">
    <view class="logistics-card__heading">
      <view>
        <text class="eyebrow">DELIVERY</text>
        <view class="logistics-card__title">物流信息</view>
      </view>
      <text class="logistics-card__status" :class="{ 'is-shipped': hasLogistics }">{{ hasLogistics ? '已发货' : '待发货' }}</text>
    </view>
    <view v-if="hasLogistics" class="logistics-card__body">
      <view class="logistics-row">
        <text class="logistics-row__label">物流公司</text>
        <text class="logistics-row__value">{{ carrier || '待补充' }}</text>
      </view>
      <view class="logistics-row">
        <text class="logistics-row__label">物流单号</text>
        <view class="logistics-row__tracking">
          <text class="logistics-row__value logistics-row__value--number">{{ trackingNo || '待补充' }}</text>
          <button v-if="trackingNo" class="logistics-row__copy" @tap="copyTrackingNo">复制</button>
        </view>
      </view>
      <view v-if="shippedAtText" class="logistics-row">
        <text class="logistics-row__label">发货时间</text>
        <text class="logistics-row__value">{{ shippedAtText }}</text>
      </view>
      <text class="logistics-card__tip">物流轨迹请以承运公司查询结果为准</text>
    </view>
    <view v-else class="logistics-card__empty">商家发货后，物流公司与单号会显示在这里。</view>
  </view>
</template>

<style scoped>
.logistics-card { margin-top: 24rpx; padding: 28rpx; }
.logistics-card__heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20rpx;
  padding-bottom: 22rpx;
  border-bottom: 1rpx solid var(--line);
}
.logistics-card__title { margin-top: 4rpx; font-size: 30rpx; font-weight: 700; }
.logistics-card__status {
  padding: 6rpx 16rpx;
  border-radius: var(--radius-sm);
  color: var(--muted);
  background: var(--surface-deep);
  font-size: 21rpx;
}
.logistics-card__status.is-shipped { color: var(--success); background: var(--success-light); }
.logistics-card__body { padding-top: 12rpx; }
.logistics-row { display: flex; align-items: flex-start; gap: 24rpx; padding: 14rpx 0; }
.logistics-row__label { width: 112rpx; flex: 0 0 auto; color: var(--muted); font-size: 23rpx; }
.logistics-row__value {
  min-width: 0;
  flex: 1;
  color: var(--ink-soft);
  font-size: 25rpx;
  overflow-wrap: anywhere;
}
.logistics-row__value--number { font-family: Arial, sans-serif; letter-spacing: 0.03em; }
.logistics-row__tracking { display: flex; min-width: 0; flex: 1; align-items: center; gap: 16rpx; }
.logistics-row__copy {
  flex: 0 0 auto;
  padding: 6rpx 14rpx;
  border: 1rpx solid var(--line-dark);
  border-radius: 8rpx;
  color: var(--brand-dark);
  font-size: 20rpx;
}
.logistics-card__tip { display: block; margin-top: 12rpx; color: var(--muted); font-size: 21rpx; }
.logistics-card__empty { padding-top: 24rpx; color: var(--muted); font-size: 24rpx; line-height: 1.8; }
</style>
