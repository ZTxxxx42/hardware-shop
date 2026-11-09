<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules, UploadFile, UploadUserFile } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import RequestError from '@/components/RequestError.vue'
import { adminApi } from '@/api/admin'
import { getApiErrorMessage, showRequestError } from '@/api/error'
import { mapCategory, mapProduct, mergeProductDetail } from '@/api/mappers'
import type { Category, Product, ProductStatus } from '@/types/business'
import { formatMoney } from '@/utils/format'
import { resolveProductImage, useFallbackImage } from '@/utils/product'

interface ProductForm {
  name: string
  categoryId: number | null
  model: string
  retailPrice: number
  stock: number
  status: ProductStatus
  mainImage: string
  specs: string
  description: string
  images: UploadUserFile[]
}
const emptyForm = (): ProductForm => ({ name: '', categoryId: null, model: '', retailPrice: 0, stock: 0, status: 'ON', mainImage: '', specs: '', description: '', images: [] })
const categories = ref<Category[]>([])
const productRows = ref<Product[]>([])
const total = ref(0)
const loading = ref(false)
const loadError = ref('')
const filters = reactive({ keyword: '', categoryId: null as number | null, status: '' as ProductStatus | '' })
const currentPage = ref(1)
const pageSize = 10
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)
const detailLoadingId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const form = reactive<ProductForm>(emptyForm())
const previewVisible = ref(false)
const previewUrl = ref('')
const rules: FormRules<ProductForm> = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  categoryId: [{ required: true, message: '请选择所属分类', trigger: 'change' }],
  retailPrice: [{ required: true, message: '请输入零售价', trigger: 'blur' }],
  stock: [{ required: true, message: '请输入库存', trigger: 'blur' }],
}
const leafCategories = computed(() => categories.value.filter((item) => !categories.value.some((child) => child.parentId === item.id)))
const filteredProducts = computed(() => productRows.value.filter((item) => {
  const keyword = filters.keyword.trim().toLowerCase()
  return (!keyword || `${item.name}${item.model}`.toLowerCase().includes(keyword))
    && (!filters.categoryId || item.categoryId === filters.categoryId)
    && (!filters.status || item.status === filters.status)
}))
const pagedProducts = computed(() => filteredProducts.value.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize))
const dialogTitle = computed(() => editingId.value ? '编辑商品' : '新增商品')

