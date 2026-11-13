<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { orderApi } from '@/api/order'
import { getErrorMessage } from '@/api/http'
import type { OrderDetail } from '@/types/shop'
import { formatPrice, isZeroAmount } from '@/utils/catalog'
import { ensureLogin } from '@/utils/auth'
import RequestState from '@/components/RequestState.vue'
import LogisticsCard from '@/components/LogisticsCard.vue'

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
  <view class="page-pad order-detail-page">
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
      <view class="status-card">
        <view class="status-card__head">
          <text class="status-tag" :class="`is-${statusMap[detail.status]?.tone ?? 'info'}`">{{ statusLabel(detail.status) }}</text>
          <text class="status-card__date">{{ formatDate(detail.created_at) }}</text>
        </view>
        <text class="status-card__no">订单号 / {{ detail.order_no }}</text>
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

      <view v-if="detail.remark" class="remark-card card">
        <text class="eyebrow">ORDER NOTE</text>
        <text class="remark-card__text">{{ detail.remark }}</text>
      </view>

      <LogisticsCard :carrier="detail.carrier" :tracking-no="detail.tracking_no" :shipped-at="detail.shipped_at" />

      <view v-if="detail.address_snapshot" class="detail-block card">
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
          <text class="detail-line__amount detail-line__amount--plain">{{ payment.status === 'PAID' ? '已支付' : '待支付' }}</text>
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
          <button class="btn detail-actions__btn detail-actions__btn--danger" :disabled="actionLoading" @tap="cancelOrder">取消订单</button>
        </template>
        <button v-else class="btn btn-primary detail-actions__btn" :disabled="actionLoading" @tap="confirmOrder">确认收货</button>
      </view>
      <text v-if="detail.status === 'PENDING_PAYMENT'" class="order-detail-page__note">支付能力尚在接入中，不会产生真实扣款</text>
    </template>
  </view>
</template>

<style scoped>
.order-detail-page { padding-bottom: 56rpx; }
.status-card { margin-top: 12rpx; padding: 26rpx 28rpx; border-top: 5rpx solid var(--brand); background: var(--brand-deep); color: var(--white); }
.status-card__head { display: flex; align-items: center; justify-content: space-between; gap: 20rpx; }
.status-card__date { color: #d6d1c7; font-size: 21rpx; }
.status-card__no { display: block; margin-top: 16rpx; color: #ded9d0; font-family: Arial, sans-serif; font-size: 23rpx; letter-spacing: 0.02em; }
.status-tag { padding: 7rpx 18rpx; border-radius: 10rpx; font-size: 22rpx; font-weight: 600; }
.status-tag.is-warning { color: #2c1c0e; background: var(--warning); }
.status-tag.is-primary { color: #2c1c0e; background: var(--brand); }
.status-tag.is-success { color: #0e3522; background: #9fd4b1; }
.status-tag.is-info { color: #e8e5df; background: #4c4e48; }
.detail-block { margin-top: 22rpx; padding: 28rpx; }
.detail-block__title { margin-bottom: 18rpx; font-size: 30rpx; font-weight: 700; }
.detail-block__text { display: block; color: var(--ink-soft); font-size: 24rpx; line-height: 1.8; }
.detail-line { display: flex; align-items: center; justify-content: space-between; gap: 20rpx; padding: 18rpx 0; border-bottom: 1rpx solid var(--line); }
.detail-line:last-child { border-bottom: 0; padding-bottom: 0; }
.detail-line__info { display: flex; min-width: 0; flex-direction: column; gap: 4rpx; }
.detail-line__name { color: var(--ink-soft); font-size: 25rpx; font-weight: 600; }
.detail-line__meta { color: var(--muted); font-size: 21rpx; }
.detail-line__amount { color: var(--price); font-family: Arial, sans-serif; font-size: 26rpx; font-weight: 700; white-space: nowrap; }
.detail-line__amount--plain { color: var(--muted); font-weight: 600; }
.remark-card { margin-top: 22rpx; padding: 28rpx; border-left: 5rpx solid var(--warning); }
.remark-card__text { display: block; margin-top: 12rpx; color: var(--ink-soft); font-size: 24rpx; line-height: 1.9; white-space: pre-wrap; }
.total-card { margin-top: 22rpx; padding: 26rpx 28rpx; background: var(--surface); box-shadow: none; }
.total-card__row { display: flex; align-items: center; justify-content: space-between; padding: 14rpx 0; color: var(--muted); font-size: 24rpx; }
.total-card__row--total { padding-top: 22rpx; border-top: 1rpx solid var(--line-dark); }
.total-card__row--total > text:first-child { color: var(--ink-soft); font-weight: 600; }
.total-card__total { color: var(--price); font-family: Arial, sans-serif; font-size: 38rpx; font-weight: 700; }
.detail-actions { display: flex; gap: 20rpx; margin-top: 28rpx; }
.detail-actions__btn { min-height: 88rpx; flex: 1; border-radius: var(--radius-sm); }
.detail-actions__btn--danger { color: var(--danger); border: 1rpx solid #f3c4bb; background: var(--danger-light); }
.order-detail-page__note { display: block; margin-top: 14rpx; color: var(--muted); font-size: 20rpx; text-align: center; }
</style>
