<script setup lang="ts">
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { orderApi } from '@/api/order'
import { memberApi } from '@/api/member'
import { getErrorMessage } from '@/api/http'
import { useCartStore } from '@/store/cart'
import { formatPrice, isZeroAmount } from '@/utils/catalog'
import { ensureLogin } from '@/utils/auth'
import type { Address } from '@/types/shop'
import ProductArtwork from '@/components/ProductArtwork.vue'
import RequestState from '@/components/RequestState.vue'
import LoginPrompt from '@/components/LoginPrompt.vue'

const cartStore = useCartStore()
const addresses = ref<Address[]>([])
const addressesLoading = ref(true)
const addressesError = ref('')
const cartLoading = ref(true)
const cartError = ref('')
const selectedAddressId = ref<number | null>(null)
const remark = ref('')
const submitting = ref(false)
const needsLogin = ref(false)

const selectedAddress = computed(() => addresses.value.find((item) => item.id === selectedAddressId.value) ?? null)

async function loadCart() {
  cartLoading.value = true
  cartError.value = ''
  try {
    await cartStore.load()
  } catch (requestError) {
    cartError.value = getErrorMessage(requestError, '购物车加载失败，请稍后重试')
  } finally {
    cartLoading.value = false
  }
}

async function loadAddresses() {
  addressesLoading.value = true
  addressesError.value = ''
  try {
    addresses.value = await memberApi.addresses()
    if (!selectedAddressId.value && addresses.value.length > 0) {
      selectedAddressId.value = addresses.value[0].id
    }
  } catch (requestError) {
    addressesError.value = getErrorMessage(requestError, '收货地址加载失败，请稍后重试')
  } finally {
    addressesLoading.value = false
  }
}

function goAddresses() {
  uni.navigateTo({ url: '/pages/address/index' })
}

function goCart() {
  uni.switchTab({ url: '/pages/cart/index' })
}

async function submitOrder() {
  if (!selectedAddressId.value) {
    uni.showToast({ title: '请先选择收货地址', icon: 'none' })
    return
  }
  submitting.value = true
  try {
    await orderApi.create({ address_id: selectedAddressId.value, remark: remark.value.trim() || undefined })
    cartStore.clear()
    uni.showToast({ title: '订单已创建', icon: 'success' })
    setTimeout(() => uni.redirectTo({ url: '/pages/orders/index' }), 600)
  } catch (requestError) {
    uni.showToast({ title: getErrorMessage(requestError, '下单失败，请稍后重试'), icon: 'none' })
  } finally {
    submitting.value = false
  }
}

onShow(() => {
  if (!ensureLogin()) {
    needsLogin.value = true
    cartLoading.value = false
    cartError.value = ''
    return
  }
  needsLogin.value = false
  void loadCart()
  void loadAddresses()
})
</script>

<template>
  <view class="page-pad checkout-page">
    <view class="page-heading">
      <text class="eyebrow">CHECKOUT</text>
      <view class="page-title">结算下单</view>
      <text class="page-subtitle">选择收货地址并确认订单，提交后生成待支付订单</text>
    </view>

    <LoginPrompt
      v-if="needsLogin"
      title="登录后结算下单"
      :redirect="'/pages/checkout/index'"
    />
    <RequestState
      v-else-if="cartLoading || cartError"
      :loading="cartLoading"
      :error="cartError"
      loading-text="正在加载订单信息..."
      @retry="loadCart"
    />
    <view v-else-if="cartStore.items.length === 0" class="empty-checkout">
      <text class="empty-checkout__text">暂无可结算的商品，请先添加商品到购物车</text>
      <button class="btn btn-primary empty-checkout__btn" @tap="goCart">返回购物车</button>
    </view>

    <template v-else>
      <view class="panel card">
        <view class="panel__title">商品清单</view>
        <view v-for="item in cartStore.items" :key="item.id" class="order-line">
          <view class="order-line__art">
            <ProductArtwork :slug="item.main_image" :alt="item.name" />
          </view>
          <view class="order-line__info">
            <view class="order-line__name">{{ item.name }}</view>
            <view class="order-line__model">规格：{{ item.model || '详询客服' }}</view>
            <view class="order-line__price">¥{{ formatPrice(item.price) }} × {{ item.quantity }}</view>
          </view>
          <text class="order-line__subtotal">¥{{ formatPrice(item.subtotal) }}</text>
        </view>
      </view>

      <view class="panel card">
        <view class="panel__title-row">
          <view class="panel__title">收货地址</view>
          <text class="panel__add" @tap="goAddresses">新增 +</text>
        </view>
        <RequestState
          v-if="addressesLoading || addressesError || addresses.length === 0"
          :loading="addressesLoading"
          :error="addressesError"
          :empty="!addressesLoading && !addressesError"
          loading-text="正在加载地址..."
          empty-text="暂无收货地址，请先新增"
          @retry="loadAddresses"
        />
        <view v-else class="address-options">
          <view
            v-for="address in addresses"
            :key="address.id"
            class="address-option"
            :class="{ 'is-selected': selectedAddressId === address.id }"
            @tap="selectedAddressId = address.id"
          >
            <view class="address-option__radio" :class="{ 'is-checked': selectedAddressId === address.id }" />
            <view class="address-option__body">
              <view class="address-option__title">
                <text class="address-option__receiver">{{ address.receiver }}</text>
                <text class="address-option__phone">{{ address.phone }}</text>
              </view>
              <text class="address-option__text">{{ address.region }} {{ address.detail }}</text>
            </view>
          </view>
        </view>
      </view>

      <view class="panel card">
        <view class="panel__title">备注</view>
        <textarea
          v-model="remark"
          class="remark-input"
          maxlength="200"
          placeholder="选填，可备注发票、配送等要求"
          placeholder-class="remark-input__placeholder"
        />
      </view>

      <view class="panel card">
        <view class="summary-row">
          <text>商品金额</text>
          <text>¥{{ formatPrice(cartStore.productAmount) }}</text>
        </view>
        <view class="summary-row">
          <text>运费</text>
          <text>{{ isZeroAmount(cartStore.freightAmount) ? '免运费' : `¥${formatPrice(cartStore.freightAmount)}` }}</text>
        </view>
        <view class="summary-row summary-row--total">
          <text>应付合计</text>
          <text class="summary-row__total">¥{{ formatPrice(cartStore.totalAmount) }}</text>
        </view>
        <button class="btn btn-primary checkout-submit" :disabled="submitting || !selectedAddress" @tap="submitOrder">
          提交订单
        </button>
        <text class="checkout-tip">提交订单后进入待支付状态，支付功能暂未接入</text>
      </view>
    </template>
  </view>
