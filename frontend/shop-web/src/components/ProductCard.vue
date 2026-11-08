<script setup lang="ts">
import { ArrowRight } from '@element-plus/icons-vue'
import type { Product } from '@/types/catalog'
import ProductArtwork from '@/components/ProductArtwork.vue'

defineProps<{ product: Product }>()
</script>

<template>
  <article class="product-card">
    <RouterLink class="product-image" :to="`/products/${product.id}`" :aria-label="`查看${product.name}详情`">
      <span v-if="product.tag" class="product-tag">{{ product.tag }}</span>
      <ProductArtwork :type="product.artwork" :alt="product.name" />
    </RouterLink>
    <div class="product-info">
      <RouterLink :to="`/products/${product.id}`"><h3>{{ product.name }}</h3></RouterLink>
      <p class="product-model">规格：{{ product.model }}</p>
      <p class="product-material">{{ product.material }}</p>
      <RouterLink class="inquiry-link" :to="{ path: '/contact', query: { product: product.name } }">
        <span class="desktop-label">询价咨询</span><span class="mobile-label">立即询价</span><el-icon><ArrowRight /></el-icon>
      </RouterLink>
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
.product-material { margin: 2px 0 12px; color: #9aa4ae; font-size: 11px; }
.inquiry-link { display: flex; align-items: center; justify-content: center; gap: 14px; width: 100%; height: 34px; border-radius: 5px; color: #fff; background: linear-gradient(110deg, #0875cf, #2498e5); font-size: 12px; font-weight: 600; transition: filter .2s; }
.inquiry-link:hover { filter: brightness(1.08); }
.mobile-label { display: none; }
@media (max-width: 767px) {
  .product-card { display: grid; grid-template-columns: 46% 54%; min-height: 154px; border: 0; border-radius: 10px; box-shadow: 0 5px 18px rgb(32 74 112 / 6%); }
  .product-card:hover { transform: none; }
  .product-image { height: 100%; min-height: 154px; padding: 20px 0 12px; background: #fff; }
  .product-tag { display: none; }
  .product-info { display: flex; min-width: 0; flex-direction: column; justify-content: center; padding: 14px 9px 14px 2px; }
  .product-info h3 { display: -webkit-box; font-size: 12px; line-height: 1.5; white-space: normal; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
  .product-model { margin-top: 8px; font-size: 10px; white-space: nowrap; }
  .product-material { display: none; }
  .inquiry-link { gap: 3px; height: 29px; margin-top: 12px; border-radius: 16px; font-size: 11px; }
  .inquiry-link .el-icon { display: none; }
  .desktop-label { display: none; }
  .mobile-label { display: inline; }
}
</style>
