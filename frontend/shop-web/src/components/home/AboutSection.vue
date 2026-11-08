<script setup lang="ts">
import { ArrowRight, Location, Medal, User } from '@element-plus/icons-vue'
import factoryUrl from '@/assets/scenes/factory-building.svg'

const stats = [
  { value: '10+', label: '年行业经验', icon: Medal },
  { value: '1000+', label: '合作客户', icon: User },
  { value: '覆盖全国', label: '多地服务', icon: Location },
]
</script>

<template>
  <section class="about-section section" aria-labelledby="about-title">
    <div class="about-grid container">
      <div class="about-visual">
        <img :src="factoryUrl" alt="恒泰五金商贸仓储与服务中心" width="900" height="520" loading="lazy" />
        <span>HENGTAI HARDWARE</span>
      </div>
      <div class="about-copy">
        <div class="about-title"><h2 id="about-title">关于我们</h2><span>ABOUT US</span></div>
        <p>恒泰五金商贸有限公司是一家专业从事五金产品批发与零售的综合性企业，致力于为客户提供高品质的五金工具、紧固件、建筑五金及机械配件等产品。</p>
        <p>我们秉承“品质为本、客户至上”的经营理念，竭诚为广大客户提供优质的产品与专业的服务。</p>
        <RouterLink class="primary-link" to="/about">了解更多<el-icon><ArrowRight /></el-icon></RouterLink>
      </div>
      <div class="about-stats">
        <div v-for="stat in stats" :key="stat.label" class="stat-item">
          <el-icon :size="30"><component :is="stat.icon" /></el-icon>
          <div><strong>{{ stat.value }}</strong><span>{{ stat.label }}</span></div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.about-section { background: #fff; }
.about-grid { display: grid; grid-template-columns: 1.12fr 1fr .48fr; align-items: center; gap: 38px; }
.about-visual { position: relative; overflow: hidden; border-radius: 9px; box-shadow: var(--shadow-sm); }
.about-visual img { width: 100%; aspect-ratio: 1.7; object-fit: cover; }
.about-visual > span { position: absolute; bottom: 0; left: 0; padding: 7px 14px; color: #fff; background: rgb(10 61 111 / 85%); font-family: Arial, sans-serif; font-size: 9px; letter-spacing: .16em; }
.about-title { display: flex; flex-direction: column; margin-bottom: 17px; }
.about-title h2 { font-size: 29px; font-weight: 750; }
.about-title span { color: #a7b0b9; font-family: Arial, sans-serif; font-size: 11px; letter-spacing: .16em; }
.about-copy > p { margin-bottom: 10px; color: #657487; font-size: 13px; line-height: 1.9; text-align: justify; }
.about-copy .primary-link { min-height: 35px; margin-top: 8px; border-radius: 18px; font-size: 12px; }
.about-stats { padding: 20px 25px; border-radius: 9px; background: #f7f9fc; }
.stat-item { display: flex; align-items: center; gap: 15px; color: #0794d2; }
.stat-item + .stat-item { margin-top: 23px; }
.stat-item > div { display: flex; flex-direction: column; }
.stat-item strong { color: #1e3145; font-family: Arial, "Microsoft YaHei", sans-serif; font-size: 20px; line-height: 1.3; }
.stat-item span { color: #83909d; font-size: 12px; }
@media (max-width: 1000px) { .about-grid { grid-template-columns: 1fr 1fr; } .about-stats { display: none; } }
@media (max-width: 767px) { .about-section { display: none; } }
</style>
