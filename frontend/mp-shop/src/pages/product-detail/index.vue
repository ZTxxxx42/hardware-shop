<script setup lang="ts">
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { catalogApi } from '@/api/catalog'
import { getErrorMessage } from '@/api/http'
import type { ProductDetail } from '@/types/catalog'
import { formatPrice, getProductStatus } from '@/utils/catalog'
import { ensureLogin } from '@/utils/auth'
import { useCartStore } from '@/store/cart'
import ProductArtwork from '@/components/ProductArtwork.vue'
import QuantityStepper from '@/components/QuantityStepper.vue'
import RequestState from '@/components/RequestState.vue'

const cartStore = useCartStore()
const product = ref<ProductDetail | null>(null)
const loading = ref(true)
const error = ref('')
const quantity = ref(1)
const adding = ref(false)
let requestId = 0

const hasMemberPrice = computed(() => product.value?.price !== product.value?.retail_price)

async function loadProduct(id: number) {
  const currentRequestId = ++requestId
  product.value = null
  error.value = ''
  loading.value = true
  try {
    const data = await catalogApi.product(id)
    if (currentRequestId !== requestId) return
    product.value = data
  } catch (requestError) {
    if (currentRequestId !== requestId) return
    error.value = getErrorMessage(requestError, '商品详情加载失败，请稍后重试')
  } finally {
    if (currentRequestId === requestId) loading.value = false
  }
}

async function addToCart(goCartAfter: boolean) {
  const current = product.value
  if (!current || current.status !== 'ON_SALE') {
    uni.showToast({ title: '该商品暂不可售', icon: 'none' })
    return
  }
  if (!ensureLogin()) return
  adding.value = true
  try {
    await cartStore.add(current.id, quantity.value)
    uni.showToast({ title: '已加入购物车', icon: 'success' })
    if (goCartAfter) {
      setTimeout(() => uni.switchTab({ url: '/pages/cart/index' }), 500)
    }
  } catch (requestError) {
    uni.showToast({ title: getErrorMessage(requestError, '加入购物车失败'), icon: 'none' })
  } finally {
    adding.value = false
  }
}

function goProducts() {
  uni.navigateTo({ url: '/pages/product/index' })
}

onLoad((options) => {
  const raw = options?.id
  const id = typeof raw === 'string' && raw ? Number(raw) : NaN
  if (Number.isInteger(id) && id > 0) {
    void loadProduct(id)
  } else {
    loading.value = false
    error.value = '商品编号无效，请返回产品中心重新选择'
  }
})
</script>

<template>
  <view class="page-pad">
    <RequestState
      v-if="loading || error || !product"
      :loading="loading"
      :error="error"
      :empty="!loading && !error"
      loading-text="正在加载商品详情..."
      empty-text="商品不存在或已删除"
      @retry="product ? loadProduct(product.id) : goProducts()"
    />

    <template v-else>
      <view class="detail-art card">
        <ProductArtwork :slug="product.main_image" :alt="product.name" />
      </view>

      <view class="detail-card card">
        <view class="detail-card__top">
          <text class="eyebrow">PRODUCT DETAIL</text>
          <text class="status-tag" :class="{ 'is-sale': product.status === 'ON_SALE' }">
            {{ getProductStatus(product.status) }}
          </text>
        </view>

        <view class="detail-card__name">{{ product.name }}</view>
        <view class="detail-card__model">产品型号：{{ product.model || '详询客服' }}</view>
        <view class="detail-card__desc">
          {{ product.description || '暂无商品描述，欢迎联系客服获取详细产品资料。' }}
        </view>

        <view class="price-panel">
          <text class="price-panel__label">当前采购价</text>
          <view class="price-panel__row">
            <text class="price-panel__price"><text class="price-mark">¥</text>{{ formatPrice(product.price) }}</text>
            <text v-if="hasMemberPrice" class="price-panel__retail">零售价 ¥{{ formatPrice(product.retail_price) }}</text>
          </view>
          <text class="price-panel__tip">价格根据当前会员等级实时计算</text>
        </view>

        <view class="quick-specs">
          <view class="quick-specs__item">
            <text class="quick-specs__label">库存数量</text>
            <text class="quick-specs__value">{{ product.stock }} 件</text>
          </view>
          <view class="quick-specs__item">
            <text class="quick-specs__label">商品编号</text>
            <text class="quick-specs__value">{{ product.id }}</text>
          </view>
          <view class="quick-specs__item">
            <text class="quick-specs__label">所属分类</text>
            <text class="quick-specs__value quick-specs__link" @tap="goProducts">查看同类 ›</text>
          </view>
        </view>
      </view>

      <view class="buy-bar card">
        <view class="buy-bar__qty">
          <text class="buy-bar__label">采购数量</text>
          <QuantityStepper v-model="quantity" :min="1" :max="product.stock || 1" :disabled="product.status !== 'ON_SALE'" />
        </view>
        <view class="buy-bar__actions">
          <button class="btn btn-ghost buy-bar__btn" :disabled="adding || product.status !== 'ON_SALE'" @tap="addToCart(false)">加入购物车</button>
          <button class="btn btn-primary buy-bar__btn" :disabled="adding || product.status !== 'ON_SALE'" @tap="addToCart(true)">立即购买</button>
        </view>
      </view>

      <view v-if="product.specs.length" class="spec-card card">
        <view class="spec-card__title">产品参数</view>
        <view v-for="spec in product.specs" :key="spec.id" class="spec-row">
          <text class="spec-row__name">{{ spec.spec_name }}</text>
          <text class="spec-row__value">{{ spec.spec_value }}</text>
        </view>
      </view>
    </template>
  </view>
