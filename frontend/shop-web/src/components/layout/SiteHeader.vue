<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowDown, Menu, Phone, Search, ShoppingCart, User } from '@element-plus/icons-vue'
import BrandLogo from '@/components/BrandLogo.vue'
import { useCartStore } from '@/stores/cart'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()
const userStore = useUserStore()
const keyword = ref('')
const drawerOpen = ref(false)
const navItems = [
  { label: '首页', to: '/' },
  { label: '产品中心', to: '/products', dropdown: true },
  { label: '关于我们', to: '/about' },
  { label: '新闻资讯', to: '/news' },
  { label: '服务支持', to: '/support', dropdown: true },
  { label: '联系我们', to: '/contact' },
]

function isActive(path: string) {
  if (path === '/') return route.path === '/'
  if (path === '/products') return ['/products', '/categories', '/search'].some((item) => route.path.startsWith(item))
  return route.path.startsWith(path)
}

function submitSearch() {
  const value = keyword.value.trim()
  void router.push({ path: '/search', query: value ? { keyword: value } : undefined })
  drawerOpen.value = false
}

watch(() => route.fullPath, () => { drawerOpen.value = false })
</script>

<template>
  <header class="site-header">
    <div class="desktop-header container">
      <RouterLink to="/" aria-label="恒泰五金首页"><BrandLogo /></RouterLink>
      <nav class="desktop-nav" aria-label="主导航">
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" class="nav-link" :class="{ active: isActive(item.to) }">
          {{ item.label }}<el-icon v-if="item.dropdown" :size="12"><ArrowDown /></el-icon>
        </RouterLink>
      </nav>
      <form class="header-search" role="search" @submit.prevent="submitSearch">
        <input v-model="keyword" type="search" aria-label="搜索产品" placeholder="请输入产品关键词..." />
        <button type="submit" aria-label="搜索"><el-icon><Search /></el-icon></button>
      </form>
      <a class="header-phone" href="tel:400-123-4567">
        <el-icon :size="29"><Phone /></el-icon>
        <span><strong>400-123-4567</strong><small>全国服务热线</small></span>
      </a>
      <div class="header-tools">
        <RouterLink to="/cart" class="tool-link" aria-label="购物车">
          <el-icon :size="22"><ShoppingCart /></el-icon>
          <span v-if="cartStore.totalQuantity" class="tool-badge">{{ cartStore.totalQuantity }}</span>
        </RouterLink>
        <RouterLink to="/account" class="tool-link" aria-label="个人中心">
          <el-icon :size="22"><User /></el-icon>
        </RouterLink>
      </div>
    </div>

    <div class="mobile-header">
      <div class="mobile-top container">
        <RouterLink to="/" aria-label="恒泰五金首页"><BrandLogo /></RouterLink>
        <div class="mobile-actions">
          <a href="tel:400-123-4567" aria-label="拨打客服热线"><el-icon :size="21"><Phone /></el-icon></a>
          <RouterLink to="/cart" aria-label="购物车">
            <span class="mobile-cart">
              <el-icon :size="21"><ShoppingCart /></el-icon>
              <span v-if="cartStore.totalQuantity" class="mobile-badge">{{ cartStore.totalQuantity }}</span>
            </span>
          </RouterLink>
          <RouterLink to="/account" aria-label="个人中心"><el-icon :size="21"><User /></el-icon></RouterLink>
          <button type="button" aria-label="打开导航菜单" @click="drawerOpen = true"><el-icon :size="23"><Menu /></el-icon></button>
        </div>
      </div>
      <form class="mobile-search container" role="search" @submit.prevent="submitSearch">
        <el-icon :size="20"><Search /></el-icon>
        <input v-model="keyword" type="search" aria-label="搜索商品或分类" placeholder="搜索商品或分类..." />
        <button type="submit">搜索</button>
      </form>
    </div>

    <el-drawer v-model="drawerOpen" title="网站导航" direction="rtl" size="82%">
      <nav class="drawer-nav" aria-label="移动端导航">
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" :class="{ active: isActive(item.to) }">{{ item.label }}</RouterLink>
        <RouterLink to="/cart">购物车</RouterLink>
        <RouterLink to="/orders">订单中心</RouterLink>
        <RouterLink to="/addresses">地址管理</RouterLink>
        <RouterLink to="/account">{{ userStore.isLoggedIn ? '个人中心' : '登录 / 注册' }}</RouterLink>
      </nav>
      <a class="drawer-phone" href="tel:400-123-4567"><el-icon><Phone /></el-icon>400-123-4567</a>
    </el-drawer>
  </header>
</template>

