<script setup lang="ts">
import { ArrowRight, Box, Medal, Service, Van } from '@element-plus/icons-vue'

const advantages = [
  { title: '品质保障', subtitle: '严格质检', description: '严格质量检测\n确保产品质量', icon: Medal },
  { title: '现货充足', subtitle: '多仓储备', description: '多仓储备货\n快速响应需求', icon: Box },
  { title: '快速发货', subtitle: '高效配送', description: '高效物流配送\n准时送达', icon: Van },
  { title: '专业服务', subtitle: '售后无忧', description: '一对一专属服务\n全程售后支持', icon: Service },
]
</script>

<template>
  <section class="advantage-section" aria-labelledby="advantage-title">
    <div class="advantage-panel container">
      <div class="advantage-intro">
        <h2 id="advantage-title">我们的优势</h2>
        <p>选择我们，选择放心</p>
        <RouterLink class="primary-link" to="/about">了解更多<el-icon><ArrowRight /></el-icon></RouterLink>
      </div>
      <div class="advantage-list">
        <div v-for="advantage in advantages" :key="advantage.title" class="advantage-item">
          <el-icon :size="38"><component :is="advantage.icon" /></el-icon>
          <div><h3>{{ advantage.title }}</h3><p class="advantage-subtitle">{{ advantage.subtitle }}</p><p class="advantage-description">{{ advantage.description }}</p></div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.advantage-section { overflow: hidden; background: linear-gradient(105deg, #f4f8fd 0%, #edf4fc 70%, #dcecf9 100%); }
.advantage-panel { position: relative; display: flex; align-items: stretch; min-height: 188px; }
.advantage-panel::after { content: ""; position: absolute; right: -90px; bottom: -110px; width: 330px; height: 330px; border: 45px solid rgb(26 111 214 / 6%); transform: rotate(45deg); pointer-events: none; }
.advantage-intro { display: flex; width: 260px; flex: 0 0 260px; flex-direction: column; align-items: flex-start; justify-content: center; padding: 30px 30px 30px 0; }
.advantage-intro h2 { font-size: 29px; font-weight: 750; letter-spacing: .02em; }
.advantage-intro p { margin-top: 3px; color: #52647a; font-size: 15px; }
.advantage-intro .primary-link { min-height: 34px; margin-top: 18px; padding: 0 20px; border-radius: 18px; font-size: 12px; }
.advantage-list { display: grid; flex: 1; grid-template-columns: repeat(4, 1fr); }
.advantage-item { position: relative; display: flex; align-items: center; justify-content: center; gap: 17px; padding: 30px 16px; color: var(--brand); }
.advantage-item:not(:last-child)::after { content: ""; position: absolute; top: 35px; right: 0; bottom: 35px; width: 1px; background: #d5e0eb; }
.advantage-item h3 { color: #243547; font-size: 16px; font-weight: 650; }
.advantage-subtitle { display: none; }
.advantage-description { margin-top: 9px; color: #7c8996; font-size: 12px; line-height: 1.8; white-space: pre-line; }
@media (max-width: 1000px) { .advantage-intro { width: 210px; flex-basis: 210px; } .advantage-item { flex-direction: column; gap: 8px; text-align: center; } }
@media (max-width: 767px) {
  .advantage-section { padding: 0 16px 22px; background: transparent; }
  .advantage-panel { width: 100%; min-height: 0; border-radius: 11px; background: #eaf2fc; }
  .advantage-panel::after, .advantage-intro { display: none; }
  .advantage-list { grid-template-columns: repeat(3, 1fr); }
  .advantage-item { gap: 8px; padding: 21px 8px; text-align: left; }
  .advantage-item .el-icon { flex: 0 0 auto; font-size: 30px; }
  .advantage-item:nth-child(2) { display: none; }
  .advantage-item:not(:last-child)::after { top: 20px; bottom: 20px; }
  .advantage-item h3 { font-size: 13px; white-space: nowrap; }
  .advantage-subtitle { display: block; margin-top: 2px; color: #7b8999; font-size: 11px; }
  .advantage-description { display: none; }
}
@media (max-width: 360px) { .advantage-item { gap: 5px; padding-inline: 5px; } .advantage-item .el-icon { font-size: 25px; } .advantage-item h3 { font-size: 12px; } }
</style>
