<script setup lang="ts">
import { Loading } from '@element-plus/icons-vue'

withDefaults(defineProps<{
  loading?: boolean
  error?: string
  empty?: boolean
  loadingText?: string
  emptyText?: string
}>(), {
  loading: false,
  error: '',
  empty: false,
  loadingText: '正在加载...',
  emptyText: '暂无数据',
})

defineEmits<{ retry: [] }>()
</script>

<template>
  <div class="request-state">
    <div v-if="loading" class="loading-state" role="status" aria-live="polite">
      <el-icon class="is-loading" :size="24"><Loading /></el-icon>
      <span>{{ loadingText }}</span>
    </div>
    <div v-else-if="error" class="error-state" role="alert">
      <p>{{ error }}</p>
      <el-button type="primary" plain @click="$emit('retry')">重新加载</el-button>
    </div>
    <el-empty v-else-if="empty" :description="emptyText" :image-size="76" />
  </div>
</template>

<style scoped>
.request-state { display: grid; min-height: 150px; place-items: center; color: var(--muted); }
.loading-state { display: flex; align-items: center; justify-content: center; gap: 10px; font-size: 13px; }
.loading-state .el-icon { color: var(--brand); }
.error-state { display: flex; flex-direction: column; align-items: center; gap: 14px; padding: 24px; text-align: center; }
.error-state p { color: #7a8795; font-size: 13px; }
.request-state :deep(.el-empty) { padding: 20px 0; }
.request-state :deep(.el-empty__description) { margin-top: 12px; }
</style>
