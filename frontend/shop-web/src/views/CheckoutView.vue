<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Location, Plus } from '@element-plus/icons-vue'
import { orderApi } from '@/api/order'
import { memberApi } from '@/api/member'
import { getErrorMessage } from '@/api/http'
import { useCartStore } from '@/stores/cart'
import { formatPrice, isZeroAmount } from '@/utils/catalog'
import type { Address } from '@/types/shop'
import ProductArtwork from '@/components/ProductArtwork.vue'
import RequestState from '@/components/RequestState.vue'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()
const addresses = ref<Address[]>([])
const addressesLoading = ref(true)
const addressesError = ref('')
const cartLoading = ref(true)
const cartError = ref('')
const selectedAddressId = ref<number | null>(null)
const remark = ref('')
const submitting = ref(false)

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
    if (!selectedAddressId.value && addresses.value.length > 0) selectedAddressId.value = addresses.value[0].id
  } catch (requestError) {
    addressesError.value = getErrorMessage(requestError, '收货地址加载失败，请稍后重试')
  } finally {
    addressesLoading.value = false
  }
}

function goAddresses() {
  void router.push({ name: 'addresses', query: { redirect: route.fullPath } })
}

function goCart() {
  void router.push({ name: 'cart' })
}

async function submitOrder() {
  if (!selectedAddressId.value) {
    ElMessage.warning('请先选择收货地址')
    return
  }
  submitting.value = true
  try {
    await orderApi.create({ address_id: selectedAddressId.value, remark: remark.value.trim() || undefined })
    cartStore.clear()
    ElMessage.success('订单已创建，等待支付')
    await router.push({ name: 'orders' })
  } catch (requestError) {
    ElMessage.error(getErrorMessage(requestError, '下单失败，请稍后重试'))
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  void loadCart()
  void loadAddresses()
})
</script>

<template>
  <section class="checkout-page">
    <div class="container">
      <nav class="breadcrumb" aria-label="面包屑"><RouterLink to="/">首页</RouterLink><span>/</span><RouterLink to="/cart">购物车</RouterLink><span>/</span><span>结算下单</span></nav>
      <div class="page-heading"><div><span>CHECKOUT</span><h1>结算下单</h1><p>选择收货地址并确认订单，提交后生成待支付订单</p></div></div>
      <RequestState
        v-if="cartLoading || cartError"
        :loading="cartLoading"
        :error="cartError"
        loading-text="正在加载订单信息..."
        @retry="loadCart"
      />
      <div v-else-if="cartStore.items.length === 0" class="empty-checkout">
        <p>暂无可结算的商品，请先添加商品到购物车</p>
        <el-button type="primary" @click="goCart">返回购物车</el-button>
      </div>
      <div v-else class="checkout-layout">
        <div class="checkout-main">
          <section class="panel">
            <h2>商品清单</h2>
            <div class="order-lines">
              <div v-for="item in cartStore.items" :key="item.id" class="order-line">
                <div class="line-art"><ProductArtwork :slug="item.main_image" :alt="item.name" /></div>
                <div class="line-info">
                  <h3>{{ item.name }}</h3>
                  <p>规格：{{ item.model || '详询客服' }}</p>
                  <span>¥{{ formatPrice(item.price) }} × {{ item.quantity }}</span>
                </div>
                <strong class="line-subtotal">¥{{ formatPrice(item.subtotal) }}</strong>
              </div>
            </div>
          </section>
        </div>
        <aside class="checkout-aside">
          <section class="panel address-panel">
            <div class="panel-title">
              <h2>收货地址</h2>
              <el-button text type="primary" :icon="Plus" @click="goAddresses">新增</el-button>
            </div>
            <RequestState
              v-if="addressesLoading || addressesError || addresses.length === 0"
              :loading="addressesLoading"
              :error="addressesError"
              :empty="!addressesLoading && !addressesError"
              loading-text="正在加载地址..."
              empty-text="暂无收货地址，请先新增"
              @retry="loadAddresses"
            />
            <el-radio-group v-else v-model="selectedAddressId" class="address-options">
              <el-radio v-for="address in addresses" :key="address.id" :value="address.id" class="address-option">
                <span class="address-option-icon"><el-icon><Location /></el-icon></span>
                <span class="address-option-body">
                  <strong>{{ address.receiver }} · {{ address.phone }}</strong>
                  <span>{{ address.region }} {{ address.detail }}</span>
                </span>
              </el-radio>
            </el-radio-group>
            <el-button v-if="!addressesLoading && !addressesError && addresses.length === 0" type="primary" plain @click="goAddresses">去新增收货地址</el-button>
          </section>
          <section class="panel">
            <h2>备注</h2>
            <el-input v-model="remark" type="textarea" :rows="3" maxlength="200" show-word-limit placeholder="选填，可备注发票、配送等要求" />
          </section>
          <section class="panel summary-panel">
            <h2>应付金额</h2>
            <dl>
              <div><dt>商品金额</dt><dd>¥{{ formatPrice(cartStore.productAmount) }}</dd></div>
              <div><dt>运费</dt><dd>{{ isZeroAmount(cartStore.freightAmount) ? '免运费' : `¥${formatPrice(cartStore.freightAmount)}` }}</dd></div>
              <div class="summary-total"><dt>合计</dt><dd>¥{{ formatPrice(cartStore.totalAmount) }}</dd></div>
            </dl>
            <el-button class="submit-button" type="primary" size="large" :loading="submitting" :disabled="!selectedAddress" @click="submitOrder">提交订单</el-button>
            <p class="summary-tip">提交订单后进入待支付状态，支付功能暂未接入</p>
          </section>
        </aside>
      </div>
    </div>
  </section>
