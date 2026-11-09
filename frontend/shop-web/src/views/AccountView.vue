<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Location, ShoppingCart, Tickets } from '@element-plus/icons-vue'
import { memberApi } from '@/api/member'
import { getErrorMessage } from '@/api/http'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'
import type { Level, Profile } from '@/types/shop'
import RequestState from '@/components/RequestState.vue'

const router = useRouter()
const userStore = useUserStore()
const cartStore = useCartStore()
const profile = ref<Profile | null>(null)
const level = ref<Level | null>(null)
const loading = ref(true)
const error = ref('')

async function loadProfile() {
  loading.value = true
  error.value = ''
  try {
    const [profileData, levelData] = await Promise.all([memberApi.profile(), memberApi.level()])
    profile.value = profileData
    level.value = levelData
  } catch (requestError) {
    error.value = getErrorMessage(requestError, '会员信息加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

function logout() {
  userStore.logout()
  cartStore.clear()
  ElMessage.success('已退出登录')
  void router.push('/')
}

onMounted(loadProfile)
</script>

<template>
  <section class="account-page">
    <div class="container">
      <nav class="breadcrumb" aria-label="面包屑"><RouterLink to="/">首页</RouterLink><span>/</span><span>个人中心</span></nav>
      <RequestState
        v-if="loading || error || !profile"
        :loading="loading"
        :error="error"
        :empty="!loading && !error"
        loading-text="正在加载会员信息..."
        @retry="loadProfile"
      />
      <template v-else>
        <div class="account-card">
          <div class="account-avatar">{{ profile.username.slice(0, 1).toUpperCase() }}</div>
          <div class="account-info">
            <h1>{{ profile.username }}</h1>
            <div class="account-tags">
              <el-tag type="primary" effect="light">{{ profile.level_name ?? '普通会员' }}</el-tag>
              <el-tag v-if="level" effect="plain" type="info">{{ level.name }}</el-tag>
            </div>
            <p>客户编号：{{ profile.user_id }}</p>
          </div>
          <el-button plain @click="logout">退出登录</el-button>
        </div>

        <div class="profile-grid">
          <div class="profile-item"><span>手机号码</span><strong>{{ profile.phone || '未填写' }}</strong></div>
          <div class="profile-item"><span>客户等级</span><strong>{{ profile.level_name ?? '普通会员' }}</strong></div>
          <div class="profile-item"><span>联系人</span><strong>{{ profile.real_name || '未填写' }}</strong></div>
          <div class="profile-item"><span>登录账号</span><strong>{{ profile.username }}</strong></div>
        </div>

        <div class="quick-links">
          <RouterLink to="/orders" class="quick-link"><el-icon :size="22"><Tickets /></el-icon><span>我的订单</span></RouterLink>
          <RouterLink to="/addresses" class="quick-link"><el-icon :size="22"><Location /></el-icon><span>收货地址</span></RouterLink>
          <RouterLink to="/cart" class="quick-link"><el-icon :size="22"><ShoppingCart /></el-icon><span>购物车</span></RouterLink>
        </div>
      </template>
    </div>
  </section>
</template>

<style scoped>
.account-page { min-height: 620px; padding: 26px 0 70px; background: #f5f8fb; }
.breadcrumb { display: flex; gap: 10px; color: #8b97a4; font-size: 12px; }
.account-card { display: flex; align-items: center; gap: 20px; margin-top: 34px; padding: 28px 30px; border: 1px solid #e7edf3; border-radius: 14px; background: #fff; box-shadow: var(--shadow-sm); }
.account-avatar { display: grid; width: 72px; height: 72px; flex: 0 0 auto; place-items: center; border-radius: 22px; color: #fff; background: linear-gradient(135deg, var(--brand-dark), #2b96e9); font-size: 28px; font-weight: 700; }
.account-info { min-width: 0; flex: 1; }
.account-info h1 { font-size: 24px; }
.account-tags { display: flex; gap: 8px; margin-top: 7px; }
.account-info > p { margin-top: 9px; color: #8a97a5; font-size: 12px; }
.profile-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin-top: 16px; }
.profile-item { padding: 18px 20px; border: 1px solid #e7edf3; border-radius: 11px; background: #fff; }
.profile-item span { display: block; color: #95a2af; font-size: 11px; }
.profile-item strong { display: block; margin-top: 5px; color: #3c4e61; font-size: 15px; }
.quick-links { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 16px; }
.quick-link { display: flex; align-items: center; justify-content: center; gap: 10px; padding: 20px; border: 1px solid #e7edf3; border-radius: 11px; color: #4e6073; background: #fff; font-size: 14px; font-weight: 600; transition: border-color .2s, color .2s; }
.quick-link:hover { border-color: #b9d7f4; color: var(--brand); }
@media (max-width: 767px) {
  .account-page { padding-top: 18px; }
  .account-card { flex-wrap: wrap; margin-top: 22px; padding: 24px 20px; }
  .account-info h1 { font-size: 21px; }
  .profile-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
  .quick-links { gap: 10px; }
  .quick-link { flex-direction: column; gap: 6px; padding: 16px 10px; font-size: 12px; }
}
</style>
