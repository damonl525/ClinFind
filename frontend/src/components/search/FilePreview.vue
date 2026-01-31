<script setup lang="ts">
import { Document, Location, CopyDocument, FolderOpened } from '@element-plus/icons-vue'
import { useFileUtils } from '@/composables/useFileUtils'
import { useElectron } from '@/composables/useElectron'
import type { SearchResult } from '@/types'

defineProps<{
  item: SearchResult | null
}>()

const { getFileName, getFileTypeColor, getFileTypeName, extractLocation, formatLocation, cleanHighlight } = useFileUtils()
const { openFile, openFolder, copyToClipboard } = useElectron()
</script>

<template>
  <div class="preview-panel">
    <div v-if="item" class="panel-content">
      <div class="preview-header">
        <div class="preview-title">
          <el-icon :size="24" :color="getFileTypeColor(item.file_path)"><Document /></el-icon>
          <h2>{{ getFileName(item.file_path) }}</h2>
        </div>
      </div>
      
      <div class="preview-body">
        <!-- 文件类型和位置信息 -->
        <div class="preview-meta">
          <el-tag 
            size="large" 
            :style="{ backgroundColor: getFileTypeColor(item.file_path), color: '#fff', border: 'none' }"
          >
            {{ getFileTypeName(item.file_path) }} 文件
          </el-tag>
          <el-tag v-if="extractLocation(item.highlight)" type="warning" size="large">
            <el-icon :size="14"><Location /></el-icon>
            {{ formatLocation(extractLocation(item.highlight)) }}
          </el-tag>
        </div>
        
        <!-- 快捷操作按钮 -->
        <div class="preview-actions">
          <el-button type="primary" @click="openFile(item.file_path)">
            <el-icon><Document /></el-icon>
            打开文件
          </el-button>
          <el-button @click="openFolder(item.file_path)">
            <el-icon><FolderOpened /></el-icon>
            打开文件夹
          </el-button>
          <el-button @click="copyToClipboard(item.file_path)">
            <el-icon><CopyDocument /></el-icon>
            复制路径
          </el-button>
        </div>
        
        <div class="preview-section">
          <h3>匹配内容</h3>
          <div class="content-box" v-html="cleanHighlight(item.highlight)"></div>
        </div>
        
        <div class="preview-section">
          <h3>文件信息</h3>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">文件名</span>
              <span class="info-value">{{ getFileName(item.file_path) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">完整路径</span>
              <span class="info-value">{{ item.file_path }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">匹配得分</span>
              <span class="info-value">{{ item.rank.toFixed(2) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="panel-content empty-content">
      <el-icon :size="80" color="#C0C4CC"><Document /></el-icon>
      <p style="color: #909399; font-size: 18px; margin-top: 20px">选择一个文件查看详情</p>
    </div>
  </div>
</template>

<style scoped>
.preview-panel {
  flex: 1;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  margin-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.preview-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.preview-title h2 {
  margin: 0;
  font-size: 22px;
  color: #303133;
}

.preview-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.preview-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.preview-meta .el-tag {
  display: flex;
  align-items: center;
  gap: 6px;
}

.preview-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.preview-section h3 {
  font-size: 16px;
  color: #606266;
  margin: 0 0 12px 0;
  font-weight: 600;
}

.content-box {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-wrap;
}

.content-box :deep(b) {
  color: #E6A23C;
  background-color: #fff;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: 700;
}

.content-box :deep(.meta) {
  display: none;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 6px;
}

.info-label {
  width: 120px;
  font-weight: 600;
  color: #606266;
}

.info-value {
  flex: 1;
  color: #303133;
  word-break: break-all;
}
</style>
