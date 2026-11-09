export interface AuthUser {
  id: number
  username: string
  role: string
  phone: string | null
  level_code: string | null
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: AuthUser
}

export interface CartItem {
  id: number
  product_id: number
  name: string
  model: string | null
  main_image: string | null
  quantity: number
  retail_price: string
  price: string
  subtotal: string
}

export interface CartSummary {
  items: CartItem[]
  product_amount: string
  freight_amount: string
  total_amount: string
}

export interface Address {
  id: number
  receiver: string
  phone: string
  region: string
  detail: string
}

export interface AddressPayload {
  receiver: string
  phone: string
  region: string
  detail: string
}

export interface OrderItem {
  id: number
  product_id: number
  product_name: string
  price: string
  quantity: number
  subtotal: string
}

export interface AddressSnapshot {
  receiver: string
  phone: string
  region: string
  detail: string
}

export interface Payment {
  id: number
  order_id: number
  channel: string
  trade_no: string | null
  amount: string
  status: string
  paid_at: string | null
}

export interface OrderBrief {
  id: number
  order_no: string
  status: string
  product_amount: string
  freight_amount: string
  total_amount: string
  created_at: string
}

export interface OrderDetail extends OrderBrief {
  items: OrderItem[]
  address_snapshot: AddressSnapshot
  payments: Payment[]
}

export interface Profile {
  user_id: number
  username: string
  phone: string | null
  level_code: string | null
  level_name: string | null
  real_name: string | null
}

export interface Level {
  code: string
  name: string
  sort: number
}
