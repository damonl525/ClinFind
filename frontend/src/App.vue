<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { searchFiles, indexFolder, checkHealth, getDebugStats, expandQueryWithAI } from './api'
import type { SearchResult, DebugStats } from './api'
import type { SearchScope, IndexingProgress } from './types'
import { useSearchHistory } from './composables/useSearchHistory'
import { useAIConfig } from './composables/useAIConfig'

// 组件导入
import TopBar from './components/layout/TopBar.vue'
import SearchBar from './components/search/SearchBar.vue'
import ResultsList from './components/search/ResultsList.vue'
import FilePreview from './components/search/FilePreview.vue'
import ScopeManager from './components/dialogs/ScopeManager.vue'
import SettingsDialog from './components/dialogs/SettingsDialog.vue'
import DebugPanel from './components/dialogs/DebugPanel.vue'
import WelcomeGuide from './components/dialogs/WelcomeGuide.vue'
import AIExpandDialog from './components/dialogs/AIExpandDialog.vue'
import DragOverlay from './components/common/DragOverlay.vue'
import IndexingProgressBar from './components/common/IndexingProgress.vue'

// =============== 状态管理 ===============
// 搜索相关
const searchQuery = ref('')
const searchPrecision = ref('medium')
const results = ref<SearchResult[]>([])
const loading = ref(false)
const loadingMore = ref(false)
const selectedItem = ref<SearchResult | null>(null)
const searchTime = ref<number>(0)

// 分页相关
const hasMoreResults = ref(false)
const currentOffset = ref(0)
const lastSearchQuery = ref('')
const lastSearchPaths = ref<string[]>([])
const PAGE_SIZE = 50

// 连接状态
const backendConnected = ref(false)

// 搜索范围
const searchScopes = ref<SearchScope[]>([])

// 对话框状态
const showScopeManager = ref(false)
const showSettings = ref(false)
const showDebugPanel = ref(false)
const showWelcome = ref(false)

// 调试信息
const debugStats = ref<DebugStats | null>(null)

// 索引进度
const indexingProgress = ref<IndexingProgress>({
  active: false,
  currentFile: '',
  totalFiles: 0,
  processedFiles: 0,
  folderPath: ''
})

// 拖拽状态
const isDragging = ref(false)

// 过滤和排序
const selectedFileType = ref('')
const sortBy = ref('relevance')

// 搜索历史
const { addToHistory } = useSearchHistory()

// AI 配置
const { aiConfig, isConfigValid } = useAIConfig()

// AI 扩展状态
const aiExpandedTerms = ref<string[]>([])

// AI 扩展弹窗状态
interface ExpandedTerm {
  original: string
  expanded: string[]
}
const showAIExpandDialog = ref(false)
const aiExpandLoading = ref(false)
const pendingExpandedTerms = ref<ExpandedTerm[]>([])

// =============== 方法 ===============
// 解析逻辑查询
const parseLogicalQuery = (query: string): { operator: 'AND' | 'OR' | null, terms: string[] } => {
  if (/\s+AND\s+/i.test(query)) {
    return { operator: 'AND', terms: query.split(/\s+AND\s+/i).map(t => t.trim()).filter(Boolean) }
  } else if (/\s+OR\s+/i.test(query)) {
    return { operator: 'OR', terms: query.split(/\s+OR\s+/i).map(t => t.trim()).filter(Boolean) }
  }
  return { operator: null, terms: [query] }
}

// AI 扩展单个词
const expandSingleTerm = async (term: string): Promise<string[]> => {
  try {
    const expandResult = await expandQueryWithAI(
      term, 
      {
        base_url: aiConfig.value.baseUrl,
        api_key: aiConfig.value.apiKey,
        model: aiConfig.value.model
      },
      aiConfig.value.expandPrompt  // 传递用户自定义的 prompt
    )
    if (expandResult.expanded && expandResult.expanded.length > 0) {
      return expandResult.expanded  // 只返回扩展词，不包含原词
    }
  } catch (e) {
    console.warn(`AI扩展词 "${term}" 失败:`, e)
  }
  return []
}

