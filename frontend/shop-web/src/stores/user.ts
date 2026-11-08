import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

const STORAGE_KEY = 'hengtai_access_token'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem(STORAGE_KEY) ?? '')
  const isLoggedIn = computed(() => Boolean(token.value))

  function setToken(value: string) {
    token.value = value
    localStorage.setItem(STORAGE_KEY, value)
  }

  function logout() {
    token.value = ''
    localStorage.removeItem(STORAGE_KEY)
  }

  return { token, isLoggedIn, setToken, logout }
})
