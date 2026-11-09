<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Box, CreditCard, Expand, Files, Fold, PriceTag, Tickets, User } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import logoUrl from '@/assets/logo-mark.svg'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const isCollapsed = ref(false)
const isMobile = ref(false)
const mobileOpen = ref(false)
const media = window.matchMedia('(max-width: 900px)')
const asideWidth = computed(() => (isCollapsed.value ? '72px' : '232px'))
const currentTitle = computed(() => route.meta.title ?? '运营管理')
const menuItems = [
  { path: '/products', title: '商品管理', icon: Box },
  { path: '/categories', title: '分类管理', icon: Files },
  { path: '/prices', title: '价格管理', icon: PriceTag },
  { path: '/customers', title: '客户管理', icon: User },
  { path: '/orders', title: '订单管理', icon: Tickets },
  { path: '/payments', title: '支付流水', icon: CreditCard },
]
function handleViewport(event: MediaQueryListEvent) {
  isMobile.value = event.matches
  if (!event.matches) mobileOpen.value = false
}
function toggleSidebar() {
  if (isMobile.value) mobileOpen.value = !mobileOpen.value
  else isCollapsed.value = !isCollapsed.value
}
async function handleCommand(command: string) {
  if (command !== 'logout') return
  await ElMessageBox.confirm('退出后需要重新登录管理后台。', '确认退出', {
    confirmButtonText: '退出登录', cancelButtonText: '取消', type: 'warning',
  })
  auth.logout()
  await router.replace('/login')
}
watch(() => route.fullPath, () => { mobileOpen.value = false })
onMounted(() => {
  isMobile.value = media.matches
  media.addEventListener('change', handleViewport)
})
onBeforeUnmount(() => media.removeEventListener('change', handleViewport))
</script>

<template>
  <div class="admin-shell">
    <a class="skip-link" href="#main-content">跳至主内容</a>
    <button v-if="mobileOpen" class="sidebar-backdrop" aria-label="关闭导航" @click="mobileOpen = false" />
    <aside class="admin-sidebar" :class="{ 'is-mobile-open': mobileOpen }" :style="{ width: asideWidth }">
      <div class="brand" :class="{ 'is-collapsed': isCollapsed && !isMobile }">
        <img :src="logoUrl" alt="" class="brand-mark" />
        <div v-show="!isCollapsed || isMobile" class="brand-copy"><strong>恒固五金</strong><span>运营管理</span></div>
      </div>
      <div v-show="!isCollapsed || isMobile" class="nav-caption">业务管理</div>
      <el-menu :default-active="route.path" :collapse="isCollapsed && !isMobile" :collapse-transition="false" router class="sidebar-menu">
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon><template #title>{{ item.title }}</template>
        </el-menu-item>
      </el-menu>
      <div v-show="!isCollapsed || isMobile" class="sidebar-foot"><span class="status-dot" />真实 API 环境</div>
    </aside>
    <section class="admin-workspace">
      <header class="admin-header">
        <div class="header-left">
          <button class="icon-button" :aria-label="isMobile ? '打开导航' : '折叠或展开导航'" @click="toggleSidebar">
            <el-icon :size="19"><Fold v-if="!isCollapsed || isMobile" /><Expand v-else /></el-icon>
          </button>
          <el-breadcrumb separator="/"><el-breadcrumb-item>管理后台</el-breadcrumb-item><el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item></el-breadcrumb>
        </div>
        <div class="header-right">
          <span class="demo-badge">管理后台</span>
          <el-dropdown trigger="click" @command="handleCommand">
            <button class="user-trigger"><span class="user-avatar">管</span><span class="user-copy"><strong>{{ auth.user?.name ?? '管理员' }}</strong><small>系统管理员</small></span></button>
            <template #dropdown><el-dropdown-menu><el-dropdown-item disabled>{{ auth.user?.username }}</el-dropdown-item><el-dropdown-item divided command="logout">退出登录</el-dropdown-item></el-dropdown-menu></template>
          </el-dropdown>
        </div>
      </header>
      <main id="main-content" class="admin-main">
        <router-view v-slot="{ Component }"><transition name="page-fade" mode="out-in"><component :is="Component" /></transition></router-view>
      </main>
    </section>
  </div>
</template>

