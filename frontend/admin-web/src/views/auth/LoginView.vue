<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Lock, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { showRequestError } from '@/api/error'
import logoUrl from '@/assets/logo.svg'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const form = reactive({ username: 'admin', password: 'admin123' })
const rules: FormRules<typeof form> = {
  username: [{ required: true, message: '请输入管理员账号', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
}
async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    ElMessage.success('登录成功')
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/products'
    await router.replace(redirect)
  } catch (error) {
    showRequestError(error, '登录失败，请检查账号与密码')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <section class="login-story">
      <div class="story-brand"><img :src="logoUrl" alt="" /><span>恒泰五金</span></div>
      <div class="story-content">
        <p class="story-eyebrow">HARDWARE TRADE OPERATIONS</p>
        <h1>把每一笔订货，<br />落实到每一件五金。</h1>
        <p>商品、分级价格、客户与订单集中管理，<br />让日常商贸业务清晰可查。</p>
        <div class="story-lines"><span>商品与库存维护</span><span>客户分级定价</span><span>订单支付对账</span></div>
      </div>
      <small>HENGTAI HARDWARE · ADMIN CONSOLE</small>
    </section>
    <section class="login-form-section">
      <div class="login-box">
        <div class="mobile-brand"><img :src="logoUrl" alt="" /><strong>恒泰五金</strong></div>
        <p class="login-kicker">管理后台</p>
        <h2>欢迎回来</h2>
        <p class="login-intro">使用管理员账号进入运营管理系统</p>
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" size="large" @submit.prevent="submit">
          <el-form-item label="管理员账号" prop="username">
            <el-input v-model="form.username" :prefix-icon="User" autocomplete="username" placeholder="请输入管理员账号" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" :prefix-icon="Lock" type="password" show-password autocomplete="current-password" placeholder="请输入密码" />
          </el-form-item>
          <el-button class="login-button" type="primary" native-type="submit" :loading="loading">登录管理后台</el-button>
        </el-form>
        <div class="demo-note"><strong>管理员登录</strong><span>使用后端管理员账号 admin，密码 admin123。登录状态由 JWT 凭证维持。</span></div>
      </div>
      <footer>恒泰五金商贸 · MVP</footer>
    </section>
  </main>
</template>

<style scoped>
.login-page { display: grid; grid-template-columns: minmax(400px, 1fr) minmax(480px, .9fr); min-height: 100vh; background: #fff; }
.login-story { position: relative; display: flex; flex-direction: column; justify-content: space-between; overflow: hidden; padding: 42px 56px; color: #fff; background: #10233f; }
.login-story::after { position: absolute; right: -140px; bottom: -140px; width: 420px; height: 420px; content: ""; border: 1px solid rgba(112,161,215,.16); border-radius: 50%; box-shadow: 0 0 0 60px rgba(112,161,215,.035), 0 0 0 120px rgba(112,161,215,.025); }
.story-brand { position: relative; z-index: 1; display: flex; align-items: center; gap: 12px; font-size: 18px; font-weight: 650; letter-spacing: .08em; }
.story-brand img { width: 38px; height: 38px; }
.story-content { position: relative; z-index: 1; max-width: 520px; margin: auto 0; padding: 64px 0; }
.story-eyebrow { margin: 0 0 20px; color: #79a9df; font-size: 11px; letter-spacing: .18em; }
.story-content h1 { margin: 0; font-size: clamp(32px, 3.5vw, 48px); font-weight: 600; line-height: 1.42; letter-spacing: -.02em; }
.story-content > p:not(.story-eyebrow) { margin: 24px 0 0; color: #a9bad0; font-size: 15px; line-height: 1.9; }
.story-lines { display: flex; flex-wrap: wrap; gap: 0; margin-top: 38px; border-top: 1px solid rgba(255,255,255,.12); }
.story-lines span { padding: 15px 22px 0 0; color: #c8d5e5; font-size: 12px; }
.login-story > small { position: relative; z-index: 1; color: #637e9f; font-size: 10px; letter-spacing: .14em; }
.login-form-section { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 48px; }
.login-box { width: 100%; max-width: 390px; margin: auto; }
.login-kicker { margin: 0 0 10px; color: #1a6fd6; font-size: 12px; font-weight: 600; letter-spacing: .14em; }
.login-box h2 { margin: 0; color: #17243a; font-size: 30px; font-weight: 650; }
.login-intro { margin: 10px 0 32px; color: #68788f; font-size: 14px; }
.login-button { width: 100%; height: 44px; margin-top: 8px; font-weight: 600; }
.demo-note { display: flex; flex-direction: column; gap: 5px; margin-top: 24px; padding: 13px 15px; color: #68788f; font-size: 12px; line-height: 1.6; background: #f5f8fc; border-left: 3px solid #a8c9ee; border-radius: 0 6px 6px 0; }
.demo-note strong { color: #465a73; font-weight: 600; }
.login-form-section footer { color: #98a4b3; font-size: 11px; }
.mobile-brand { display: none; }
@media (max-width: 900px) {
  .login-page { display: block; background: #f4f7fb; }
  .login-story { display: none; }
  .login-form-section { min-height: 100vh; padding: 32px 22px; }
  .login-box { padding: 30px 24px; background: #fff; border: 1px solid #e3eaf3; border-radius: 12px; }
  .mobile-brand { display: flex; align-items: center; gap: 10px; margin-bottom: 32px; }
  .mobile-brand img { width: 32px; height: 32px; }
}
</style>
