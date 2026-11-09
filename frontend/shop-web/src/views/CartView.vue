<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowRight, Delete } from '@element-plus/icons-vue'
import { useCartStore } from '@/stores/cart'
import { getErrorMessage } from '@/api/http'
import { formatPrice, isZeroAmount } from '@/utils/catalog'
import type { CartItem } from '@/types/shop'
import ProductArtwork from '@/components/ProductArtwork.vue'
import RequestState from '@/components/RequestState.vue'

const router = useRouter()
const cartStore = useCartStore()
const loading = ref(true)
const error = ref('')
const busyItem = ref<number | null>(null)

async function load() {
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

async function changeQuantity(item: CartItem, value: number | undefined) {
  if (!value || value < 1 || value === item.quantity) return
  busyItem.value = item.id
  try {
    await cartStore.updateQuantity(item.id, value)
  } catch (requestError) {
    ElMessage.error(getErrorMessage(requestError, '修改数量失败，请稍后重试'))
  } finally {
    busyItem.value = null
  }
}

async function removeItem(item: CartItem) {
  try {
    await ElMessageBox.confirm(`确定将“${item.name}”移出购物车吗？`, '移出商品', {
      type: 'warning',
      confirmButtonText: '移出',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  busyItem.value = item.id
  try {
    await cartStore.remove(item.id)
    ElMessage.success('已移出购物车')
  } catch (requestError) {
    ElMessage.error(getErrorMessage(requestError, '删除失败，请稍后重试'))
  } finally {
    busyItem.value = null
  }
}

function goCheckout() {
  void router.push('/checkout')
}

function goProducts() {
  void router.push('/products')
}

onMounted(load)
</script>

<template>
  <section class="cart-page">
    <div class="container">
      <nav class="breadcrumb" aria-label="面包屑"><RouterLink to="/">首页</RouterLink><span>/</span><span>购物车</span></nav>
      <div class="page-heading"><div><span>SHOPPING CART</span><h1>购物车</h1><p>已选商品将按当前会员等级实时计价</p></div></div>
      <RequestState
        v-if="loading || error"
        :loading="loading"
        :error="error"
        loading-text="正在加载购物车..."
        @retry="load"
      />
      <div v-else-if="cartStore.items.length === 0" class="empty-cart">
        <p>购物车还是空的，去挑选需要的五金商品吧</p>
        <el-button type="primary" @click="goProducts">去选购商品</el-button>
      </div>
      <div v-else class="cart-layout">
        <div class="cart-list">
          <article v-for="item in cartStore.items" :key="item.id" class="cart-line">
            <RouterLink class="line-art" :to="`/products/${item.product_id}`"><ProductArtwork :slug="item.main_image" :alt="item.name" /></RouterLink>
            <div class="line-info">
              <RouterLink :to="`/products/${item.product_id}`"><h3>{{ item.name }}</h3></RouterLink>
              <p class="line-model">规格：{{ item.model || '详询客服' }}</p>
              <p class="line-price"><span>¥</span>{{ formatPrice(item.price) }}</p>
            </div>
            <div class="line-tools">
              <el-input-number
                :model-value="item.quantity"
                :min="1"
                :max="999"
                :disabled="busyItem === item.id"
                aria-label="采购数量"
                @change="changeQuantity(item, $event)"
              />
              <p class="line-subtotal"><span>小计</span><strong>¥{{ formatPrice(item.subtotal) }}</strong></p>
              <el-button class="line-delete" text type="danger" :icon="Delete" :loading="busyItem === item.id" aria-label="移出购物车" @click="removeItem(item)" />
            </div>
          </article>
        </div>
        <aside class="cart-summary">
          <h2>订单汇总</h2>
          <dl>
            <div><dt>商品金额</dt><dd>¥{{ formatPrice(cartStore.productAmount) }}</dd></div>
            <div><dt>运费</dt><dd>{{ isZeroAmount(cartStore.freightAmount) ? '免运费' : `¥${formatPrice(cartStore.freightAmount)}` }}</dd></div>
            <div class="summary-total"><dt>应付合计</dt><dd>¥{{ formatPrice(cartStore.totalAmount) }}</dd></div>
          </dl>
          <el-button class="checkout-button" type="primary" size="large" @click="goCheckout">去结算<el-icon><ArrowRight /></el-icon></el-button>
          <p class="summary-tip">价格以提交订单时后端实时计价为准</p>
        </aside>
      </div>
    </div>
  </section>
</template>

<style scoped>
.cart-page { min-height: 620px; padding: 26px 0 70px; background: #f5f8fb; }
.breadcrumb { display: flex; gap: 10px; color: #8b97a4; font-size: 12px; }
.page-heading { margin: 32px 0 25px; }
.page-heading > div > span { color: var(--brand); font-family: Arial, sans-serif; font-size: 10px; letter-spacing: .18em; }
.page-heading h1 { margin-top: 3px; font-size: 30px; }
.page-heading p { margin-top: 6px; color: #7b8998; font-size: 13px; }
.empty-cart { display: flex; min-height: 320px; flex-direction: column; align-items: center; justify-content: center; gap: 16px; border: 1px solid #e7edf3; border-radius: 14px; background: #fff; box-shadow: var(--shadow-sm); }
.empty-cart p { color: #7b8998; font-size: 14px; }
.cart-layout { display: grid; grid-template-columns: minmax(0, 1fr) 300px; gap: 20px; align-items: start; }
.cart-list { display: flex; flex-direction: column; gap: 14px; }
.cart-line { display: grid; grid-template-columns: 128px minmax(0, 1fr) auto; gap: 20px; align-items: center; padding: 18px 20px; border: 1px solid #e7edf3; border-radius: 12px; background: #fff; box-shadow: var(--shadow-sm); }
.line-art { display: grid; width: 128px; height: 112px; place-items: center; overflow: hidden; border-radius: 9px; background: radial-gradient(circle at 50% 42%, #fff 20%, #f0f4f8 80%); }
.line-art :deep(.product-artwork) { max-height: 92px; }
.line-info { min-width: 0; }
.line-info h3 { overflow: hidden; color: #26384c; font-size: 16px; font-weight: 650; text-overflow: ellipsis; white-space: nowrap; }
.line-info a:hover h3 { color: var(--brand); }
.line-model { margin-top: 5px; color: #8a97a5; font-size: 12px; }
.line-price { margin-top: 6px; color: #e45b32; font-family: Arial, sans-serif; font-size: 17px; font-weight: 700; }
.line-price span { margin-right: 2px; font-size: 12px; }
.line-tools { display: flex; flex-direction: column; align-items: flex-end; gap: 10px; }
.line-tools :deep(.el-input-number) { width: 122px; }
.line-subtotal { display: flex; align-items: baseline; gap: 8px; }
.line-subtotal span { color: #95a2af; font-size: 11px; }
.line-subtotal strong { color: #e45b32; font-family: Arial, sans-serif; font-size: 15px; }
.cart-summary { position: sticky; top: 20px; padding: 24px 25px; border: 1px solid #e7edf3; border-radius: 12px; background: #fff; box-shadow: var(--shadow-sm); }
.cart-summary h2 { font-size: 18px; }
.cart-summary dl { margin: 18px 0 0; }
.cart-summary dl > div { display: flex; align-items: center; justify-content: space-between; padding: 11px 0; border-bottom: 1px solid #edf1f5; font-size: 13px; }
.cart-summary dt { color: #7b8998; }
.cart-summary dd { margin: 0; color: #3c4e61; font-weight: 600; }
.cart-summary .summary-total { padding-top: 14px; border-bottom: 0; }
.cart-summary .summary-total dt { color: #3c4e61; font-size: 14px; font-weight: 600; }
.cart-summary .summary-total dd { color: #e45b32; font-family: Arial, sans-serif; font-size: 24px; }
.checkout-button { width: 100%; height: 46px; margin-top: 20px; font-size: 15px; }
.summary-tip { margin-top: 14px; color: #a0abb7; font-size: 11px; line-height: 1.6; }
@media (max-width: 900px) { .cart-layout { grid-template-columns: 1fr; } .cart-summary { position: static; } }
@media (max-width: 767px) {
  .cart-page { padding-top: 18px; }
  .page-heading { margin: 25px 0 20px; }
  .page-heading h1 { font-size: 26px; }
  .page-heading p { font-size: 12px; }
  .cart-line { grid-template-columns: 92px minmax(0, 1fr); gap: 12px; padding: 14px; }
  .line-art { width: 92px; height: 84px; }
  .line-art :deep(.product-artwork) { max-height: 68px; }
  .line-info h3 { font-size: 14px; }
  .line-tools { grid-column: 1 / -1; flex-direction: row; align-items: center; justify-content: space-between; gap: 10px; padding-top: 12px; border-top: 1px solid #f0f3f7; }
  .line-tools :deep(.el-input-number) { width: 112px; }
  .line-subtotal { margin-left: auto; }
}
</style>
