<script setup lang="ts">
defineProps<{ message: string }>()
const emit = defineEmits<{ retry: [] }>()
</script>

<template>
  <el-alert class="request-error" :title="message" type="error" :closable="false" show-icon>
    <el-button link type="danger" @click="emit('retry')">重新加载</el-button>
  </el-alert>
</template>

<style scoped>
.request-error { margin-bottom: 16px; }
</style>
