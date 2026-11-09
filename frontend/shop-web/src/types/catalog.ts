export type CategoryIconName = 'wrench' | 'drill' | 'fastener' | 'hinge' | 'bearing' | 'profile' | 'grid'

export interface Category {
  id: number
  parent_id: number | null
  name: string
  sort: number
}

export interface Product {
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

export interface ProductImage {
  id: number
  url: string
  sort: number
}

export interface ProductSpec {
  id: number
  spec_name: string
  spec_value: string
}

export interface ProductPrice {
  level_code: string
  price: string
}

export interface ProductDetail extends Product {
  description: string | null
  images: ProductImage[]
  specs: ProductSpec[]
  level_prices: ProductPrice[]
}

export interface PageResult<T> {
  total: number
  items: T[]
}

export interface NewsItem {
  id: number
  date: string
  year: string
  title: string
  summary: string
}
