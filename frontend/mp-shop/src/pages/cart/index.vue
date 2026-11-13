<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useCartStore } from '@/store/cart'
import { getErrorMessage } from '@/api/http'
import { formatPrice, isZeroAmount } from '@/utils/catalog'
import { ensureLogin } from '@/utils/auth'
import type { CartItem } from '@/types/shop'
import ProductArtwork from '@/components/ProductArtwork.vue'
import QuantityStepper from '@/components/QuantityStepper.vue'
import RequestState from '@/components/RequestState.vue'

const cartStore = useCartStore()
const loading = ref(true)
const error = ref('')
const busyItem = ref<number | null>(null)

async function load() {
  if (!ensureLogin('/pages/cart/index')) {
    loading.value = false
    return
  }
  loading.value = true
  error.value = ''
  try {
    await cartStore.load()
  } catch (requestError) {
    error.value = getErrorMessage(requestError, '购物车加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

function goDetail(item: CartItem) {
  uni.navigateTo({ url: `/pages/product-detail/index?id=${item.product_id}` })
}

async function changeQuantity(item: CartItem, value: number) {
  if (value < 1 || value === item.quantity) return
  busyItem.value = item.id
  try {
    await cartStore.updateQuantity(item.id, value)
  } catch (requestError) {
    uni.showToast({ title: getErrorMessage(requestError, '修改数量失败'), icon: 'none' })
  } finally {
    busyItem.value = null
  }
}

async function removeItem(item: CartItem) {
  const confirm = await new Promise<boolean>((resolve) => {
    uni.showModal({
      title: '移出商品',
      content: `确定将“${item.name}”移出购物车吗？`,
      confirmText: '移出',
      cancelText: '取消',
      success: (res) => resolve(res.confirm),
      fail: () => resolve(false),
    })
  })
  if (!confirm) return
  busyItem.value = item.id
  try {
    await cartStore.remove(item.id)
    uni.showToast({ title: '已移出购物车', icon: 'success' })
  } catch (requestError) {
    uni.showToast({ title: getErrorMessage(requestError, '删除失败'), icon: 'none' })
  } finally {
    busyItem.value = null
  }
}

function goCheckout() {
  if (cartStore.items.length === 0) return
  uni.navigateTo({ url: '/pages/checkout/index' })
}

function goProducts() {
  uni.switchTab({ url: '/pages/index/index' })
}

onShow(load)
</script>

<template>
  <view class="cart-page">
    <view class="page-pad cart-page__body">
      <RequestState
        v-if="loading || error"
        :loading="loading"
        :error="error"
        loading-text="正在加载购物车..."
        @retry="load"
      />
      <view v-else-if="cartStore.items.length === 0" class="empty-cart">
        <view class="empty-cart__mark">空</view>
        <text class="empty-cart__text">购物车还是空的，去挑选需要的五金商品吧</text>
        <button class="btn btn-primary empty-cart__btn" @tap="goProducts">去选购商品</button>
      </view>
      <view v-else class="cart-list">
        <view v-for="item in cartStore.items" :key="item.id" class="cart-line card">
          <view class="cart-line__art" @tap="goDetail(item)">
            <ProductArtwork :slug="item.main_image" :alt="item.name" />
          </view>
          <view class="cart-line__info">
            <view class="cart-line__name" @tap="goDetail(item)">{{ item.name }}</view>
            <view class="cart-line__model">规格：{{ item.model || '详询客服' }}</view>
            <view class="cart-line__price"><text class="price-mark">¥</text>{{ formatPrice(item.price) }}</view>
          </view>
          <view class="cart-line__tools">
            <QuantityStepper
              :model-value="item.quantity"
              :min="1"
              :max="999"
              :disabled="busyItem === item.id"
              @update:model-value="(value: number) => changeQuantity(item, value)"
            />
            <view class="cart-line__foot">
              <text class="cart-line__subtotal">小计 ¥{{ formatPrice(item.subtotal) }}</text>
              <text class="cart-line__remove" @tap="removeItem(item)">删除</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view v-if="!loading && !error && cartStore.items.length > 0" class="cart-bar">
      <view class="cart-bar__summary">
        <view class="cart-bar__total">
          <text class="cart-bar__total-label">合计</text>
          <text class="cart-bar__total-price"><text class="price-mark">¥</text>{{ formatPrice(cartStore.totalAmount) }}</text>
        </view>
        <text class="cart-bar__detail">
          商品 ¥{{ formatPrice(cartStore.productAmount) }} · 运费 {{ isZeroAmount(cartStore.freightAmount) ? '免运费' : `¥${formatPrice(cartStore.freightAmount)}` }}
        </text>
      </view>
      <button class="btn btn-primary cart-bar__btn" @tap="goCheckout">去结算</button>
    </view>
  </view>
</template>

<style scoped>
.cart-page {
  min-height: 100vh;
  padding-bottom: 200rpx;
}

.cart-page__body {
  padding-bottom: 40rpx;
}

.empty-cart {
  display: flex;
  min-height: 560rpx;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20rpx;
}

.empty-cart__mark {
  display: flex;
  width: 110rpx;
  height: 110rpx;
  align-items: center; justify-content: center;
  border-radius: 32rpx;
  color: var(--brand);
  background: var(--brand-light);
  font-size: 48rpx;
  font-weight: 700;
}

.empty-cart__text {
  color: #7b8998;
  font-size: 25rpx;
}

.empty-cart__btn {
  min-height: 76rpx;
  margin-top: 10rpx;
  padding: 0 44rpx;
}

.cart-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.cart-line {
  display: flex;
  flex-wrap: wrap;
  padding: 22rpx;
}

.cart-line__art {
  display: flex;
  width: 180rpx;
  height: 160rpx;
  flex: 0 0 auto;
  align-items: center; justify-content: center;
  overflow: hidden;
  border-radius: 16rpx;
  background: radial-gradient(circle at 50% 42%, #ffffff 20%, #f0f4f8 80%);
}

.cart-line__info {
  display: flex;
  min-width: 0;
  width: calc(100% - 202rpx);
  flex-direction: column;
  padding-left: 22rpx;
}

.cart-line__name {
  overflow: hidden;
  color: #26384c;
  font-size: 27rpx;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cart-line__model {
  margin-top: 8rpx;
  color: #8a97a5;
  font-size: 21rpx;
}

.cart-line__price {
  margin-top: 10rpx;
  color: var(--price);
  font-family: Arial, sans-serif;
  font-size: 30rpx;
  font-weight: 700;
}

.cart-line__tools {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  margin-top: 20rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #f0f3f7;
}

.cart-line__foot {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8rpx;
}

.cart-line__subtotal {
  color: var(--price);
  font-family: Arial, sans-serif;
  font-size: 26rpx;
  font-weight: 600;
}

.cart-line__remove {
  color: #95a2af;
  font-size: 22rpx;
}

.cart-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 20rpx 24rpx calc(20rpx + env(safe-area-inset-bottom));
  background: #ffffff;
  box-shadow: 0 -8rpx 26rpx rgb(30 64 97 / 8%);
}

.cart-bar__summary {
  min-width: 0;
  flex: 1;
}

.cart-bar__total {
  display: flex;
  align-items: baseline;
  gap: 12rpx;
}

.cart-bar__total-label {
  color: #3c4e61;
  font-size: 26rpx;
  font-weight: 600;
}

.cart-bar__total-price {
  color: var(--price);
  font-family: Arial, sans-serif;
  font-size: 42rpx;
  font-weight: 700;
}

.cart-bar__detail {
  display: block;
  margin-top: 2rpx;
  color: #a0abb7;
  font-size: 20rpx;
}

.cart-bar__btn {
  min-height: 84rpx;
  padding: 0 52rpx;
  border-radius: 42rpx;
}
</style>
