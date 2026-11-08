<script setup lang="ts">
import type { ArtworkType } from '@/types/catalog'
import boltUrl from '@/assets/products/bolt.svg'
import nutUrl from '@/assets/products/nut.svg'
import washerUrl from '@/assets/products/washer.svg'
import anchorUrl from '@/assets/products/anchor.svg'
import hingeUrl from '@/assets/products/hinge.svg'
import bearingUrl from '@/assets/products/bearing.svg'

const props = withDefaults(defineProps<{ type: ArtworkType; alt?: string }>(), { alt: '' })
const artwork: Record<ArtworkType, string> = { bolt: boltUrl, nut: nutUrl, washer: washerUrl, anchor: anchorUrl, hinge: hingeUrl, bearing: bearingUrl }
</script>

<template>
  <img class="product-artwork" :src="artwork[props.type]" :alt="alt" width="480" height="360" loading="lazy" />
</template>

<style scoped>
.product-artwork { width: 100%; height: 100%; object-fit: contain; }
</style>
