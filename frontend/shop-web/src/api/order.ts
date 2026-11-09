import http from './http'
import type { OrderBrief, OrderDetail } from '@/types/shop'

export interface OrderCreatePayload {
  address_id: number
  channel?: string
  remark?: string
}

export const orderApi = {
  async list(): Promise<OrderBrief[]> {
    const { data } = await http.get<OrderBrief[]>('/api/orders')
    return data
  },
  async detail(id: number): Promise<OrderDetail> {
    const { data } = await http.get<OrderDetail>(`/api/orders/${id}`)
    return data
  },
  async create(payload: OrderCreatePayload): Promise<OrderDetail> {
    const { data } = await http.post<OrderDetail>('/api/orders', payload)
    return data
  },
  async cancel(id: number): Promise<OrderDetail> {
    const { data } = await http.post<OrderDetail>(`/api/orders/${id}/cancel`)
    return data
  },
  async confirm(id: number): Promise<OrderDetail> {
    const { data } = await http.post<OrderDetail>(`/api/orders/${id}/confirm`)
    return data
  },
}
