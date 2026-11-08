<script setup lang="ts">
import { Location, Message, Phone } from '@element-plus/icons-vue'
import BrandLogo from '@/components/BrandLogo.vue'
import qrCodeUrl from '@/assets/contact/service-qr.png'

const productLinks = ['手动工具', '电动工具', '紧固件', '建筑五金', '机械配件']
</script>

<template>
  <footer class="site-footer">
    <div class="footer-main container">
      <div class="footer-brand">
        <RouterLink to="/"><BrandLogo inverse /></RouterLink>
        <p>与您携手，共创更大价值</p>
        <span>品质五金 · 专业服务 · 值得信赖</span>
      </div>
      <div class="footer-column">
        <h3>快速链接</h3>
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/products">产品中心</RouterLink>
        <RouterLink to="/about">关于我们</RouterLink>
        <RouterLink to="/news">新闻资讯</RouterLink>
        <RouterLink to="/contact">联系我们</RouterLink>
      </div>
      <div class="footer-column">
        <h3>产品分类</h3>
        <RouterLink v-for="(item, index) in productLinks" :key="item" :to="{ path: '/products', query: { category: index + 1 } }">{{ item }}</RouterLink>
      </div>
      <div class="footer-contact">
        <h3>联系我们</h3>
        <a href="tel:400-123-4567"><el-icon><Phone /></el-icon><strong>400-123-4567</strong></a>
        <p><el-icon><Location /></el-icon>上海市浦东新区金科路88号</p>
        <a href="mailto:info@hengtai.com"><el-icon><Message /></el-icon>info@hengtai.com</a>
      </div>
      <div class="footer-qr">
        <img :src="qrCodeUrl" alt="扫码拨打恒泰客服热线" width="106" height="106" />
        <p>扫码联系客服<br />获取更多资讯</p>
      </div>
    </div>
    <div class="footer-bottom container">
      <p>Copyright © 2025 恒泰五金商贸有限公司　版权所有　备案号：沪ICP备12345678号</p>
      <div><a href="#privacy">隐私政策</a><span>|</span><a href="#terms">使用条款</a></div>
    </div>
  </footer>
</template>

<style scoped>
.site-footer { color: #c5d0dc; background: var(--brand-deep); }
.footer-main { display: grid; grid-template-columns: 1.45fr .75fr .75fr 1.25fr .75fr; gap: 40px; padding-top: 44px; padding-bottom: 35px; }
.footer-brand p { margin-top: 24px; color: #e2e8ef; font-size: 15px; }
.footer-brand > span { display: block; margin-top: 6px; color: #8296aa; font-size: 12px; }
.footer-column, .footer-contact { display: flex; flex-direction: column; align-items: flex-start; gap: 8px; }
.footer-column h3, .footer-contact h3 { margin-bottom: 8px; color: #fff; font-size: 15px; font-weight: 600; }
.footer-column a { color: #aebdcc; font-size: 13px; transition: color .2s, transform .2s; }
.footer-column a:hover { color: #fff; transform: translateX(3px); }
.footer-contact a, .footer-contact p { display: flex; align-items: center; gap: 8px; color: #b8c6d3; font-size: 12px; }
.footer-contact strong { color: #fff; font-family: Arial, sans-serif; font-size: 17px; }
.footer-contact .el-icon { color: #fff; font-size: 16px; }
.footer-qr { text-align: center; }
.footer-qr img { width: 98px; height: 98px; margin: 0 auto; padding: 5px; border-radius: 3px; background: #fff; }
.footer-qr p { margin-top: 9px; color: #afbecd; font-size: 11px; line-height: 1.7; }
.footer-bottom { display: flex; justify-content: space-between; gap: 20px; padding-top: 16px; padding-bottom: 16px; border-top: 1px solid rgb(255 255 255 / 9%); color: #8295a9; font-size: 11px; }
.footer-bottom div { display: flex; gap: 14px; white-space: nowrap; }
.footer-bottom a:hover { color: #fff; }
@media (max-width: 1024px) { .footer-main { grid-template-columns: 1.4fr .7fr .7fr 1.2fr; gap: 28px; } .footer-qr { display: none; } }
@media (max-width: 767px) { .site-footer { display: none; } }
</style>
