<script setup lang="ts">
import { computed, ref } from 'vue'
import { onLoad, onReachBottom } from '@dcloudio/uni-app'
import { catalogApi } from '@/api/catalog'
import { getErrorMessage } from '@/api/http'
import type { Product } from '@/types/catalog'
import ProductCard from '@/components/ProductCard.vue'
import RequestState from '@/components/RequestState.vue'

const pageSize = 10
const keyword = ref('')
const products = ref<Product[]>([])
const total = ref(0)
const page = ref(1)
const loading = ref(true)
const error = ref('')
const finished = ref(false)
let requestId = 0

const pageTitle = computed(() => (keyword.value ? `“${keyword.value}”的搜索结果` : '全部商品'))
const emptyText = computed(() => (keyword.value ? `未找到与“${keyword.value}”相关的商品` : '暂无商品'))

function query(): { keyword?: string; page: number; page_size: number } {
  return { keyword: keyword.value || undefined, page: page.value, page_size: pageSize }
}

async function resetAndLoad() {
  const id = ++requestId
  page.value = 1
  products.value = []
  finished.value = false
  loading.value = true
  error.value = ''
  try {
    const data = await catalogApi.products(query())
    if (id !== requestId) return
    products.value = data.items
    total.value = data.total
    finished.value = data.items.length >= data.total
  } catch (requestError) {
    if (id !== requestId) return
    products.value = []
    total.value = 0
    error.value = getErrorMessage(requestError, '搜索失败，请稍后重试')
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
    const data = await catalogApi.products(query())
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

function submitSearch() {
  void resetAndLoad()
}

onLoad((options) => {
  const raw = options?.keyword
  keyword.value = typeof raw === 'string' ? raw.trim() : ''
  void resetAndLoad()
})

onReachBottom(() => {
  void loadMore()
})
</script>

<template>
  <view class="search-page">
    <view class="search-bar">
      <view class="search-bar__box">
        <text class="search-bar__icon">⌕</text>
        <input
          v-model="keyword"
          class="search-bar__input"
          type="text"
          confirm-type="search"
          placeholder="输入商品名称或型号"
          placeholder-class="search-bar__placeholder"
          @confirm="submitSearch"
        />
      </view>
      <view class="search-bar__submit" @tap="submitSearch">搜索</view>
    </view>

    <view class="page-pad search-page__body">
      <view class="result-heading">
        <text class="result-heading__title">{{ pageTitle }}</text>
        <text v-if="!loading && !error" class="result-heading__count">共 {{ total }} 件</text>
      </view>

      <RequestState
        v-if="loading || error || products.length === 0"
        :loading="loading"
        :error="error"
        :empty="!loading && !error"
        loading-text="正在搜索商品..."
        :empty-text="emptyText"
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
  </view>
</template>

<style scoped>
.search-page {
  display: flex;
  min-height: 100vh;
  flex-direction: column;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 18rpx;
  padding: 20rpx 24rpx;
  background: #ffffff;
  box-shadow: 0 6rpx 20rpx rgb(33 69 103 / 5%);
}

.search-bar__box {
  display: flex;
  align-items: center;
  gap: 12rpx;
  min-width: 0;
  height: 76rpx;
  flex: 1;
  padding: 0 26rpx;
  border-radius: 38rpx;
  background: #f2f6fa;
}

.search-bar__icon {
  color: #8a9aad;
  font-size: 36rpx;
}

.search-bar__input {
  min-width: 0;
  height: 100%;
  flex: 1;
  font-size: 26rpx;
}

.search-bar__placeholder {
  color: #9aa6b2;
}

.search-bar__submit {
  color: var(--brand);
  font-size: 28rpx;
  font-weight: 600;
}

.search-page__body {
  padding-top: 24rpx;
}

.result-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 22rpx;
}

.result-heading__title {
  overflow: hidden;
  color: #26384c;
  font-size: 30rpx;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-heading__count {
  color: #8593a2;
  font-size: 22rpx;
  white-space: nowrap;
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