<style scoped>
.admin-shell { min-height: 100vh; }
.skip-link { position: fixed; z-index: 3000; top: 8px; left: 8px; padding: 8px 12px; color: #fff; background: #1a6fd6; border-radius: 6px; transform: translateY(-150%); }
.skip-link:focus { transform: translateY(0); }
.admin-sidebar { position: fixed; z-index: 1001; inset: 0 auto 0 0; display: flex; flex-direction: column; overflow: hidden; color: #c6d3e3; background: #10233f; border-right: 1px solid rgba(255,255,255,.04); transition: width .2s ease, transform .2s ease; }
.brand { display: flex; align-items: center; gap: 11px; height: 72px; padding: 0 20px; border-bottom: 1px solid rgba(255,255,255,.08); }
.brand.is-collapsed { justify-content: center; padding: 0; }
.brand-mark { flex: none; width: 34px; height: 34px; }
.brand-copy { display: flex; flex-direction: column; white-space: nowrap; }
.brand-copy strong { color: #fff; font-size: 16px; font-weight: 650; letter-spacing: .08em; }
.brand-copy span { margin-top: 3px; color: #8197b3; font-size: 10px; letter-spacing: .24em; }
.nav-caption { padding: 24px 22px 9px; color: #6f88a7; font-size: 10px; letter-spacing: .16em; white-space: nowrap; }
.sidebar-menu { flex: 1; border: 0; background: transparent; }
.sidebar-menu:not(.el-menu--collapse) { width: 232px; }
.sidebar-menu :deep(.el-menu-item) { height: 48px; margin: 3px 12px; color: #aebdd0; border-radius: 7px; }
.sidebar-menu :deep(.el-menu-item:hover) { color: #fff; background: rgba(255,255,255,.06); }
.sidebar-menu :deep(.el-menu-item.is-active) { color: #fff; background: #1a6fd6; box-shadow: 0 5px 16px rgba(4,20,43,.22); }
.sidebar-menu.el-menu--collapse :deep(.el-menu-item) { margin: 3px 8px; }
.sidebar-foot { display: flex; align-items: center; gap: 8px; margin: 16px; padding: 12px; color: #8fa2b9; font-size: 11px; white-space: nowrap; background: rgba(255,255,255,.035); border: 1px solid rgba(255,255,255,.06); border-radius: 7px; }
.status-dot { width: 6px; height: 6px; background: #55b98a; border-radius: 50%; box-shadow: 0 0 0 3px rgba(85,185,138,.12); }
.admin-workspace { min-height: 100vh; margin-left: v-bind(asideWidth); transition: margin-left .2s ease; }
.admin-header { position: sticky; z-index: 100; top: 0; display: flex; align-items: center; justify-content: space-between; height: 64px; padding: 0 26px; background: rgba(255,255,255,.96); border-bottom: 1px solid #e3eaf3; backdrop-filter: blur(10px); }
.header-left, .header-right { display: flex; align-items: center; gap: 18px; }
.icon-button { display: inline-flex; align-items: center; justify-content: center; width: 34px; height: 34px; padding: 0; color: #52647c; cursor: pointer; background: transparent; border: 0; border-radius: 6px; }
.icon-button:hover { color: #1a6fd6; background: #edf3fa; }
.demo-badge { padding: 4px 8px; color: #52647c; font-size: 11px; background: #f1f5f9; border: 1px solid #e3eaf3; border-radius: 4px; }
.user-trigger { display: flex; align-items: center; gap: 10px; padding: 3px 0; text-align: left; cursor: pointer; background: transparent; border: 0; }
.user-avatar { display: grid; width: 34px; height: 34px; place-items: center; color: #1a6fd6; font-size: 13px; font-weight: 650; background: #e9f2fd; border-radius: 8px; }
.user-copy { display: flex; flex-direction: column; gap: 2px; }
.user-copy strong { color: #273a52; font-size: 12px; font-weight: 600; }
.user-copy small { color: #8492a6; font-size: 10px; }
.admin-main { padding: 26px; }
.page-fade-enter-active, .page-fade-leave-active { transition: opacity .12s ease; }
.page-fade-enter-from, .page-fade-leave-to { opacity: 0; }
.sidebar-backdrop { display: none; }
@media (max-width: 900px) {
  .admin-sidebar { width: 232px !important; transform: translateX(-100%); }
  .admin-sidebar.is-mobile-open { transform: translateX(0); }
  .admin-workspace { margin-left: 0; }
  .sidebar-backdrop { position: fixed; z-index: 1000; inset: 0; display: block; padding: 0; cursor: pointer; background: rgba(9,24,43,.45); border: 0; }
}
@media (max-width: 600px) {
  .admin-header { padding: 0 14px; }
  .admin-main { padding: 18px 14px; }
  .header-left { gap: 8px; }
  .demo-badge, .user-copy { display: none; }
}
</style>
