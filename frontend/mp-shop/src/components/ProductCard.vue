<script setup lang="ts">
import type { Product } from '@/types/catalog'
import { formatPrice } from '@/utils/catalog'
import { getErrorMessage } from '@/api/http'
import { ensureLogin } from '@/utils/auth'
import { useCartStore } from '@/store/cart'
import ProductArtwork from './ProductArtwork.vue'

const props = defineProps<{ product: Product }>()

const cartStore = useCartStore()

function goDetail() {
  uni.navigateTo({ url: `/pages/product-detail/index?id=${props.product.id}` })
}

async function addToCart() {
  if (props.product.status !== 'ON_SALE') {
    uni.showToast({ title: '该商品暂不可售', icon: 'none' })
    return
  }
  if (!ensureLogin()) return
  try {
    await cartStore.add(props.product.id, 1)
    uni.showToast({ title: '已加入购物车', icon: 'success' })
  } catch (error) {
    uni.showToast({ title: getErrorMessage(error, '加入购物车失败'), icon: 'none' })
  }
}
</script>

<template>
  <view class="product-card">
    <view class="product-card__art" @tap="goDetail">
      <ProductArtwork :slug="product.main_image" :alt="product.name" />
      <view v-if="product.status !== 'ON_SALE'" class="product-card__tag">暂不可售</view>
    </view>
    <view class="product-card__info">
      <view class="product-card__name" @tap="goDetail">{{ product.name }}</view>
      <view class="product-card__model">规格：{{ product.model || '详询客服' }}</view>
      <view class="product-card__foot">
        <view class="product-card__price">
          <text class="price-mark">¥</text>{{ formatPrice(product.price) }}
        </view>
        <view
          class="product-card__cart"
          :class="{ 'is-disabled': product.status !== 'ON_SALE' }"
          @tap="addToCart"
        >＋</view>
      </view>
    </view>
  </view>
</template>

<style scoped>
.product-card {
  display: flex;
  min-width: 0;
  flex-direction: column;
  overflow: hidden;
  border: 1rpx solid var(--line);
  border-radius: var(--radius-md);
  background: var(--white);
  box-shadow: 0 8rpx 26rpx rgb(60 48 32 / 5%);
}

.product-card__art {
  position: relative;
  height: 300rpx;
  padding: 28rpx 20rpx 8rpx;
  background: radial-gradient(circle at 50% 44%, #fffdf8 20%, #f2ede2 78%);
}

.product-card__tag {
  position: absolute;
  top: 20rpx;
  left: 0;
  padding: 6rpx 18rpx 6rpx 14rpx;
  border-radius: 0 10rpx 10rpx 0;
  color: #ffffff;
  background: var(--brand);
  font-size: 20rpx;
  letter-spacing: 0.06em;
}

.product-card__info {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
  padding: 20rpx 24rpx 24rpx;
}

.product-card__name {
  overflow: hidden;
  color: var(--ink-soft);
  font-size: 27rpx;
  font-weight: 650;
  line-height: 1.45;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-card__model {
  margin-top: 6rpx;
  overflow: hidden;
  color: var(--muted);
  font-size: 21rpx;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-card__foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12rpx;
  margin-top: 18rpx;
}

.product-card__price {
  min-width: 0;
  color: var(--price);
  font-family: Arial, sans-serif;
  font-size: 32rpx;
  font-weight: 700;
  line-height: 1;
}

.product-card__price .price-mark {
  margin-right: 4rpx;
  font-size: 22rpx;
}

.product-card__cart {
  display: flex;
  width: 56rpx;
  height: 56rpx;
  flex: 0 0 auto;
  align-items: center; justify-content: center;
  border-radius: 50%;
  color: var(--white);
  background: var(--brand);
  font-size: 34rpx;
  line-height: 1;
  box-shadow: 0 8rpx 18rpx rgb(154 60 22 / 22%);
}

.product-card__cart:active {
  filter: brightness(1.08);
}

.product-card__cart.is-disabled {
  color: #b7b2a7;
  background: var(--surface-deep);
  box-shadow: none;
}
</style>
