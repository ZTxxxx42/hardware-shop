import { useUserStore } from '@/store/user'

export function ensureLogin(redirect?: string): boolean {
  const userStore = useUserStore()
  if (userStore.isLoggedIn) return true
  const url = redirect
    ? `/pages/login/index?redirect=${encodeURIComponent(redirect)}`
    : '/pages/login/index'
  uni.navigateTo({ url })
  return false
}
