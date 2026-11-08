<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { categories, hotProducts } from '@/data/home'
import ProductCard from '@/components/ProductCard.vue'

const route = useRoute()
const activeCategory = computed(() => categories.find((item) => item.id === Number(route.query.category)))
</script>

<template>
  <section class="products-page">
    <div class="container">
      <nav class="breadcrumb" aria-label="面包屑"><RouterLink to="/">首页</RouterLink><span>/</span><span>产品中心</span></nav>
      <div class="list-heading"><div><span>QUALITY HARDWARE</span><h1>{{ activeCategory?.name ?? '产品中心' }}</h1><p>{{ activeCategory?.description ?? '精选工业五金，规格齐全，支持批量采购与询价' }}</p></div><el-tag effect="plain">静态示例商品</el-tag></div>
      <div class="category-filter">
        <RouterLink to="/products" :class="{ active: !activeCategory }">全部产品</RouterLink>
        <RouterLink v-for="category in categories" :key="category.id" :to="{ query: { category: category.id } }" :class="{ active: activeCategory?.id === category.id }">{{ category.name }}</RouterLink>
      </div>
      <div class="products-grid"><ProductCard v-for="product in hotProducts" :key="product.id" :product="product" /></div>
    </div>
  </section>
</template>

<style scoped>
.products-page { min-height: 650px; padding: 26px 0 70px; background: #f5f8fb; }
.breadcrumb { display: flex; gap: 10px; color: #8b97a4; font-size: 12px; }
.list-heading { display: flex; align-items: flex-end; justify-content: space-between; margin: 32px 0 25px; }
.list-heading > div > span { color: var(--brand); font-family: Arial, sans-serif; font-size: 10px; letter-spacing: .18em; }
.list-heading h1 { margin-top: 3px; font-size: 31px; }
.list-heading p { margin-top: 6px; color: #7b8998; font-size: 13px; }
.category-filter { display: flex; gap: 8px; margin-bottom: 24px; overflow-x: auto; }
.category-filter a { padding: 7px 18px; border: 1px solid #e0e7ef; border-radius: 20px; color: #64768a; background: #fff; font-size: 12px; white-space: nowrap; }
.category-filter a.active { border-color: var(--brand); color: #fff; background: var(--brand); }
.products-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 20px; }
@media (max-width: 1000px) { .products-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 767px) { .products-page { padding-top: 18px; } .list-heading { align-items: flex-start; margin: 25px 0 20px; } .list-heading h1 { font-size: 27px; } .list-heading p { font-size: 12px; } .list-heading > .el-tag { display: none; } .products-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; } }
</style>
