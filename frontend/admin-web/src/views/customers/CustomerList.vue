<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import RequestError from '@/components/RequestError.vue'
import { adminApi } from '@/api/admin'
import { getApiErrorMessage, showRequestError } from '@/api/error'
import { mapCustomer } from '@/api/mappers'
import type { Customer, CustomerLevel } from '@/types/business'
import { levelMeta } from '@/utils/format'

const rows = ref<Customer[]>([])
const loading = ref(false)
const loadError = ref('')
const savingId = ref<number | null>(null)
const levels: CustomerLevel[] = ['retail', 'wholesale', 'vip']
const filters = reactive({ keyword: '', level: '' as CustomerLevel | '' })
const filteredRows = computed(() => rows.value.filter((item) => !filters.level || item.level === filters.level))

async function loadData() {
  loading.value = true
  loadError.value = ''
  try {
    const { data } = await adminApi.getCustomers({ keyword: filters.keyword.trim() || undefined })
    rows.value = data.map(mapCustomer)
  } catch (error) {
    loadError.value = getApiErrorMessage(error) || '客户数据加载失败'
    showRequestError(error, '客户数据加载失败')
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  Object.assign(filters, { keyword: '', level: '' })
  loadData()
}

async function saveLevel(row: Customer) {
  if (!row.level) {
    ElMessage.warning('请先选择客户等级')
    return
  }
  savingId.value = row.id
  try {
    const { data } = await adminApi.updateCustomerLevel(row.id, row.level)
    Object.assign(row, mapCustomer(data))
    ElMessage.success(`已将「${row.username}」等级设为${levelMeta[data.level_code as CustomerLevel].label}`)
  } catch (error) {
    showRequestError(error, '等级保存失败')
  } finally {
    savingId.value = null
  }
}

onMounted(loadData)
</script>

<template>
  <div class="page">
    <PageHeader title="客户管理" description="查看前台注册客户，并人工指定零售、批发或 VIP 等级。" />
    <section class="level-guide">
      <div v-for="level in levels" :key="level"><el-tag :type="levelMeta[level].type" effect="plain">{{ levelMeta[level].label }}</el-tag><span>{{ level === 'retail' ? '默认等级，取商品零售价' : level === 'wholesale' ? '适用于稳定批量采购客户' : '适用于重点合作客户' }}</span></div>
    </section>
    <RequestError v-if="loadError" :message="loadError" @retry="loadData" />
    <section v-loading="loading" class="table-card">
      <div class="table-toolbar"><div class="filter-bar">
        <el-input v-model="filters.keyword" :prefix-icon="Search" clearable placeholder="搜索客户 / 账号 / 手机" @keyup.enter="loadData" @clear="loadData" />
        <el-select v-model="filters.level" clearable placeholder="全部等级"><el-option label="零售" value="retail" /><el-option label="批发" value="wholesale" /><el-option label="VIP" value="vip" /></el-select>
        <el-button type="primary" @click="loadData">搜索</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div></div>
      <el-table :data="filteredRows" row-key="id">
        <el-table-column label="客户" min-width="210"><template #default="{ row }"><div class="customer-cell"><span class="customer-avatar">{{ (row.realName || row.username).slice(0, 1) }}</span><div><div class="table-product-name">{{ row.realName || row.username }}</div><div class="table-subtext">账号：{{ row.username }}</div></div></div></template></el-table-column>
        <el-table-column prop="phone" label="联系电话" min-width="140"><template #default="{ row }">{{ row.phone || '—' }}</template></el-table-column>
        <el-table-column label="客户等级" width="170"><template #default="{ row }"><el-select v-model="row.level" placeholder="未指定" style="width: 130px"><el-option v-for="level in levels" :key="level" :label="levelMeta[level].label" :value="level" /></el-select></template></el-table-column>
        <el-table-column label="操作" width="110" fixed="right"><template #default="{ row }"><el-button link type="primary" :loading="savingId === row.id" @click="saveLevel(row)">保存等级</el-button></template></el-table-column>
        <template #empty><el-empty :description="loadError ? '客户数据加载失败' : '暂无客户'" /></template>
      </el-table>
      <div class="table-footer"><span>共 {{ filteredRows.length }} 位客户 · 等级修改后点击「保存等级」生效</span></div>
    </section>
  </div>
</template>

<style scoped>
.level-guide { display: flex; flex-wrap: wrap; gap: 12px 28px; margin-bottom: 16px; padding: 14px 18px; background: #fff; border: 1px solid #e3eaf3; border-radius: 10px; }
.level-guide > div { display: flex; align-items: center; gap: 10px; color: #68788f; font-size: 12px; }
.customer-cell { display: flex; align-items: center; gap: 11px; }
.customer-avatar { display: grid; flex: none; width: 36px; height: 36px; place-items: center; color: #1a6fd6; font-size: 12px; font-weight: 600; background: #eaf2fc; border-radius: 8px; }
</style>
