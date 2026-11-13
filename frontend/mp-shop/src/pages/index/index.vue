<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { catalogApi } from '@/api/catalog'
import { getErrorMessage } from '@/api/http'
import type { Category, Product } from '@/types/catalog'
import { getCategoryIcon } from '@/utils/catalog'
import CategoryIcon from '@/components/CategoryIcon.vue'
import ProductCard from '@/components/ProductCard.vue'

const categories = ref<Category[]>([])
const products = ref<Product[]>([])
const categoriesLoading = ref(true)
const productsLoading = ref(true)
const categoriesError = ref('')
const productsError = ref('')

const advantages = [
  { title: '品质保障', subtitle: '严格质检' },
  { title: '现货充足', subtitle: '多仓储备' },
  { title: '专业服务', subtitle: '售后无忧' },
]

async function loadHome() {
  categoriesError.value = ''
  productsError.value = ''
  const [categoryResult, productResult] = await Promise.allSettled([
    catalogApi.categories(),
    catalogApi.products({ page: 1, page_size: 4 }),
  ])

  if (categoryResult.status === 'fulfilled') {
    categories.value = [...categoryResult.value].sort((a, b) => a.sort - b.sort || a.id - b.id)
  } else {
    categories.value = []
    categoriesError.value = getErrorMessage(categoryResult.reason, '分类加载失败')
  }
  categoriesLoading.value = false

  if (productResult.status === 'fulfilled') {
    products.value = productResult.value.items
  } else {
    products.value = []
    productsError.value = getErrorMessage(productResult.reason, '热销商品加载失败')
  }
  productsLoading.value = false
}

function goSearch() {
  uni.navigateTo({ url: '/pages/search/index' })
}

function goProducts() {
  uni.navigateTo({ url: '/pages/product/index' })
}

function goAllCategories() {
  uni.switchTab({ url: '/pages/category/index' })
}

function goCategory(id: number) {
  uni.navigateTo({ url: `/pages/product/index?category=${id}` })
}

onShow(loadHome)
</script>

<template>
  <view class="home">
    <view class="hero">
      <view class="hero__rail" />
      <view class="hero__content">
        <text class="hero__eyebrow">HENGTAI / INDUSTRIAL SUPPLY</text>
        <view class="hero__title">五金采购<text class="hero__accent">一站配齐</text></view>
        <text class="hero__subtitle">紧固件 · 电动工具 · 五金配件，按需选型</text>
        <view class="hero__meta">
          <view class="hero__meta-item"><text class="hero__meta-value">按级</text><text class="hero__meta-label">价格实时计算</text></view>
          <view class="hero__meta-item"><text class="hero__meta-value">可查</text><text class="hero__meta-label">订单进度追踪</text></view>
          <view class="hero__meta-item"><text class="hero__meta-value">可靠</text><text class="hero__meta-label">现货快速发货</text></view>
        </view>
        <view class="hero__cta" @tap="goProducts">进入产品中心</view>
      </view>
    </view>

    <view class="page-pad home__body">
      <view class="search-pill" @tap="goSearch">
        <text class="search-pill__icon">⌕</text>
        <text class="search-pill__placeholder">搜索商品名称或型号</text>
      </view>

      <view class="section-card">
        <view class="section-heading">
          <view class="section-heading__title">产品分类</view>
          <view class="section-heading__more" @tap="goAllCategories">全部分类 ›</view>
        </view>
        <view v-if="categoriesLoading" class="home__note"><view class="home__loading" />正在加载分类...</view>
        <view v-else-if="categoriesError" class="home__note" @tap="loadHome">{{ categoriesError }}，点击重试</view>
        <view v-else-if="categories.length === 0" class="home__note">暂无产品分类</view>
        <view v-else class="category-grid">
          <view v-for="category in categories.slice(0, 6)" :key="category.id" class="category-item" @tap="goCategory(category.id)">
            <view class="category-item__icon">
              <CategoryIcon :name="getCategoryIcon(category)" />
            </view>
            <text class="category-item__name">{{ category.name }}</text>
          </view>
        </view>
      </view>

      <view class="section-card">
        <view class="section-heading">
          <view class="section-heading__title">热销推荐</view>
          <view class="section-heading__more" @tap="goProducts">查看更多 ›</view>
        </view>
        <view v-if="productsLoading" class="home__note"><view class="home__loading" />正在加载热销商品...</view>
        <view v-else-if="productsError" class="home__note" @tap="loadHome">{{ productsError }}，点击重试</view>
        <view v-else-if="products.length === 0" class="home__note">暂无热销商品</view>
        <view v-else class="products-grid">
          <view v-for="product in products" :key="product.id" class="products-grid__cell">
            <ProductCard :product="product" />
          </view>
        </view>
      </view>

      <view class="advantage-card">
        <view v-for="advantage in advantages" :key="advantage.title" class="advantage-item">
          <text class="advantage-item__title">{{ advantage.title }}</text>
          <text class="advantage-item__subtitle">{{ advantage.subtitle }}</text>
        </view>
      </view>

      <view class="brand-footer">
        <image class="brand-footer__logo" src="/static/brand/logo.svg" mode="aspectFit" />
        <text class="brand-footer__name">恒泰五金 · 工业供应</text>
        <text class="brand-footer__slogan">品质可查 · 采购可追踪</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.home { min-height: 100vh; }
