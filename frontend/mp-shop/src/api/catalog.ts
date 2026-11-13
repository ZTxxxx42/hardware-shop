import { request } from './http'
import type { Category, PageResult, Product, ProductDetail } from '@/types/catalog'

export interface ProductQuery {
  category_id?: number
  keyword?: string
  page?: number
  page_size?: number
}

export const catalogApi = {
  categories(): Promise<Category[]> {
    return request<Category[]>({ url: '/api/catalog/categories' })
  },
  products(params: ProductQuery = {}): Promise<PageResult<Product>> {
    return request<PageResult<Product>>({
      url: '/api/catalog/products',
      data: params as unknown as Record<string, unknown>,
    })
  },
  product(id: number | string): Promise<ProductDetail> {
    return request<ProductDetail>({ url: `/api/catalog/products/${id}` })
  },
}
