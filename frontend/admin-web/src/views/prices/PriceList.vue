<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { Discount, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { products } from '@/mock'
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
const overrides: Record<number, PriceMap> = {
  1001: { retail: null, wholesale: 0.54, vip: 0.46 },
  1002: { retail: null, wholesale: 0.34, vip: 0.28 },
  2001: { retail: null, wholesale: 298, vip: 279 },
  3001: { retail: null, wholesale: 7.2, vip: 6.6 },
  3002: { retail: null, wholesale: 10.8, vip: null },
  4001: { retail: null, wholesale: 5.2, vip: 4.6 },
}
const rows = ref<PriceRow[]>(products.map((item) => ({ id: item.id, name: item.name, model: item.model, retailPrice: item.retailPrice, prices: { ...overrides[item.id] } })))
const keyword = ref('')
const levels: CustomerLevel[] = ['retail', 'wholesale', 'vip']
const selectedRows = ref<PriceRow[]>([])
const filteredRows = computed(() => rows.value.filter((item) => `${item.name}${item.model}`.toLowerCase().includes(keyword.value.trim().toLowerCase())))
const editVisible = ref(false)
const editingId = ref<number | null>(null)
const editingName = ref('')
const priceForm = reactive<PriceMap>({ retail: null, wholesale: null, vip: null })
const batchVisible = ref(false)
const batchForm = reactive({ level: 'wholesale' as CustomerLevel, discount: 90, scope: 'all' as 'all' | 'selected' })
const batchTargets = computed(() => batchForm.scope === 'selected' ? selectedRows.value : rows.value)
const previewPrice = computed(() => batchTargets.value.length ? (batchTargets.value[0].retailPrice * batchForm.discount / 100).toFixed(2) : '0.00')
function openEdit(row: PriceRow) {
  editingId.value = row.id
  editingName.value = row.name
  Object.assign(priceForm, row.prices)
  editVisible.value = true
}
function savePrices() {
  const target = rows.value.find((item) => item.id === editingId.value)
  if (target) Object.assign(target.prices, priceForm)
  editVisible.value = false
  ElMessage.success('等级价格已保存（示例数据）')
}
function openBatch() {
  batchForm.scope = selectedRows.value.length ? 'selected' : 'all'
  batchVisible.value = true
}
function applyBatch() {
  if (!batchTargets.value.length) {
    ElMessage.warning('请先选择需要设置价格的商品')
    return
  }
  batchTargets.value.forEach((item) => {
    item.prices[batchForm.level] = Number((item.retailPrice * batchForm.discount / 100).toFixed(2))
  })
  ElMessage.success(`已展开 ${batchTargets.value.length} 件商品的${levelMeta[batchForm.level].label}价格（示例数据）`)
  batchVisible.value = false
}
</script>

<template>
  <div class="page">
    <PageHeader title="价格管理" description="按商品与客户等级维护固定售价；会员未设置等级价时，自动回退零售价。">
      <el-button type="primary" :icon="Discount" @click="openBatch">按等级批量折扣</el-button>
    </PageHeader>
    <el-alert class="price-tip" title="批量折扣会立即按当前零售价展开为固定等级价，后续零售价变更不会自动联动。" type="info" :closable="false" show-icon />
    <section class="table-card">
      <div class="table-toolbar"><div class="filter-bar"><el-input v-model="keyword" :prefix-icon="Search" clearable placeholder="搜索商品名称 / 型号" /></div><span class="selection-count">已选 {{ selectedRows.length }} 件</span></div>
      <el-table :data="filteredRows" row-key="id" @selection-change="selectedRows = $event">
        <el-table-column type="selection" width="48" />
        <el-table-column label="商品" min-width="250"><template #default="{ row }"><div class="table-product-name">{{ row.name }}</div><div class="table-subtext">{{ row.model }}</div></template></el-table-column>
        <el-table-column label="零售价" width="120" align="right"><template #default="{ row }"><span class="money">{{ formatMoney(row.retailPrice) }}</span></template></el-table-column>
        <el-table-column label="零售价等级" width="140" align="right"><template #default="{ row }"><div v-if="row.prices.retail !== null" class="money">{{ formatMoney(row.prices.retail) }}</div><div v-else class="fallback-price"><span>{{ formatMoney(row.retailPrice) }}</span><small>回退零售</small></div></template></el-table-column>
        <el-table-column label="批发价" width="140" align="right"><template #default="{ row }"><div v-if="row.prices.wholesale !== null" class="money">{{ formatMoney(row.prices.wholesale) }}</div><div v-else class="fallback-price"><span>{{ formatMoney(row.retailPrice) }}</span><small>回退零售</small></div></template></el-table-column>
        <el-table-column label="VIP 价" width="140" align="right"><template #default="{ row }"><div v-if="row.prices.vip !== null" class="money">{{ formatMoney(row.prices.vip) }}</div><div v-else class="fallback-price"><span>{{ formatMoney(row.retailPrice) }}</span><small>回退零售</small></div></template></el-table-column>
        <el-table-column label="操作" width="100" fixed="right"><template #default="{ row }"><el-button link type="primary" @click="openEdit(row)">设置价格</el-button></template></el-table-column>
      </el-table>
      <div class="table-footer"><span>共 {{ filteredRows.length }} 件商品 · 金额单位：元</span><span>零售价 / 批发 / VIP 三级定价</span></div>
    </section>
    <el-dialog v-model="editVisible" title="设置等级价格" width="520px">
      <div class="editing-product"><span>当前商品</span><strong>{{ editingName }}</strong></div>
      <el-form label-width="96px">
        <el-form-item v-for="level in levels" :key="level" :label="`${levelMeta[level].label}价格`">
          <el-input-number v-model="priceForm[level]" :min="0" :precision="2" controls-position="right" placeholder="留空回退零售价" style="width: 100%" />
        </el-form-item>
      </el-form>
      <p class="form-tip">清空输入框表示不单独设置该等级价格，客户下单时取商品零售价。</p>
      <template #footer><div class="dialog-footer"><el-button @click="editVisible = false">取消</el-button><el-button type="primary" @click="savePrices">保存价格</el-button></div></template>
    </el-dialog>
    <el-dialog v-model="batchVisible" title="按等级批量折扣" width="540px">
      <el-alert title="此操作会覆盖目标商品已设置的同等级价格，请确认折扣与适用范围。" type="warning" :closable="false" show-icon />
      <el-form label-width="96px" class="batch-form">
        <el-form-item label="目标等级"><el-radio-group v-model="batchForm.level"><el-radio-button value="retail">零售</el-radio-button><el-radio-button value="wholesale">批发</el-radio-button><el-radio-button value="vip">VIP</el-radio-button></el-radio-group></el-form-item>
        <el-form-item label="折扣率"><div class="discount-input"><el-input-number v-model="batchForm.discount" :min="1" :max="100" :precision="0" controls-position="right" /><span>%</span></div><p class="form-tip">90% 表示按零售价的九折设置；100% 表示与零售价一致。</p></el-form-item>
        <el-form-item label="适用商品"><el-radio-group v-model="batchForm.scope"><el-radio value="all">全部 {{ rows.length }} 件商品</el-radio><el-radio value="selected" :disabled="!selectedRows.length">已选 {{ selectedRows.length }} 件商品</el-radio></el-radio-group></el-form-item>
      </el-form>
      <div class="batch-preview"><span>首件商品折后价</span><strong>{{ formatMoney(Number(previewPrice)) }}</strong><small>共影响 {{ batchTargets.length }} 件商品，实际按各自零售价计算</small></div>
      <template #footer><div class="dialog-footer"><el-button @click="batchVisible = false">取消</el-button><el-button type="primary" @click="applyBatch">展开并保存价格</el-button></div></template>
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
