import { request } from './http'
import type { AuthUser, TokenResponse } from '@/types/shop'

export const authApi = {
  login(data: { username: string; password: string }): Promise<TokenResponse> {
    return request<TokenResponse>({ url: '/api/auth/login', method: 'POST', data })
  },
  wechatLogin(data: { code: string }): Promise<TokenResponse> {
    return request<TokenResponse>({ url: '/api/auth/wechat/login', method: 'POST', data })
  },
  me(): Promise<AuthUser> {
    return request<AuthUser>({ url: '/api/auth/me' })
  },
}
