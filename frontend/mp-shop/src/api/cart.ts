import { request } from './http'
import type { CartSummary } from '@/types/shop'

export const cartApi = {
  summary(): Promise<CartSummary> {
    return request<CartSummary>({ url: '/api/cart' })
  },
  addItem(productId: number, quantity: number): Promise<CartSummary> {
    return request<CartSummary>({ url: '/api/cart/items', method: 'POST', data: { product_id: productId, quantity } })
  },
  updateItem(itemId: number, quantity: number): Promise<CartSummary> {
    return request<CartSummary>({ url: `/api/cart/items/${itemId}`, method: 'PATCH', data: { quantity } })
  },
  removeItem(itemId: number): Promise<CartSummary> {
    return request<CartSummary>({ url: `/api/cart/items/${itemId}`, method: 'DELETE' })
  },
}
