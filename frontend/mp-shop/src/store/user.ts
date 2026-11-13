import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { AuthUser } from '@/types/shop'
import { getToken, removeToken, setToken } from '@/utils/storage'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(getToken())
  const user = ref<AuthUser | null>(null)
  const isLoggedIn = computed(() => Boolean(token.value))

  function setSession(value: string, profile: AuthUser) {
    token.value = value
    user.value = profile
    setToken(value)
  }

  function setUser(profile: AuthUser) {
    user.value = profile
  }

  function logout() {
    token.value = ''
    user.value = null
    removeToken()
  }

  return { token, user, isLoggedIn, setSession, setUser, logout }
})
