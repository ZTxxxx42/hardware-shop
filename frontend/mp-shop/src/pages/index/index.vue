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

  if (productResult.status === 'fulfilled') {
    products.value = productResult.value.items
  } else {
    products.value = []
    productsError.value = getErrorMessage(productResult.reason, '热销商品加载失败')
  }
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
      <image class="hero__bg" src="/static/scenes/hero-industrial.svg" mode="aspectFill" />
      <view class="hero__shade" />
      <view class="hero__content">
        <view class="hero__eyebrow">
          <view class="hero__line" />
          <text>专业 · 品质 · 共赢</text>
          <view class="hero__line" />
        </view>
        <view class="hero__title">一站式<text class="hero__accent">五金</text>商贸平台</view>
        <view class="hero__subtitle">优质五金产品 · 可靠品质保障</view>
        <view class="hero__cta" @tap="goProducts">立即选购</view>
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
        <view v-if="categoriesError" class="home__note" @tap="loadHome">{{ categoriesError }}，点击重试</view>
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
        <view v-if="productsError" class="home__note" @tap="loadHome">{{ productsError }}，点击重试</view>
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
        <text class="brand-footer__slogan">专业 · 品质 · 共赢</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.hero {
  position: relative;
  height: 420rpx;
  overflow: hidden;
  background: #0c56ad;
}

.hero__bg {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.hero__shade {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  background: linear-gradient(160deg, rgb(6 45 86 / 88%) 0%, rgb(12 86 173 / 76%) 55%, rgb(26 111 214 / 46%) 100%);
}

.hero__content {
  position: relative;
  z-index: 1;
  display: flex;
  height: 100%;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  padding: 0 40rpx 20rpx;
  color: #ffffff;
}

.hero__eyebrow {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 18rpx;
  font-size: 24rpx;
  font-weight: 600;
  letter-spacing: 0.16em;
}

.hero__line {
  width: 40rpx;
  height: 2rpx;
  background: #b9d8f1;
}

.hero__title {
  font-size: 56rpx;
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: 0.02em;
}

.hero__accent {
  color: #38a9f5;
}

.hero__subtitle {
  margin-top: 18rpx;
  color: #eef6fc;
  font-size: 26rpx;
  letter-spacing: 0.04em;
}

.hero__cta {
  display: inline-flex;
  align-items: center;
  min-height: 64rpx;
  margin-top: 30rpx;
  padding: 0 36rpx;
  border: 1rpx solid rgb(255 255 255 / 30%);
  border-radius: 32rpx;
  color: #ffffff;
  background: linear-gradient(110deg, #278de4, #0865c5);
  box-shadow: 0 10rpx 22rpx rgb(0 56 123 / 26%);
  font-size: 26rpx;
  font-weight: 600;
}

.home__body {
  padding-top: 0;
}

.search-pill {
  display: flex;
  align-items: center;
  gap: 14rpx;
  height: 88rpx;
  margin-top: -44rpx;
  padding: 0 30rpx;
  border-radius: 44rpx;
  background: #ffffff;
  box-shadow: 0 14rpx 34rpx rgb(27 91 149 / 14%);
}

.search-pill__icon {
  color: var(--brand);
  font-size: 40rpx;
}

.search-pill__placeholder {
  color: #9aa6b2;
  font-size: 26rpx;
}

.category-grid {
  display: flex;
  flex-wrap: wrap;
}

.category-item {
  display: flex;
  min-width: 0;
  width: 33.33%;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24rpx;
  gap: 10rpx;
}

.category-item__icon {
  width: 104rpx;
  height: 104rpx;
}

.category-item__name {
  color: #263646;
  font-size: 24rpx;
  font-weight: 600;
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

.home__note {
  padding: 24rpx 0;
  color: #8b97a4;
  font-size: 24rpx;
  text-align: center;
}

.advantage-card {
  display: flex;
  margin-top: 24rpx;
  padding: 30rpx 12rpx;
  border-radius: 20rpx;
  background: #eaf2fc;
}

.advantage-item {
  display: flex;
  width: 33.33%;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
}

.advantage-item + .advantage-item {
  border-left: 1rpx solid #d5e0eb;
}

.advantage-item__title {
  color: #243547;
  font-size: 27rpx;
  font-weight: 650;
}

.advantage-item__subtitle {
  color: #7b8999;
  font-size: 21rpx;
}

.brand-footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  margin-top: 40rpx;
  padding: 40rpx 0 20rpx;
  color: #7b8998;
}

.brand-footer__logo {
  width: 96rpx;
  height: 96rpx;
}

.brand-footer__name {
  margin-top: 10rpx;
  font-size: 26rpx;
  font-weight: 600;
}

.brand-footer__slogan {
  font-size: 22rpx;
  letter-spacing: 0.08em;
}
</style>
