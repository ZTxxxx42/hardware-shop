<script setup lang="ts">
import { computed } from 'vue'
import { Box, Document, Grid, Location, Lock, Phone, Search, Service, ShoppingCart, User } from '@element-plus/icons-vue'

type PlaceholderIcon = 'box' | 'document' | 'grid' | 'location' | 'lock' | 'phone' | 'search' | 'service' | 'cart' | 'user'

const props = withDefaults(defineProps<{
  title: string
  description: string
  eyebrow?: string
  icon?: PlaceholderIcon
  actionText?: string
  actionTo?: string
}>(), {
  eyebrow: 'HENGTAI HARDWARE',
  icon: 'box',
  actionText: '浏览产品',
  actionTo: '/products',
})

const icons = { box: Box, document: Document, grid: Grid, location: Location, lock: Lock, phone: Phone, search: Search, service: Service, cart: ShoppingCart, user: User }
const iconComponent = computed(() => icons[props.icon])
</script>

<template>
  <section class="placeholder-page">
    <div class="container">
      <nav class="breadcrumb" aria-label="面包屑"><RouterLink to="/">首页</RouterLink><span>/</span><span>{{ title }}</span></nav>
      <div class="placeholder-card">
        <div class="placeholder-icon"><el-icon :size="43"><component :is="iconComponent" /></el-icon></div>
        <span class="placeholder-eyebrow">{{ eyebrow }}</span>
        <h1>{{ title }}</h1>
        <p>{{ description }}</p>
        <el-tag effect="plain" type="info">MVP 功能页面已预留</el-tag>
        <div class="placeholder-actions">
          <RouterLink class="primary-link" :to="actionTo">{{ actionText }}</RouterLink>
          <RouterLink class="secondary-link" to="/">返回首页</RouterLink>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.placeholder-page { min-height: 560px; padding: 26px 0 70px; background: #f5f8fb; }
.breadcrumb { display: flex; gap: 10px; margin-bottom: 24px; color: #8b97a4; font-size: 12px; }
.breadcrumb a:hover { color: var(--brand); }
.placeholder-card { display: flex; min-height: 430px; flex-direction: column; align-items: center; justify-content: center; padding: 50px 24px; border: 1px solid #e9eef4; border-radius: 14px; background: #fff; box-shadow: var(--shadow-sm); text-align: center; }
.placeholder-icon { display: grid; width: 86px; height: 86px; margin-bottom: 21px; place-items: center; border-radius: 24px; color: var(--brand); background: var(--brand-light); transform: rotate(-4deg); }
.placeholder-icon .el-icon { transform: rotate(4deg); }
.placeholder-eyebrow { color: #91a1b1; font-family: Arial, sans-serif; font-size: 10px; letter-spacing: .2em; }
.placeholder-card h1 { margin-top: 5px; font-size: 31px; font-weight: 750; }
.placeholder-card > p { max-width: 550px; margin: 13px 0 20px; color: #748396; font-size: 14px; }
.placeholder-actions { display: flex; align-items: center; gap: 22px; margin-top: 29px; }
.secondary-link { color: #68798c; font-size: 13px; }
.secondary-link:hover { color: var(--brand); }
@media (max-width: 767px) { .placeholder-page { min-height: 480px; padding-top: 18px; } .placeholder-card { min-height: 390px; padding-inline: 20px; } .placeholder-card h1 { font-size: 27px; } }
</style>
