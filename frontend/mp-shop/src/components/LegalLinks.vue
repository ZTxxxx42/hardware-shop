<script setup lang="ts">
withDefaults(defineProps<{ align?: 'left' | 'center'; quiet?: boolean }>(), {
  align: 'center',
  quiet: false,
})

function openLegal(tab: 'privacy' | 'agreement') {
  uni.navigateTo({ url: `/pages/legal/index?tab=${tab}` })
}
</script>

<template>
  <view class="legal-links" :class="[`is-${align}`, { 'is-quiet': quiet }]">
    <text class="legal-links__item" role="link" @tap.stop="openLegal('privacy')">隐私政策</text>
    <text class="legal-links__divider">/</text>
    <text class="legal-links__item" role="link" @tap.stop="openLegal('agreement')">用户协议</text>
  </view>
</template>

<style scoped>
.legal-links {
  display: flex;
  align-items: center;
  gap: 14rpx;
  font-size: 23rpx;
  line-height: 1.6;
}
.legal-links.is-center { justify-content: center; }
.legal-links.is-left { justify-content: flex-start; }
.legal-links__item {
  padding: 8rpx 0;
  color: var(--brand-dark);
  text-decoration: underline;
  text-underline-offset: 5rpx;
}
.legal-links__divider { color: var(--line-dark); }
.legal-links.is-quiet .legal-links__item {
  color: var(--muted);
  text-decoration: none;
}
</style>
