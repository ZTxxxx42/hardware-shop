<script setup lang="ts">
import { computed } from 'vue'
import boltUrl from '@/assets/products/bolt.svg'
import nutUrl from '@/assets/products/nut.svg'
import washerUrl from '@/assets/products/washer.svg'
import anchorUrl from '@/assets/products/anchor.svg'
import hingeUrl from '@/assets/products/hinge.svg'
import bearingUrl from '@/assets/products/bearing.svg'
import drillUrl from '@/assets/products/drill.svg'
import wrenchUrl from '@/assets/products/wrench.svg'
import placeholderUrl from '@/assets/products/placeholder.svg'

const props = withDefaults(defineProps<{ slug?: string | null; alt?: string }>(), { slug: null, alt: '' })
const artwork: Record<string, string> = {
  bolt: boltUrl,
  nut: nutUrl,
  washer: washerUrl,
  anchor: anchorUrl,
  hinge: hingeUrl,
  bearing: bearingUrl,
  drill: drillUrl,
  wrench: wrenchUrl,
}
const source = computed(() => {
  const slug = props.slug?.trim().toLowerCase()
  return (slug && artwork[slug]) || placeholderUrl
})
</script>

<template>
  <img class="product-artwork" :src="source" :alt="alt" width="480" height="360" loading="lazy" />
</template>

<style scoped>
.product-artwork { width: 100%; height: 100%; object-fit: contain; }
</style>