// 搜索
const handleSearch = async () => {
  if (!searchQuery.value.trim()) return
  
  const query = searchQuery.value.trim()
  const activePaths = searchScopes.value.filter(s => s.active).map(s => s.path)
  const { terms } = parseLogicalQuery(query)
  
  // AI 智能模式：先获取扩展词，弹窗让用户确认
  if (searchPrecision.value === 'ai' && aiConfig.value.enabled && isConfigValid()) {
    showAIExpandDialog.value = true
    aiExpandLoading.value = true
    pendingExpandedTerms.value = []
    
    try {
      // 对每个词分别进行 AI 扩展
      const expandedTermsArray: ExpandedTerm[] = []
      for (const term of terms) {
        const expanded = await expandSingleTerm(term)
        expandedTermsArray.push({
          original: term,
          expanded: expanded
        })
      }
      pendingExpandedTerms.value = expandedTermsArray
    } catch (e) {
      console.error('AI 扩展失败:', e)
      ElMessage.error('AI 扩展失败，请检查 API 配置')
      showAIExpandDialog.value = false
    } finally {
      aiExpandLoading.value = false
    }
  } else {
    // 精确匹配或普通模式：直接搜索
    await executeSearch(query, activePaths)
  }
}

// 用户确认扩展词后执行搜索
const handleAIExpandConfirm = async (confirmedTerms: ExpandedTerm[]) => {
  const activePaths = searchScopes.value.filter(s => s.active).map(s => s.path)
  const { operator } = parseLogicalQuery(searchQuery.value.trim())
  
  loading.value = true
  const start = performance.now()
  results.value = []
  selectedItem.value = null
  aiExpandedTerms.value = []
  currentOffset.value = 0
  hasMoreResults.value = false
  
  try {
    // 收集所有扩展词（用于显示）
    const allExpanded: string[] = []
    confirmedTerms.forEach(t => {
      allExpanded.push(...t.expanded)
    })
    aiExpandedTerms.value = allExpanded
    
    // 构建搜索查询
    const termResults: SearchResult[][] = []
    for (const termItem of confirmedTerms) {
      // 用 OR 连接原词和扩展词
      const searchTerms = [termItem.original, ...termItem.expanded]
      const orQuery = searchTerms.join(' OR ')
      const searchResponse = await searchFiles(
        orQuery, 
        PAGE_SIZE, 
        'medium', 
        activePaths.length > 0 ? activePaths : undefined,
        0
      )
      termResults.push(searchResponse.results)
    }
    
    // 根据操作符处理结果
    if (operator === 'AND') {
      // AND：取交集
      if (termResults.length > 0) {
        const pathSets = termResults.map(r => new Set(r.map(item => item.file_path)))
        const intersection = [...pathSets[0]].filter(path => 
          pathSets.every(set => set.has(path))
        )
        const resultMap = new Map(termResults[0].map(r => [r.file_path, r]))
        results.value = intersection
          .map(path => resultMap.get(path)!)
          .filter(Boolean)
      }
    } else if (operator === 'OR') {
      // OR：取并集（去重）
      const seen = new Set<string>()
      const merged: SearchResult[] = []
      for (const resultSet of termResults) {
        for (const result of resultSet) {
          if (!seen.has(result.file_path)) {
            seen.add(result.file_path)
            merged.push(result)
          }
        }
      }
      results.value = merged
    } else {
      // 无操作符：直接使用第一个结果
      results.value = termResults[0] || []
    }
    
    // AI 模式目前不支持分页（因为涉及多个搜索结果合并）
    hasMoreResults.value = false
    
    // 保存搜索条件
    lastSearchQuery.value = searchQuery.value.trim()
    lastSearchPaths.value = activePaths
    
    // 记录搜索历史
    addToHistory(searchQuery.value, results.value.length)
    
    console.log(`AI 搜索完成，扩展词: [${allExpanded.join(', ')}]，结果: ${results.value.length} 条`)
    
    if (results.value.length === 0) {
      ElMessage.info('未找到匹配结果')
    } else {
      ElMessage.success(`AI 搜索完成，使用了 ${allExpanded.length} 个扩展词`)
    }
  } catch (error) {
    ElMessage.error('搜索失败: ' + error)
  } finally {
    loading.value = false
    searchTime.value = Math.round(performance.now() - start)
  }
}

// AI 扩展取消
const handleAIExpandCancel = () => {
  showAIExpandDialog.value = false
  pendingExpandedTerms.value = []
}

// 执行普通搜索（非 AI 模式）
const executeSearch = async (query: string, activePaths: string[]) => {
  loading.value = true
  const start = performance.now()
  results.value = []
  selectedItem.value = null
  aiExpandedTerms.value = []
  currentOffset.value = 0
  hasMoreResults.value = false
  
  try {
    // 保存搜索条件用于加载更多
    lastSearchQuery.value = query
    lastSearchPaths.value = activePaths
    
    const response = await searchFiles(
      query, 
      PAGE_SIZE, 
      searchPrecision.value === 'exact' ? 'exact' : 'medium', 
      activePaths.length > 0 ? activePaths : undefined,
      0
    )
    results.value = response.results
    hasMoreResults.value = response.has_more
    currentOffset.value = PAGE_SIZE
    
    // 记录搜索历史
    addToHistory(searchQuery.value, results.value.length)
    
    if (results.value.length === 0) {
      ElMessage.info('未找到匹配结果')
    }
  } catch (error) {
    ElMessage.error('搜索失败: ' + error)
  } finally {
    loading.value = false
    searchTime.value = Math.round(performance.now() - start)
  }
}

