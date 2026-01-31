<script setup lang="ts">
import { computed } from 'vue'
import { Folder, FolderAdd, Loading } from '@element-plus/icons-vue'
import type { SearchResult } from '@/types'
import ResultCard from './ResultCard.vue'

const props = defineProps<{
  results: SearchResult[]
  loading: boolean
  loadingMore: boolean
  hasMore: boolean
  searchTime: number
  selectedItem: SearchResult | null
  hasScopes: boolean
}>()

const emit = defineEmits<{
  select: [item: SearchResult]
  open: [path: string]
  addFolder: []
  loadMore: []
  'update:fileType': [value: string]
  'update:sortBy': [value: string]
}>()

// 文件类型过滤
const selectedFileType = defineModel<string>('fileType', { default: '' })
const sortBy = defineModel<string>('sortBy', { default: 'relevance' })

const fileTypeOptions = [
  { label: '全部类型', value: '' },
  { label: 'PDF', value: '.pdf' },
  { label: 'Word', value: '.docx' },
  { label: 'Excel', value: '.xlsx' },
  { label: 'PPT', value: '.pptx' },
  { label: 'TXT', value: '.txt' },
]

const sortOptions = [
  { label: '相关度', value: 'relevance' },
  { label: '文件名', value: 'filename' },
  { label: '文件类型', value: 'filetype' },
]

// 过滤和排序后的结果
const filteredResults = computed(() => {
  let list = props.results
  
  // 文件类型过滤
  if (selectedFileType.value) {
    list = list.filter(item => 
      item.file_path.toLowerCase().endsWith(selectedFileType.value)
    )
  }
  
  // 排序
  if (sortBy.value === 'filename') {
    list = [...list].sort((a, b) => {
      const nameA = a.file_path.split('\\').pop() || ''
      const nameB = b.file_path.split('\\').pop() || ''
      return nameA.localeCompare(nameB, 'zh-CN')
    })
  } else if (sortBy.value === 'filetype') {
    list = [...list].sort((a, b) => {
      const extA = a.file_path.split('.').pop() || ''
      const extB = b.file_path.split('.').pop() || ''
      return extA.localeCompare(extB)
    })
  }
  
  return list
})
</script>

<template>
  <div class="results-panel">
    <!-- 加载状态 -->
    <div v-if="loading" class="panel-content">
      <el-skeleton :rows="8" animated />
    </div>
    
    <!-- 空状态 -->
    <div v-else-if="results.length === 0" class="panel-content empty-content">
      <!-- 无搜索范围时的引导 -->
      <div v-if="!hasScopes" class="onboarding-hint">
        <el-icon :size="64" color="#409EFF"><Folder /></el-icon>
        <h3>开始使用</h3>
        <p>点击上方「管理搜索范围」添加文件夹</p>
        <p class="hint-sub">或直接拖拽文件夹到窗口</p>
        <el-button type="primary" size="large" @click="emit('addFolder')" style="margin-top: 16px">
          <el-icon><FolderAdd /></el-icon>
          添加第一个文件夹
        </el-button>
      </div>
      <!-- 有范围但无结果 -->
      <el-empty v-else description="暂无搜索结果" :image-size="120">
        <template #description>
          <p style="color: #909399; font-size: 16px">输入关键词开始搜索</p>
        </template>
      </el-empty>
    </div>
    
    <!-- 结果列表 -->
    <div v-else class="panel-content">
      <!-- 结果头部工具栏 -->
      <div class="results-toolbar">
        <div class="results-info">
          <span class="results-count">找到 <strong>{{ filteredResults.length }}</strong> 个结果</span>
          <span v-if="selectedFileType" class="filter-badge">
            已筛选: {{ fileTypeOptions.find(o => o.value === selectedFileType)?.label }}
          </span>
          <span class="results-time">耗时 {{ searchTime }}ms</span>
        </div>
        <div class="results-filters">
          <el-select v-model="selectedFileType" placeholder="文件类型" size="small" style="width: 110px">
            <el-option
              v-for="item in fileTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
          <el-select v-model="sortBy" placeholder="排序" size="small" style="width: 100px">
            <el-option
              v-for="item in sortOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </div>
      </div>
      
      <div class="results-list">
        <ResultCard
          v-for="(item, index) in filteredResults"
          :key="index"
          :item="item"
          :active="selectedItem === item"
          @select="emit('select', $event)"
          @open="emit('open', $event)"
        />
        
        <!-- 加载更多按钮 -->
        <div v-if="hasMore" class="load-more-container">
          <el-button 
            type="primary" 
            plain 
            :loading="loadingMore"
            @click="emit('loadMore')"
          >
            <el-icon v-if="!loadingMore"><Loading /></el-icon>
            {{ loadingMore ? '加载中...' : '加载更多结果' }}
          </el-button>
        </div>
        
        <!-- 已加载全部提示 -->
        <div v-else-if="results.length > 0" class="all-loaded-hint">
          <span>—— 已显示全部 {{ results.length }} 个结果 ——</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.results-panel {
  width: 480px;
  flex-shrink: 0;
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

.results-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 2px solid #f0f0f0;
  flex-wrap: wrap;
  gap: 12px;
}

.results-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.results-filters {
  display: flex;
  gap: 8px;
}

.filter-badge {
  background: #ecf5ff;
  color: #409EFF;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.results-count {
  font-size: 16px;
  color: #606266;
}

.results-count strong {
  color: #409EFF;
  font-size: 20px;
}

.results-time {
  font-size: 14px;
  color: #909399;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 引导提示 */
.onboarding-hint {
  text-align: center;
  padding: 40px 20px;
}

.onboarding-hint h3 {
  margin: 20px 0 12px;
  font-size: 22px;
  color: #303133;
}

.onboarding-hint p {
  color: #606266;
  font-size: 15px;
  margin: 8px 0;
}

.onboarding-hint .hint-sub {
  color: #909399;
  font-size: 13px;
}

/* 加载更多 */
.load-more-container {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.load-more-container .el-button {
  min-width: 200px;
}

.all-loaded-hint {
  text-align: center;
  padding: 16px 0;
  color: #909399;
  font-size: 13px;
}
</style>
