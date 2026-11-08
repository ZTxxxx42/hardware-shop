<script setup lang="ts">
import SiteHeader from '@/components/layout/SiteHeader.vue'
import SiteFooter from '@/components/layout/SiteFooter.vue'
import MobileTabbar from '@/components/layout/MobileTabbar.vue'
</script>

<template>
  <div class="app-shell">
    <a class="skip-link" href="#main-content">跳到主要内容</a>
    <SiteHeader />
    <main id="main-content" class="page-main">
      <RouterView />
    </main>
    <SiteFooter />
    <MobileTabbar />
  </div>
</template>

<style scoped>
.skip-link { position: fixed; z-index: 100; top: 8px; left: 8px; padding: 8px 14px; border-radius: 4px; color: #fff; background: var(--brand); transform: translateY(-160%); }
.skip-link:focus { transform: translateY(0); }
@media (max-width: 767px) { .app-shell { padding-bottom: calc(66px + env(safe-area-inset-bottom)); } }
</style>
