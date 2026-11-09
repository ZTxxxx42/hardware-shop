<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import type { Customer, CustomerLevel } from '@/types/business'
import { formatMoney, levelMeta } from '@/utils/format'

const rows = ref<Customer[]>([])
const levels: CustomerLevel[] = ['retail', 'wholesale', 'vip']
const filters = reactive({ keyword: '', level: '' as CustomerLevel | '' })
const filteredRows = computed(() => rows.value.filter((item) => {
  const keyword = filters.keyword.trim().toLowerCase()
  return (!keyword || `${item.realName}${item.username}${item.phone}`.toLowerCase().includes(keyword)) && (!filters.level || item.level === filters.level)
}))
function resetFilters() { Object.assign(filters, { keyword: '', level: '' }) }
</script>

<template>
  <div class="page">
    <PageHeader title="客户管理" description="查看前台注册客户与累计订货情况，并人工指定零售、批发或 VIP 等级。" />
    <el-alert class="customer-tip" title="后端缺失：客户列表、客户资料编辑与等级指定管理端点。页面不再展示静态 mock 客户，待接口补齐后接入。" type="warning" :closable="false" show-icon />
    <section class="level-guide">
      <div v-for="level in levels" :key="level"><el-tag :type="levelMeta[level].type" effect="plain">{{ levelMeta[level].label }}</el-tag><span>{{ level === 'retail' ? '默认等级，取商品零售价' : level === 'wholesale' ? '适用于稳定批量采购客户' : '适用于重点合作客户' }}</span></div>
    </section>
    <section class="table-card">
      <div class="table-toolbar"><div class="filter-bar">
        <el-input v-model="filters.keyword" :prefix-icon="Search" clearable disabled placeholder="搜索客户 / 账号 / 手机" />
        <el-select v-model="filters.level" clearable disabled placeholder="全部等级"><el-option label="零售" value="retail" /><el-option label="批发" value="wholesale" /><el-option label="VIP" value="vip" /></el-select>
        <el-button disabled @click="resetFilters">重置</el-button>
      </div></div>
      <el-table :data="filteredRows" row-key="id">
        <el-table-column label="客户" min-width="210"><template #default="{ row }"><div class="customer-cell"><span class="customer-avatar">{{ row.realName.slice(0, 1) }}</span><div><div class="table-product-name">{{ row.realName }}</div><div class="table-subtext">账号：{{ row.username }}</div></div></div></template></el-table-column>
        <el-table-column prop="phone" label="联系电话" min-width="140" />
        <el-table-column label="客户等级" width="140"><template #default="{ row }"><el-select v-model="row.level" disabled><el-option v-for="level in levels" :key="level" :label="levelMeta[level].label" :value="level" /></el-select></template></el-table-column>
        <el-table-column prop="orderCount" label="累计订单" width="110" align="right"><template #default="{ row }">{{ row.orderCount }} 笔</template></el-table-column>
        <el-table-column label="累计消费" width="140" align="right"><template #default="{ row }"><span class="money">{{ formatMoney(row.totalSpent) }}</span></template></el-table-column>
        <el-table-column prop="createdAt" label="注册时间" width="160" />
        <el-table-column label="操作" width="90" fixed="right"><template #default><el-button link type="primary" disabled>编辑</el-button></template></el-table-column>
        <template #empty><el-empty description="后端暂未提供客户列表数据" /></template>
      </el-table>
      <div class="table-footer"><span>客户管理端点待后端补齐</span><el-pagination background layout="prev, pager, next" :total="0" :page-size="10" /></div>
    </section>
  </div>
</template>

<style scoped>
.customer-tip { margin-bottom: 16px; }
.level-guide { display: flex; flex-wrap: wrap; gap: 12px 28px; margin-bottom: 16px; padding: 14px 18px; background: #fff; border: 1px solid #e3eaf3; border-radius: 10px; }
.level-guide > div { display: flex; align-items: center; gap: 10px; color: #68788f; font-size: 12px; }
.customer-cell { display: flex; align-items: center; gap: 11px; }
.customer-avatar { display: grid; flex: none; width: 36px; height: 36px; place-items: center; color: #1a6fd6; font-size: 12px; font-weight: 600; background: #eaf2fc; border-radius: 8px; }
@media (max-width: 600px) { :deep(.el-dialog) { width: calc(100% - 24px) !important; } }
</style>
