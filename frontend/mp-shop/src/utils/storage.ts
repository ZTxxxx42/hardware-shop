export const TOKEN_STORAGE_KEY = 'hengtai_access_token'

export function getToken(): string {
  return (uni.getStorageSync(TOKEN_STORAGE_KEY) as string) ?? ''
}

export function setToken(token: string): void {
  uni.setStorageSync(TOKEN_STORAGE_KEY, token)
}

export function removeToken(): void {
  uni.removeStorageSync(TOKEN_STORAGE_KEY)
}
