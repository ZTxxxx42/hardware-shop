import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

interface AdminUser {
  username: string
  name: string
  role: 'admin'
}

const TOKEN_KEY = 'admin_access_token'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) ?? '')
  const user = ref<AdminUser | null>(
    token.value ? { username: 'admin', name: '运营管理员', role: 'admin' } : null,
  )
  const isAuthenticated = computed(() => Boolean(token.value))

  async function login(username: string, _password: string) {
    // 脚手架阶段仅模拟登录，后续替换为 POST /api/auth/login。
    await new Promise((resolve) => window.setTimeout(resolve, 350))
    token.value = `mock-admin-${Date.now()}`
    user.value = { username, name: '运营管理员', role: 'admin' }
    localStorage.setItem(TOKEN_KEY, token.value)
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  return { token, user, isAuthenticated, login, logout }
})
