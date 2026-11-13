<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { orderApi } from '@/api/order'
import { getErrorMessage } from '@/api/http'
import type { OrderBrief } from '@/types/shop'
import { formatPrice } from '@/utils/catalog'
import { ensureLogin } from '@/utils/auth'
import RequestState from '@/components/RequestState.vue'
import LoginPrompt from '@/components/LoginPrompt.vue'

type StatusTone = 'warning' | 'primary' | 'success' | 'info'

const orders = ref<OrderBrief[]>([])
const loading = ref(true)
const error = ref('')
const needsLogin = ref(false)
const actionOrderId = ref<number | null>(null)

const statusMap: Record<string, { label: string; tone: StatusTone }> = {
  PENDING_PAYMENT: { label: '待支付', tone: 'warning' },
  PAID: { label: '已支付', tone: 'primary' },
  SHIPPED: { label: '已发货', tone: 'success' },
  COMPLETED: { label: '已完成', tone: 'info' },
  CANCELLED: { label: '已取消', tone: 'info' },
}

function statusLabel(status: string): string {
  return statusMap[status]?.label ?? status
}

function statusTone(status: string): StatusTone {
  return statusMap[status]?.tone ?? 'info'
}

function formatDate(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { hour12: false })
}

function confirm(content: string, confirmText: string): Promise<boolean> {
  return new Promise((resolve) => {
    uni.showModal({
      title: '提示',
      content,
      confirmText,
      cancelText: '取消',
      success: (res) => resolve(res.confirm),
      fail: () => resolve(false),
    })
  })
}

async function loadOrders() {
  loading.value = true
  error.value = ''
  try {
    orders.value = await orderApi.list()
  } catch (requestError) {
    orders.value = []
    error.value = getErrorMessage(requestError, '订单加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

function openDetail(order: OrderBrief) {
  uni.navigateTo({ url: `/pages/order-detail/index?id=${order.id}` })
}

async function cancelOrder(order: OrderBrief) {
  const ok = await confirm(`确定取消订单 ${order.order_no} 吗？`, '取消订单')
  if (!ok) return
  actionOrderId.value = order.id
  try {
    await orderApi.cancel(order.id)
    uni.showToast({ title: '订单已取消', icon: 'success' })
    await loadOrders()
  } catch (requestError) {
    uni.showToast({ title: getErrorMessage(requestError, '取消订单失败'), icon: 'none' })
  } finally {
    actionOrderId.value = null
  }
}

async function confirmOrder(order: OrderBrief) {
  const ok = await confirm('确认已收到全部商品？', '确认收货')
  if (!ok) return
  actionOrderId.value = order.id
  try {
    await orderApi.confirm(order.id)
    uni.showToast({ title: '已确认收货', icon: 'success' })
    await loadOrders()
  } catch (requestError) {
    uni.showToast({ title: getErrorMessage(requestError, '确认收货失败'), icon: 'none' })
  } finally {
    actionOrderId.value = null
  }
}

function goPay() {
  uni.showToast({ title: '支付暂未接入，敬请期待', icon: 'none' })
}

onShow(() => {
  if (!ensureLogin()) {
    needsLogin.value = true
    loading.value = false
    error.value = ''
    return
  }
  needsLogin.value = false
  void loadOrders()
})
</script>

<template>
  <view class="page-pad">
    <view class="page-heading">
      <text class="eyebrow">MY ORDERS</text>
      <view class="page-title">订单中心</view>
      <text class="page-subtitle">查看待支付、已支付、已发货及已完成订单</text>
    </view>

    <LoginPrompt
      v-if="needsLogin"
      title="登录后查看订单"
      :redirect="'/pages/orders/index'"
    />
    <RequestState
      v-else-if="loading || error || orders.length === 0"
      :loading="loading"
      :error="error"
      :empty="!loading && !error"
      loading-text="正在加载订单..."
      empty-text="暂无订单，快去选购商品吧"
      @retry="loadOrders"
    />
    <view v-else class="order-list">
      <view v-for="order in orders" :key="order.id" class="order-card card" @tap="openDetail(order)">
        <view class="order-card__head">
          <view class="order-card__no">
            <text class="order-card__no-label">订单号</text>
            <text class="order-card__no-value">{{ order.order_no }}</text>
          </view>
          <text class="status-tag" :class="`is-${statusTone(order.status)}`">{{ statusLabel(order.status) }}</text>
        </view>
        <view class="order-card__meta">
          <text>下单时间：{{ formatDate(order.created_at) }}</text>
          <text class="order-card__total">¥{{ formatPrice(order.total_amount) }}</text>
        </view>
        <view class="order-card__actions" @tap.stop>
          <view class="action-btn" @tap="openDetail(order)">查看详情</view>
          <template v-if="order.status === 'PENDING_PAYMENT'">
            <view class="action-btn" @tap="goPay">去支付</view>
            <view class="action-btn action-btn--danger" @tap="cancelOrder(order)">取消订单</view>
          </template>
          <view v-else-if="order.status === 'SHIPPED'" class="action-btn action-btn--success" @tap="confirmOrder(order)">确认收货</view>
        </view>
      </view>
    </view>
  </view>
</template>

<style scoped>
.page-heading {
  padding: 10rpx 0 26rpx;
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.order-card {
  padding: 26rpx 28rpx;
}

.order-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
}

.order-card__no {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 4rpx;
}

.order-card__no-label {
  color: #95a2af;
  font-size: 20rpx;
}

.order-card__no-value {
  overflow: hidden;
  color: #3c4e61;
  font-family: Arial, sans-serif;
  font-size: 25rpx;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-tag {
  flex: 0 0 auto;
  padding: 6rpx 18rpx;
  border-radius: 10rpx;
  font-size: 21rpx;
}

.status-tag.is-warning {
  color: #b26a12;
  background: #fff3e2;
}

.status-tag.is-primary {
  color: var(--brand-dark);
  background: var(--brand-light);
}

.status-tag.is-success {
  color: #14833c;
  background: #e8f7ee;
}

.status-tag.is-info {
  color: #7a8795;
  background: #f0f3f7;
}

.order-card__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  margin-top: 20rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #f0f3f7;
  color: #7b8998;
  font-size: 22rpx;
}

.order-card__total {
  color: var(--price);
  font-family: Arial, sans-serif;
  font-size: 32rpx;
  font-weight: 700;
}

.order-card__actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 30rpx;
  margin-top: 20rpx;
}

.action-btn {
  padding: 10rpx 0;
  color: var(--brand);
  font-size: 24rpx;
  font-weight: 600;
}

.action-btn--danger {
  color: #ef5350;
}

.action-btn--success {
  color: #14833c;
}
</style>