.hero { position: relative; padding: 44rpx 36rpx 76rpx; overflow: hidden; background: var(--brand-deep); color: var(--white); }
.hero__rail { position: absolute; top: 0; left: 0; bottom: 0; width: 10rpx; background: var(--brand); }
.hero__content { position: relative; }
.hero__eyebrow { display: block; color: #d6d1c7; font-family: Arial, sans-serif; font-size: 20rpx; letter-spacing: 0.16em; }
.hero__title { margin-top: 20rpx; font-size: 58rpx; font-weight: 800; line-height: 1.2; letter-spacing: 0.03em; }
.hero__accent { color: var(--brand); }
.hero__subtitle { display: block; margin-top: 18rpx; color: #d6d1c7; font-size: 25rpx; }
.hero__meta { display: flex; gap: 30rpx; margin-top: 34rpx; padding: 22rpx 0; border-top: 1rpx solid #494a44; border-bottom: 1rpx solid #494a44; }
.hero__meta-item { display: flex; flex-direction: column; gap: 4rpx; }
.hero__meta-value { color: var(--white); font-size: 27rpx; font-weight: 700; }
.hero__meta-label { color: #a8a49a; font-size: 19rpx; }
.hero__cta { display: inline-flex; align-items: center; min-height: 68rpx; margin-top: 34rpx; padding: 0 34rpx; color: var(--white); background: var(--brand); font-size: 26rpx; font-weight: 600; }
.home__body { padding-top: 0; }
.search-pill { display: flex; align-items: center; gap: 14rpx; height: 88rpx; margin-top: -44rpx; padding: 0 30rpx; border: 1rpx solid var(--line); border-radius: 44rpx; background: var(--white); box-shadow: 0 14rpx 34rpx rgb(60 48 32 / 12%); }
.search-pill__icon { color: var(--brand); font-size: 40rpx; }
.search-pill__placeholder { color: var(--placeholder); font-size: 26rpx; }
.category-grid { display: flex; flex-wrap: wrap; }
.category-item { display: flex; min-width: 0; width: 33.33%; flex-direction: column; align-items: center; margin-bottom: 24rpx; gap: 10rpx; }
.category-item__icon { width: 104rpx; height: 104rpx; }
.category-item__name { color: var(--ink-soft); font-size: 24rpx; font-weight: 600; white-space: nowrap; }
.products-grid { display: flex; flex-wrap: wrap; justify-content: space-between; }
.products-grid__cell { width: calc(50% - 10rpx); margin-bottom: 20rpx; }
.home__note { display: flex; align-items: center; justify-content: center; gap: 14rpx; padding: 24rpx 0; color: var(--muted); font-size: 24rpx; text-align: center; }
.home__loading { width: 30rpx; height: 30rpx; border: 4rpx solid var(--surface-deep); border-top-color: var(--brand); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.advantage-card { display: flex; margin-top: 24rpx; padding: 30rpx 12rpx; border-top: 1rpx solid var(--line); border-bottom: 1rpx solid var(--line); background: var(--surface-deep); }
.advantage-item { display: flex; width: 33.33%; flex-direction: column; align-items: center; gap: 4rpx; }
.advantage-item + .advantage-item { border-left: 1rpx solid var(--line-dark); }
.advantage-item__title { color: var(--ink-soft); font-size: 27rpx; font-weight: 650; }
.advantage-item__subtitle { color: var(--muted); font-size: 21rpx; }
.brand-footer { display: flex; flex-direction: column; align-items: center; gap: 8rpx; margin-top: 40rpx; padding: 40rpx 0 20rpx; color: var(--muted); }
.brand-footer__logo { width: 96rpx; height: 96rpx; }
.brand-footer__name { margin-top: 10rpx; font-size: 26rpx; font-weight: 600; }
.brand-footer__slogan { font-size: 22rpx; letter-spacing: 0.08em; }
</style>
