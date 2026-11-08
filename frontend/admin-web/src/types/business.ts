export type ProductStatus = 'ON' | 'OFF'
export type CustomerLevel = 'retail' | 'wholesale' | 'vip'
export type OrderStatus = 'PENDING_PAYMENT' | 'PAID' | 'SHIPPED' | 'COMPLETED' | 'CANCELLED'

export interface Category {
  id: number
  parentId: number | null
  name: string
  sort: number
  productCount: number
  status: 'ENABLED' | 'DISABLED'
}

export interface Product {
  id: number
  name: string
  categoryId: number
  categoryName: string
  model: string
  retailPrice: number
  stock: number
  status: ProductStatus
  mainImage: string
  specs: string
  description: string
}

export interface Customer {
  id: number
  username: string
  realName: string
  phone: string
  level: CustomerLevel
  orderCount: number
  totalSpent: number
  createdAt: string
}

export interface OrderItem {
  id: number
  productName: string
  model: string
  price: number
  quantity: number
  subtotal: number
}

export interface Order {
  id: number
  orderNo: string
  customerName: string
  level: CustomerLevel
  status: OrderStatus
  productAmount: number
  freightAmount: number
  totalAmount: number
  items: OrderItem[]
  receiver: string
  phone: string
  address: string
  createdAt: string
  paidAt?: string
}

export interface Payment {
  id: number
  orderNo: string
  tradeNo: string
  channel: 'wechat' | 'alipay'
  amount: number
  orderAmount: number
  status: 'SUCCESS' | 'PENDING' | 'FAILED'
  createdAt: string
  paidAt?: string
}
