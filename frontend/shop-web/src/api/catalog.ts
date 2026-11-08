import http from './http'

export interface ProductQuery {
  category_id?: number
  keyword?: string
  page?: number
  page_size?: number
}

export const catalogApi = {
  categories: () => http.get('/api/catalog/categories'),
  products: (params: ProductQuery) => http.get('/api/catalog/products', { params }),
  product: (id: number | string) => http.get(`/api/catalog/products/${id}`),
}
