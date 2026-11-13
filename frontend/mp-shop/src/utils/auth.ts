import { useUserStore } from '@/store/user'

export function ensureLogin(): boolean {
  const userStore = useUserStore()
  return userStore.isLoggedIn
}

export function goLogin(redirect?: string): void {
  const url = redirect
    ? `/pages/login/index?redirect=${encodeURIComponent(redirect)}`
    : '/pages/login/index'
  uni.navigateTo({ url })
}
