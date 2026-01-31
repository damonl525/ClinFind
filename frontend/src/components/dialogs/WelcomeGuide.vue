<script setup lang="ts">
import { Search, FolderAdd } from '@element-plus/icons-vue'

const visible = defineModel<boolean>({ required: true })

const emit = defineEmits<{
  addFolder: []
  close: []
}>()

const handleAddFolder = () => {
  emit('addFolder')
}

const handleClose = () => {
  emit('close')
}
</script>

<template>
  <el-dialog 
    v-model="visible" 
    title="" 
    width="520px" 
    :show-close="false"
    :close-on-click-modal="false"
    class="welcome-dialog"
  >
    <div class="welcome-content">
      <div class="welcome-icon">
        <el-icon :size="64" color="#409EFF"><Search /></el-icon>
      </div>
      <h2>🎉 欢迎使用 ClinFind</h2>
      <p class="welcome-desc">强大的本地文件内容搜索工具，支持 PDF、Word、Excel、PPT 等格式</p>
      
      <div class="welcome-steps">
        <div class="step-item">
          <span class="step-num">1</span>
          <span class="step-text">添加包含文档的文件夹</span>
        </div>
        <div class="step-item">
          <span class="step-num">2</span>
          <span class="step-text">等待索引完成</span>
        </div>
        <div class="step-item">
          <span class="step-num">3</span>
          <span class="step-text">输入关键词即可搜索</span>
        </div>
      </div>
      
      <div class="welcome-formats">
        <span class="format-label">支持格式：</span>
        <el-tag size="small">PDF</el-tag>
        <el-tag size="small" type="success">Word</el-tag>
        <el-tag size="small" type="warning">Excel</el-tag>
        <el-tag size="small" type="danger">PPT</el-tag>
        <el-tag size="small" type="info">TXT</el-tag>
      </div>
      
      <div class="welcome-actions">
        <el-button type="primary" size="large" @click="handleAddFolder">
          <el-icon><FolderAdd /></el-icon>
          添加第一个文件夹
        </el-button>
        <el-button size="large" @click="handleClose">稍后再说</el-button>
      </div>
    </div>
  </el-dialog>
</template>

<style scoped>
.welcome-content {
  text-align: center;
  padding: 20px 0;
}

.welcome-icon {
  margin-bottom: 16px;
}

.welcome-content h2 {
  margin: 0 0 12px;
  font-size: 26px;
  color: #303133;
}

.welcome-desc {
  color: #606266;
  font-size: 15px;
  margin-bottom: 28px;
}

.welcome-steps {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 20px;
  margin: 24px 0;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 0;
}

.step-item:not(:last-child) {
  border-bottom: 1px solid #e4e7ed;
}

.step-num {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
}

.step-text {
  color: #303133;
  font-size: 15px;
}

.welcome-formats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin: 20px 0;
  flex-wrap: wrap;
}

.format-label {
  color: #909399;
  font-size: 14px;
}

.welcome-actions {
  margin-top: 28px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

.welcome-actions .el-button {
  min-width: 160px;
}
</style>