</template>

<style scoped>
.detail-art { height: 520rpx; padding: 48rpx; background: radial-gradient(circle at 50% 42%, #ffffff 20%, #eef3f8 82%); }
.detail-card { margin-top: 24rpx; padding: 30rpx 28rpx; }
.detail-card__top { display: flex; align-items: center; justify-content: space-between; gap: 16rpx; }
.status-tag { padding: 6rpx 18rpx; border-radius: 10rpx; color: var(--muted); background: var(--surface-deep); font-size: 20rpx; }
.status-tag.is-sale { color: var(--success); background: var(--success-light); }
.detail-card__name { margin-top: 16rpx; font-size: 44rpx; font-weight: 750; line-height: 1.35; }
.detail-card__model { margin-top: 10rpx; color: var(--muted); font-size: 25rpx; }
.detail-card__desc { margin-top: 24rpx; color: var(--ink-soft); font-size: 25rpx; line-height: 1.9; }
.price-panel { margin-top: 28rpx; padding: 24rpx; border-left: 6rpx solid var(--brand); border-radius: 8rpx; background: var(--brand-light); }
.price-panel__label { color: var(--brand-dark); font-size: 22rpx; }
.price-panel__row { display: flex; align-items: baseline; gap: 18rpx; margin-top: 4rpx; }
.price-panel__price { color: var(--price); font-family: Arial, sans-serif; font-size: 52rpx; font-weight: 700; line-height: 1.3; }
.price-panel__retail { color: var(--muted); font-size: 22rpx; text-decoration: line-through; }
.price-panel__tip { display: block; margin-top: 4rpx; color: var(--muted); font-size: 20rpx; }
.quick-specs { display: flex; flex-wrap: wrap; margin-top: 28rpx; }
.quick-specs__item { display: flex; min-width: 0; width: 33.33%; flex-direction: column; gap: 4rpx; margin-bottom: 16rpx; }
.quick-specs__label { color: var(--muted); font-size: 20rpx; }
.quick-specs__value { color: var(--ink-soft); font-size: 24rpx; }
.quick-specs__link { color: var(--brand-dark); }
.buy-bar { margin-top: 24rpx; padding: 28rpx; }
.buy-bar__qty { display: flex; align-items: center; justify-content: space-between; gap: 20rpx; }
.buy-bar__label { color: var(--ink-soft); font-size: 25rpx; }
.buy-bar__actions { display: flex; gap: 20rpx; margin-top: 28rpx; }
.buy-bar__btn { min-height: 88rpx; flex: 1; border-radius: var(--radius-sm); }
.spec-card { margin-top: 24rpx; padding: 28rpx; }
.spec-card__title { font-size: 32rpx; font-weight: 700; }
.spec-row { display: flex; gap: 20rpx; padding: 22rpx 0; border-bottom: 1rpx solid var(--line); font-size: 24rpx; }
.spec-row:last-child { border-bottom: 0; }
.spec-row__name { width: 200rpx; flex: 0 0 auto; color: var(--muted); }
.spec-row__value { color: var(--ink-soft); }
</style>
