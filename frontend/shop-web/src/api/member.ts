import http from './http'
import type { Address, AddressPayload, Level, Profile } from '@/types/shop'

export const memberApi = {
  async profile(): Promise<Profile> {
    const { data } = await http.get<Profile>('/api/member/profile')
    return data
  },
  async level(): Promise<Level | null> {
    const { data } = await http.get<Level | null>('/api/member/level')
    return data
  },
  async addresses(): Promise<Address[]> {
    const { data } = await http.get<Address[]>('/api/member/addresses')
    return data
  },
  async createAddress(payload: AddressPayload): Promise<Address> {
    const { data } = await http.post<Address>('/api/member/addresses', payload)
    return data
  },
  async updateAddress(id: number, payload: AddressPayload): Promise<Address> {
    const { data } = await http.patch<Address>(`/api/member/addresses/${id}`, payload)
    return data
  },
  async removeAddress(id: number): Promise<void> {
    await http.delete(`/api/member/addresses/${id}`)
  },
}
