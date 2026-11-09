import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { AuthUser } from '@/types/shop'

const STORAGE_KEY = 'hengtai_access_token'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem(STORAGE_KEY) ?? '')
  const user = ref<AuthUser | null>(null)
  const isLoggedIn = computed(() => Boolean(token.value))

  function setSession(value: string, profile: AuthUser) {
    token.value = value
    user.value = profile
    localStorage.setItem(STORAGE_KEY, value)
  }

  function setUser(profile: AuthUser) {
    user.value = profile
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem(STORAGE_KEY)
  }

  return { token, user, isLoggedIn, setSession, setUser, logout }
})
