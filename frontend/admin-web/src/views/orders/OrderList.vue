<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import RequestError from '@/components/RequestError.vue'
import { adminApi } from '@/api/admin'
import { getApiErrorMessage, showRequestError } from '@/api/error'
import { mapOrder, mapOrderDetail } from '@/api/mappers'
import type { Order, OrderStatus } from '@/types/business'
import { formatMoney, levelMeta, orderStatusMeta } from '@/utils/format'

const route = useRoute()
const rows = ref<Order[]>([])
const loading = ref(false)
const loadError = ref('')
const filters = reactive({ keyword: typeof route.query.keyword === 'string' ? route.query.keyword : '', status: '' as OrderStatus | '' })
const statusOptions: OrderStatus[] = ['PENDING_PAYMENT', 'PAID', 'SHIPPED', 'COMPLETED', 'CANCELLED']
const filteredRows = computed(() => rows.value.filter((item) => {
  const keyword = filters.keyword.trim().toLowerCase()
  return (!keyword || `${item.orderNo}${item.customerName ?? ''}${item.receiver ?? ''}`.toLowerCase().includes(keyword)) && (!filters.status || item.status === filters.status)
}))
const drawerVisible = ref(false)
const selectedOrder = ref<Order | null>(null)
const detailLoaded = ref(false)
const activeStep = computed(() => {
  if (!selectedOrder.value) return 0
  return { PENDING_PAYMENT: 0, PAID: 1, SHIPPED: 2, COMPLETED: 3, CANCELLED: 0 }[selectedOrder.value.status]
})
const shipVisible = ref(false)
const shipping = ref(false)
const shipForm = reactive({ carrier: '顺丰速运', trackingNo: '' })

async function loadData() {
  loading.value = true
  loadError.value = ''
  try {
    const { data } = await adminApi.getOrders()
    rows.value = data.map(mapOrder)
  } catch (error) {
    loadError.value = getApiErrorMessage(error) || '订单数据加载失败'
    showRequestError(error, '订单数据加载失败')
  } finally {
    loading.value = false
  }
}
function orderQuantity(order: Order) { return order.items.reduce((sum, item) => sum + item.quantity, 0) }
function resetFilters() { Object.assign(filters, { keyword: '', status: '' }) }
function openDetail(row: Order) {
  selectedOrder.value = row
  detailLoaded.value = row.items.length > 0
  drawerVisible.value = true
}
function openShipment(row: Order) {
  selectedOrder.value = row
  Object.assign(shipForm, { carrier: '顺丰速运', trackingNo: '' })
  shipVisible.value = true
}
async function confirmShipment() {
  if (!selectedOrder.value) return
  const target = rows.value.find((item) => item.id === selectedOrder.value?.id)
  if (target?.status !== 'PAID') {
    ElMessage.warning('仅已支付订单可以发货')
    return
  }
  shipping.value = true
  try {
    const { data } = await adminApi.shipOrder(target.id)
    const detail = mapOrderDetail(data)
    Object.assign(target, detail)
    selectedOrder.value = target
    detailLoaded.value = true
    shipVisible.value = false
    ElMessage.success('订单已发货')
  } catch (error) {
    showRequestError(error, '订单发货失败')
  } finally {
    shipping.value = false
  }
}
onMounted(loadData)
</script>

