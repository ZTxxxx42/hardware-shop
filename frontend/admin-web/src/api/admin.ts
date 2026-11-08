import http from './http'

// 后续联调时使用；当前页面均读取 src/mock 中的数据。
export const adminApi = {
  login: (data: { username: string; password: string }) => http.post('/api/auth/login', data),
  getProducts: (params?: Record<string, unknown>) => http.get('/api/admin/products', { params }),
  getCategories: () => http.get('/api/admin/categories'),
  getOrders: () => http.get('/api/admin/orders'),
  shipOrder: (id: number) => http.patch(`/api/admin/orders/${id}/ship`),
  getPayments: () => http.get('/api/admin/payments'),
}
