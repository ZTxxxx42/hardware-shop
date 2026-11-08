export type ArtworkType = 'bolt' | 'nut' | 'washer' | 'anchor' | 'hinge' | 'bearing'
export type CategoryIcon = 'wrench' | 'drill' | 'fastener' | 'hinge' | 'bearing' | 'profile' | 'grid'

export interface Category {
  id: number
  name: string
  icon: CategoryIcon
  description: string
}

export interface Product {
  id: number
  name: string
  model: string
  material: string
  artwork: ArtworkType
  tag?: string
}

export interface NewsItem {
  id: number
  date: string
  year: string
  title: string
  summary: string
}
