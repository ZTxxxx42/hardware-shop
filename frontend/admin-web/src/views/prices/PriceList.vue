<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { Discount, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import RequestError from '@/components/RequestError.vue'
import { adminApi } from '@/api/admin'
import type { ProductDetailOut } from '@/api/admin'
import { getApiErrorMessage, showRequestError } from '@/api/error'
import type { CustomerLevel } from '@/types/business'
import { formatMoney, levelMeta } from '@/utils/format'

type PriceMap = Record<CustomerLevel, number | null>
interface PriceRow {
  id: number
  name: string
  model: string
  retailPrice: number
  prices: PriceMap
}
const rows = ref<PriceRow[]>([])
const loading = ref(false)
const loadError = ref('')
const keyword = ref('')
const levels: CustomerLevel[] = ['retail', 'wholesale', 'vip']
const selectedRows = ref<PriceRow[]>([])
const filteredRows = computed(() => rows.value.filter((item) => `${item.name}${item.model}`.toLowerCase().includes(keyword.value.trim().toLowerCase())))
const editVisible = ref(false)
const editingId = ref<number | null>(null)
const editingName = ref('')
const saving = ref(false)
const priceForm = reactive<PriceMap>({ retail: null, wholesale: null, vip: null })
const batchVisible = ref(false)
const batchSaving = ref(false)
const batchForm = reactive({ level: 'wholesale' as CustomerLevel, discount: 90, scope: 'all' as 'all' | 'selected' })
const batchTargets = computed(() => batchForm.scope === 'selected' ? selectedRows.value : rows.value)
const previewPrice = computed(() => batchTargets.value.length ? (batchTargets.value[0].retailPrice * batchForm.discount / 100).toFixed(2) : '0.00')

function pricesFromDetail(detail: ProductDetailOut): PriceMap {
  const prices: PriceMap = { retail: null, wholesale: null, vip: null }
  detail.level_prices.forEach((item) => {
    if (levels.includes(item.level_code as CustomerLevel)) prices[item.level_code as CustomerLevel] = Number(item.price)
  })
  return prices
}
async function loadData() {
  loading.value = true
  loadError.value = ''
  try {
    const { data } = await adminApi.getProducts({ page: 1, page_size: 100 })
    const details = await Promise.all(data.items.map((item) => adminApi.getProductDetail(item.id)))
    rows.value = details.map(({ data: detail }) => ({
      id: detail.id,
      name: detail.name,
      model: detail.model ?? '',
      retailPrice: Number(detail.retail_price),
      prices: pricesFromDetail(detail),
    }))
    selectedRows.value = []
  } catch (error) {
    loadError.value = getApiErrorMessage(error) || '等级价格加载失败'
    showRequestError(error, '等级价格加载失败')
  } finally {
    loading.value = false
  }
}
function openEdit(row: PriceRow) {
  editingId.value = row.id
  editingName.value = row.name
  Object.assign(priceForm, row.prices)
  editVisible.value = true
}
async function savePrices() {
  if (!editingId.value) return
  const prices = levels.flatMap((level) => priceForm[level] === null ? [] : [{ level_code: level, price: priceForm[level]! }])
  if (!prices.length) {
    ElMessage.warning('请至少填写一个等级价格；后端暂不支持删除已配置价格')
    return
  }
  saving.value = true
  try {
    const { data } = await adminApi.updateProductPrices(editingId.value, prices)
    const target = rows.value.find((item) => item.id === editingId.value)
    if (target) {
      const nextPrices: PriceMap = { retail: null, wholesale: null, vip: null }
      data.forEach((item) => {
        if (levels.includes(item.level_code as CustomerLevel)) nextPrices[item.level_code as CustomerLevel] = Number(item.price)
      })
      Object.assign(target.prices, nextPrices)
    }
    editVisible.value = false
    ElMessage.success('等级价格已保存')
  } catch (error) {
    showRequestError(error, '等级价格保存失败')
  } finally {
    saving.value = false
  }
}
function openBatch() {
  batchForm.scope = selectedRows.value.length ? 'selected' : 'all'
  batchVisible.value = true
}
async function applyBatch() {
  const targets = [...batchTargets.value]
  if (!targets.length) {
    ElMessage.warning('请先选择需要设置价格的商品')
    return
  }
  batchSaving.value = true
  try {
    await Promise.all(targets.map(async (item) => {
      const price = Number((item.retailPrice * batchForm.discount / 100).toFixed(2))
      const { data } = await adminApi.updateProductPrices(item.id, [{ level_code: batchForm.level, price }])
      const saved = data.find((priceItem) => priceItem.level_code === batchForm.level)
      if (saved) item.prices[batchForm.level] = Number(saved.price)
    }))
    ElMessage.success(`已保存 ${targets.length} 件商品的${levelMeta[batchForm.level].label}价格`)
    batchVisible.value = false
  } catch (error) {
    showRequestError(error, '批量价格保存失败，部分商品可能已更新')
    await loadData()
  } finally {
    batchSaving.value = false
  }
}
onMounted(loadData)
</script>

<template>
  <div class="page">
    <PageHeader title="价格管理" description="按商品与客户等级维护固定售价；会员未设置等级价时，自动回退零售价。">
      <el-button type="primary" :icon="Discount" @click="openBatch">按等级批量折扣</el-button>
    </PageHeader>
    <el-alert class="price-tip" title="批量折扣会按当前零售价展开为固定等级价。后端仅支持新增或覆盖，留空不会删除已配置价格。" type="info" :closable="false" show-icon />
    <RequestError v-if="loadError" :message="loadError" @retry="loadData" />
    <section v-loading="loading" class="table-card">
      <div class="table-toolbar"><div class="filter-bar"><el-input v-model="keyword" :prefix-icon="Search" clearable placeholder="搜索商品名称 / 型号" /></div><span class="selection-count">已选 {{ selectedRows.length }} 件</span></div>
      <el-table :data="filteredRows" row-key="id" @selection-change="selectedRows = $event">
        <el-table-column type="selection" width="48" />
        <el-table-column label="商品" min-width="250"><template #default="{ row }"><div class="table-product-name">{{ row.name }}</div><div class="table-subtext">{{ row.model || '—' }}</div></template></el-table-column>
        <el-table-column label="零售价" width="120" align="right"><template #default="{ row }"><span class="money">{{ formatMoney(row.retailPrice) }}</span></template></el-table-column>
        <el-table-column label="零售价等级" width="140" align="right"><template #default="{ row }"><div v-if="row.prices.retail !== null" class="money">{{ formatMoney(row.prices.retail) }}</div><div v-else class="fallback-price"><span>{{ formatMoney(row.retailPrice) }}</span><small>回退零售</small></div></template></el-table-column>
        <el-table-column label="批发价" width="140" align="right"><template #default="{ row }"><div v-if="row.prices.wholesale !== null" class="money">{{ formatMoney(row.prices.wholesale) }}</div><div v-else class="fallback-price"><span>{{ formatMoney(row.retailPrice) }}</span><small>回退零售</small></div></template></el-table-column>
        <el-table-column label="VIP 价" width="140" align="right"><template #default="{ row }"><div v-if="row.prices.vip !== null" class="money">{{ formatMoney(row.prices.vip) }}</div><div v-else class="fallback-price"><span>{{ formatMoney(row.retailPrice) }}</span><small>回退零售</small></div></template></el-table-column>
        <el-table-column label="操作" width="100" fixed="right"><template #default="{ row }"><el-button link type="primary" @click="openEdit(row)">设置价格</el-button></template></el-table-column>
        <template #empty><el-empty :description="loadError ? '价格数据加载失败' : '没有符合条件的商品'" /></template>
      </el-table>
      <div class="table-footer"><span>共 {{ filteredRows.length }} 件商品 · 金额单位：元</span><span>零售价 / 批发 / VIP 三级定价</span></div>
    </section>
    <el-dialog v-model="editVisible" title="设置等级价格" width="520px">
      <div class="editing-product"><span>当前商品</span><strong>{{ editingName }}</strong></div>
      <el-form label-width="96px">
        <el-form-item v-for="level in levels" :key="level" :label="`${levelMeta[level].label}价格`">
          <el-input-number v-model="priceForm[level]" :min="0" :precision="2" controls-position="right" placeholder="留空表示本次不修改" style="width: 100%" />
        </el-form-item>
      </el-form>
      <p class="form-tip">留空表示本次不提交该等级；未设置价格的等级下单时回退零售价。后端暂无等级价删除能力。</p>
      <template #footer><div class="dialog-footer"><el-button @click="editVisible = false">取消</el-button><el-button type="primary" :loading="saving" @click="savePrices">保存价格</el-button></div></template>
    </el-dialog>
    <el-dialog v-model="batchVisible" title="按等级批量折扣" width="540px">
      <el-alert title="此操作会覆盖目标商品已设置的同等级价格，请确认折扣与适用范围。" type="warning" :closable="false" show-icon />
      <el-form label-width="96px" class="batch-form">
        <el-form-item label="目标等级"><el-radio-group v-model="batchForm.level"><el-radio-button value="retail">零售</el-radio-button><el-radio-button value="wholesale">批发</el-radio-button><el-radio-button value="vip">VIP</el-radio-button></el-radio-group></el-form-item>
        <el-form-item label="折扣率"><div class="discount-input"><el-input-number v-model="batchForm.discount" :min="1" :max="100" :precision="0" controls-position="right" /><span>%</span></div><p class="form-tip">90% 表示按零售价的九折设置；100% 表示与零售价一致。</p></el-form-item>
        <el-form-item label="适用商品"><el-radio-group v-model="batchForm.scope"><el-radio value="all">全部 {{ rows.length }} 件商品</el-radio><el-radio value="selected" :disabled="!selectedRows.length">已选 {{ selectedRows.length }} 件商品</el-radio></el-radio-group></el-form-item>
      </el-form>
      <div class="batch-preview"><span>首件商品折后价</span><strong>{{ formatMoney(Number(previewPrice)) }}</strong><small>共影响 {{ batchTargets.length }} 件商品，实际按各自零售价计算</small></div>
      <template #footer><div class="dialog-footer"><el-button @click="batchVisible = false">取消</el-button><el-button type="primary" :loading="batchSaving" @click="applyBatch">展开并保存价格</el-button></div></template>
    </el-dialog>
  </div>
</template>

<style scoped>
.price-tip { margin-bottom: 16px; }
.selection-count { flex: none; color: #68788f; font-size: 12px; }
.fallback-price { display: flex; flex-direction: column; align-items: flex-end; color: #7b8a9e; font-variant-numeric: tabular-nums; }
.fallback-price small { margin-top: 2px; color: #a0abba; font-size: 10px; }
.editing-product { display: flex; flex-direction: column; gap: 6px; margin-bottom: 22px; padding: 12px 14px; background: #f5f8fc; border-radius: 7px; }
.editing-product span { color: #68788f; font-size: 11px; }
.editing-product strong { color: #273a52; font-size: 14px; font-weight: 600; }
.batch-form { margin-top: 22px; }
.discount-input { display: flex; align-items: center; gap: 10px; width: 180px; }
.discount-input .el-input-number { flex: 1; }
.discount-input span { color: #52647c; }
.batch-preview { display: grid; grid-template-columns: 1fr auto; gap: 5px 12px; padding: 14px; background: #f5f8fc; border-radius: 7px; }
.batch-preview span { color: #52647c; font-size: 12px; }
.batch-preview strong { color: #1a6fd6; font-size: 18px; }
.batch-preview small { grid-column: 1 / -1; color: #8492a6; font-size: 11px; }
@media (max-width: 600px) { :deep(.el-dialog) { width: calc(100% - 24px) !important; } }
</style>
