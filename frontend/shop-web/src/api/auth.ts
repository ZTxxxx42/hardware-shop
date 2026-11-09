import http from './http'
import type { AuthUser, TokenResponse } from '@/types/shop'

export const authApi = {
  async login(data: { username: string; password: string }): Promise<TokenResponse> {
    const { data: body } = await http.post<TokenResponse>('/api/auth/login', data)
    return body
  },
  async register(data: { username: string; password: string; phone?: string }): Promise<TokenResponse> {
    const { data: body } = await http.post<TokenResponse>('/api/auth/register', data)
    return body
  },
  async me(): Promise<AuthUser> {
    const { data } = await http.get<AuthUser>('/api/auth/me')
    return data
  },
}
