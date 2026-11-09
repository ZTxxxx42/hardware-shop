import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { adminApi } from '@/api/admin'

interface AdminUser {
  id: number
  username: string
  name: string
  role: 'admin'
}

const TOKEN_KEY = 'admin_access_token'
const USER_KEY = 'admin_user'

function readStoredUser(): AdminUser | null {
  try {
    const value = JSON.parse(localStorage.getItem(USER_KEY) ?? 'null') as Partial<AdminUser> | null
    if (value?.role === 'admin' && typeof value.username === 'string' && typeof value.id === 'number') {
      return { id: value.id, username: value.username, name: value.name || value.username, role: 'admin' }
    }
  } catch {
    localStorage.removeItem(USER_KEY)
  }
  return null
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) ?? '')
  const user = ref<AdminUser | null>(token.value ? readStoredUser() : null)
  const isAuthenticated = computed(() => Boolean(token.value))

  async function login(username: string, password: string) {
    const { data } = await adminApi.login({ username, password })
    if (data.user.role !== 'admin') throw new Error('该账号没有管理后台访问权限')

    token.value = data.access_token
    user.value = {
      id: data.user.id,
      username: data.user.username,
      name: data.user.username,
      role: 'admin',
    }
    localStorage.setItem(TOKEN_KEY, token.value)
    localStorage.setItem(USER_KEY, JSON.stringify(user.value))
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  return { token, user, isAuthenticated, login, logout }
})
