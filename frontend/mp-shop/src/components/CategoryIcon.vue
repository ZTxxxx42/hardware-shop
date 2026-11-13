<script setup lang="ts">
import { computed } from 'vue'
import type { CategoryIconName } from '@/types/catalog'

const props = defineProps<{ name: CategoryIconName }>()

const icons: Record<CategoryIconName, string> = {
  wrench: '/static/categories/wrench.svg',
  drill: '/static/categories/drill.svg',
  fastener: '/static/categories/fastener.svg',
  hinge: '/static/categories/hinge.svg',
  bearing: '/static/categories/bearing.svg',
  profile: '/static/categories/profile.svg',
  grid: '/static/categories/grid.svg',
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
