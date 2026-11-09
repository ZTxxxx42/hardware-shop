<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Lock, Phone, User } from '@element-plus/icons-vue'
import { authApi } from '@/api/auth'
import { getErrorMessage } from '@/api/http'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'

const router = useRouter()
const userStore = useUserStore()
const cartStore = useCartStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const form = reactive({ username: '', password: '', confirmPassword: '', phone: '' })

const rules: FormRules = {
  username: [
    { required: true, message: '请输入会员账号', trigger: 'blur' },
    { min: 3, message: '账号至少 3 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (_rule, value: string, callback) => {
        if (value !== form.password) callback(new Error('两次输入的密码不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号', trigger: 'blur' }],
}

async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const session = await authApi.register({
      username: form.username.trim(),
      password: form.password,
      phone: form.phone.trim() || undefined,
    })
    userStore.setSession(session.access_token, session.user)
    void cartStore.load().catch(() => {})
    ElMessage.success('注册成功，已自动登录')
    await router.push('/account')
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '注册失败，请稍后重试'))
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="auth-page">
    <div class="container">
      <nav class="breadcrumb" aria-label="面包屑"><RouterLink to="/">首页</RouterLink><span>/</span><span>会员注册</span></nav>
      <div class="auth-card">
        <div class="auth-heading">
          <span>MEMBER REGISTER</span>
          <h1>会员注册</h1>
          <p>注册即成为会员，享受分级价格与专属采购服务</p>
        </div>
        <el-form ref="formRef" class="auth-form" :model="form" :rules="rules" label-position="top" @submit.prevent="submit">
          <el-form-item label="会员账号" prop="username">
            <el-input v-model="form.username" size="large" placeholder="请输入会员账号" autocomplete="username" :prefix-icon="User" clearable />
          </el-form-item>
          <el-form-item label="登录密码" prop="password">
            <el-input v-model="form.password" size="large" type="password" placeholder="请输入密码（至少 6 位）" autocomplete="new-password" :prefix-icon="Lock" show-password />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input v-model="form.confirmPassword" size="large" type="password" placeholder="请再次输入密码" autocomplete="new-password" :prefix-icon="Lock" show-password />
          </el-form-item>
          <el-form-item label="手机号码" prop="phone">
            <el-input v-model="form.phone" size="large" placeholder="请输入手机号（选填）" :prefix-icon="Phone" clearable />
          </el-form-item>
          <el-button class="auth-submit" type="primary" size="large" :loading="loading" @click="submit">注册并登录</el-button>
        </el-form>
        <p class="auth-switch">已有采购账户？<RouterLink to="/login">返回登录</RouterLink></p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.auth-page { min-height: 680px; padding: 26px 0 70px; background: #f5f8fb; }
.breadcrumb { display: flex; gap: 10px; color: #8b97a4; font-size: 12px; }
.auth-card { width: min(450px, 100%); margin: 34px auto 0; padding: 40px 42px 36px; border: 1px solid #e7edf3; border-radius: 14px; background: #fff; box-shadow: var(--shadow-sm); }
.auth-heading { text-align: center; }
.auth-heading > span { color: var(--brand); font-family: Arial, sans-serif; font-size: 10px; letter-spacing: .2em; }
.auth-heading h1 { margin-top: 4px; font-size: 28px; font-weight: 750; }
.auth-heading p { margin-top: 8px; color: #7b8998; font-size: 13px; }
.auth-form { margin-top: 26px; }
.auth-form :deep(.el-form-item__label) { padding-bottom: 6px; color: #46586b; font-size: 13px; }
.auth-submit { width: 100%; height: 46px; margin-top: 4px; font-size: 15px; }
.auth-switch { margin-top: 22px; color: #7b8998; font-size: 13px; text-align: center; }
.auth-switch a { color: var(--brand); font-weight: 600; }
@media (max-width: 767px) {
  .auth-page { padding-top: 18px; }
  .auth-card { margin-top: 22px; padding: 30px 22px 30px; }
  .auth-heading h1 { font-size: 25px; }
  .auth-heading p { font-size: 12px; }
}
</style>
