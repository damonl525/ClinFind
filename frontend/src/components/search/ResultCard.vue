<script setup lang="ts">
import { Document, Location, CopyDocument, FolderOpened } from '@element-plus/icons-vue'
import { useFileUtils } from '@/composables/useFileUtils'
import { useElectron } from '@/composables/useElectron'
import type { SearchResult } from '@/types'

const props = defineProps<{
  item: SearchResult
  active: boolean
}>()

const emit = defineEmits<{
  select: [item: SearchResult]
  open: [path: string]
}>()

const { getFileName, getFileTypeColor, getFileTypeName, extractLocation, formatLocation, cleanHighlight } = useFileUtils()
const { openFile, openFolder, copyToClipboard } = useElectron()

const handleCopyPath = (e: Event) => {
  e.stopPropagation()
  copyToClipboard(props.item.file_path)
}

const handleOpenFolder = (e: Event) => {
  e.stopPropagation()
  openFolder(props.item.file_path)
}

const handleOpenFile = (e: Event) => {
  e.stopPropagation()
  openFile(props.item.file_path)
}
</script>

<template>
  <div
    class="result-card"
    :class="{ active }"
    @click="emit('select', item)"
    @dblclick="emit('open', item.file_path)"
  >
    <!-- 结果卡片头部 -->
    <div class="result-header">
      <div class="result-header-left">
        <el-tag 
          size="small" 
          :style="{ backgroundColor: getFileTypeColor(item.file_path), color: '#fff', border: 'none' }"
          class="file-type-tag"
        >
          {{ getFileTypeName(item.file_path) }}
        </el-tag>
        <span class="file-name">{{ getFileName(item.file_path) }}</span>
      </div>
      <!-- 位置信息标签 -->
      <el-tag v-if="extractLocation(item.highlight)" type="warning" size="small" class="location-tag">
        <el-icon :size="12"><Location /></el-icon>
        {{ formatLocation(extractLocation(item.highlight)) }}
      </el-tag>
    </div>
    
    <!-- 文件路径 -->
    <div class="result-path">{{ item.file_path }}</div>
    
    <!-- 匹配内容摘要 -->
    <div class="result-snippet" v-html="cleanHighlight(item.highlight)"></div>
    
    <!-- 快捷操作按钮 -->
    <div class="result-actions">
      <el-button-group size="small">
        <el-tooltip content="打开文件" placement="top">
          <el-button @click="handleOpenFile">
            <el-icon><Document /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="打开所在文件夹" placement="top">
          <el-button @click="handleOpenFolder">
            <el-icon><FolderOpened /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="复制路径" placement="top">
          <el-button @click="handleCopyPath">
            <el-icon><CopyDocument /></el-icon>
          </el-button>
        </el-tooltip>
      </el-button-group>
      <span class="result-score">得分: {{ item.rank.toFixed(1) }}</span>
    </div>
  </div>
</template>

<style scoped>
.result-card {
  padding: 16px;
  border: 2px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.result-card:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
  transform: translateY(-2px);
}

.result-card.active {
  border-color: #409EFF;
  background: linear-gradient(135deg, #ecf5ff 0%, #f0f9ff 100%);
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 8px;
}

.result-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.file-type-tag {
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 600;
}

.location-tag {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 4px;
}

.file-name {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-path {
  font-size: 11px;
  color: #909399;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-snippet {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 12px;
  max-height: 60px;
  overflow: hidden;
}

.result-snippet :deep(b) {
  color: #E6A23C;
  background-color: #fdf6ec;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: 600;
}

.result-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.result-actions .el-button-group {
  opacity: 0.7;
  transition: opacity 0.2s;
}

.result-card:hover .result-actions .el-button-group {
  opacity: 1;
}

.result-score {
  font-size: 12px;
  color: #909399;
}
</style>
