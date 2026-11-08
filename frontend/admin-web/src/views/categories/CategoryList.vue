<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { categories as mockCategories } from '@/mock'
import type { Category } from '@/types/business'

type CategoryRow = Category & { children?: CategoryRow[] }
const rows = ref<Category[]>(mockCategories.map((item) => ({ ...item })))
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const form = reactive({ name: '', parentId: null as number | null, sort: 10, status: 'ENABLED' as Category['status'] })
const rules: FormRules = { name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }] }
const roots = computed(() => rows.value.filter((item) => item.parentId === null).sort((a, b) => a.sort - b.sort))
const treeRows = computed<CategoryRow[]>(() => roots.value.map((root) => ({
  ...root,
  children: rows.value.filter((item) => item.parentId === root.id).sort((a, b) => a.sort - b.sort),
})))
const isEditing = computed(() => editingId.value !== null)
function openCreate(parent?: Category) {
  editingId.value = null
  Object.assign(form, { name: '', parentId: parent?.id ?? null, sort: 10, status: 'ENABLED' })
  dialogVisible.value = true
  formRef.value?.clearValidate()
}
function openEdit(row: Category) {
  editingId.value = row.id
  Object.assign(form, { name: row.name, parentId: row.parentId, sort: row.sort, status: row.status })
  dialogVisible.value = true
  formRef.value?.clearValidate()
}
async function save() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  if (editingId.value) {
    const target = rows.value.find((item) => item.id === editingId.value)
    if (target) Object.assign(target, { name: form.name, sort: form.sort, status: form.status })
  } else {
    rows.value.push({ id: Math.max(...rows.value.map((item) => item.id)) + 1, ...form, productCount: 0 })
  }
  dialogVisible.value = false
  ElMessage.success(isEditing.value ? '分类已保存（示例数据）' : '分类已新增（示例数据）')
}
async function toggleStatus(row: Category) {
  row.status = row.status === 'ENABLED' ? 'DISABLED' : 'ENABLED'
  ElMessage.success(row.status === 'ENABLED' ? '分类已启用' : '分类已停用')
}
async function remove(row: Category) {
  if (rows.value.some((item) => item.parentId === row.id)) {
    ElMessage.warning('请先删除该分类下的子分类')
    return
  }
  if (row.productCount > 0) {
    ElMessage.warning('该分类仍有关联商品，暂不能删除')
    return
  }
  try {
    await ElMessageBox.confirm(`确认删除“${row.name}”？`, '删除分类', { type: 'warning', confirmButtonText: '删除' })
    rows.value = rows.value.filter((item) => item.id !== row.id)
    ElMessage.success('分类已删除')
  } catch { /* 用户取消操作 */ }
}
</script>

<template>
  <div class="page">
    <PageHeader title="分类管理" description="按两级目录组织商品，一级分类用于业务分组，二级分类用于商品归档。">
      <el-button type="primary" :icon="Plus" @click="openCreate()">新增一级分类</el-button>
    </PageHeader>
    <el-alert class="category-tip" title="当前最多支持两级分类；有关联商品或子分类的目录不可直接删除。" type="info" :closable="false" show-icon />
    <section class="table-card">
      <el-table :data="treeRows" row-key="id" default-expand-all :tree-props="{ children: 'children' }">
        <el-table-column prop="name" label="分类名称" min-width="240" />
        <el-table-column label="层级" width="110"><template #default="{ row }"><el-tag :type="row.parentId ? 'info' : 'primary'" effect="plain">{{ row.parentId ? '二级分类' : '一级分类' }}</el-tag></template></el-table-column>
        <el-table-column prop="sort" label="排序值" width="100" align="center" />
        <el-table-column prop="productCount" label="关联商品" width="110" align="right"><template #default="{ row }">{{ row.productCount }} 件</template></el-table-column>
        <el-table-column label="状态" width="100"><template #default="{ row }"><el-tag :type="row.status === 'ENABLED' ? 'success' : 'info'">{{ row.status === 'ENABLED' ? '启用' : '停用' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" min-width="250" fixed="right"><template #default="{ row }"><div class="inline-actions"><el-button v-if="!row.parentId" link type="primary" @click="openCreate(row)">添加子类</el-button><el-button link type="primary" @click="openEdit(row)">编辑</el-button><el-button link @click="toggleStatus(row)">{{ row.status === 'ENABLED' ? '停用' : '启用' }}</el-button><el-button link type="danger" @click="remove(row)">删除</el-button></div></template></el-table-column>
      </el-table>
      <div class="table-footer"><span>共 {{ rows.length }} 个分类 · {{ roots.length }} 个一级分类</span></div>
    </section>
    <el-dialog v-model="dialogVisible" :title="isEditing ? '编辑分类' : '新增分类'" width="480px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="88px">
        <el-form-item label="上级分类"><el-select v-model="form.parentId" :disabled="isEditing" clearable placeholder="无（作为一级分类）" style="width: 100%"><el-option v-for="item in roots" :key="item.id" :label="item.name" :value="item.id" /></el-select><p class="form-tip">留空创建一级分类；选择上级后创建二级分类。</p></el-form-item>
        <el-form-item label="分类名称" prop="name"><el-input v-model="form.name" maxlength="30" placeholder="请输入分类名称" /></el-form-item>
        <el-form-item label="排序值"><el-input-number v-model="form.sort" :min="0" :max="9999" controls-position="right" style="width: 100%" /><p class="form-tip">数值越小，展示顺序越靠前。</p></el-form-item>
        <el-form-item label="状态"><el-radio-group v-model="form.status"><el-radio value="ENABLED">启用</el-radio><el-radio value="DISABLED">停用</el-radio></el-radio-group></el-form-item>
      </el-form>
      <template #footer><div class="dialog-footer"><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" @click="save">保存分类</el-button></div></template>
    </el-dialog>
  </div>
</template>

<style scoped>
.category-tip { margin-bottom: 16px; }
@media (max-width: 600px) { :deep(.el-dialog) { width: calc(100% - 24px) !important; } }
</style>
