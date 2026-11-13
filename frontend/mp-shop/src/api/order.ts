import { request } from './http'
import type { OrderBrief, OrderDetail } from '@/types/shop'

export interface OrderCreatePayload {
  address_id: number
  channel?: string
  remark?: string
}

export const orderApi = {
  list(): Promise<OrderBrief[]> {
    return request<OrderBrief[]>({ url: '/api/orders' })
  },
  detail(id: number | string): Promise<OrderDetail> {
    return request<OrderDetail>({ url: `/api/orders/${id}` })
  },
  create(payload: OrderCreatePayload): Promise<OrderDetail> {
    return request<OrderDetail>({ url: '/api/orders', method: 'POST', data: payload as unknown as Record<string, unknown> })
  },
  cancel(id: number | string): Promise<OrderDetail> {
    return request<OrderDetail>({ url: `/api/orders/${id}/cancel`, method: 'POST' })
  },
  confirm(id: number | string): Promise<OrderDetail> {
    return request<OrderDetail>({ url: `/api/orders/${id}/confirm`, method: 'POST' })
  },
}
