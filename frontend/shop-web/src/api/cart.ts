import http from './http'
import type { CartSummary } from '@/types/shop'

export const cartApi = {
  async summary(): Promise<CartSummary> {
    const { data } = await http.get<CartSummary>('/api/cart')
    return data
  },
  async addItem(productId: number, quantity: number): Promise<CartSummary> {
    const { data } = await http.post<CartSummary>('/api/cart/items', { product_id: productId, quantity })
    return data
  },
  async updateItem(itemId: number, quantity: number): Promise<CartSummary> {
    const { data } = await http.patch<CartSummary>(`/api/cart/items/${itemId}`, { quantity })
    return data
  },
  async removeItem(itemId: number): Promise<CartSummary> {
    const { data } = await http.delete<CartSummary>(`/api/cart/items/${itemId}`)
    return data
  },
}
