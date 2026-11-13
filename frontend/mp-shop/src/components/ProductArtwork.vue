<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{ slug?: string | null; alt?: string }>(), { slug: null, alt: '' })

const artwork: Record<string, string> = {
  bolt: '/static/products/bolt.png',
  nut: '/static/products/nut.png',
  washer: '/static/products/washer.png',
  anchor: '/static/products/anchor.png',
  hinge: '/static/products/hinge.png',
  bearing: '/static/products/bearing.png',
  drill: '/static/products/drill.png',
  wrench: '/static/products/wrench.png',
}

const source = computed(() => {
  const slug = props.slug?.trim().toLowerCase()
  return (slug && artwork[slug]) || '/static/products/placeholder.png'
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
