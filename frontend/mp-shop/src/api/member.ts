import { request } from './http'
import type { Address, AddressPayload, Level, Profile } from '@/types/shop'

export const memberApi = {
  profile(): Promise<Profile> {
    return request<Profile>({ url: '/api/member/profile' })
  },
  level(): Promise<Level | null> {
    return request<Level | null>({ url: '/api/member/level' })
  },
  addresses(): Promise<Address[]> {
    return request<Address[]>({ url: '/api/member/addresses' })
  },
  createAddress(payload: AddressPayload): Promise<Address> {
    return request<Address>({ url: '/api/member/addresses', method: 'POST', data: payload as unknown as Record<string, unknown> })
  },
  updateAddress(id: number, payload: AddressPayload): Promise<Address> {
    return request<Address>({ url: `/api/member/addresses/${id}`, method: 'PATCH', data: payload as unknown as Record<string, unknown> })
  },
  removeAddress(id: number): Promise<void> {
    return request<void>({ url: `/api/member/addresses/${id}`, method: 'DELETE' })
  },
}
