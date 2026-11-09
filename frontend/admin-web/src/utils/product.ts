import boltImage from '@/assets/products/bolt.svg'
import drillImage from '@/assets/products/drill.svg'
import hingeImage from '@/assets/products/hinge.svg'

const localImages: Record<string, string> = {
  bolt: boltImage,
  nut: boltImage,
  washer: boltImage,
  anchor: boltImage,
  wrench: boltImage,
  bearing: boltImage,
  drill: drillImage,
  hinge: hingeImage,
}

export function resolveProductImage(source: string) {
  if (localImages[source]) return localImages[source]
  if (/^(https?:\/\/|\/|data:image\/|blob:)/.test(source)) return source
  return boltImage
}

export function useFallbackImage(event: Event) {
  const image = event.target as HTMLImageElement
  image.onerror = null
  image.src = boltImage
}
