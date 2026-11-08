<script setup lang="ts">
import type { CategoryIcon } from '@/types/catalog'
import wrenchUrl from '@/assets/categories/wrench.svg'
import drillUrl from '@/assets/categories/drill.svg'
import fastenerUrl from '@/assets/categories/fastener.svg'
import hingeUrl from '@/assets/categories/hinge.svg'
import bearingUrl from '@/assets/categories/bearing.svg'
import profileUrl from '@/assets/categories/profile.svg'
import gridUrl from '@/assets/categories/grid.svg'

const props = defineProps<{ name: CategoryIcon }>()
const icons: Record<CategoryIcon, string> = { wrench: wrenchUrl, drill: drillUrl, fastener: fastenerUrl, hinge: hingeUrl, bearing: bearingUrl, profile: profileUrl, grid: gridUrl }
</script>

<template>
  <img class="category-icon" :src="icons[props.name]" alt="" width="80" height="80" loading="lazy" />
</template>

<style scoped>
.category-icon { width: 100%; height: 100%; object-fit: contain; }
</style>
