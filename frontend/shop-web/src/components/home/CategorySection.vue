<script setup lang="ts">
import { ArrowRight, Grid } from '@element-plus/icons-vue'
import { categories } from '@/data/home'
import CategoryIcon from '@/components/CategoryIcon.vue'

const mobileCategories = [
  ...categories.slice(0, 5),
  { id: 0, name: '全部分类', icon: 'grid' as const, description: '查看全部商品' },
]
</script>

<template>
  <section class="category-section" aria-labelledby="category-title">
    <div class="category-panel container">
      <div class="category-intro">
        <el-icon :size="29"><Grid /></el-icon>
        <h2 id="category-title">产品分类</h2>
        <p>多品类 · 全覆盖</p>
        <RouterLink to="/categories" aria-label="查看全部分类"><el-icon><ArrowRight /></el-icon></RouterLink>
      </div>
      <div class="desktop-categories">
        <RouterLink v-for="category in categories" :key="category.id" class="category-item" :to="{ path: '/products', query: { category: category.id } }">
          <div class="category-image"><CategoryIcon :name="category.icon" /></div>
          <h3>{{ category.name }}</h3>
          <p>{{ category.description }}</p>
        </RouterLink>
      </div>
      <div class="mobile-categories">
        <RouterLink v-for="category in mobileCategories" :key="category.id" class="category-item" :to="category.id ? { path: '/products', query: { category: category.id } } : '/categories'">
          <div class="category-image"><CategoryIcon :name="category.icon" /></div>
          <h3>{{ category.name }}</h3>
        </RouterLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
.category-section { position: relative; z-index: 2; padding: 18px 0 24px; background: #fff; }
.category-panel { display: flex; min-height: 158px; overflow: hidden; border: 1px solid #e9eef4; border-radius: 11px; background: #fff; box-shadow: 0 12px 35px rgb(33 69 103 / 8%); }
.category-intro { display: flex; width: 164px; flex: 0 0 164px; flex-direction: column; align-items: center; justify-content: center; color: #fff; background: linear-gradient(145deg, #075cba, #1597e2); clip-path: polygon(0 0, 91% 0, 100% 50%, 91% 100%, 0 100%); }
.category-intro h2 { margin-top: 6px; font-size: 22px; font-weight: 700; }
.category-intro p { color: #c6e7ff; font-size: 11px; letter-spacing: .08em; }
.category-intro a { display: grid; width: 25px; height: 25px; margin-top: 10px; place-items: center; border: 1px solid rgb(255 255 255 / 65%); border-radius: 50%; }
.desktop-categories { display: grid; min-width: 0; flex: 1; grid-template-columns: repeat(6, 1fr); }
.category-item { position: relative; display: flex; min-width: 0; flex-direction: column; align-items: center; justify-content: center; padding: 13px 6px; text-align: center; }
.desktop-categories .category-item:not(:last-child)::after { content: ""; position: absolute; top: 24px; right: 0; bottom: 24px; width: 1px; background: #edf0f3; }
.category-image { width: 78px; height: 78px; transition: transform .25s ease; }
.category-item:hover .category-image { transform: translateY(-4px) scale(1.04); }
.category-item h3 { margin-top: 2px; color: #263646; font-size: 14px; font-weight: 600; }
.category-item p { color: #98a3ae; font-size: 10px; white-space: nowrap; }
.mobile-categories { display: none; }
@media (max-width: 1000px) { .category-intro { width: 135px; flex-basis: 135px; } .category-item p { display: none; } }
@media (max-width: 767px) {
  .category-section { padding: 20px 0 0; background: transparent; }
  .category-panel { display: block; min-height: 0; overflow: visible; border: 0; border-radius: 12px; box-shadow: 0 7px 24px rgb(38 77 115 / 6%); }
  .category-intro, .desktop-categories { display: none; }
  .mobile-categories { display: grid; grid-template-columns: repeat(6, 1fr); padding: 15px 5px 12px; }
  .category-item { padding: 0 1px; }
  .category-image { width: clamp(38px, 12vw, 54px); height: clamp(38px, 12vw, 54px); }
  .category-item h3 { margin-top: 7px; font-size: clamp(10px, 2.8vw, 12px); font-weight: 500; white-space: nowrap; }
}
</style>
