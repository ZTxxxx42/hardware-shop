<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { orderApi } from '@/api/order'
import { getErrorMessage } from '@/api/http'
import type { OrderBrief, OrderDetail } from '@/types/shop'
import { formatPrice, isZeroAmount } from '@/utils/catalog'
import RequestState from '@/components/RequestState.vue'

type TagType = 'primary' | 'success' | 'warning' | 'info' | 'danger'

const orders = ref<OrderBrief[]>([])
const loading = ref(true)
const error = ref('')
const drawerOpen = ref(false)
const detailLoading = ref(false)
const detail = ref<OrderDetail | null>(null)
const actionOrderId = ref<number | null>(null)

const statusMap: Record<string, { label: string; type: TagType }> = {
  PENDING_PAYMENT: { label: '待支付', type: 'warning' },
  PAID: { label: '已支付', type: 'primary' },
  SHIPPED: { label: '已发货', type: 'success' },
  COMPLETED: { label: '已完成', type: 'info' },
  CANCELLED: { label: '已取消', type: 'info' },
}

function statusLabel(status: string): string {
  return statusMap[status]?.label ?? status
}

function statusType(status: string): TagType {
  return statusMap[status]?.type ?? 'info'
}

function formatDate(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', { hour12: false })
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

async function openDetail(order: OrderBrief) {
  drawerOpen.value = true
  detail.value = null
  detailLoading.value = true
  try {
    detail.value = await orderApi.detail(order.id)
  } catch (requestError) {
    ElMessage.error(getErrorMessage(requestError, '订单详情加载失败'))
    drawerOpen.value = false
  } finally {
    detailLoading.value = false
  }
}

async function cancelOrder(order: OrderBrief) {
  try {
    await ElMessageBox.confirm(`确定取消订单 ${order.order_no} 吗？`, '取消订单', {
      type: 'warning',
      confirmButtonText: '取消订单',
      cancelButtonText: '暂不取消',
    })
  } catch {
    return
  }
  actionOrderId.value = order.id
  try {
    const updated = await orderApi.cancel(order.id)
    ElMessage.success('订单已取消')
    await loadOrders()
    if (detail.value?.id === order.id) detail.value = updated
  } catch (requestError) {
    ElMessage.error(getErrorMessage(requestError, '取消订单失败'))
  } finally {
    actionOrderId.value = null
  }
}

async function confirmOrder(order: OrderBrief) {
  try {
    await ElMessageBox.confirm('确认已收到全部商品？', '确认收货', {
      type: 'success',
      confirmButtonText: '确认收货',
      cancelButtonText: '再等等',
    })
  } catch {
    return
  }
  actionOrderId.value = order.id
  try {
    const updated = await orderApi.confirm(order.id)
    ElMessage.success('已确认收货，订单完成')
    await loadOrders()
    if (detail.value?.id === order.id) detail.value = updated
  } catch (requestError) {
    ElMessage.error(getErrorMessage(requestError, '确认收货失败'))
  } finally {
    actionOrderId.value = null
  }
}

function goPay() {
  ElMessage.info('支付暂未接入，敬请期待')
}

onMounted(loadOrders)
</script>

<template>
  <section class="orders-page">
    <div class="container">
      <nav class="breadcrumb" aria-label="面包屑"><RouterLink to="/">首页</RouterLink><span>/</span><span>订单中心</span></nav>
      <div class="page-heading"><div><span>MY ORDERS</span><h1>订单中心</h1><p>查看待支付、已支付、已发货及已完成订单</p></div></div>
      <RequestState
        v-if="loading || error || orders.length === 0"
        :loading="loading"
        :error="error"
        :empty="!loading && !error"
        loading-text="正在加载订单..."
        empty-text="暂无订单，快去选购商品吧"
        @retry="loadOrders"
      />
      <div v-else class="order-list">
        <article v-for="order in orders" :key="order.id" class="order-card">
          <div class="order-head">
            <div class="order-no">
              <span>订单号</span>
              <strong>{{ order.order_no }}</strong>
            </div>
            <el-tag :type="statusType(order.status)" effect="light">{{ statusLabel(order.status) }}</el-tag>
          </div>
          <div class="order-meta">
            <span>下单时间：{{ formatDate(order.created_at) }}</span>
            <span class="order-total">应付金额：<strong>¥{{ formatPrice(order.total_amount) }}</strong></span>
          </div>
          <div class="order-actions">
            <el-button text type="primary" @click="openDetail(order)">查看详情</el-button>
            <template v-if="order.status === 'PENDING_PAYMENT'">
              <el-button text type="warning" @click="goPay">去支付</el-button>
              <el-button text type="danger" :loading="actionOrderId === order.id" @click="cancelOrder(order)">取消订单</el-button>
            </template>
            <el-button v-else-if="order.status === 'SHIPPED'" text type="success" :loading="actionOrderId === order.id" @click="confirmOrder(order)">确认收货</el-button>
          </div>
        </article>
      </div>
    </div>

    <el-drawer v-model="drawerOpen" title="订单详情" size="min(520px, 92%)" destroy-on-close>
      <div v-loading="detailLoading" class="order-detail">
        <template v-if="detail">
          <div class="detail-status">
            <el-tag :type="statusType(detail.status)" effect="light">{{ statusLabel(detail.status) }}</el-tag>
            <span class="detail-date">{{ formatDate(detail.created_at) }}</span>
          </div>
          <div class="detail-block">
            <h3>商品明细</h3>
            <div v-for="item in detail.items" :key="item.id" class="detail-line">
              <div><strong>{{ item.product_name }}</strong><span>¥{{ formatPrice(item.price) }} × {{ item.quantity }}</span></div>
              <span>¥{{ formatPrice(item.subtotal) }}</span>
            </div>
          </div>
          <div class="detail-block">
            <h3>收货地址</h3>
            <p>{{ detail.address_snapshot.receiver }} · {{ detail.address_snapshot.phone }}</p>
            <p>{{ detail.address_snapshot.region }} {{ detail.address_snapshot.detail }}</p>
          </div>
          <div class="detail-block">
            <h3>支付信息</h3>
            <p v-if="detail.payments.length === 0">暂无支付记录</p>
            <div v-for="payment in detail.payments" :key="payment.id" class="detail-line">
              <div><strong>{{ payment.channel === 'wechat' ? '微信支付' : payment.channel === 'alipay' ? '支付宝' : payment.channel }}</strong><span>¥{{ formatPrice(payment.amount) }}</span></div>
              <span>{{ payment.status === 'PAID' ? '已支付' : '待支付' }}</span>
            </div>
          </div>
          <div class="detail-total">
            <span>商品金额 ¥{{ formatPrice(detail.product_amount) }}</span>
            <span>运费 {{ isZeroAmount(detail.freight_amount) ? '免运费' : `¥${formatPrice(detail.freight_amount)}` }}</span>
            <strong>应付合计 ¥{{ formatPrice(detail.total_amount) }}</strong>
          </div>
          <div class="detail-actions">
            <template v-if="detail.status === 'PENDING_PAYMENT'">
              <el-button type="primary" @click="goPay">去支付</el-button>
              <el-button type="danger" plain :loading="actionOrderId === detail.id" @click="cancelOrder(detail)">取消订单</el-button>
            </template>
            <el-button v-else-if="detail.status === 'SHIPPED'" type="success" :loading="actionOrderId === detail.id" @click="confirmOrder(detail)">确认收货</el-button>
          </div>
        </template>
      </div>
    </el-drawer>
  </section>
</template>

<style scoped>
.orders-page { min-height: 620px; padding: 26px 0 70px; background: #f5f8fb; }
.breadcrumb { display: flex; gap: 10px; color: #8b97a4; font-size: 12px; }
.page-heading { margin: 32px 0 25px; }
.page-heading > div > span { color: var(--brand); font-family: Arial, sans-serif; font-size: 10px; letter-spacing: .18em; }
.page-heading h1 { margin-top: 3px; font-size: 30px; }
.page-heading p { margin-top: 6px; color: #7b8998; font-size: 13px; }
.order-list { display: flex; flex-direction: column; gap: 14px; }
.order-card { padding: 19px 22px; border: 1px solid #e7edf3; border-radius: 12px; background: #fff; box-shadow: var(--shadow-sm); }
.order-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.order-no { display: flex; min-width: 0; flex-direction: column; gap: 2px; }
.order-no span { color: #95a2af; font-size: 11px; }
.order-no strong { overflow: hidden; color: #3c4e61; font-family: Arial, sans-serif; font-size: 14px; font-weight: 600; text-overflow: ellipsis; white-space: nowrap; }
.order-meta { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-top: 14px; padding-top: 13px; border-top: 1px solid #f0f3f7; color: #7b8998; font-size: 12px; }
.order-total strong { color: #e45b32; font-family: Arial, sans-serif; font-size: 16px; }
.order-actions { display: flex; align-items: center; justify-content: flex-end; gap: 4px; margin-top: 10px; }
.order-detail { min-height: 240px; }
.detail-status { display: flex; align-items: center; gap: 14px; padding-bottom: 16px; border-bottom: 1px solid #edf1f5; }
.detail-date { color: #8a97a5; font-size: 12px; }
.detail-block { margin-top: 20px; }
.detail-block h3 { margin-bottom: 10px; font-size: 14px; font-weight: 650; }
.detail-block > p { margin: 4px 0; color: #657689; font-size: 13px; line-height: 1.7; }
.detail-line { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 9px 0; border-bottom: 1px solid #f2f5f8; font-size: 13px; }
.detail-line > div { display: flex; min-width: 0; flex-direction: column; gap: 2px; }
.detail-line strong { color: #3c4e61; }
.detail-line span { color: #8a97a5; font-size: 12px; }
.detail-total { display: flex; flex-direction: column; align-items: flex-end; gap: 5px; margin-top: 22px; padding: 16px; border-radius: 9px; background: #f6f9fd; color: #657689; font-size: 12px; }
.detail-total strong { color: #e45b32; font-family: Arial, sans-serif; font-size: 18px; }
.detail-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 18px; }
@media (max-width: 767px) {
  .orders-page { padding-top: 18px; }
  .page-heading { margin: 25px 0 20px; }
  .page-heading h1 { font-size: 26px; }
  .page-heading p { font-size: 12px; }
  .order-card { padding: 16px; }
  .order-meta { flex-direction: column; align-items: flex-start; gap: 5px; }
  .order-actions { justify-content: flex-start; flex-wrap: wrap; }
}
</style>
