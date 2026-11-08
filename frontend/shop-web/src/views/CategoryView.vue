<script setup lang="ts">
import { ArrowRight } from '@element-plus/icons-vue'
import { categories } from '@/data/home'
import CategoryIcon from '@/components/CategoryIcon.vue'
</script>

<template>
  <section class="catalog-page">
    <div class="container">
      <nav class="breadcrumb" aria-label="面包屑"><RouterLink to="/">首页</RouterLink><span>/</span><span>产品分类</span></nav>
      <div class="page-title"><span>PRODUCT CATEGORIES</span><h1>产品分类</h1><p>多品类五金产品，一站式满足工程与生产采购需求</p></div>
      <div class="category-grid">
        <RouterLink v-for="category in categories" :key="category.id" :to="{ path: '/products', query: { category: category.id } }" class="category-card">
          <div class="category-art"><CategoryIcon :name="category.icon" /></div>
          <div><h2>{{ category.name }}</h2><p>{{ category.description }}</p><span>查看产品<el-icon><ArrowRight /></el-icon></span></div>
        </RouterLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
.catalog-page { min-height: 600px; padding: 26px 0 70px; background: #f5f8fb; }
.breadcrumb { display: flex; gap: 10px; color: #8b97a4; font-size: 12px; }
.page-title { margin: 35px 0 30px; text-align: center; }
.page-title > span { color: var(--brand); font-family: Arial, sans-serif; font-size: 10px; letter-spacing: .2em; }
.page-title h1 { margin-top: 4px; font-size: 32px; }
.page-title p { margin-top: 8px; color: #7d8b9a; }
.category-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.category-card { display: flex; align-items: center; gap: 22px; padding: 26px; border: 1px solid #e7edf3; border-radius: 12px; background: #fff; box-shadow: var(--shadow-sm); transition: transform .2s, border-color .2s; }
.category-card:hover { border-color: #b9d7f4; transform: translateY(-3px); }
.category-art { width: 90px; height: 90px; flex: 0 0 auto; }
.category-card h2 { font-size: 19px; }
.category-card p { margin-top: 4px; color: #8593a2; font-size: 12px; }
.category-card div > span { display: inline-flex; align-items: center; gap: 7px; margin-top: 12px; color: var(--brand); font-size: 12px; }
@media (max-width: 767px) { .catalog-page { padding-top: 18px; } .page-title { margin: 25px 0 22px; text-align: left; } .page-title h1 { font-size: 27px; } .page-title p { font-size: 12px; } .category-grid { grid-template-columns: 1fr; gap: 12px; } .category-card { padding: 17px 22px; } .category-art { width: 68px; height: 68px; } }
</style>
