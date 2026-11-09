import http from './http'
import type { Category, PageResult, Product, ProductDetail } from '@/types/catalog'

export interface ProductQuery {
  category_id?: number
  keyword?: string
  page?: number
  page_size?: number
}

export const catalogApi = {
  async categories(): Promise<Category[]> {
    const { data } = await http.get<Category[]>('/api/catalog/categories')
    return data
  },
  async products(params: ProductQuery = {}): Promise<PageResult<Product>> {
    const { data } = await http.get<PageResult<Product>>('/api/catalog/products', { params })
    return data
  },
  async product(id: number | string): Promise<ProductDetail> {
    const { data } = await http.get<ProductDetail>(`/api/catalog/products/${id}`)
    return data
  },
}
