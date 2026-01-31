<script setup lang="ts">
import { FolderAdd } from '@element-plus/icons-vue'
</script>

<template>
  <div class="drag-overlay">
    <div class="drag-content">
      <el-icon :size="80" color="#409EFF"><FolderAdd /></el-icon>
      <h2>释放以添加文件夹</h2>
      <p>将文件夹拖放到此处进行索引</p>
    </div>
  </div>
</template>

<style scoped>
.drag-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(64, 158, 255, 0.95);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(8px);
}

.drag-content {
  text-align: center;
  color: white;
}

.drag-content h2 {
  margin: 20px 0 10px;
  font-size: 28px;
  font-weight: 600;
}

.drag-content p {
  font-size: 16px;
  opacity: 0.9;
}
</style>
