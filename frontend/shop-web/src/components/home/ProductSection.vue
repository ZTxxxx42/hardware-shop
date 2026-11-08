<script setup lang="ts">
import { ArrowRight } from '@element-plus/icons-vue'
import { hotProducts } from '@/data/home'
import ProductCard from '@/components/ProductCard.vue'

const desktopProducts = hotProducts.slice(0, 5)
const mobileProducts = [hotProducts[0], hotProducts[5], hotProducts[1], hotProducts[2]].filter((product) => product !== undefined)
</script>

<template>
  <section class="product-section section" aria-labelledby="hot-products-title">
    <div class="container">
      <div class="product-heading">
        <div class="section-heading section-heading--lines">
          <div>
            <h2 id="hot-products-title"><span class="desktop-title">热销产品</span><span class="mobile-title">热销推荐</span></h2>
            <p>品质之选 · 值得信赖</p>
          </div>
        </div>
        <RouterLink class="text-link more-link" to="/products">查看更多<el-icon><ArrowRight /></el-icon></RouterLink>
      </div>
      <div class="desktop-product-grid">
        <ProductCard v-for="product in desktopProducts" :key="product.id" :product="product" />
      </div>
      <div class="mobile-product-grid">
        <ProductCard v-for="product in mobileProducts" :key="product.id" :product="product" />
      </div>
    </div>
  </section>
</template>

<style scoped>
.product-section { padding-top: 22px; background: #fff; }
.product-heading { position: relative; }
.product-heading .section-heading { margin-bottom: 28px; }
.more-link { position: absolute; right: 0; bottom: 32px; }
.desktop-product-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 18px; }
.mobile-product-grid, .mobile-title { display: none; }
@media (max-width: 1000px) and (min-width: 768px) { .desktop-product-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 767px) {
  .product-section { padding-top: 28px; background: transparent; }
  .product-heading .section-heading { margin-bottom: 18px; }
  .desktop-product-grid, .desktop-title { display: none; }
  .mobile-title { display: inline; }
  .mobile-product-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
  .more-link { right: 0; bottom: 20px; color: #69798b; font-size: 12px; font-weight: 400; }
}
@media (max-width: 360px) { .mobile-product-grid { gap: 9px; } }
</style>
