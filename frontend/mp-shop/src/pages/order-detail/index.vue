<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { orderApi } from '@/api/order'
import { getErrorMessage } from '@/api/http'
import type { OrderDetail } from '@/types/shop'
import { formatPrice, isZeroAmount } from '@/utils/catalog'
import { ensureLogin } from '@/utils/auth'
import RequestState from '@/components/RequestState.vue'

const detail = ref<OrderDetail | null>(null)
const loading = ref(true)
const error = ref('')
const actionLoading = ref(false)
const orderId = ref<number | null>(null)

const statusMap: Record<string, { label: string; tone: string }> = {
  PENDING_PAYMENT: { label: '待支付', tone: 'warning' },
  PAID: { label: '已支付', tone: 'primary' },
  SHIPPED: { label: '已发货', tone: 'success' },
  COMPLETED: { label: '已完成', tone: 'info' },
  CANCELLED: { label: '已取消', tone: 'info' },
}

function statusLabel(status: string): string {
  return statusMap[status]?.label ?? status
}

function formatDate(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { hour12: false })
}

function channelLabel(channel: string): string {
  if (channel === 'wechat') return '微信支付'
  if (channel === 'alipay') return '支付宝'
  return channel
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

async function loadDetail() {
  if (!orderId.value) {
    loading.value = false
    error.value = '订单编号无效'
    return
  }
  loading.value = true
  error.value = ''
  try {
    detail.value = await orderApi.detail(orderId.value)
  } catch (requestError) {
    error.value = getErrorMessage(requestError, '订单详情加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

async function cancelOrder() {
  if (!detail.value) return
  const ok = await confirm(`确定取消订单 ${detail.value.order_no} 吗？`, '取消订单')
  if (!ok) return
  actionLoading.value = true
  try {
    detail.value = await orderApi.cancel(detail.value.id)
    uni.showToast({ title: '订单已取消', icon: 'success' })
  } catch (requestError) {
    uni.showToast({ title: getErrorMessage(requestError, '取消订单失败'), icon: 'none' })
  } finally {
    actionLoading.value = false
  }
}

async function confirmOrder() {
  if (!detail.value) return
  const ok = await confirm('确认已收到全部商品？', '确认收货')
  if (!ok) return
  actionLoading.value = true
  try {
    detail.value = await orderApi.confirm(detail.value.id)
    uni.showToast({ title: '已确认收货', icon: 'success' })
  } catch (requestError) {
    uni.showToast({ title: getErrorMessage(requestError, '确认收货失败'), icon: 'none' })
  } finally {
    actionLoading.value = false
  }
}

function goPay() {
  uni.showToast({ title: '支付暂未接入，敬请期待', icon: 'none' })
}

onLoad((options) => {
  const raw = options?.id
  const id = typeof raw === 'string' && raw ? Number(raw) : NaN
  orderId.value = Number.isInteger(id) && id > 0 ? id : null
  if (!ensureLogin('/pages/orders/index')) return
  void loadDetail()
})
</script>

<template>
  <view class="page-pad">
    <RequestState
      v-if="loading || error || !detail"
      :loading="loading"
      :error="error"
      :empty="!loading && !error"
      loading-text="正在加载订单详情..."
      empty-text="订单不存在"
      @retry="loadDetail"
    />

    <template v-else>
      <view class="status-card card">
        <view class="status-card__row">
          <text class="status-tag" :class="`is-${statusMap[detail.status]?.tone ?? 'info'}`">{{ statusLabel(detail.status) }}</text>
          <text class="status-card__date">{{ formatDate(detail.created_at) }}</text>
        </view>
        <text class="status-card__no">订单号：{{ detail.order_no }}</text>
      </view>

      <view class="detail-block card">
        <view class="detail-block__title">商品明细</view>
        <view v-for="item in detail.items" :key="item.id" class="detail-line">
          <view class="detail-line__info">
            <text class="detail-line__name">{{ item.product_name }}</text>
            <text class="detail-line__meta">¥{{ formatPrice(item.price) }} × {{ item.quantity }}</text>
          </view>
          <text class="detail-line__amount">¥{{ formatPrice(item.subtotal) }}</text>
        </view>
      </view>

      <view class="detail-block card">
        <view class="detail-block__title">收货地址</view>
        <text class="detail-block__text">{{ detail.address_snapshot.receiver }} · {{ detail.address_snapshot.phone }}</text>
        <text class="detail-block__text">{{ detail.address_snapshot.region }} {{ detail.address_snapshot.detail }}</text>
      </view>

      <view class="detail-block card">
        <view class="detail-block__title">支付信息</view>
        <text v-if="detail.payments.length === 0" class="detail-block__text">暂无支付记录</text>
        <view v-for="payment in detail.payments" :key="payment.id" class="detail-line">
          <view class="detail-line__info">
            <text class="detail-line__name">{{ channelLabel(payment.channel) }}</text>
            <text class="detail-line__meta">¥{{ formatPrice(payment.amount) }}</text>
          </view>
          <text class="detail-line__amount">{{ payment.status === 'PAID' ? '已支付' : '待支付' }}</text>
        </view>
      </view>

      <view class="total-card card">
        <view class="total-card__row"><text>商品金额</text><text>¥{{ formatPrice(detail.product_amount) }}</text></view>
        <view class="total-card__row">
          <text>运费</text>
          <text>{{ isZeroAmount(detail.freight_amount) ? '免运费' : `¥${formatPrice(detail.freight_amount)}` }}</text>
        </view>
        <view class="total-card__row total-card__row--total">
          <text>应付合计</text>
          <text class="total-card__total">¥{{ formatPrice(detail.total_amount) }}</text>
        </view>
      </view>

      <view v-if="detail.status === 'PENDING_PAYMENT' || detail.status === 'SHIPPED'" class="detail-actions">
        <template v-if="detail.status === 'PENDING_PAYMENT'">
          <button class="btn btn-primary detail-actions__btn" @tap="goPay">去支付</button>
          <button class="btn btn-danger detail-actions__btn" :disabled="actionLoading" @tap="cancelOrder">取消订单</button>
        </template>
        <button v-else class="btn btn-primary detail-actions__btn" :disabled="actionLoading" @tap="confirmOrder">确认收货</button>
      </view>
    </template>
  </view>
</template>

<style scoped>
.status-card {
  padding: 28rpx;
}

.status-card__row {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.status-card__date {
  color: #8a97a5;
  font-size: 22rpx;
}

.status-card__no {
  display: block;
  margin-top: 16rpx;
  color: #657689;
  font-family: Arial, sans-serif;
  font-size: 24rpx;
}

.status-tag {
  padding: 8rpx 20rpx;
  border-radius: 10rpx;
  font-size: 24rpx;
  font-weight: 600;
}

.status-tag.is-warning {
  color: #b26a12;
  background: #fff3e2;
}

.status-tag.is-primary {
  color: #1559ab;
  background: #eaf3ff;
}

.status-tag.is-success {
  color: #14833c;
  background: #e8f7ee;
}

.status-tag.is-info {
  color: #7a8795;
  background: #f0f3f7;
}

.detail-block {
  margin-top: 24rpx;
  padding: 28rpx;
}

.detail-block__title {
  margin-bottom: 18rpx;
  font-size: 30rpx;
  font-weight: 700;
}

.detail-block__text {
  display: block;
  color: #657689;
  font-size: 24rpx;
  line-height: 1.8;
}

.detail-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  padding: 18rpx 0;
  border-bottom: 1rpx solid #f2f5f8;
}

.detail-line:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.detail-line__info {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 4rpx;
}

.detail-line__name {
  color: #3c4e61;
  font-size: 25rpx;
  font-weight: 600;
}

.detail-line__meta {
  color: #8a97a5;
  font-size: 21rpx;
}

.detail-line__amount {
  color: var(--price);
  font-family: Arial, sans-serif;
  font-size: 26rpx;
  font-weight: 700;
  white-space: nowrap;
}

.total-card {
  margin-top: 24rpx;
  padding: 26rpx 28rpx;
  background: #f6f9fd;
}

.total-card__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14rpx 0;
  color: #657689;
  font-size: 24rpx;
}

.total-card__row--total {
  padding-top: 22rpx;
  border-top: 1rpx solid #e4ebf2;
}

.total-card__row--total > text:first-child {
  color: #3c4e61;
  font-weight: 600;
}

.total-card__total {
  color: var(--price);
  font-family: Arial, sans-serif;
  font-size: 38rpx;
  font-weight: 700;
}

.detail-actions {
  display: flex;
  gap: 20rpx;
  margin-top: 28rpx;
}

.detail-actions__btn {
  min-height: 88rpx;
  flex: 1;
  border-radius: 14rpx;
}
</style>
