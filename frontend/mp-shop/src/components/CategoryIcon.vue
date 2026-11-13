<script setup lang="ts">
import { computed } from 'vue'
import type { CategoryIconName } from '@/types/catalog'

const props = defineProps<{ name: CategoryIconName }>()

const icons: Record<CategoryIconName, string> = {
  wrench: '/static/categories/wrench.png',
  drill: '/static/categories/drill.png',
  fastener: '/static/categories/fastener.png',
  hinge: '/static/categories/hinge.png',
  bearing: '/static/categories/bearing.png',
  profile: '/static/categories/profile.png',
  grid: '/static/categories/grid.png',
}

const source = computed(() => icons[props.name] ?? icons.grid)
</script>

<template>
  <image class="category-icon" :src="source" mode="aspectFit" />
</template>

<style scoped>
.category-icon {
  width: 100%;
  height: 100%;
}
</style>