// 加载更多结果
const loadMoreResults = async () => {
  if (loadingMore.value || !hasMoreResults.value) return
  
  loadingMore.value = true
  
  try {
    const response = await searchFiles(
      lastSearchQuery.value,
      PAGE_SIZE,
      searchPrecision.value === 'exact' ? 'exact' : 'medium',
      lastSearchPaths.value.length > 0 ? lastSearchPaths.value : undefined,
      currentOffset.value
    )
    
    // 追加结果
    results.value = [...results.value, ...response.results]
    hasMoreResults.value = response.has_more
    currentOffset.value += PAGE_SIZE
    
  } catch (error) {
    ElMessage.error('加载更多失败: ' + error)
  } finally {
    loadingMore.value = false
  }
}

// 选择结果
const selectResult = (result: SearchResult) => {
  selectedItem.value = result
}

// 打开文件
const openFile = async (filePath: string) => {
  if (window.electronAPI) {
    await window.electronAPI.openFile(filePath)
  } else {
    ElMessage.warning('浏览器模式下无法打开文件')
  }
}

// 索引文件夹（带进度显示）
const indexFolderWithProgress = async (path: string) => {
  if (searchScopes.value.some(s => s.path === path)) {
    ElMessage.warning('该路径已添加')
    return
  }
  
  searchScopes.value.push({ path, type: 'folder', active: true })
  
  indexingProgress.value = {
    active: true,
    currentFile: '正在扫描文件...',
    totalFiles: 0,
    processedFiles: 0,
    folderPath: path
  }
  
  try {
    const result = await indexFolder(path)
    
    indexingProgress.value.processedFiles = result.total_count
    indexingProgress.value.totalFiles = result.total_count
    indexingProgress.value.currentFile = '索引完成！'
    
    setTimeout(() => {
      indexingProgress.value.active = false
    }, 1500)
    
    if (result.indexed_count > 0) {
      ElMessage.success(`索引完成！已索引 ${result.indexed_count} 个文件，总计 ${result.total_count} 个文件`)
    } else {
      ElMessage.warning('文件夹已索引或无可索引文件')
    }
    
    if (showDebugPanel.value) {
      await loadDebugStats()
    }
  } catch (error: any) {
    indexingProgress.value.active = false
    ElMessage.error('索引失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 浏览文件夹
const browseFolder = async () => {
  if (window.electronAPI) {
    const path = await window.electronAPI.selectDirectory()
    if (path) {
      await indexFolderWithProgress(path)
    }
  }
}

// 浏览文件
const browseFile = async () => {
  if (window.electronAPI) {
    const path = await window.electronAPI.selectFile()
    if (path && !searchScopes.value.some(s => s.path === path)) {
      searchScopes.value.push({ path, type: 'file', active: true })
      
      indexingProgress.value = {
        active: true,
        currentFile: path.split('\\').pop() || path,
        totalFiles: 1,
        processedFiles: 0,
        folderPath: path
      }
      
      try {
        const result = await indexFolder(path)
        indexingProgress.value.processedFiles = 1
        indexingProgress.value.currentFile = '索引完成！'
        
        setTimeout(() => {
          indexingProgress.value.active = false
        }, 1500)
        
        if (result.indexed_count > 0) {
          ElMessage.success(`索引完成！已索引 ${result.indexed_count} 个文件`)
        } else {
          ElMessage.warning('文件已索引或无法索引')
        }
        
        if (showDebugPanel.value) {
          await loadDebugStats()
        }
      } catch (error: any) {
        indexingProgress.value.active = false
        ElMessage.error('索引失败: ' + (error.response?.data?.detail || error.message))
      }
    }
  }
}

// 移除搜索范围
const removeScope = (path: string) => {
  searchScopes.value = searchScopes.value.filter(s => s.path !== path)
}

// 重新索引
const reindexScope = async (path: string) => {
  indexingProgress.value = {
    active: true,
    currentFile: '重新索引中...',
    totalFiles: 0,
    processedFiles: 0,
    folderPath: path
  }
  
  try {
    const result = await indexFolder(path)
    
    indexingProgress.value.processedFiles = result.total_count
    indexingProgress.value.totalFiles = result.total_count
    indexingProgress.value.currentFile = '重新索引完成！'
    
    setTimeout(() => {
      indexingProgress.value.active = false
    }, 1500)
    
    ElMessage.success(`重新索引完成！更新了 ${result.indexed_count} 个文件`)
  } catch (error: any) {
    indexingProgress.value.active = false
    ElMessage.error('重新索引失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 拖拽处理
const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = true
}

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = false
}

const handleDrop = async (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = false
  
  if (!window.electronAPI) {
    ElMessage.warning('浏览器模式下无法添加文件夹')
    return
  }
  
  const items = e.dataTransfer?.items
  if (items) {
    for (let i = 0; i < items.length; i++) {
      const item = items[i]
      if (item.kind === 'file') {
        const file = item.getAsFile()
        if (file) {
          const path = (file as any).path
          if (path) {
            await indexFolderWithProgress(path)
          }
        }
      }
    }
  }
}

// 欢迎对话框
const closeWelcome = () => {
  showWelcome.value = false
  localStorage.setItem('file_searcher_welcomed', 'true')
}

const addFolderFromWelcome = async () => {
  closeWelcome()
  await browseFolder()
}

// 检查后端
const checkBackendConnection = async () => {
  const health = await checkHealth()
  backendConnected.value = !!health
  if (!backendConnected.value) {
    ElMessage.error('后端服务未连接')
  }
}

// 加载调试信息
const loadDebugStats = async () => {
  debugStats.value = await getDebugStats()
}

const openDebugPanel = async () => {
  await loadDebugStats()
  showDebugPanel.value = true
}

// 保存搜索范围
watch(searchScopes, (newVal) => {
  localStorage.setItem('search_scopes', JSON.stringify(newVal))
}, { deep: true })

// 初始化
onMounted(async () => {
  await checkBackendConnection()
  const saved = localStorage.getItem('search_scopes')
  if (saved) {
    searchScopes.value = JSON.parse(saved)
  }
  
  // 检查是否是首次访问
  const welcomed = localStorage.getItem('file_searcher_welcomed')
  if (!welcomed && searchScopes.value.length === 0) {
    showWelcome.value = true
  }
})
</script>

<template>
  <div class="app-wrapper"
    @dragover="handleDragOver"
    @dragleave="handleDragLeave"
    @drop="handleDrop"
  >
    <!-- 拖拽覆盖层 -->
    <DragOverlay v-if="isDragging" />
    
    <!-- 索引进度条 -->
    <IndexingProgressBar :progress="indexingProgress" />

    <!-- 顶部工具栏 -->
    <TopBar 
      :backend-connected="backendConnected"
      @open-scope-manager="showScopeManager = true"
      @check-backend="checkBackendConnection"
      @open-settings="showSettings = true"
    />

    <!-- 搜索栏 -->
    <SearchBar
      v-model="searchQuery"
      v-model:precision="searchPrecision"
      :loading="loading"
      :scope-count="searchScopes.filter(s => s.active).length"
      @search="handleSearch"
    />

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧：搜索结果 -->
      <ResultsList
        :results="results"
        :loading="loading"
        :loading-more="loadingMore"
        :has-more="hasMoreResults"
        :search-time="searchTime"
        :selected-item="selectedItem"
        :has-scopes="searchScopes.length > 0"
        v-model:file-type="selectedFileType"
        v-model:sort-by="sortBy"
        @select="selectResult"
        @open="openFile"
        @add-folder="browseFolder"
        @load-more="loadMoreResults"
      />

      <!-- 右侧：文件预览 -->
      <FilePreview :item="selectedItem" />
    </div>

    <!-- 对话框 -->
    <ScopeManager
      v-model="showScopeManager"
      :scopes="searchScopes"
      @browse-folder="browseFolder"
      @browse-file="browseFile"
      @remove-scope="removeScope"
      @reindex-scope="reindexScope"
    />
    
    <SettingsDialog
      v-model="showSettings"
      @open-debug-panel="openDebugPanel"
    />
    
    <DebugPanel
      v-model="showDebugPanel"
      :stats="debugStats"
    />
    
    <WelcomeGuide
      v-model="showWelcome"
      @add-folder="addFolderFromWelcome"
      @close="closeWelcome"
    />
    
    <!-- AI 扩展词确认弹窗 -->
    <AIExpandDialog
      v-model:visible="showAIExpandDialog"
      :loading="aiExpandLoading"
      :original-query="searchQuery"
      :expanded-terms="pendingExpandedTerms"
      @confirm="handleAIExpandConfirm"
      @cancel="handleAIExpandCancel"
    />
  </div>
</template>

<style scoped>
* {
  box-sizing: border-box;
}

.app-wrapper {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  gap: 20px;
  padding: 20px 40px 40px;
  overflow: hidden;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