</template>

<style scoped>
.checkout-page { min-height: 650px; padding: 26px 0 70px; background: #f5f8fb; }
.breadcrumb { display: flex; gap: 10px; color: #8b97a4; font-size: 12px; }
.page-heading { margin: 32px 0 25px; }
.page-heading > div > span { color: var(--brand); font-family: Arial, sans-serif; font-size: 10px; letter-spacing: .18em; }
.page-heading h1 { margin-top: 3px; font-size: 30px; }
.page-heading p { margin-top: 6px; color: #7b8998; font-size: 13px; }
.empty-checkout { display: flex; min-height: 300px; flex-direction: column; align-items: center; justify-content: center; gap: 16px; border: 1px solid #e7edf3; border-radius: 14px; background: #fff; }
.empty-checkout p { color: #7b8998; font-size: 14px; }
.checkout-layout { display: grid; grid-template-columns: minmax(0, 1fr) 360px; gap: 20px; align-items: start; }
.checkout-main, .checkout-aside { display: flex; flex-direction: column; gap: 16px; }
.panel { padding: 22px 24px; border: 1px solid #e7edf3; border-radius: 12px; background: #fff; box-shadow: var(--shadow-sm); }
.panel h2 { font-size: 17px; }
.panel-title { display: flex; align-items: center; justify-content: space-between; }
.order-lines { display: flex; flex-direction: column; margin-top: 16px; }
.order-line { display: grid; grid-template-columns: 72px minmax(0, 1fr) auto; gap: 15px; align-items: center; padding: 14px 0; border-top: 1px solid #edf1f5; }
.order-line:first-child { border-top: 0; padding-top: 6px; }
.line-art { display: grid; width: 72px; height: 64px; place-items: center; overflow: hidden; border-radius: 8px; background: radial-gradient(circle at 50% 42%, #fff 20%, #f0f4f8 80%); }
.line-art :deep(.product-artwork) { max-height: 52px; }
.line-info { min-width: 0; }
.line-info h3 { overflow: hidden; color: #26384c; font-size: 14px; font-weight: 650; text-overflow: ellipsis; white-space: nowrap; }
.line-info p { margin-top: 3px; color: #8a97a5; font-size: 12px; }
.line-info span { display: inline-block; margin-top: 5px; color: #e45b32; font-family: Arial, sans-serif; font-size: 13px; font-weight: 600; }
.line-subtotal { color: #e45b32; font-family: Arial, sans-serif; font-size: 15px; white-space: nowrap; }
.address-options { display: flex; width: 100%; flex-direction: column; gap: 10px; margin-top: 16px; }
.address-option { display: flex; align-items: flex-start; gap: 11px; width: 100%; height: auto; margin: 0; padding: 13px 14px; border: 1px solid #e4ebf2; border-radius: 9px; white-space: normal; }
.address-option :deep(.el-radio__label) { display: flex; align-items: flex-start; gap: 11px; width: 100%; white-space: normal; }
.address-option-icon { display: grid; width: 30px; height: 30px; flex: 0 0 auto; place-items: center; border-radius: 9px; color: var(--brand); background: var(--brand-light); }
.address-option-body { display: flex; min-width: 0; flex-direction: column; gap: 3px; }
.address-option-body strong { color: #26384c; font-size: 13px; }
.address-option-body span { color: #748396; font-size: 12px; line-height: 1.6; }
.address-panel .el-button { margin-top: 10px; }
.summary-panel dl { margin: 16px 0 0; }
.summary-panel dl > div { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #edf1f5; font-size: 13px; }
.summary-panel dt { color: #7b8998; }
.summary-panel dd { margin: 0; color: #3c4e61; font-weight: 600; }
.summary-panel .summary-total { border-bottom: 0; padding-top: 13px; }
.summary-panel .summary-total dt { color: #3c4e61; font-size: 14px; font-weight: 600; }
.summary-panel .summary-total dd { color: #e45b32; font-family: Arial, sans-serif; font-size: 24px; }
.submit-button { width: 100%; height: 46px; margin-top: 18px; font-size: 15px; }
.summary-tip { margin-top: 12px; color: #a0abb7; font-size: 11px; line-height: 1.6; text-align: center; }
@media (max-width: 900px) { .checkout-layout { grid-template-columns: 1fr; } }
@media (max-width: 767px) {
  .checkout-page { padding-top: 18px; }
  .page-heading { margin: 25px 0 20px; }
  .page-heading h1 { font-size: 26px; }
  .page-heading p { font-size: 12px; }
  .panel { padding: 18px 16px; }
}
</style>
