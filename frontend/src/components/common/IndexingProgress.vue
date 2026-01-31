<script setup lang="ts">
import { RefreshRight } from '@element-plus/icons-vue'
import { computed } from 'vue'
import type { IndexingProgress } from '@/types'

const props = defineProps<{
  progress: IndexingProgress
}>()

const percentage = computed(() => {
  if (props.progress.totalFiles <= 0) return 0
  return Math.round(props.progress.processedFiles / props.progress.totalFiles * 100)
})
</script>

<template>
  <div v-if="progress.active" class="indexing-bar">
    <div class="indexing-content">
      <el-icon class="spinning" :size="20" color="#fff"><RefreshRight /></el-icon>
      <span class="indexing-text">{{ progress.currentFile }}</span>
      <span v-if="progress.totalFiles > 0" class="indexing-count">
        ({{ progress.processedFiles }}/{{ progress.totalFiles }})
      </span>
    </div>
    <el-progress 
      :percentage="percentage"
      :stroke-width="4"
      :show-text="false"
      color="#fff"
      class="indexing-progress"
    />
  </div>
</template>

<style scoped>
.indexing-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 12px 40px;
  z-index: 1000;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.indexing-content {
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
  margin-bottom: 8px;
}

.indexing-text {
  flex: 1;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.indexing-count {
  font-size: 13px;
  opacity: 0.9;
}

.indexing-progress {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
