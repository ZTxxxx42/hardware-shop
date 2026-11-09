<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowRight } from '@element-plus/icons-vue'
import { catalogApi } from '@/api/catalog'
import { getErrorMessage } from '@/api/http'
import type { ProductDetail } from '@/types/catalog'
import { formatPrice, getProductStatus } from '@/utils/catalog'
import ProductArtwork from '@/components/ProductArtwork.vue'
import RequestState from '@/components/RequestState.vue'

const route = useRoute()
const product = ref<ProductDetail | null>(null)
const loading = ref(true)
const error = ref('')
let requestId = 0

function positiveInteger(value: unknown): number | undefined {
  if (typeof value !== 'string') return undefined
  const parsed = Number(value)
  return Number.isInteger(parsed) && parsed > 0 ? parsed : undefined
}

const productId = computed(() => positiveInteger(route.params.id))
const hasMemberPrice = computed(() => product.value?.price !== product.value?.retail_price)

async function loadProduct() {
  const currentRequestId = ++requestId
  const id = productId.value
  product.value = null
  error.value = ''
  if (!id) {
    loading.value = false
    error.value = '商品编号无效，请返回产品中心重新选择'
    return
  }

  loading.value = true
  try {
    const data = await catalogApi.product(id)
    if (currentRequestId !== requestId) return
    product.value = data
    document.title = `${data.name}｜恒泰五金商贸`
  } catch (requestError) {
    if (currentRequestId !== requestId) return
    error.value = getErrorMessage(requestError, '商品详情加载失败，请稍后重试')
  } finally {
    if (currentRequestId === requestId) loading.value = false
  }
}

watch(productId, loadProduct, { immediate: true })
</script>

<template>
  <section class="detail-page">
    <div class="container">
      <nav class="breadcrumb" aria-label="面包屑">
        <RouterLink to="/">首页</RouterLink><span>/</span><RouterLink to="/products">产品中心</RouterLink><span>/</span><span>{{ product?.name ?? '商品详情' }}</span>
      </nav>
      <RequestState
        v-if="loading || error || !product"
        :loading="loading"
        :error="error"
        :empty="!loading && !error"
        loading-text="正在加载商品详情..."
        empty-text="商品不存在或已删除"
        @retry="loadProduct"
      />
      <template v-else-if="product">
        <div class="detail-card">
          <div class="detail-art"><ProductArtwork :slug="product.main_image" :alt="product.name" /></div>
          <div class="detail-info">
            <div class="detail-title-row">
              <span class="detail-eyebrow">PRODUCT DETAIL</span>
              <el-tag :type="product.status === 'ON_SALE' ? 'success' : 'info'" effect="light">{{ getProductStatus(product.status) }}</el-tag>
            </div>
            <h1>{{ product.name }}</h1>
            <p class="detail-model">产品型号：{{ product.model || '详询客服' }}</p>
            <p class="detail-description">{{ product.description || '暂无商品描述，欢迎联系客服获取详细产品资料。' }}</p>
            <div class="price-panel">
              <span>当前采购价</span>
              <div><strong><small>¥</small>{{ formatPrice(product.price) }}</strong><del v-if="hasMemberPrice">零售价 ¥{{ formatPrice(product.retail_price) }}</del></div>
              <p>价格根据当前会员等级实时计算，批量采购可联系客服询价</p>
            </div>
            <dl class="quick-specs">
              <div><dt>库存数量</dt><dd>{{ product.stock }} 件</dd></div>
              <div><dt>商品编号</dt><dd>{{ product.id }}</dd></div>
              <div><dt>所属分类</dt><dd><RouterLink :to="{ path: '/products', query: { category: product.category_id } }">查看同类商品</RouterLink></dd></div>
            </dl>
            <div class="detail-actions">
              <RouterLink class="primary-link" :to="{ path: '/contact', query: { product: product.name } }">询价咨询<el-icon><ArrowRight /></el-icon></RouterLink>
              <RouterLink class="secondary-link" to="/products">返回产品中心</RouterLink>
            </div>
          </div>
        </div>
        <section v-if="product.specs.length" class="spec-section" aria-labelledby="spec-title">
          <h2 id="spec-title">产品参数</h2>
          <dl class="spec-grid">
            <div v-for="spec in product.specs" :key="spec.id"><dt>{{ spec.spec_name }}</dt><dd>{{ spec.spec_value }}</dd></div>
          </dl>
        </section>
      </template>
    </div>
  </section>
