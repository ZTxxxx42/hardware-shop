<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { catalogApi } from '@/api/catalog'
import { getErrorMessage } from '@/api/http'
import type { Category, Product } from '@/types/catalog'
import { getCategoryDescription } from '@/utils/catalog'
import ProductCard from '@/components/ProductCard.vue'
import RequestState from '@/components/RequestState.vue'

const route = useRoute()
const router = useRouter()
const pageSize = 8
const categories = ref<Category[]>([])
const products = ref<Product[]>([])
const total = ref(0)
const categoriesLoading = ref(true)
const productsLoading = ref(true)
const categoryError = ref('')
const productsError = ref('')
let productRequestId = 0

function positiveInteger(value: unknown): number | undefined {
  if (typeof value !== 'string') return undefined
  const parsed = Number(value)
  return Number.isInteger(parsed) && parsed > 0 ? parsed : undefined
}

const categoryId = computed(() => positiveInteger(route.query.category))
const currentPage = computed(() => positiveInteger(route.query.page) ?? 1)
const activeCategory = computed(() => categories.value.find((item) => item.id === categoryId.value))

async function loadCategories() {
  categoriesLoading.value = true
  categoryError.value = ''
  try {
    const data = await catalogApi.categories()
    categories.value = [...data].sort((a, b) => a.sort - b.sort || a.id - b.id)
  } catch (requestError) {
    categoryError.value = getErrorMessage(requestError, '分类加载失败')
  } finally {
    categoriesLoading.value = false
  }
}

async function loadProducts() {
  const requestId = ++productRequestId
  const requestedPage = currentPage.value
  productsLoading.value = true
  productsError.value = ''
  try {
    const data = await catalogApi.products({
      category_id: categoryId.value,
      page: requestedPage,
      page_size: pageSize,
    })
    if (requestId !== productRequestId) return

    const lastPage = Math.max(1, Math.ceil(data.total / pageSize))
    if (data.total > 0 && data.items.length === 0 && requestedPage > lastPage) {
      await router.replace({ query: { ...route.query, page: lastPage > 1 ? String(lastPage) : undefined } })
      return
    }
    products.value = data.items
    total.value = data.total
  } catch (requestError) {
    if (requestId !== productRequestId) return
    products.value = []
    total.value = 0
    productsError.value = getErrorMessage(requestError, '商品加载失败，请稍后重试')
  } finally {
    if (requestId === productRequestId) productsLoading.value = false
  }
}

function changePage(page: number) {
  void router.push({ query: { ...route.query, page: page > 1 ? String(page) : undefined } })
}

watch([categoryId, currentPage], loadProducts, { immediate: true })
onMounted(loadCategories)
</script>

<template>
  <section class="products-page">
    <div class="container">
      <nav class="breadcrumb" aria-label="面包屑"><RouterLink to="/">首页</RouterLink><span>/</span><span>产品中心</span></nav>
      <div class="list-heading">
        <div><span>QUALITY HARDWARE</span><h1>{{ activeCategory?.name ?? '产品中心' }}</h1><p>{{ activeCategory ? getCategoryDescription(activeCategory) : '精选工业五金，规格齐全，支持批量采购与询价' }}</p></div>
        <el-tag effect="plain">共 {{ total }} 件商品</el-tag>
      </div>
      <div class="category-filter">
        <RouterLink to="/products" :class="{ active: !categoryId }">全部产品</RouterLink>
        <RouterLink v-for="category in categories" :key="category.id" :to="{ path: '/products', query: { category: category.id } }" :class="{ active: categoryId === category.id }">{{ category.name }}</RouterLink>
        <span v-if="categoriesLoading" class="filter-message">正在加载分类...</span>
        <button v-else-if="categoryError" type="button" class="filter-retry" @click="loadCategories">{{ categoryError }}，点击重试</button>
      </div>
      <RequestState
        v-if="productsLoading || productsError || products.length === 0"
        :loading="productsLoading"
        :error="productsError"
        :empty="!productsLoading && !productsError"
        loading-text="正在加载商品..."
        :empty-text="activeCategory ? '该分类暂无商品' : '暂无商品'"
        @retry="loadProducts"
      />
      <div v-else class="products-grid"><ProductCard v-for="product in products" :key="product.id" :product="product" /></div>
      <el-pagination
        v-if="!productsLoading && !productsError && total > pageSize"
        :current-page="currentPage"
        class="products-pagination"
        background
        layout="prev, pager, next"
        :page-size="pageSize"
        :total="total"
        @current-change="changePage"
      />
    </div>
  </section>
</template>

<style scoped>
.products-page { min-height: 650px; padding: 26px 0 70px; background: #f5f8fb; }
.breadcrumb { display: flex; gap: 10px; color: #8b97a4; font-size: 12px; }
.list-heading { display: flex; align-items: flex-end; justify-content: space-between; margin: 32px 0 25px; }
.list-heading > div > span { color: var(--brand); font-family: Arial, sans-serif; font-size: 10px; letter-spacing: .18em; }
.list-heading h1 { margin-top: 3px; font-size: 31px; }
.list-heading p { margin-top: 6px; color: #7b8998; font-size: 13px; }
.category-filter { display: flex; align-items: center; gap: 8px; margin-bottom: 24px; overflow-x: auto; }
.category-filter a { padding: 7px 18px; border: 1px solid #e0e7ef; border-radius: 20px; color: #64768a; background: #fff; font-size: 12px; white-space: nowrap; }
.category-filter a.active { border-color: var(--brand); color: #fff; background: var(--brand); }
.filter-message, .filter-retry { color: #8b97a4; font-size: 12px; white-space: nowrap; }
.filter-retry { padding: 7px 0; border: 0; background: transparent; }
.filter-retry:hover { color: var(--brand); }
.products-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 20px; }
.products-pagination { justify-content: center; margin-top: 34px; }
@media (max-width: 1000px) { .products-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 767px) { .products-page { padding-top: 18px; } .list-heading { align-items: flex-start; margin: 25px 0 20px; } .list-heading h1 { font-size: 27px; } .list-heading p { font-size: 12px; } .list-heading > .el-tag { display: none; } .products-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; } .products-pagination { margin-top: 26px; } }
</style>