async function loadData() {
  loading.value = true
  loadError.value = ''
  try {
    const [categoryResponse, productResponse] = await Promise.all([
      adminApi.getCategories(),
      adminApi.getProducts({ page: 1, page_size: 100 }),
    ])
    categories.value = categoryResponse.data.map((item) => mapCategory(item))
    const categoryNames = new Map(categories.value.map((item) => [item.id, item.name]))
    productRows.value = productResponse.data.items.map((item) => mapProduct(item, categoryNames.get(item.category_id)))
    total.value = productResponse.data.total
  } catch (error) {
    loadError.value = getApiErrorMessage(error) || '商品数据加载失败'
    showRequestError(error, '商品数据加载失败')
  } finally {
    loading.value = false
  }
}
function resetFilters() { Object.assign(filters, { keyword: '', categoryId: null, status: '' }) }
function openCreate() {
  editingId.value = null
  Object.assign(form, emptyForm())
  dialogVisible.value = true
  formRef.value?.clearValidate()
}
async function openEdit(row: Product) {
  detailLoadingId.value = row.id
  try {
    const { data } = await adminApi.getProductDetail(row.id)
    mergeProductDetail(row, data)
    editingId.value = row.id
    Object.assign(form, {
      name: row.name,
      categoryId: row.categoryId,
      model: row.model,
      retailPrice: row.retailPrice,
      stock: row.stock,
      status: row.status,
      mainImage: row.mainImage,
      specs: row.specs,
      description: row.description,
      images: row.mainImage ? [{ name: '商品主图', url: resolveProductImage(row.mainImage) }] : [],
    })
    dialogVisible.value = true
    formRef.value?.clearValidate()
  } catch (error) {
    showRequestError(error, '商品详情加载失败')
  } finally {
    detailLoadingId.value = null
  }
}
async function saveProduct() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    const payload = {
      category_id: form.categoryId!,
      name: form.name.trim(),
      model: form.model.trim() || null,
      description: form.description.trim() || null,
      retail_price: form.retailPrice,
      stock: form.stock,
      status: form.status === 'ON' ? 'ON_SALE' : 'OFF_SALE',
      main_image: form.mainImage.trim() || null,
    }
    if (editingId.value) await adminApi.updateProduct(editingId.value, payload)
    else await adminApi.createProduct(payload)
    const wasEditing = Boolean(editingId.value)
    dialogVisible.value = false
    await loadData()
    ElMessage.success(wasEditing ? '商品已保存' : '商品已新增')
  } catch (error) {
    showRequestError(error, '商品保存失败')
  } finally {
    saving.value = false
  }
}
async function toggleStatus(row: Product) {
  const nextStatus = row.status === 'ON' ? 'OFF' : 'ON'
  try {
    await ElMessageBox.confirm(`确认${nextStatus === 'ON' ? '上架' : '下架'}“${row.name}”？`, '状态变更', { type: 'warning' })
    const { data } = await adminApi.updateProduct(row.id, { status: nextStatus === 'ON' ? 'ON_SALE' : 'OFF_SALE' })
    Object.assign(row, mapProduct(data, row.categoryName))
    ElMessage.success(nextStatus === 'ON' ? '已上架' : '已下架')
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    showRequestError(error, '商品状态更新失败')
  }
}
function removeProduct() {
  ElMessage.warning('后端缺失：DELETE /api/admin/products/{id}，暂不能删除商品')
}
function previewImage(file: UploadFile) {
  previewUrl.value = file.url ?? ''
  previewVisible.value = true
}
watch(() => [filters.keyword, filters.categoryId, filters.status], () => { currentPage.value = 1 })
onMounted(loadData)
</script>