</template>

<style scoped>
.detail-page { min-height: 650px; padding: 26px 0 70px; background: #f5f8fb; }
.breadcrumb { display: flex; gap: 10px; margin-bottom: 26px; overflow: hidden; color: #8b97a4; font-size: 12px; white-space: nowrap; }
.breadcrumb > span:last-child { overflow: hidden; text-overflow: ellipsis; }
.breadcrumb a:hover { color: var(--brand); }
.detail-card { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.06fr); overflow: hidden; border: 1px solid #e7edf3; border-radius: 14px; background: #fff; box-shadow: var(--shadow-sm); }
.detail-art { min-height: 490px; padding: 40px; background: radial-gradient(circle at 50% 42%, #fff 20%, #eef3f8 82%); }
.detail-info { padding: 45px 48px; border-left: 1px solid #edf1f5; }
.detail-title-row { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
.detail-eyebrow { color: var(--brand); font-family: Arial, sans-serif; font-size: 10px; letter-spacing: .18em; }
.detail-info h1 { margin-top: 12px; font-size: clamp(26px, 2.6vw, 36px); line-height: 1.35; }
.detail-model { margin-top: 8px; color: #748396; font-size: 14px; }
.detail-description { margin-top: 22px; color: #657689; font-size: 14px; line-height: 1.9; }
.price-panel { margin-top: 26px; padding: 18px 21px; border-left: 3px solid var(--brand); background: #f3f8fd; }
.price-panel > span { color: #71859a; font-size: 12px; }
.price-panel > div { display: flex; align-items: baseline; gap: 15px; margin-top: 2px; }
.price-panel strong { color: #e45b32; font-family: Arial, sans-serif; font-size: 32px; line-height: 1.4; }
.price-panel strong small { margin-right: 4px; font-size: 16px; }
.price-panel del { color: #94a1af; font-size: 12px; }
.price-panel p { margin-top: 2px; color: #8797a8; font-size: 11px; }
.quick-specs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 25px 0 0; }
.quick-specs div { min-width: 0; }
.quick-specs dt { color: #95a2af; font-size: 11px; }
.quick-specs dd { margin: 3px 0 0; color: #3c4e61; font-size: 13px; }
.quick-specs a { color: var(--brand); }
.detail-actions { display: flex; align-items: center; gap: 24px; margin-top: 30px; }
.secondary-link { color: #68798c; font-size: 13px; }
.secondary-link:hover { color: var(--brand); }
.spec-section { margin-top: 24px; padding: 28px 32px; border: 1px solid #e7edf3; border-radius: 12px; background: #fff; }
.spec-section h2 { font-size: 20px; }
.spec-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 35px; margin: 18px 0 0; }
.spec-grid div { display: grid; grid-template-columns: 130px 1fr; padding: 11px 0; border-bottom: 1px solid #edf1f5; font-size: 13px; }
.spec-grid dt { color: #8593a2; }
.spec-grid dd { margin: 0; color: #3c4e61; }
@media (max-width: 1000px) { .detail-info { padding: 34px 30px; } .detail-art { min-height: 450px; padding: 25px; } .quick-specs { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 767px) {
  .detail-page { padding-top: 18px; }
  .breadcrumb { margin-bottom: 18px; }
  .detail-card { grid-template-columns: 1fr; border-radius: 11px; }
  .detail-art { min-height: 280px; height: 58vw; max-height: 350px; padding: 20px; }
  .detail-info { padding: 24px 20px 27px; border-top: 1px solid #edf1f5; border-left: 0; }
  .detail-info h1 { font-size: 25px; }
  .detail-description { margin-top: 17px; font-size: 13px; }
  .price-panel { margin-top: 20px; padding: 15px; }
  .price-panel strong { font-size: 28px; }
  .price-panel > div { flex-wrap: wrap; gap: 8px; }
  .quick-specs { margin-top: 20px; }
  .detail-actions { gap: 18px; margin-top: 24px; }
  .spec-section { padding: 22px 18px; }
  .spec-grid { grid-template-columns: 1fr; }
  .spec-grid div { grid-template-columns: 105px 1fr; }
}
</style>
