<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowRight, ShoppingCart } from '@element-plus/icons-vue'
import type { Product } from '@/types/catalog'
import { formatPrice } from '@/utils/catalog'
import { getErrorMessage } from '@/api/http'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'
import ProductArtwork from '@/components/ProductArtwork.vue'

defineProps<{ product: Product }>()

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const cartStore = useCartStore()

async function addToCart(product: Product) {
  if (product.status !== 'ON_SALE') return
  if (!userStore.isLoggedIn) {
    await router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }
  try {
    await cartStore.add(product.id, 1)
    ElMessage.success('已加入购物车')
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '加入购物车失败，请稍后重试'))
  }
}
</script>

<template>
  <article class="product-card">
    <RouterLink class="product-image" :to="`/products/${product.id}`" :aria-label="`查看${product.name}详情`">
      <span v-if="product.status !== 'ON_SALE'" class="product-tag">暂不可售</span>
      <ProductArtwork :slug="product.main_image" :alt="product.name" />
    </RouterLink>
    <div class="product-info">
      <RouterLink :to="`/products/${product.id}`"><h3>{{ product.name }}</h3></RouterLink>
      <p class="product-model">规格：{{ product.model || '详询客服' }}</p>
      <p class="product-price"><span>¥</span>{{ formatPrice(product.price) }}</p>
      <div class="card-actions">
        <RouterLink class="inquiry-link" :to="{ path: '/contact', query: { product: product.name } }">
          <span class="desktop-label">询价咨询</span><span class="mobile-label">立即询价</span><el-icon><ArrowRight /></el-icon>
        </RouterLink>
        <button class="cart-button" type="button" :disabled="product.status !== 'ON_SALE'" :aria-label="`将${product.name}加入购物车`" @click="addToCart(product)">
          <el-icon><ShoppingCart /></el-icon>
        </button>
      </div>
    </div>
  </article>
</template>

<style scoped>
.product-card { position: relative; min-width: 0; overflow: hidden; border: 1px solid #edf0f4; border-radius: 9px; background: #fff; box-shadow: 0 5px 16px rgb(33 58 82 / 5%); transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease; }
.product-card:hover { border-color: #d2e5f8; box-shadow: 0 16px 30px rgb(33 83 130 / 12%); transform: translateY(-5px); }
.product-image { position: relative; display: block; height: 176px; padding: 5px 12px 0; overflow: hidden; background: radial-gradient(circle at 50% 44%, #fff 20%, #f4f6f9 78%); }
.product-image :deep(.product-artwork) { transition: transform .3s ease; }
.product-card:hover .product-image :deep(.product-artwork) { transform: scale(1.045); }
.product-tag { position: absolute; z-index: 1; top: 11px; left: 0; padding: 3px 10px 3px 8px; border-radius: 0 4px 4px 0; color: #fff; background: var(--brand); font-size: 10px; letter-spacing: .06em; }
.product-info { padding: 2px 17px 16px; }
.product-info h3 { overflow: hidden; color: #1d2a37; font-size: 15px; font-weight: 650; line-height: 1.5; text-overflow: ellipsis; white-space: nowrap; }
.product-info a:hover h3 { color: var(--brand); }
.product-model { margin-top: 3px; color: #7c8792; font-size: 12px; }
.product-price { margin: 2px 0 12px; color: #e45b32; font-family: Arial, sans-serif; font-size: 18px; font-weight: 700; line-height: 1.5; }
.product-price span { margin-right: 2px; font-size: 12px; }
.card-actions { display: flex; align-items: center; gap: 8px; }
.inquiry-link { display: flex; align-items: center; justify-content: center; gap: 14px; min-width: 0; flex: 1; height: 34px; border-radius: 5px; color: #fff; background: linear-gradient(110deg, #0875cf, #2498e5); font-size: 12px; font-weight: 600; transition: filter .2s; }
.inquiry-link:hover { filter: brightness(1.08); }
.cart-button { display: grid; width: 34px; height: 34px; flex: 0 0 auto; place-items: center; border: 1px solid #d7e4f2; border-radius: 5px; color: var(--brand); background: #f3f9ff; font-size: 16px; transition: background .2s, border-color .2s; }
.cart-button:hover { border-color: #9ec7ef; background: #e7f2ff; }
.cart-button:disabled { cursor: not-allowed; color: #b7c2cd; border-color: #e5ebf2; background: #f5f7fa; }
.mobile-label { display: none; }
@media (max-width: 767px) {
  .product-card { display: grid; grid-template-columns: 46% 54%; min-height: 154px; border: 0; border-radius: 10px; box-shadow: 0 5px 18px rgb(32 74 112 / 6%); }
  .product-card:hover { transform: none; }
  .product-image { height: 100%; min-height: 154px; padding: 20px 0 12px; background: #fff; }
  .product-tag { display: none; }
  .product-info { display: flex; min-width: 0; flex-direction: column; justify-content: center; padding: 14px 9px 14px 2px; }
  .product-info h3 { display: -webkit-box; font-size: 12px; line-height: 1.5; white-space: normal; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
  .product-model { margin-top: 5px; overflow: hidden; font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }
  .product-price { margin: 0; font-size: 15px; }
  .product-price span { font-size: 10px; }
  .card-actions { margin-top: 8px; }
  .inquiry-link { gap: 3px; height: 29px; border-radius: 16px; font-size: 11px; }
  .inquiry-link .el-icon { display: none; }
  .cart-button { width: 29px; height: 29px; border-radius: 50%; font-size: 14px; }
  .desktop-label { display: none; }
  .mobile-label { display: inline; }
}
</style>
