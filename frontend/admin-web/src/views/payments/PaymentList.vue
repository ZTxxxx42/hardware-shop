<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import RequestError from '@/components/RequestError.vue'
import { adminApi } from '@/api/admin'
import { getApiErrorMessage, showRequestError } from '@/api/error'
import { mapOrder, mapPayment } from '@/api/mappers'
import type { Payment } from '@/types/business'
import { formatMoney } from '@/utils/format'

type Reconciliation = { label: string; type: 'success' | 'warning' | 'danger' | 'info' }
const router = useRouter()
const rows = ref<Payment[]>([])
const loading = ref(false)
const loadError = ref('')
const filters = reactive({ keyword: '', channel: '' as Payment['channel'] | '', status: '' as Payment['status'] | '' })
const filteredRows = computed(() => rows.value.filter((item) => {
  const keyword = filters.keyword.trim().toLowerCase()
  return (!keyword || `${item.orderNo}${item.tradeNo}`.toLowerCase().includes(keyword))
    && (!filters.channel || item.channel === filters.channel)
    && (!filters.status || item.status === filters.status)
}))
const successRows = computed(() => rows.value.filter((item) => item.status === 'SUCCESS'))
const successAmount = computed(() => successRows.value.reduce((sum, item) => sum + item.amount, 0))
const mismatchCount = computed(() => successRows.value.filter((item) => item.orderAmount !== null && item.amount !== item.orderAmount).length)
const paymentStatus = {
  SUCCESS: { label: '支付成功', type: 'success' },
  PENDING: { label: '等待支付', type: 'warning' },
  FAILED: { label: '支付失败', type: 'danger' },
  CLOSED: { label: '已关闭', type: 'info' },
} as const

async function loadData() {
  loading.value = true
  loadError.value = ''
  try {
    const [paymentResponse, orderResponse] = await Promise.all([adminApi.getPayments(), adminApi.getOrders()])
    const orders = new Map(orderResponse.data.map((item) => {
      const order = mapOrder(item)
      return [order.id, order] as const
    }))
    rows.value = paymentResponse.data.map((item) => mapPayment(item, orders))
  } catch (error) {
    loadError.value = getApiErrorMessage(error) || '支付流水加载失败'
    showRequestError(error, '支付流水加载失败')
  } finally {
    loading.value = false
  }
}
function reconciliation(row: Payment): Reconciliation {
  if (row.status === 'PENDING') return { label: '等待到账', type: 'warning' }
  if (row.status === 'FAILED' || row.status === 'CLOSED') return { label: '无需对账', type: 'info' }
  if (row.orderAmount === null) return { label: '订单缺失', type: 'info' }
  return row.amount === row.orderAmount ? { label: '账实一致', type: 'success' } : { label: '金额不符', type: 'danger' }
}
function resetFilters() { Object.assign(filters, { keyword: '', channel: '', status: '' }) }
function viewOrder(row: Payment) { router.push({ path: '/orders', query: { keyword: row.orderNo } }) }
onMounted(loadData)
</script>

<template>
  <div class="page">
    <PageHeader title="支付流水" description="按订单号与第三方交易号核对支付结果，成功流水金额应与订单总额一致。" />
    <section class="payment-summary">
      <div><span>成功支付流水</span><strong>{{ successRows.length }}<small>笔</small></strong></div>
      <div><span>成功支付金额</span><strong class="summary-money">{{ formatMoney(successAmount) }}</strong></div>
      <div><span>金额异常</span><strong :class="{ 'text-danger': mismatchCount }">{{ mismatchCount }}<small>笔</small></strong></div>
    </section>
    <RequestError v-if="loadError" :message="loadError" @retry="loadData" />
    <section v-loading="loading" class="table-card">
      <div class="table-toolbar"><div class="filter-bar">
        <el-input v-model="filters.keyword" :prefix-icon="Search" clearable placeholder="搜索订单号 / 交易号" />
        <el-select v-model="filters.channel" clearable placeholder="全部渠道"><el-option label="微信支付" value="wechat" /><el-option label="支付宝" value="alipay" /></el-select>
        <el-select v-model="filters.status" clearable placeholder="全部状态"><el-option label="支付成功" value="SUCCESS" /><el-option label="等待支付" value="PENDING" /><el-option label="支付失败" value="FAILED" /><el-option label="已关闭" value="CLOSED" /></el-select>
        <el-button @click="resetFilters">重置</el-button>
      </div></div>
      <el-table :data="filteredRows" row-key="id">
        <el-table-column label="关联订单" min-width="175"><template #default="{ row }"><el-button link class="mono" @click="viewOrder(row)">{{ row.orderNo }}</el-button></template></el-table-column>
        <el-table-column label="支付渠道" width="110"><template #default="{ row }"><span class="channel" :class="row.channel"><i />{{ row.channel === 'wechat' ? '微信支付' : '支付宝' }}</span></template></el-table-column>
        <el-table-column label="第三方交易号" min-width="220" show-overflow-tooltip><template #default="{ row }"><span class="mono">{{ row.tradeNo }}</span></template></el-table-column>
        <el-table-column label="支付金额" width="120" align="right"><template #default="{ row }"><span class="money">{{ formatMoney(row.amount) }}</span></template></el-table-column>
        <el-table-column label="订单金额" width="120" align="right"><template #default="{ row }">{{ row.orderAmount === null ? '—' : formatMoney(row.orderAmount) }}</template></el-table-column>
        <el-table-column label="支付状态" width="105"><template #default="{ row }"><el-tag :type="paymentStatus[row.status as Payment['status']].type">{{ paymentStatus[row.status as Payment['status']].label }}</el-tag></template></el-table-column>
        <el-table-column label="对账结果" width="100"><template #default="{ row }"><el-tag :type="reconciliation(row).type" effect="plain">{{ reconciliation(row).label }}</el-tag></template></el-table-column>
        <el-table-column label="支付时间" width="160"><template #default="{ row }">{{ row.paidAt ?? '—' }}</template></el-table-column>
        <template #empty><el-empty :description="loadError ? '支付流水加载失败' : '没有符合条件的支付流水'" /></template>
      </el-table>
      <div class="table-footer"><span>共 {{ filteredRows.length }} 条流水 · 点击订单号可查看订单详情</span><span>金额单位：元</span></div>
    </section>
  </div>
</template>

<style scoped>
.payment-summary { display: grid; grid-template-columns: repeat(3, 1fr); margin-bottom: 16px; background: #fff; border: 1px solid #e3eaf3; border-radius: 10px; }
.payment-summary > div { display: flex; flex-direction: column; gap: 9px; padding: 18px 22px; }
.payment-summary > div + div { border-left: 1px solid #e3eaf3; }
.payment-summary span { color: #68788f; font-size: 12px; }
.payment-summary strong { color: #273a52; font-size: 25px; font-weight: 650; font-variant-numeric: tabular-nums; }
.payment-summary small { margin-left: 5px; color: #8492a6; font-size: 11px; font-weight: 400; }
.payment-summary .summary-money { color: #1a6fd6; font-size: 23px; }
.channel { display: inline-flex; align-items: center; gap: 7px; color: #465a73; font-size: 12px; }
.channel i { width: 7px; height: 7px; background: #8a9aaf; border-radius: 50%; }
.channel.wechat i { background: #2baa64; }
.channel.alipay i { background: #1677ff; }
@media (max-width: 650px) { .payment-summary { grid-template-columns: 1fr; } .payment-summary > div + div { border-top: 1px solid #e3eaf3; border-left: 0; } }
</style>
