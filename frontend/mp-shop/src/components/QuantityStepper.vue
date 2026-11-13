<script setup lang="ts">
const props = withDefaults(defineProps<{ modelValue: number; min?: number; max?: number; disabled?: boolean }>(), {
  min: 1,
  max: 999,
  disabled: false,
})

const emit = defineEmits<{ 'update:modelValue': [value: number] }>()

function change(delta: number) {
  if (props.disabled) return
  const next = props.modelValue + delta
  if (next < props.min || next > props.max) return
  emit('update:modelValue', next)
}
</script>

<template>
  <view class="stepper" :class="{ 'is-disabled': disabled }">
    <view class="stepper__btn" :class="{ 'is-disabled': disabled || modelValue <= min }" @tap="change(-1)">−</view>
    <view class="stepper__value">{{ modelValue }}</view>
    <view class="stepper__btn" :class="{ 'is-disabled': disabled || modelValue >= max }" @tap="change(1)">＋</view>
  </view>
</template>

<style scoped>
.stepper {
  display: inline-flex;
  align-items: center;
  border: 1rpx solid var(--line-dark);
  border-radius: 10rpx;
  overflow: hidden;
  background: var(--white);
}

.stepper__btn {
  display: flex;
  width: 64rpx;
  height: 60rpx;
  align-items: center; justify-content: center;
  color: var(--brand);
  font-size: 34rpx;
  line-height: 1;
}

.stepper__btn:active {
  background: var(--brand-light);
}

.stepper__value {
  display: flex;
  min-width: 76rpx;
  height: 60rpx;
  align-items: center; justify-content: center;
  border-left: 1rpx solid var(--line);
  border-right: 1rpx solid var(--line);
  color: var(--ink-soft);
  font-size: 26rpx;
  font-weight: 600;
}

.stepper__btn.is-disabled {
  color: #aab6c4;
  background: var(--surface-deep);
}
</style>
