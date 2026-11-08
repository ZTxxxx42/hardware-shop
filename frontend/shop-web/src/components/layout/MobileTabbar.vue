<script setup lang="ts">
import { Grid, HomeFilled, ShoppingCart, User } from '@element-plus/icons-vue'
import { useCartStore } from '@/stores/cart'

const cartStore = useCartStore()
const tabs = [
  { label: '首页', to: '/', icon: HomeFilled },
  { label: '分类', to: '/categories', icon: Grid },
  { label: '购物车', to: '/cart', icon: ShoppingCart },
  { label: '我的', to: '/account', icon: User },
]
</script>

<template>
  <nav class="mobile-tabbar" aria-label="移动端快捷导航">
    <RouterLink v-for="tab in tabs" :key="tab.to" :to="tab.to" class="tab-item" active-class="active">
      <span class="tab-icon">
        <el-icon :size="25"><component :is="tab.icon" /></el-icon>
        <span v-if="tab.to === '/cart' && cartStore.totalQuantity" class="cart-badge">{{ cartStore.totalQuantity }}</span>
      </span>
      <span>{{ tab.label }}</span>
    </RouterLink>
  </nav>
</template>

<style scoped>
.mobile-tabbar { display: none; }
@media (max-width: 767px) {
  .mobile-tabbar { position: fixed; z-index: 50; right: 0; bottom: 0; left: 0; display: grid; grid-template-columns: repeat(4, 1fr); height: calc(66px + env(safe-area-inset-bottom)); padding: 7px 8px env(safe-area-inset-bottom); border-top: 1px solid #e5ebf2; background: rgb(255 255 255 / 96%); box-shadow: 0 -6px 22px rgb(30 64 97 / 6%); backdrop-filter: blur(14px); }
  .tab-item { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; color: #758292; font-size: 11px; }
  .tab-item.active { color: var(--brand); }
  .tab-icon { position: relative; display: grid; place-items: center; height: 29px; }
  .cart-badge { position: absolute; top: -5px; left: 17px; min-width: 16px; height: 16px; padding: 0 4px; border: 2px solid #fff; border-radius: 9px; color: #fff; background: #ef5350; font-size: 9px; line-height: 12px; text-align: center; }
}
</style>
