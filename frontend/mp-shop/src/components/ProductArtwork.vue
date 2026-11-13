<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{ slug?: string | null; alt?: string }>(), { slug: null, alt: '' })

const artwork: Record<string, string> = {
  bolt: '/static/products/bolt.svg',
  nut: '/static/products/nut.svg',
  washer: '/static/products/washer.svg',
  anchor: '/static/products/anchor.svg',
  hinge: '/static/products/hinge.svg',
  bearing: '/static/products/bearing.svg',
  drill: '/static/products/drill.svg',
  wrench: '/static/products/wrench.svg',
}

const source = computed(() => {
  const slug = props.slug?.trim().toLowerCase()
  return (slug && artwork[slug]) || '/static/products/placeholder.svg'
})
</script>

<template>
  <image class="product-artwork" :src="source" :alt="alt" mode="aspectFit" />
</template>

<style scoped>
.product-artwork {
  width: 100%;
  height: 100%;
}
</style>
