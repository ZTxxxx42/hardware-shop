<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Lock, User } from '@element-plus/icons-vue'
import { authApi } from '@/api/auth'
import { getErrorMessage } from '@/api/http'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const cartStore = useCartStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

const redirect = computed(() => (typeof route.query.redirect === 'string' && route.query.redirect ? route.query.redirect : '/account'))

const rules: FormRules = {
  username: [{ required: true, message: '请输入会员账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const session = await authApi.login({ username: form.username.trim(), password: form.password })
    userStore.setSession(session.access_token, session.user)
    void cartStore.load().catch(() => {})
    ElMessage.success('登录成功')
    await router.push(redirect.value)
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '登录失败，请检查账号密码'))
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="auth-page">
    <div class="container">
      <nav class="breadcrumb" aria-label="面包屑"><RouterLink to="/">首页</RouterLink><span>/</span><span>会员登录</span></nav>
      <div class="auth-card">
        <div class="auth-heading">
          <span>MEMBER LOGIN</span>
          <h1>会员登录</h1>
          <p>登录后可查看会员价格、管理购物车并提交订单</p>
        </div>
        <el-form ref="formRef" class="auth-form" :model="form" :rules="rules" label-position="top" @submit.prevent="submit">
          <el-form-item label="会员账号" prop="username">
            <el-input v-model="form.username" size="large" placeholder="请输入会员账号" autocomplete="username" :prefix-icon="User" clearable />
          </el-form-item>
          <el-form-item label="登录密码" prop="password">
            <el-input v-model="form.password" size="large" type="password" placeholder="请输入密码" autocomplete="current-password" :prefix-icon="Lock" show-password @keyup.enter="submit" />
          </el-form-item>
          <el-button class="auth-submit" type="primary" size="large" :loading="loading" @click="submit">登录</el-button>
        </el-form>
        <p class="auth-switch">还没有采购账户？<RouterLink to="/register">立即注册</RouterLink></p>
        <p class="auth-tip">测试会员账号：member / member123</p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.auth-page { min-height: 620px; padding: 26px 0 70px; background: #f5f8fb; }
.breadcrumb { display: flex; gap: 10px; color: #8b97a4; font-size: 12px; }
.auth-card { width: min(430px, 100%); margin: 34px auto 0; padding: 40px 42px 36px; border: 1px solid #e7edf3; border-radius: 14px; background: #fff; box-shadow: var(--shadow-sm); }
.auth-heading { text-align: center; }
.auth-heading > span { color: var(--brand); font-family: Arial, sans-serif; font-size: 10px; letter-spacing: .2em; }
.auth-heading h1 { margin-top: 4px; font-size: 28px; font-weight: 750; }
.auth-heading p { margin-top: 8px; color: #7b8998; font-size: 13px; }
.auth-form { margin-top: 28px; }
.auth-form :deep(.el-form-item__label) { padding-bottom: 6px; color: #46586b; font-size: 13px; }
.auth-submit { width: 100%; height: 46px; margin-top: 4px; font-size: 15px; }
.auth-switch { margin-top: 22px; color: #7b8998; font-size: 13px; text-align: center; }
.auth-switch a { color: var(--brand); font-weight: 600; }
.auth-tip { margin-top: 18px; padding-top: 16px; border-top: 1px dashed #e2e9f0; color: #a0abb7; font-size: 12px; text-align: center; }
@media (max-width: 767px) {
  .auth-page { padding-top: 18px; }
  .auth-card { margin-top: 22px; padding: 30px 22px 30px; }
  .auth-heading h1 { font-size: 25px; }
  .auth-heading p { font-size: 12px; }
}
</style>
