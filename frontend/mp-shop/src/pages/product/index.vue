<script setup lang="ts">
import { ref } from 'vue'
import { onLoad, onReachBottom } from '@dcloudio/uni-app'
import { catalogApi } from '@/api/catalog'
import { getErrorMessage } from '@/api/http'
import type { Category, Product } from '@/types/catalog'
import { getCategoryDescription } from '@/utils/catalog'
import ProductCard from '@/components/ProductCard.vue'
import RequestState from '@/components/RequestState.vue'

const pageSize = 10
const categories = ref<Category[]>([])
const products = ref<Product[]>([])
const activeCategoryId = ref<number | null>(null)
const activeCategory = ref<Category | null>(null)
const page = ref(1)
const total = ref(0)
const loading = ref(true)
const error = ref('')
const finished = ref(false)
let requestId = 0

function categoryQuery(): { category_id?: number; page: number; page_size: number } {
  return {
    category_id: activeCategoryId.value ?? undefined,
    page: page.value,
    page_size: pageSize,
  }
}

async function loadCategories() {
  try {
    const data = await catalogApi.categories()
    categories.value = [...data].sort((a, b) => a.sort - b.sort || a.id - b.id)
  } catch {
    // 分类筛选失败不阻塞商品列表
  }
}

function refreshActiveCategory() {
  activeCategory.value = categories.value.find((item) => item.id === activeCategoryId.value) ?? null
}

async function resetAndLoad() {
  const id = ++requestId
  page.value = 1
  products.value = []
  finished.value = false
  loading.value = true
  error.value = ''
  refreshActiveCategory()
  try {
    const data = await catalogApi.products(categoryQuery())
    if (id !== requestId) return
    products.value = data.items
    total.value = data.total
    finished.value = data.items.length >= data.total
  } catch (requestError) {
    if (id !== requestId) return
    products.value = []
    total.value = 0
    error.value = getErrorMessage(requestError, '商品加载失败，请稍后重试')
  } finally {
    if (id === requestId) loading.value = false
  }
}

async function loadMore() {
  if (loading.value || finished.value || error.value) return
  const id = requestId
  page.value += 1
  loading.value = true
  try {
    const data = await catalogApi.products(categoryQuery())
    if (id !== requestId) return
    products.value = [...products.value, ...data.items]
    total.value = data.total
    finished.value = products.value.length >= data.total
  } catch (requestError) {
    if (id !== requestId) return
    error.value = getErrorMessage(requestError, '加载更多失败')
  } finally {
    if (id === requestId) loading.value = false
  }
}

function selectCategory(id: number | null) {
  if (activeCategoryId.value === id) return
  activeCategoryId.value = id
  void resetAndLoad()
}

onLoad((options) => {
  const raw = options?.category
  const parsed = typeof raw === 'string' && raw ? Number(raw) : NaN
  activeCategoryId.value = Number.isInteger(parsed) && parsed > 0 ? parsed : null
  void loadCategories()
  void resetAndLoad()
})

onReachBottom(() => {
  void loadMore()
})
</script>

<template>
  <view class="page-pad">
    <view class="list-heading">
      <text class="eyebrow">QUALITY HARDWARE</text>
      <view class="page-title">{{ activeCategory?.name ?? '产品中心' }}</view>
      <text class="page-subtitle">
        {{ activeCategory ? getCategoryDescription(activeCategory) : '精选工业五金，规格齐全，支持批量采购' }}
      </text>
      <text class="list-heading__count">共 {{ total }} 件商品</text>
    </view>

    <scroll-view class="chips" scroll-x :show-scrollbar="false">
      <view class="chips__row">
        <view class="chip" :class="{ 'is-active': activeCategoryId === null }" @tap="selectCategory(null)">全部产品</view>
        <view
          v-for="category in categories"
          :key="category.id"
          class="chip"
          :class="{ 'is-active': activeCategoryId === category.id }"
          @tap="selectCategory(category.id)"
        >{{ category.name }}</view>
      </view>
    </scroll-view>

    <RequestState
      v-if="loading || error || products.length === 0"
      :loading="loading"
      :error="error"
      :empty="!loading && !error"
      loading-text="正在加载商品..."
      :empty-text="activeCategory ? '该分类暂无商品' : '暂无商品'"
      @retry="resetAndLoad"
    />
    <view v-else class="products-grid">
      <view v-for="product in products" :key="product.id" class="products-grid__cell">
        <ProductCard :product="product" />
      </view>
    </view>

    <view v-if="!loading && !error && products.length > 0" class="load-more">
      {{ finished ? '已加载全部商品' : '上拉加载更多' }}
    </view>
  </view>
</template>

<style scoped>
.list-heading {
  padding: 10rpx 0 22rpx;
}

.list-heading__count {
  display: inline-block;
  margin-top: 10rpx;
  color: #8593a2;
  font-size: 22rpx;
}

.chips {
  width: 100%;
  margin-bottom: 24rpx;
  white-space: nowrap;
}

.chips__row {
  display: inline-flex;
  gap: 14rpx;
  padding-right: 24rpx;
}

.chip {
  display: inline-flex;
  align-items: center;
  min-height: 64rpx;
  padding: 0 30rpx;
  border: 1rpx solid #e0e7ef;
  border-radius: 32rpx;
  color: #64768a;
  background: #ffffff;
  font-size: 24rpx;
  white-space: nowrap;
}

.chip.is-active {
  border-color: var(--brand);
  color: #ffffff;
  background: var(--brand);
}

.products-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
}

.products-grid__cell {
  width: calc(50% - 10rpx);
  margin-bottom: 20rpx;
}

.load-more {
  padding: 30rpx 0 10rpx;
  color: #a0abb7;
  font-size: 22rpx;
  text-align: center;
}
</style>
