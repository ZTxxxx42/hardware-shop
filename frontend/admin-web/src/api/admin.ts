import http from './http'

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: {
    id: number
    username: string
    role: string
    phone: string | null
    level_code: string | null
  }
}

export interface CategoryOut {
  id: number
  parent_id: number | null
  name: string
  sort: number
}

export interface CategoryPayload {
  name: string
  parent_id?: number | null
  sort?: number
}

export interface ProductBriefOut {
  id: number
  category_id: number
  name: string
  model: string | null
  main_image: string | null
  retail_price: string
  price: string
  stock: number
  status: string
}

export interface ProductDetailOut extends ProductBriefOut {
  description: string | null
  images: Array<{ id: number; url: string; sort: number }>
  specs: Array<{ id: number; spec_name: string; spec_value: string }>
  level_prices: ProductPriceItem[]
}

export interface ProductPayload {
  category_id: number
  name: string
  model: string | null
  description: string | null
  retail_price: number
  stock: number
  status: string
  main_image: string | null
}

export interface ProductPriceItem {
  level_code: string
  price: string
}

export interface ProductPricePayload {
  level_code: string
  price: number
}

export interface PageResult<T> {
  total: number
  items: T[]
}

export interface OrderBriefOut {
  id: number
  order_no: string
  status: string
  product_amount: string
  freight_amount: string
  total_amount: string
  remark: string | null
  carrier: string | null
  tracking_no: string | null
  shipped_at: string | null
  created_at: string
}

export interface OrderItemOut {
  id: number
  product_id: number | null
  product_name: string
  price: string
  quantity: number
  subtotal: string
}

export interface PaymentOut {
  id: number
  order_id: number
  channel: string
  trade_no: string | null
  amount: string
  status: string
  paid_at: string | null
}

export interface CustomerOut {
  user_id: number
  username: string
  phone: string | null
  level_code: string | null
  level_name: string | null
  real_name: string | null
}

export interface OrderDetailOut extends OrderBriefOut {
  items: OrderItemOut[]
  address_snapshot: {
    receiver?: string
    phone?: string
    region?: string
    detail?: string
  } | null
  payments: PaymentOut[]
}

export const adminApi = {
  login: (data: { username: string; password: string }) => http.post<TokenResponse>('/api/auth/login', data),
  getProducts: (params?: { page?: number; page_size?: number }) => http.get<PageResult<ProductBriefOut>>('/api/admin/products', { params }),
  getProductDetail: (id: number) => http.get<ProductDetailOut>(`/api/catalog/products/${id}`),
  createProduct: (data: ProductPayload) => http.post<ProductBriefOut>('/api/admin/products', data),
  updateProduct: (id: number, data: Partial<ProductPayload>) => http.patch<ProductBriefOut>(`/api/admin/products/${id}`, data),
  updateProductPrices: (id: number, prices: ProductPricePayload[]) => http.put<ProductPriceItem[]>(`/api/admin/products/${id}/prices`, { prices }),
  getCategories: () => http.get<CategoryOut[]>('/api/admin/categories'),
  createCategory: (data: CategoryPayload) => http.post<CategoryOut>('/api/admin/categories', data),
  updateCategory: (id: number, data: CategoryPayload) => http.patch<CategoryOut>(`/api/admin/categories/${id}`, data),
  deleteCategory: (id: number) => http.delete(`/api/admin/categories/${id}`),
  getOrders: () => http.get<OrderBriefOut[]>('/api/admin/orders'),
  shipOrder: (id: number, data: { carrier: string; tracking_no: string }) => http.patch<OrderDetailOut>(`/api/admin/orders/${id}/ship`, data),
  getPayments: () => http.get<PaymentOut[]>('/api/admin/payments'),
  getCustomers: (params?: { keyword?: string }) => http.get<CustomerOut[]>('/api/admin/customers', { params }),
  updateCustomerLevel: (id: number, level_code: string) => http.patch<CustomerOut>(`/api/admin/customers/${id}`, { level_code }),
}
