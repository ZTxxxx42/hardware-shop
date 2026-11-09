<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { catalogApi } from '@/api/catalog'
import { getErrorMessage } from '@/api/http'
import type { Product } from '@/types/catalog'
import ProductCard from '@/components/ProductCard.vue'
import RequestState from '@/components/RequestState.vue'

const route = useRoute()
const router = useRouter()
const pageSize = 8
const products = ref<Product[]>([])
const total = ref(0)
const loading = ref(true)
const error = ref('')
let requestId = 0

function queryText(value: unknown): string {
  return typeof value === 'string' ? value.trim() : ''
}

function positiveInteger(value: unknown): number | undefined {
  if (typeof value !== 'string') return undefined
  const parsed = Number(value)
  return Number.isInteger(parsed) && parsed > 0 ? parsed : undefined
}

const keyword = computed(() => queryText(route.query.keyword))
const currentPage = computed(() => positiveInteger(route.query.page) ?? 1)
const searchInput = ref(keyword.value)
const pageTitle = computed(() => keyword.value ? `“${keyword.value}”的搜索结果` : '全部商品')
const emptyText = computed(() => keyword.value ? `未找到与“${keyword.value}”相关的商品` : '暂无商品')

async function loadProducts() {
  const currentRequestId = ++requestId
  const requestedPage = currentPage.value
  loading.value = true
  error.value = ''
  try {
    const data = await catalogApi.products({
      keyword: keyword.value || undefined,
      page: requestedPage,
      page_size: pageSize,
    })
    if (currentRequestId !== requestId) return

    const lastPage = Math.max(1, Math.ceil(data.total / pageSize))
    if (data.total > 0 && data.items.length === 0 && requestedPage > lastPage) {
      await router.replace({ query: { ...route.query, page: lastPage > 1 ? String(lastPage) : undefined } })
      return
    }
    products.value = data.items
    total.value = data.total
  } catch (requestError) {
    if (currentRequestId !== requestId) return
    products.value = []
    total.value = 0
    error.value = getErrorMessage(requestError, '搜索失败，请稍后重试')
  } finally {
    if (currentRequestId === requestId) loading.value = false
  }
}

function submitSearch() {
  const value = searchInput.value.trim()
  void router.push({ path: '/search', query: value ? { keyword: value } : {} })
}

function changePage(page: number) {
  void router.push({ query: { ...route.query, page: page > 1 ? String(page) : undefined } })
}

watch(keyword, (value) => { searchInput.value = value })
watch([keyword, currentPage], loadProducts, { immediate: true })
</script>

<template>
  <section class="search-page">
    <div class="container">
      <nav class="breadcrumb" aria-label="面包屑"><RouterLink to="/">首页</RouterLink><span>/</span><span>搜索商品</span></nav>
      <div class="search-heading">
        <span>PRODUCT SEARCH</span>
        <h1>搜索商品</h1>
        <p>按商品名称或型号查找所需五金产品</p>
        <form class="page-search" role="search" @submit.prevent="submitSearch">
          <el-icon :size="20"><Search /></el-icon>
          <input v-model="searchInput" type="search" aria-label="搜索商品" placeholder="输入商品名称或型号" />
          <button type="submit">搜索</button>
        </form>
      </div>
      <div class="result-heading"><h2>{{ pageTitle }}</h2><span v-if="!loading && !error">共 {{ total }} 件商品</span></div>
      <RequestState
        v-if="loading || error || products.length === 0"
        :loading="loading"
        :error="error"
        :empty="!loading && !error"
        loading-text="正在搜索商品..."
        :empty-text="emptyText"
        @retry="loadProducts"
      />
      <div v-else class="products-grid"><ProductCard v-for="product in products" :key="product.id" :product="product" /></div>
      <el-pagination
        v-if="!loading && !error && total > pageSize"
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
.search-page { min-height: 650px; padding: 26px 0 70px; background: #f5f8fb; }
.breadcrumb { display: flex; gap: 10px; color: #8b97a4; font-size: 12px; }
.search-heading { margin: 31px 0 30px; text-align: center; }
.search-heading > span { color: var(--brand); font-family: Arial, sans-serif; font-size: 10px; letter-spacing: .18em; }
.search-heading h1 { margin-top: 3px; font-size: 31px; }
.search-heading > p { margin-top: 6px; color: #7b8998; font-size: 13px; }
.page-search { display: flex; align-items: center; width: min(580px, 100%); height: 48px; margin: 23px auto 0; padding-left: 17px; border: 1px solid #dfe7ef; border-radius: 25px; color: #8a9aad; background: #fff; box-shadow: var(--shadow-sm); }
.page-search:focus-within { border-color: #8cb7e9; }
.page-search input { min-width: 0; height: 100%; flex: 1; padding: 0 12px; border: 0; outline: 0; color: var(--ink); background: transparent; font-size: 14px; }
.page-search input::-webkit-search-cancel-button { display: none; }
.page-search button { height: 38px; margin-right: 4px; padding: 0 25px; border: 0; border-radius: 20px; color: #fff; background: var(--brand); font-size: 13px; }
.result-heading { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; padding-bottom: 13px; border-bottom: 1px solid #e3eaf1; }
.result-heading h2 { font-size: 18px; font-weight: 650; }
.result-heading > span { color: #8593a2; font-size: 12px; white-space: nowrap; }
.products-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 20px; }
.products-pagination { justify-content: center; margin-top: 34px; }
@media (max-width: 1000px) { .products-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 767px) { .search-page { padding-top: 18px; } .search-heading { margin: 24px 0 23px; text-align: left; } .search-heading h1 { font-size: 27px; } .search-heading > p { font-size: 12px; } .page-search { height: 44px; margin-top: 18px; } .page-search button { height: 34px; padding-inline: 19px; } .result-heading { align-items: flex-start; gap: 12px; } .result-heading h2 { overflow-wrap: anywhere; font-size: 16px; } .products-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; } .products-pagination { margin-top: 26px; } }
</style>