</template>

<style scoped>
.page-heading {
  padding: 10rpx 0 26rpx;
}

.empty-checkout {
  display: flex;
  min-height: 400rpx;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24rpx;
}

.empty-checkout__text {
  color: #7b8998;
  font-size: 25rpx;
}

.empty-checkout__btn {
  min-height: 76rpx;
  padding: 0 44rpx;
}

.panel {
  margin-top: 24rpx;
  padding: 28rpx;
}

.panel__title {
  font-size: 30rpx;
  font-weight: 700;
}

.panel__title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.panel__add {
  color: var(--brand);
  font-size: 24rpx;
  font-weight: 600;
}

.order-line {
  display: flex;
  align-items: center;
  padding: 22rpx 0;
  border-top: 1rpx solid #edf1f5;
}

.order-line:first-of-type {
  border-top: 0;
}

.order-line__art {
  display: flex;
  width: 120rpx;
  height: 106rpx;
  flex: 0 0 auto;
  align-items: center; justify-content: center;
  margin-right: 20rpx;
  overflow: hidden;
  border-radius: 14rpx;
  background: radial-gradient(circle at 50% 42%, #ffffff 20%, #f0f4f8 80%);
}

.order-line__info {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
  margin-right: 20rpx;
}

.order-line__name {
  overflow: hidden;
  color: #26384c;
  font-size: 26rpx;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.order-line__model {
  margin-top: 4rpx;
  color: #8a97a5;
  font-size: 21rpx;
}

.order-line__price {
  margin-top: 6rpx;
  color: var(--price);
  font-family: Arial, sans-serif;
  font-size: 24rpx;
  font-weight: 600;
}

.order-line__subtotal {
  color: var(--price);
  font-family: Arial, sans-serif;
  font-size: 26rpx;
  font-weight: 700;
  white-space: nowrap;
}

.address-options {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-top: 22rpx;
}

.address-option {
  display: flex;
  align-items: flex-start;
  gap: 18rpx;
  padding: 24rpx;
  border: 1rpx solid #e4ebf2;
  border-radius: 16rpx;
}

.address-option.is-selected {
  border-color: var(--brand);
  background: #f6faff;
}

.address-option__radio {
  width: 36rpx;
  height: 36rpx;
  flex: 0 0 auto;
  margin-top: 4rpx;
  border: 2rpx solid #c6d2de;
  border-radius: 50%;
}

.address-option__radio.is-checked {
  border-color: var(--brand);
  background: var(--brand);
  box-shadow: inset 0 0 0 8rpx #ffffff;
}

.address-option__body {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 6rpx;
}

.address-option__title {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.address-option__receiver {
  color: #26384c;
  font-size: 27rpx;
  font-weight: 650;
}

.address-option__phone {
  color: #8391a0;
  font-size: 22rpx;
}

.address-option__text {
  color: #657689;
  font-size: 23rpx;
  line-height: 1.7;
}

.remark-input {
  width: 100%;
  min-height: 160rpx;
  margin-top: 20rpx;
  padding: 20rpx;
  border-radius: 14rpx;
  background: #f5f8fb;
  font-size: 24rpx;
}

.remark-input__placeholder {
  color: #a0abb7;
}

.summary-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18rpx 0;
  border-bottom: 1rpx solid #edf1f5;
  color: #7b8998;
  font-size: 24rpx;
}

.summary-row--total {
  border-bottom: 0;
  padding-top: 24rpx;
}

.summary-row--total > text:first-child {
  color: #3c4e61;
  font-weight: 600;
}

.summary-row__total {
  color: var(--price);
  font-family: Arial, sans-serif;
  font-size: 40rpx;
  font-weight: 700;
}

.checkout-submit {
  width: 100%;
  min-height: 92rpx;
  margin-top: 10rpx;
}

.checkout-tip {
  display: block;
  margin-top: 16rpx;
  color: #a0abb7;
  font-size: 20rpx;
  text-align: center;
}
</style>
