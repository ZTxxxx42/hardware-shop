<script setup lang="ts">
import { ArrowRight } from '@element-plus/icons-vue'
import heroUrl from '@/assets/scenes/hero-industrial.svg'

const slides = [
  { title: '品质五金', accent: '助力高效生产', subtitle: '一站式五金采购平台', action: '立即选购' },
  { title: '现货充足', accent: '交付快人一步', subtitle: '多仓备货 · 快速响应', action: '查看产品' },
  { title: '专业服务', accent: '采购省心无忧', subtitle: '选型支持 · 售后保障', action: '咨询客服' },
]
</script>

<template>
  <section class="hero-section" aria-label="恒泰五金一站式采购平台">
    <div class="desktop-hero" :style="{ backgroundImage: `url(${heroUrl})` }">
      <div class="hero-shade"></div>
      <div class="hero-content container">
        <div class="hero-eyebrow"><span></span>专业 · 品质 · 共赢<span></span></div>
        <h1>一站式<em>五金</em>商贸平台</h1>
        <p>优质五金产品 · 可靠品质保障 · 助力您的项目与事业</p>
        <RouterLink class="primary-link" to="/about">了解更多<el-icon><ArrowRight /></el-icon></RouterLink>
      </div>
      <span class="hero-caption">HENGTAI · INDUSTRIAL SUPPLY</span>
    </div>

    <div class="mobile-hero container">
      <el-carousel height="100%" :interval="5000" arrow="never" pause-on-hover>
        <el-carousel-item v-for="(slide, index) in slides" :key="slide.title">
          <div class="mobile-slide" :style="{ backgroundImage: `url(${heroUrl})` }">
            <div class="mobile-slide__shade"></div>
            <div class="mobile-slide__content">
              <h1>{{ slide.title }}<br /><em>{{ slide.accent }}</em></h1>
              <p><span></span>{{ slide.subtitle }}<span></span></p>
              <RouterLink :to="index === 2 ? '/contact' : '/products'">{{ slide.action }}<el-icon><ArrowRight /></el-icon></RouterLink>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </div>
  </section>
</template>

<style scoped>
.desktop-hero { position: relative; height: clamp(390px, 36vw, 500px); overflow: hidden; background-position: center; background-size: cover; }
.hero-shade { position: absolute; inset: 0; background: linear-gradient(90deg, rgb(5 25 45 / 88%) 0%, rgb(7 31 54 / 68%) 35%, rgb(9 33 52 / 10%) 66%, transparent 100%); }
.hero-content { position: relative; z-index: 1; display: flex; height: 100%; flex-direction: column; align-items: flex-start; justify-content: center; padding-bottom: 12px; color: #fff; }
.hero-eyebrow { display: flex; align-items: center; gap: 15px; margin-bottom: 16px; font-size: 16px; font-weight: 600; letter-spacing: .16em; }
.hero-eyebrow span { width: 40px; height: 1px; background: #b9d8f1; }
.hero-content h1 { font-size: clamp(38px, 4.2vw, 59px); font-weight: 800; line-height: 1.2; letter-spacing: .025em; text-shadow: 0 3px 14px rgb(0 0 0 / 16%); }
.hero-content h1 em { color: #38a9f5; font-style: normal; }
.hero-content p { margin: 18px 0 30px; color: #eef6fc; font-size: clamp(15px, 1.5vw, 19px); letter-spacing: .045em; }
.hero-caption { position: absolute; right: 28px; bottom: 18px; color: rgb(255 255 255 / 48%); font-family: Arial, sans-serif; font-size: 10px; letter-spacing: .2em; writing-mode: vertical-rl; }
.mobile-hero { display: none; }
@media (max-width: 767px) {
  .desktop-hero { display: none; }
  .mobile-hero { display: block; height: 270px; }
  .mobile-slide { position: relative; height: 100%; overflow: hidden; border-radius: 13px; background-position: 67% center; background-size: cover; box-shadow: 0 12px 28px rgb(27 91 149 / 13%); }
  .mobile-slide__shade { position: absolute; inset: 0; background: linear-gradient(90deg, rgb(5 74 148 / 96%), rgb(20 120 210 / 68%) 47%, rgb(9 47 77 / 3%) 78%); }
  .mobile-slide__content { position: relative; z-index: 1; display: flex; height: 100%; flex-direction: column; align-items: flex-start; justify-content: center; padding: 22px; color: #fff; }
  .mobile-slide h1 { font-size: clamp(25px, 7vw, 31px); font-weight: 800; line-height: 1.34; letter-spacing: .02em; }
  .mobile-slide h1 em { font-style: normal; }
  .mobile-slide p { display: flex; align-items: center; gap: 7px; margin: 9px 0 17px; color: #e5f3ff; font-size: 12px; white-space: nowrap; }
  .mobile-slide p span { width: 10px; height: 1px; background: #d5ecff; }
  .mobile-slide a { display: inline-flex; align-items: center; gap: 7px; min-height: 36px; padding: 0 17px; border: 1px solid rgb(255 255 255 / 24%); border-radius: 19px; color: #fff; background: linear-gradient(110deg, #278de4, #0865c5); box-shadow: 0 6px 15px rgb(0 56 123 / 22%); font-size: 13px; font-weight: 600; }
  .mobile-hero :deep(.el-carousel) { height: 100%; }
  .mobile-hero :deep(.el-carousel__indicators--horizontal) { bottom: -2px; }
  .mobile-hero :deep(.el-carousel__indicator--horizontal) { padding: 8px 3px; }
  .mobile-hero :deep(.el-carousel__button) { background: var(--brand); }
}
@media (max-width: 360px) { .mobile-hero { height: 240px; } .mobile-slide__content { padding: 17px; } .mobile-slide h1 { font-size: 24px; } }
</style>
