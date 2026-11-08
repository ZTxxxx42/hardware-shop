<script setup lang="ts">
import { ArrowRight } from '@element-plus/icons-vue'
import { newsItems } from '@/data/home'
import fastenersUrl from '@/assets/products/bolt.svg'
import drillUrl from '@/assets/categories/drill.svg'
import bearingUrl from '@/assets/products/bearing.svg'
</script>

<template>
  <section class="news-section" aria-labelledby="news-title">
    <div class="news-grid container">
      <div class="news-intro">
        <h2 id="news-title">新闻资讯</h2><span>NEWS CENTER</span><p>了解行业动态，掌握最新资讯</p>
        <RouterLink class="news-more" to="/news">查看更多<el-icon><ArrowRight /></el-icon></RouterLink>
      </div>
      <div class="news-list">
        <img :src="fastenersUrl" alt="不锈钢紧固件" width="480" height="360" loading="lazy" />
        <div>
          <RouterLink v-for="news in newsItems" :key="news.id" to="/news" class="news-item">
            <time><strong>{{ news.date }}</strong><span>{{ news.year }}</span></time>
            <div><h3>{{ news.title }}</h3><p>{{ news.summary }}</p></div>
          </RouterLink>
        </div>
      </div>
      <RouterLink class="news-promo" to="/products">
        <img class="promo-bearing" :src="bearingUrl" alt="" /><img class="promo-drill" :src="drillUrl" alt="" />
        <div><h3>品质五金<br />成就更好工程</h3><p>专业 · 高效 · 可靠</p><span>立即咨询<el-icon><ArrowRight /></el-icon></span></div>
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.news-section { padding: 14px 0 44px; background: #fff; }
.news-grid { display: grid; grid-template-columns: .55fr 1.25fr .9fr; align-items: center; gap: 34px; padding-top: 28px; border-top: 1px solid var(--line); }
.news-intro h2 { font-size: 25px; font-weight: 750; }
.news-intro > span { color: #6c7f91; font-family: Arial, sans-serif; font-size: 11px; letter-spacing: .09em; }
.news-intro p { margin-top: 14px; color: #8a96a2; font-size: 12px; }
.news-more { display: inline-flex; align-items: center; gap: 12px; margin-top: 17px; padding: 5px 14px; border: 1px solid #a6b5c3; border-radius: 17px; color: #5f7081; font-size: 11px; }
.news-list { display: grid; grid-template-columns: 145px 1fr; align-items: center; gap: 15px; }
.news-list > img { width: 145px; height: 145px; border-radius: 7px; object-fit: cover; background: #e5f2fc; }
.news-item { display: grid; grid-template-columns: 52px 1fr; gap: 12px; }
.news-item + .news-item { margin-top: 18px; }
.news-item time { display: flex; flex-direction: column; padding-top: 2px; color: var(--brand); }
.news-item time strong { font-family: Arial, sans-serif; font-size: 17px; }
.news-item time span { color: #a4afba; font-family: Arial, sans-serif; font-size: 10px; }
.news-item h3 { overflow: hidden; color: #2d3a47; font-size: 13px; font-weight: 600; text-overflow: ellipsis; white-space: nowrap; }
.news-item p { display: -webkit-box; margin-top: 5px; overflow: hidden; color: #98a2ac; font-size: 10px; line-height: 1.6; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.news-item:hover h3 { color: var(--brand); }
.news-promo { position: relative; min-height: 148px; overflow: hidden; border-radius: 8px; color: #fff; background: linear-gradient(115deg, #0a3c68, #116da8); }
.news-promo > div { position: relative; z-index: 2; padding: 19px 22px; }
.news-promo h3 { font-size: 22px; line-height: 1.3; letter-spacing: .04em; }
.news-promo p { margin-top: 4px; color: #aed7ee; font-size: 10px; }
.news-promo span { display: inline-flex; align-items: center; gap: 8px; margin-top: 10px; padding: 3px 12px; border-radius: 3px; color: #263848; background: #f5bd43; font-size: 10px; font-weight: 600; }
.promo-bearing { position: absolute; right: -30px; bottom: -45px; width: 200px; opacity: .75; }
.promo-drill { position: absolute; z-index: 1; right: 48px; bottom: 3px; width: 105px; transform: rotate(-18deg); }
@media (max-width: 1050px) { .news-grid { grid-template-columns: .45fr 1.3fr; } .news-promo { display: none; } }
@media (max-width: 767px) { .news-section { display: none; } }
</style>
