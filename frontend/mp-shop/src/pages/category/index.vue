<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { catalogApi } from '@/api/catalog'
import { getErrorMessage } from '@/api/http'
import type { Category } from '@/types/catalog'
import { getCategoryDescription, getCategoryIcon } from '@/utils/catalog'
import CategoryIcon from '@/components/CategoryIcon.vue'
import RequestState from '@/components/RequestState.vue'

const categories = ref<Category[]>([])
const loading = ref(true)
const error = ref('')

async function loadCategories() {
  loading.value = true
  error.value = ''
  try {
    const data = await catalogApi.categories()
    categories.value = [...data].sort((a, b) => a.sort - b.sort || a.id - b.id)
  } catch (requestError) {
    categories.value = []
    error.value = getErrorMessage(requestError, '分类加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

function goCategory(category: Category) {
  uni.navigateTo({ url: `/pages/product/index?category=${category.id}` })
}

onShow(loadCategories)
</script>

<template>
  <view class="page-pad">
    <view class="category-heading">
      <text class="eyebrow">PRODUCT CATEGORIES</text>
      <view class="page-title">产品分类</view>
      <text class="page-subtitle">多品类五金产品，一站式满足采购需求</text>
    </view>

    <RequestState
      v-if="loading || error || categories.length === 0"
      :loading="loading"
      :error="error"
      :empty="!loading && !error"
      loading-text="正在加载产品分类..."
      empty-text="暂无产品分类"
      @retry="loadCategories"
    />
    <view v-else class="category-list">
      <view v-for="category in categories" :key="category.id" class="category-card" @tap="goCategory(category)">
        <view class="category-card__icon">
          <CategoryIcon :name="getCategoryIcon(category)" />
        </view>
        <view class="category-card__body">
          <view class="category-card__name">{{ category.name }}</view>
          <view class="category-card__desc">{{ getCategoryDescription(category) }}</view>
        </view>
        <text class="category-card__arrow">›</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.category-heading { padding: 10rpx 0 26rpx; }
.category-list { display: flex; flex-direction: column; gap: 18rpx; }
.category-card { display: flex; align-items: center; gap: 24rpx; padding: 26rpx 28rpx; border: 1rpx solid var(--line); border-left: 5rpx solid transparent; border-radius: var(--radius-md); background: var(--white); box-shadow: 0 8rpx 26rpx rgb(60 48 32 / 4%); }
.category-card:active { border-color: var(--line-dark); border-left-color: var(--brand); }
.category-card__icon { width: 96rpx; height: 96rpx; flex: 0 0 auto; }
.category-card__body { min-width: 0; flex: 1; }
.category-card__name { color: var(--ink-soft); font-size: 30rpx; font-weight: 650; }
.category-card__desc { margin-top: 6rpx; color: var(--muted); font-size: 22rpx; }
.category-card__arrow { color: var(--line-dark); font-size: 40rpx; line-height: 1; }
</style>
