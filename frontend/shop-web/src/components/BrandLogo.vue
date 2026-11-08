<script setup lang="ts">
import logoUrl from '@/assets/brand/logo.svg'

withDefaults(defineProps<{ inverse?: boolean; compact?: boolean }>(), {
  inverse: false,
  compact: false,
})
</script>

<template>
  <div class="brand-logo" :class="{ 'brand-logo--inverse': inverse, 'brand-logo--compact': compact }">
    <img class="brand-logo__mark" :src="logoUrl" alt="" width="46" height="52" />
    <div class="brand-logo__copy">
      <strong>恒泰五金商贸</strong>
      <span>Hengtai Hardware Trade</span>
    </div>
  </div>
</template>

<style scoped>
.brand-logo { display: inline-flex; align-items: center; gap: 11px; color: var(--brand-ink); }
.brand-logo__mark { width: 43px; height: 49px; flex: 0 0 auto; }
.brand-logo__copy { display: flex; flex-direction: column; }
.brand-logo strong { font-size: 22px; font-weight: 800; line-height: 1.25; letter-spacing: .02em; white-space: nowrap; }
.brand-logo span { margin-top: 3px; color: #788592; font-family: Arial, sans-serif; font-size: 10px; line-height: 1.2; letter-spacing: .035em; }
.brand-logo--inverse { color: #fff; }
.brand-logo--inverse span { color: #b6c5d5; }
@media (max-width: 767px) {
  .brand-logo { gap: 8px; }
  .brand-logo__mark { width: 34px; height: 39px; }
  .brand-logo strong { font-size: 19px; }
  .brand-logo span { font-size: 8px; letter-spacing: .01em; }
}
</style>