<template>
  <div class="page">
    <PageHeader title="商品管理" description="维护单品、规格文本与库存；商品价格按客户等级单独设置。">
      <el-button type="primary" :icon="Plus" @click="openCreate">新增商品</el-button>
    </PageHeader>
    <RequestError v-if="loadError" :message="loadError" @retry="loadData" />
    <section v-loading="loading" class="table-card">
      <div class="table-toolbar"><div class="filter-bar">
        <el-input v-model="filters.keyword" :prefix-icon="Search" clearable placeholder="搜索商品名称 / 型号" />
        <el-select v-model="filters.categoryId" clearable placeholder="全部分类"><el-option v-for="item in leafCategories" :key="item.id" :label="item.name" :value="item.id" /></el-select>
        <el-select v-model="filters.status" clearable placeholder="全部状态"><el-option label="已上架" value="ON" /><el-option label="已下架" value="OFF" /></el-select>
        <el-button @click="resetFilters">重置</el-button>
      </div></div>
      <el-table :data="pagedProducts" row-key="id">
        <el-table-column label="商品" min-width="280"><template #default="{ row }"><div class="table-product"><img :src="resolveProductImage(row.mainImage)" :alt="row.name" @error="useFallbackImage" /><div><div class="table-product-name">{{ row.name }}</div><div class="table-subtext">{{ row.model || '—' }}</div></div></div></template></el-table-column>
        <el-table-column prop="categoryName" label="分类" min-width="120" />
        <el-table-column label="零售价" width="110" align="right"><template #default="{ row }"><span class="money">{{ formatMoney(row.retailPrice) }}</span></template></el-table-column>
        <el-table-column label="库存" width="110" align="right"><template #default="{ row }"><span :class="{ 'text-danger': row.stock < 50 }">{{ row.stock.toLocaleString() }}</span><span v-if="row.stock < 50" class="table-subtext">{{ row.stock === 0 ? '缺货' : '库存偏低' }}</span></template></el-table-column>
        <el-table-column label="状态" width="90"><template #default="{ row }"><el-tag :type="row.status === 'ON' ? 'success' : 'info'">{{ row.status === 'ON' ? '已上架' : '已下架' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="190" fixed="right"><template #default="{ row }"><div class="inline-actions"><el-button link type="primary" :loading="detailLoadingId === row.id" @click="openEdit(row)">编辑</el-button><el-button link :type="row.status === 'ON' ? 'warning' : 'success'" @click="toggleStatus(row)">{{ row.status === 'ON' ? '下架' : '上架' }}</el-button><el-button link type="danger" title="后端暂未提供商品删除端点" @click="removeProduct">删除</el-button></div></template></el-table-column>
        <template #empty><el-empty :description="loadError ? '商品数据加载失败' : '没有符合条件的商品'" /></template>
      </el-table>
      <div class="table-footer"><span>后端共 {{ total }} 件商品 · 当前加载 {{ productRows.length }} 件</span><el-pagination v-model:current-page="currentPage" background layout="prev, pager, next" :total="filteredProducts.length" :page-size="pageSize" /></div>
    </section>
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="760px" top="5vh" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="92px">
        <el-row :gutter="18">
          <el-col :span="16"><el-form-item label="商品名称" prop="name"><el-input v-model="form.name" maxlength="200" placeholder="例如：304 不锈钢外六角螺栓" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="商品状态"><el-radio-group v-model="form.status"><el-radio value="ON">上架</el-radio><el-radio value="OFF">下架</el-radio></el-radio-group></el-form-item></el-col>
        </el-row>
        <el-row :gutter="18">
          <el-col :span="12"><el-form-item label="所属分类" prop="categoryId"><el-select v-model="form.categoryId" placeholder="请选择分类" style="width: 100%"><el-option v-for="item in leafCategories" :key="item.id" :label="item.name" :value="item.id" /></el-select></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="规格型号"><el-input v-model="form.model" placeholder="例如：DIN933 / M8×30" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="18">
          <el-col :span="12"><el-form-item label="零售价" prop="retailPrice"><el-input-number v-model="form.retailPrice" :min="0" :precision="2" :step="1" controls-position="right" style="width: 100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="库存" prop="stock"><el-input-number v-model="form.stock" :min="0" :precision="0" :step="10" controls-position="right" style="width: 100%" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="主图地址"><el-input v-model="form.mainImage" placeholder="输入可访问的图片 URL，或保留种子图片标识" /><p class="form-tip">后端暂无图片上传接口；下方本地选图仅用于预览，不会上传。</p></el-form-item>
        <el-form-item label="图片预览">
          <div class="upload-field">
            <el-upload v-model:file-list="form.images" action="#" list-type="picture-card" :auto-upload="false" :limit="6" multiple accept="image/*" :on-preview="previewImage">
              <el-icon><Plus /></el-icon><span class="upload-text">添加图片</span>
            </el-upload>
          </div>
        </el-form-item>
        <el-form-item label="规格文本"><el-input v-model="form.specs" type="textarea" :rows="4" disabled placeholder="后端暂未提供规格写入端点" /><p class="form-tip">规格文本只读展示；商品新增/编辑接口当前不接收规格字段。</p></el-form-item>
        <el-form-item label="商品描述"><el-input v-model="form.description" type="textarea" :rows="3" maxlength="500" show-word-limit placeholder="补充使用场景、包装与交付说明" /></el-form-item>
      </el-form>
      <template #footer><div class="dialog-footer"><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" :loading="saving" @click="saveProduct">保存商品</el-button></div></template>
    </el-dialog>
    <el-dialog v-model="previewVisible" title="图片预览" width="420px" append-to-body><img class="image-preview" :src="previewUrl" alt="商品图片预览" /></el-dialog>
  </div>
</template>

<style scoped>
.upload-field { width: 100%; }
.upload-text { display: block; margin-top: 3px; color: #68788f; font-size: 11px; }
.upload-field :deep(.el-upload--picture-card) { display: flex; flex-direction: column; width: 88px; height: 88px; }
.upload-field :deep(.el-upload-list--picture-card .el-upload-list__item) { width: 88px; height: 88px; }
.image-preview { display: block; width: 100%; max-height: 460px; object-fit: contain; background: #f4f7fb; border-radius: 8px; }
@media (max-width: 768px) {
  :deep(.el-dialog) { width: calc(100% - 24px) !important; }
  :deep(.el-col) { max-width: 100%; flex: 0 0 100%; }
}
</style>
