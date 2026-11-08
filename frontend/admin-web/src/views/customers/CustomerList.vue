<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { customers as mockCustomers } from '@/mock'
import type { Customer, CustomerLevel } from '@/types/business'
import { formatMoney, levelMeta } from '@/utils/format'

const rows = ref<Customer[]>(mockCustomers.map((item) => ({ ...item })))
const levels: CustomerLevel[] = ['retail', 'wholesale', 'vip']
const filters = reactive({ keyword: '', level: '' as CustomerLevel | '' })
const filteredRows = computed(() => rows.value.filter((item) => {
  const keyword = filters.keyword.trim().toLowerCase()
  return (!keyword || `${item.realName}${item.username}${item.phone}`.toLowerCase().includes(keyword)) && (!filters.level || item.level === filters.level)
}))
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const form = reactive({ realName: '', phone: '', level: 'retail' as CustomerLevel })
const rules: FormRules = {
  realName: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
}
function resetFilters() { Object.assign(filters, { keyword: '', level: '' }) }
function openEdit(row: Customer) {
  editingId.value = row.id
  Object.assign(form, { realName: row.realName, phone: row.phone, level: row.level })
  dialogVisible.value = true
  formRef.value?.clearValidate()
}
async function save() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  const target = rows.value.find((item) => item.id === editingId.value)
  if (target) Object.assign(target, form)
  dialogVisible.value = false
  ElMessage.success('客户资料已保存（示例数据）')
}
function levelChanged(row: Customer) {
  ElMessage.success(`${row.realName}已指定为${levelMeta[row.level].label}客户（示例数据）`)
}
</script>

<template>
  <div class="page">
    <PageHeader title="客户管理" description="查看前台注册客户与累计订货情况，并人工指定零售、批发或 VIP 等级。" />
    <section class="level-guide">
      <div v-for="level in levels" :key="level"><el-tag :type="levelMeta[level].type" effect="plain">{{ levelMeta[level].label }}</el-tag><span>{{ level === 'retail' ? '默认等级，取商品零售价' : level === 'wholesale' ? '适用于稳定批量采购客户' : '适用于重点合作客户' }}</span></div>
    </section>
    <section class="table-card">
      <div class="table-toolbar"><div class="filter-bar">
        <el-input v-model="filters.keyword" :prefix-icon="Search" clearable placeholder="搜索客户 / 账号 / 手机" />
        <el-select v-model="filters.level" clearable placeholder="全部等级"><el-option label="零售" value="retail" /><el-option label="批发" value="wholesale" /><el-option label="VIP" value="vip" /></el-select>
        <el-button @click="resetFilters">重置</el-button>
      </div></div>
      <el-table :data="filteredRows" row-key="id">
        <el-table-column label="客户" min-width="210"><template #default="{ row }"><div class="customer-cell"><span class="customer-avatar">{{ row.realName.slice(0, 1) }}</span><div><div class="table-product-name">{{ row.realName }}</div><div class="table-subtext">账号：{{ row.username }}</div></div></div></template></el-table-column>
        <el-table-column prop="phone" label="联系电话" min-width="140" />
        <el-table-column label="客户等级" width="140"><template #default="{ row }"><el-select v-model="row.level" @change="levelChanged(row)"><el-option v-for="level in levels" :key="level" :label="levelMeta[level].label" :value="level"><span>{{ levelMeta[level].label }}</span></el-option></el-select></template></el-table-column>
        <el-table-column prop="orderCount" label="累计订单" width="110" align="right"><template #default="{ row }">{{ row.orderCount }} 笔</template></el-table-column>
        <el-table-column label="累计消费" width="140" align="right"><template #default="{ row }"><span class="money">{{ formatMoney(row.totalSpent) }}</span></template></el-table-column>
        <el-table-column prop="createdAt" label="注册时间" width="160" />
        <el-table-column label="操作" width="90" fixed="right"><template #default="{ row }"><el-button link type="primary" @click="openEdit(row)">编辑</el-button></template></el-table-column>
      </el-table>
      <div class="table-footer"><span>共 {{ filteredRows.length }} 位客户 · 等级变更仅保存在当前页面</span><el-pagination background layout="prev, pager, next" :total="filteredRows.length" :page-size="10" /></div>
    </section>
    <el-dialog v-model="dialogVisible" title="编辑客户资料" width="480px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="88px">
        <el-form-item label="客户名称" prop="realName"><el-input v-model="form.realName" maxlength="40" /></el-form-item>
        <el-form-item label="联系电话" prop="phone"><el-input v-model="form.phone" maxlength="20" /></el-form-item>
        <el-form-item label="客户等级"><el-radio-group v-model="form.level"><el-radio value="retail">零售</el-radio><el-radio value="wholesale">批发</el-radio><el-radio value="vip">VIP</el-radio></el-radio-group><p class="form-tip">等级决定客户在商品详情和下单时看到的价格。</p></el-form-item>
      </el-form>
      <template #footer><div class="dialog-footer"><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" @click="save">保存客户</el-button></div></template>
    </el-dialog>
  </div>
</template>

<style scoped>
.level-guide { display: flex; flex-wrap: wrap; gap: 12px 28px; margin-bottom: 16px; padding: 14px 18px; background: #fff; border: 1px solid #e3eaf3; border-radius: 10px; }
.level-guide > div { display: flex; align-items: center; gap: 10px; color: #68788f; font-size: 12px; }
.customer-cell { display: flex; align-items: center; gap: 11px; }
.customer-avatar { display: grid; flex: none; width: 36px; height: 36px; place-items: center; color: #1a6fd6; font-size: 12px; font-weight: 600; background: #eaf2fc; border-radius: 8px; }
@media (max-width: 600px) { :deep(.el-dialog) { width: calc(100% - 24px) !important; } }
</style>