<style scoped>
.site-header { position: relative; z-index: 20; background: #fff; border-bottom: 1px solid #eef2f6; }
.desktop-header { height: 86px; display: flex; align-items: center; gap: 26px; }
.desktop-nav { display: flex; align-self: stretch; align-items: center; gap: clamp(17px, 2vw, 30px); margin-left: auto; }
.nav-link { position: relative; display: inline-flex; align-items: center; gap: 4px; height: 100%; color: #26384c; font-size: 14px; white-space: nowrap; transition: color .2s; }
.nav-link::after { content: ""; position: absolute; right: 0; bottom: 16px; left: 0; height: 2px; border-radius: 2px; background: var(--brand); transform: scaleX(0); transition: transform .2s; }
.nav-link:hover, .nav-link.active { color: var(--brand); }
.nav-link.active::after { transform: scaleX(1); }
.header-search { display: flex; flex: 0 1 222px; height: 36px; overflow: hidden; border: 1px solid #e2e8ef; border-radius: 20px; background: #f8fafc; }
.header-search input { min-width: 0; flex: 1; padding: 0 4px 0 15px; border: 0; outline: 0; color: var(--ink); background: transparent; font-size: 12px; }
.header-search input::-webkit-search-cancel-button { display: none; }
.header-search button { width: 38px; border: 0; color: #fff; background: var(--brand); font-size: 18px; }
.header-phone { display: flex; align-items: center; gap: 8px; color: var(--brand); white-space: nowrap; }
.header-phone span { display: flex; flex-direction: column; }
.header-phone strong { color: var(--brand-ink); font-family: Arial, sans-serif; font-size: 15px; line-height: 1.25; }
.header-phone small { color: #8995a2; font-size: 10px; }
.header-tools { display: flex; align-items: center; gap: 7px; }
.tool-link { position: relative; display: grid; width: 38px; height: 38px; place-items: center; border-radius: 50%; color: #4e6073; background: #f3f7fb; transition: color .2s, background .2s; }
.tool-link:hover { color: var(--brand); background: var(--brand-light); }
.tool-badge { position: absolute; top: -4px; right: -4px; min-width: 17px; height: 17px; padding: 0 4px; border: 2px solid #fff; border-radius: 9px; color: #fff; background: #ef5350; font-size: 10px; line-height: 13px; text-align: center; }
.mobile-header { display: none; }
@media (max-width: 1180px) {
  .desktop-header { gap: 18px; }
  .desktop-nav { gap: 16px; }
  .header-phone { display: none; }
}
@media (max-width: 900px) and (min-width: 768px) {
  .desktop-nav { gap: 12px; }
  .nav-link { font-size: 12px; }
  .header-search { display: none; }
}
@media (max-width: 767px) {
  .site-header { border: 0; background: linear-gradient(180deg, #e9f2ff, #f3f7fc); }
  .desktop-header { display: none; }
  .mobile-header { display: block; padding: 17px 0 14px; }
  .mobile-top { display: flex; align-items: center; justify-content: space-between; }
  .mobile-actions { display: flex; align-items: center; gap: 4px; }
  .mobile-actions a, .mobile-actions button { display: grid; width: 34px; height: 34px; place-items: center; border: 0; border-radius: 50%; color: #4e6073; background: transparent; }
  .mobile-cart { position: relative; display: grid; place-items: center; }
  .mobile-badge { position: absolute; top: -8px; left: 13px; min-width: 16px; height: 16px; padding: 0 4px; border: 2px solid #fff; border-radius: 9px; color: #fff; background: #ef5350; font-size: 9px; line-height: 12px; text-align: center; }
  .mobile-search { display: flex; align-items: center; height: 48px; margin-top: 14px; padding: 0 7px 0 15px; border: 1px solid rgb(255 255 255 / 80%); border-radius: 25px; color: #8a9aad; background: rgb(255 255 255 / 82%); box-shadow: 0 5px 20px rgb(61 105 150 / 5%); }
  .mobile-search input { min-width: 0; flex: 1; height: 100%; padding: 0 10px; border: 0; outline: 0; background: transparent; font-size: 14px; }
  .mobile-search input::-webkit-search-cancel-button { display: none; }
  .mobile-search button { height: 34px; padding: 0 13px; border: 0; border-radius: 17px; color: #fff; background: var(--brand); font-size: 12px; }
  .drawer-nav { display: flex; flex-direction: column; }
  .drawer-nav a { padding: 14px 4px; border-bottom: 1px solid var(--line); font-size: 16px; }
  .drawer-nav a.active { color: var(--brand); font-weight: 600; }
  .drawer-phone { display: flex; align-items: center; gap: 9px; margin-top: 30px; color: var(--brand); font-size: 19px; font-weight: 700; }
}
</style>
