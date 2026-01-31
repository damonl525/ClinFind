<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Search, Clock, Close, Aim, MagicStick } from '@element-plus/icons-vue'
import { useSearchHistory } from '@/composables/useSearchHistory'
import { useAIConfig } from '@/composables/useAIConfig'

const props = defineProps<{
  modelValue: string
  precision: string
  loading: boolean
  scopeCount: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'update:precision': [value: string]
  search: []
}>()

// 搜索历史
const { 
  searchHistory, 
  getMatchingHistory, 
  removeFromHistory, 
  clearHistory,
  formatTime 
} = useSearchHistory()

// AI 配置
const { aiConfig } = useAIConfig()

// 本地状态
const showSuggestions = ref(false)

const searchQuery = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const searchPrecision = computed({
  get: () => props.precision,
  set: (val) => emit('update:precision', val)
})

// 搜索模式选项
const searchModes = computed(() => [
  { 
    label: '精确匹配', 
    value: 'exact', 
    icon: Aim,
    description: '只匹配完全一致的关键词'
  },
  { 
    label: aiConfig.value.enabled ? 'AI 智能' : '模糊匹配', 
    value: 'ai', 
    icon: MagicStick,
    description: aiConfig.value.enabled 
      ? 'AI 自动扩展关键词，找到更多相关结果' 
      : '包含相似词和扩展匹配（设置中启用 AI 获得更好效果）',
    aiEnabled: aiConfig.value.enabled
  },
])

// 获取匹配的建议
const suggestions = computed(() => {
  return getMatchingHistory(searchQuery.value)
})

// 处理搜索
const handleSearch = () => {
  showSuggestions.value = false
  emit('search')
}

// 选择建议
const selectSuggestion = (query: string) => {
  searchQuery.value = query
  showSuggestions.value = false
  emit('search')
}

// 删除历史项
const deleteHistoryItem = (e: MouseEvent, query: string) => {
  e.stopPropagation()
  removeFromHistory(query)
}

// 处理输入框焦点
const handleFocus = () => {
  if (searchHistory.value.length > 0) {
    showSuggestions.value = true
  }
}

const handleBlur = () => {
  // 延迟关闭，允许点击建议项
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}

// 监听搜索词变化
watch(() => props.modelValue, (val) => {
  if (val && searchHistory.value.length > 0) {
    showSuggestions.value = true
  }
})
</script>

<template>
  <div class="search-bar-container">
    <div class="search-bar">
      <!-- 搜索模式切换 -->
      <div class="search-mode-toggle">
        <el-tooltip 
          v-for="mode in searchModes" 
          :key="mode.value"
          :content="mode.description" 
          placement="bottom"
        >
          <el-button
            :type="searchPrecision === mode.value ? 'primary' : 'default'"
            :icon="mode.icon"
            size="large"
            @click="searchPrecision = mode.value"
          >
            {{ mode.label }}
          </el-button>
        </el-tooltip>
      </div>
      
      <div class="search-input-wrapper">
        <el-input
          v-model="searchQuery"
          placeholder="输入搜索关键词，按回车搜索..."
          clearable
          size="large"
          @keyup.enter="handleSearch"
          @focus="handleFocus"
          @blur="handleBlur"
          class="search-input"
        >
          <template #append>
            <el-button :icon="Search" @click="handleSearch" :loading="loading" size="large">
              搜索
            </el-button>
          </template>
        </el-input>
        
        <!-- 搜索历史下拉 -->
        <transition name="fade">
          <div v-if="showSuggestions && suggestions.length > 0" class="suggestions-dropdown">
            <div class="suggestions-header">
              <span class="suggestions-title">
                <el-icon><Clock /></el-icon>
                搜索历史
              </span>
              <el-button 
                v-if="searchHistory.length > 0" 
                text 
                size="small" 
                @click="clearHistory"
              >
                清空
              </el-button>
            </div>
            <div class="suggestions-list">
              <div 
                v-for="item in suggestions" 
                :key="item.query"
                class="suggestion-item"
                @click="selectSuggestion(item.query)"
              >
                <div class="suggestion-content">
                  <el-icon class="suggestion-icon"><Clock /></el-icon>
                  <span class="suggestion-text">{{ item.query }}</span>
                  <span v-if="item.resultCount !== undefined" class="suggestion-count">
                    {{ item.resultCount }} 结果
                  </span>
                </div>
                <div class="suggestion-meta">
                  <span class="suggestion-time">{{ formatTime(item.timestamp) }}</span>
                  <el-button 
                    :icon="Close" 
                    circle 
                    size="small" 
                    text
                    @click="deleteHistoryItem($event, item.query)"
                    class="delete-btn"
                  />
                </div>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>
    
    <!-- 搜索提示 -->
    <div class="search-tips">
      <span class="tip-item">💡 <code>词1 AND 词2</code> 同时包含</span>
      <span class="tip-item"><code>词1 OR 词2</code> 任意包含</span>
      <span v-if="scopeCount > 0" class="tip-item scope-tip">📂 搜索范围: {{ scopeCount }} 个文件夹</span>
    </div>
  </div>
</template>

<style scoped>
.search-bar-container {
  padding: 30px 40px 20px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.search-bar {
  display: flex;
  gap: 12px;
  max-width: 1400px;
  margin: 0 auto;
  align-items: center;
}

.search-mode-toggle {
  display: flex;
  gap: 0;
}

.search-mode-toggle .el-button {
  border-radius: 0;
}

.search-mode-toggle .el-button:first-child {
  border-radius: 8px 0 0 8px;
}

.search-mode-toggle .el-button:last-child {
  border-radius: 0 8px 8px 0;
  margin-left: -1px;
}

.search-input-wrapper {
  flex: 1;
  position: relative;
}

.search-input {
  width: 100%;
}

.scope-info {
  text-align: center;
  margin-top: 12px;
  color: #606266;
  font-size: 14px;
}

/* 搜索历史下拉框 */
.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  margin-top: 4px;
  overflow: hidden;
}

.suggestions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.suggestions-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #909399;
  font-weight: 500;
}

.suggestions-list {
  max-height: 320px;
  overflow-y: auto;
}

.suggestion-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.suggestion-item:hover {
  background: #f5f7fa;
}

.suggestion-content {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.suggestion-icon {
  color: #909399;
  flex-shrink: 0;
}

.suggestion-text {
  font-size: 14px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.suggestion-count {
  font-size: 12px;
  color: #909399;
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 10px;
  flex-shrink: 0;
}

.suggestion-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.suggestion-time {
  font-size: 12px;
  color: #c0c4cc;
}

.delete-btn {
  opacity: 0;
  transition: opacity 0.2s;
}

.suggestion-item:hover .delete-btn {
  opacity: 1;
}

/* 动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* 搜索提示 */
.search-tips {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 12px;
  padding: 0 4px;
}

.tip-item {
  font-size: 12px;
  color: #909399;
}

.tip-item code {
  background: #f4f4f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  color: #606266;
  font-size: 11px;
}

.scope-tip {
  margin-left: auto;
  color: #409EFF;
}
</style>