<template>
  <div class="page">
    <PageHeader title="订单管理" description="核对订单价格快照与收货信息，按状态机完成发货；支付结果以支付流水为准。" />
    <RequestError v-if="loadError" :message="loadError" @retry="loadData" />
    <section v-loading="loading" class="table-card">
      <div class="table-toolbar"><div class="filter-bar">
        <el-input v-model="filters.keyword" :prefix-icon="Search" clearable placeholder="搜索订单号 / 客户 / 收货人" />
        <el-select v-model="filters.status" clearable placeholder="全部订单状态"><el-option v-for="status in statusOptions" :key="status" :label="orderStatusMeta[status].label" :value="status" /></el-select>
        <el-button @click="resetFilters">重置</el-button>
      </div></div>
      <el-table :data="filteredRows" row-key="id">
        <el-table-column label="订单号" min-width="180"><template #default="{ row }"><el-button link class="order-number mono" @click="openDetail(row)">{{ row.orderNo }}</el-button></template></el-table-column>
        <el-table-column label="客户" min-width="160"><template #default="{ row }"><div class="table-product-name">{{ row.customerName ?? '后端未返回' }}</div><el-tag v-if="row.level" class="level-tag" :type="levelMeta[row.level as keyof typeof levelMeta].type" effect="plain">{{ levelMeta[row.level as keyof typeof levelMeta].label }}</el-tag></template></el-table-column>
        <el-table-column label="商品" min-width="220"><template #default="{ row }"><div>{{ row.items[0]?.productName ?? '详情端点未提供' }}</div><div v-if="row.items.length" class="table-subtext">共 {{ row.items.length }} 种 / {{ orderQuantity(row) }} 件</div></template></el-table-column>
        <el-table-column label="订单金额" width="130" align="right"><template #default="{ row }"><span class="money">{{ formatMoney(row.totalAmount) }}</span><div v-if="row.freightAmount" class="table-subtext">含运费 {{ formatMoney(row.freightAmount) }}</div></template></el-table-column>
        <el-table-column label="状态" width="100"><template #default="{ row }"><el-tag :type="orderStatusMeta[row.status as OrderStatus].type">{{ orderStatusMeta[row.status as OrderStatus].label }}</el-tag></template></el-table-column>
        <el-table-column prop="createdAt" label="下单时间" width="160" />
        <el-table-column label="操作" width="140" fixed="right"><template #default="{ row }"><div class="inline-actions"><el-button link type="primary" @click="openDetail(row)">详情</el-button><el-button v-if="row.status === 'PAID'" link type="success" @click="openShipment(row)">发货</el-button></div></template></el-table-column>
        <template #empty><el-empty :description="loadError ? '订单数据加载失败' : '没有符合条件的订单'" /></template>
      </el-table>
      <div class="table-footer"><span>共 {{ filteredRows.length }} 笔订单 · 数据来自后端</span><el-pagination background layout="prev, pager, next" :total="filteredRows.length" :page-size="10" /></div>
    </section>
    <el-drawer v-model="drawerVisible" title="订单详情" size="680px">
      <template v-if="selectedOrder">
        <div class="order-detail-head"><div><span>订单号</span><strong class="mono">{{ selectedOrder.orderNo }}</strong></div><el-tag :type="orderStatusMeta[selectedOrder.status].type">{{ orderStatusMeta[selectedOrder.status].label }}</el-tag></div>
        <el-alert v-if="!detailLoaded" title="后端缺失 GET /api/admin/orders/{id}，当前仅展示订单列表返回的字段；发货成功后会展示接口返回的详情。" type="info" :closable="false" show-icon class="detail-tip" />
        <el-alert v-if="selectedOrder.status === 'CANCELLED'" title="订单已取消，不再进入后续支付与发货流程。" type="info" :closable="false" show-icon />
        <el-steps v-else :active="activeStep" align-center finish-status="success" class="order-steps">
          <el-step title="待支付" /><el-step title="已支付" /><el-step title="已发货" /><el-step title="已完成" />
        </el-steps>
        <h3 class="detail-section-title">订单信息</h3>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="下单客户">{{ selectedOrder.customerName ?? '后端未返回' }}</el-descriptions-item>
          <el-descriptions-item label="客户等级"><el-tag v-if="selectedOrder.level" :type="levelMeta[selectedOrder.level].type" effect="plain">{{ levelMeta[selectedOrder.level].label }}</el-tag><span v-else>后端未返回</span></el-descriptions-item>
          <el-descriptions-item label="下单时间">{{ selectedOrder.createdAt }}</el-descriptions-item>
          <el-descriptions-item label="支付时间">{{ selectedOrder.paidAt ?? '—' }}</el-descriptions-item>
          <el-descriptions-item label="收货人">{{ selectedOrder.receiver ? `${selectedOrder.receiver} · ${selectedOrder.phone ?? ''}` : '后端未返回' }}</el-descriptions-item>
          <el-descriptions-item label="收货地址" :span="2">{{ selectedOrder.address ?? '后端未返回' }}</el-descriptions-item>
        </el-descriptions>
        <h3 class="detail-section-title">商品与价格快照</h3>
        <el-table :data="selectedOrder.items" size="small" border>
          <el-table-column label="商品" min-width="190"><template #default="{ row }"><div>{{ row.productName }}</div><div class="table-subtext">{{ row.model }}</div></template></el-table-column>
          <el-table-column label="单价" width="100" align="right"><template #default="{ row }">{{ formatMoney(row.price) }}</template></el-table-column>
          <el-table-column prop="quantity" label="数量" width="65" align="right" />
          <el-table-column label="小计" width="110" align="right"><template #default="{ row }"><span class="money">{{ formatMoney(row.subtotal) }}</span></template></el-table-column>
          <template #empty><el-empty description="订单详情端点未提供商品快照" /></template>
        </el-table>
        <div class="amount-summary"><div><span>商品金额</span><span>{{ formatMoney(selectedOrder.productAmount) }}</span></div><div><span>运费</span><span>{{ formatMoney(selectedOrder.freightAmount) }}</span></div><div class="amount-total"><span>订单合计</span><strong>{{ formatMoney(selectedOrder.totalAmount) }}</strong></div></div>
        <div class="drawer-actions"><el-button v-if="selectedOrder.status === 'PAID'" type="primary" @click="openShipment(selectedOrder)">填写物流并发货</el-button></div>
      </template>
    </el-drawer>
    <el-dialog v-model="shipVisible" title="订单发货" width="480px" append-to-body>
      <el-alert v-if="selectedOrder" :title="`订单 ${selectedOrder.orderNo} 发货后将进入“已发货”状态。`" type="info" :closable="false" />
      <el-form :model="shipForm" label-width="88px" class="ship-form">
        <el-form-item label="物流公司"><el-select v-model="shipForm.carrier" style="width: 100%"><el-option label="顺丰速运" value="顺丰速运" /><el-option label="京东物流" value="京东物流" /><el-option label="德邦快递" value="德邦快递" /><el-option label="其他物流" value="其他物流" /></el-select></el-form-item>
        <el-form-item label="物流单号"><el-input v-model="shipForm.trackingNo" placeholder="界面占位，不会提交到后端" /></el-form-item>
      </el-form>
      <p class="form-tip">物流字段为界面占位；当前后端发货端点无需请求体。</p>
      <template #footer><div class="dialog-footer"><el-button @click="shipVisible = false">取消</el-button><el-button type="primary" :loading="shipping" @click="confirmShipment">确认发货</el-button></div></template>
    </el-dialog>
  </div>
</template>

<style scoped>
.order-number { font-weight: 500; }
.level-tag { margin-top: 5px; }
.detail-tip { margin-bottom: 20px; }
.order-detail-head { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 24px; }
.order-detail-head > div { display: flex; flex-direction: column; gap: 6px; }
.order-detail-head span { color: #8492a6; font-size: 11px; }
.order-detail-head strong { color: #273a52; font-size: 15px; }
.order-steps { margin: 10px 0 28px; }
.detail-section-title { margin: 24px 0 12px; color: #465a73; font-size: 13px; font-weight: 600; }
.amount-summary { width: 260px; margin: 18px 0 0 auto; }
.amount-summary > div { display: flex; justify-content: space-between; padding: 5px 0; color: #68788f; font-size: 12px; }
.amount-summary .amount-total { margin-top: 6px; padding-top: 12px; color: #273a52; border-top: 1px solid #e3eaf3; }
.amount-total strong { color: #1a6fd6; font-size: 18px; }
.drawer-actions { display: flex; justify-content: flex-end; margin-top: 24px; }
.ship-form { margin-top: 22px; }
@media (max-width: 700px) { :deep(.el-drawer) { width: 100% !important; } :deep(.el-dialog) { width: calc(100% - 24px) !important; } }
</style>
