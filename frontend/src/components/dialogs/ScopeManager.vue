<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Folder, Document, Delete, RefreshRight, InfoFilled, Check, Warning } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { SearchScope } from '@/types'
import { getIndexStatus, batchIndex, deleteIndex } from '@/api'

const visible = defineModel<boolean>({ required: true })

const props = defineProps<{
  scopes: SearchScope[]
}>()

const emit = defineEmits<{
  browseFolder: []
  browseFile: []
  removeScope: [path: string]
  reindexScope: [path: string]
  'update:scopes': [scopes: SearchScope[]]
}>()

// 索引状态
const indexingPaths = ref<Set<string>>(new Set())
const selectedForIndex = ref<Set<string>>(new Set())

// 计算已选中待索引的数量
const selectedCount = computed(() => selectedForIndex.value.size)

// 计算未索引的数量
const notIndexedCount = computed(() => {
  return props.scopes.filter(s => s.indexStatus === 'not_indexed').length
})

// 全选/取消全选未索引项
const selectAllNotIndexed = () => {
  const notIndexed = props.scopes.filter(s => s.indexStatus === 'not_indexed')
  if (notIndexed.every(s => selectedForIndex.value.has(s.path))) {
    // 已全选，取消全选
    notIndexed.forEach(s => selectedForIndex.value.delete(s.path))
  } else {
    // 全选
    notIndexed.forEach(s => selectedForIndex.value.add(s.path))
  }
}

// 切换选中状态
const toggleSelection = (path: string) => {
  if (selectedForIndex.value.has(path)) {
    selectedForIndex.value.delete(path)
  } else {
    selectedForIndex.value.add(path)
  }
}

// 加载索引状态
const loadIndexStatus = async () => {
  if (props.scopes.length === 0) return
  
  try {
    const paths = props.scopes.map(s => s.path)
    const statuses = await getIndexStatus(paths)
    
    // 更新 scopes 的索引状态
    statuses.forEach(status => {
      const scope = props.scopes.find(s => 
        s.path.toLowerCase() === status.path.toLowerCase()
      )
      if (scope) {
        scope.indexStatus = status.status
        scope.indexedCount = status.indexed_count
      }
    })
  } catch (error) {
    console.error('Failed to load index status:', error)
  }
}

// 批量索引选中的路径
const handleBatchIndex = async () => {
  const pathsToIndex = Array.from(selectedForIndex.value)
  if (pathsToIndex.length === 0) {
    ElMessage.warning('请先选择要索引的文件夹或文件')
    return
  }
  
  // 标记为索引中
  pathsToIndex.forEach(path => {
    indexingPaths.value.add(path)
    const scope = props.scopes.find(s => s.path === path)
    if (scope) scope.indexStatus = 'indexing'
  })
  
  try {
    const result = await batchIndex(pathsToIndex)
    
    ElMessage.success(
      `索引完成！处理 ${result.paths_processed} 个路径，新增 ${result.new_files_indexed} 个文件`
    )
    
    // 清空选中
    selectedForIndex.value.clear()
    
    // 重新加载状态
    await loadIndexStatus()
  } catch (error) {
    ElMessage.error('索引失败：' + error)
  } finally {
    pathsToIndex.forEach(path => indexingPaths.value.delete(path))
  }
}

// 单个路径索引
const handleSingleIndex = async (path: string) => {
  indexingPaths.value.add(path)
  const scope = props.scopes.find(s => s.path === path)
  if (scope) scope.indexStatus = 'indexing'
  
  try {
    const result = await batchIndex([path])
    ElMessage.success(`索引完成，新增 ${result.new_files_indexed} 个文件`)
    await loadIndexStatus()
  } catch (error) {
    ElMessage.error('索引失败：' + error)
  } finally {
    indexingPaths.value.delete(path)
  }
}

// 格式化路径（显示最后两级目录）
const formatPath = (path: string): string => {
  const parts = path.split('\\')
  if (parts.length <= 2) return path
  return '...' + '\\' + parts.slice(-2).join('\\')
}

// 删除范围（带确认弹窗）
const handleRemoveScope = async (scope: SearchScope) => {
  const isIndexed = scope.indexStatus === 'indexed'
  const indexedCount = scope.indexedCount || 0
  
  if (isIndexed && indexedCount > 0) {
    // 已索引的路径，询问是否同时删除索引
    try {
      const action = await ElMessageBox.confirm(
        `该路径已索引 ${indexedCount} 个文件，是否同时删除索引数据？`,
        '删除确认',
        {
          confirmButtonText: '删除范围和索引',
          cancelButtonText: '仅删除范围',
          distinguishCancelAndClose: true,
          type: 'warning',
        }
      )
      
      if (action === 'confirm') {
        // 用户选择删除索引
        try {
          const result = await deleteIndex(scope.path)
          ElMessage.success(`已删除 ${result.deleted_count} 条索引数据`)
        } catch (error) {
          ElMessage.error('删除索引失败：' + error)
        }
      }
      // 无论选择什么，都删除范围
      emit('removeScope', scope.path)
    } catch (action) {
      if (action === 'cancel') {
        // 用户选择仅删除范围
        emit('removeScope', scope.path)
      }
      // close 则不做任何操作
    }
  } else {
    // 未索引的路径，直接删除
    emit('removeScope', scope.path)
  }
}

// 监听 scopes 变化，加载索引状态
watch(() => props.scopes.length, () => {
  loadIndexStatus()
})

// 监听对话框打开
watch(visible, (val) => {
  if (val) {
    loadIndexStatus()
  }
})

onMounted(() => {
  if (visible.value) {
    loadIndexStatus()
  }
})
</script>

<template>
  <el-dialog v-model="visible" title="管理搜索范围" width="800px">
    <div class="scope-manager">
      <!-- 操作按钮 -->
      <div class="button-group">
        <el-button :icon="Folder" @click="emit('browseFolder')" type="primary" size="large">
          添加文件夹
        </el-button>
        <el-button :icon="Document" @click="emit('browseFile')" type="primary" size="large">
          添加文件
        </el-button>
      </div>
      
      <!-- 提示信息 -->
      <div v-if="scopes.length > 0" class="scope-summary">
        <el-icon><InfoFilled /></el-icon>
        <span>共 {{ scopes.length }} 个搜索范围，{{ scopes.filter(s => s.active).length }} 个已启用</span>
        
        <!-- 批量索引按钮 -->
        <div class="batch-actions">
          <el-button 
            v-if="notIndexedCount > 0"
            size="small" 
            @click="selectAllNotIndexed"
          >
            全选未索引
          </el-button>
          <el-button 
            v-if="selectedCount > 0"
            type="success" 
            size="small"
            :loading="indexingPaths.size > 0"
            @click="handleBatchIndex"
          >
            索引选中 ({{ selectedCount }})
          </el-button>
        </div>
      </div>
      
      <!-- 范围列表 -->
      <div class="scope-list">
        <el-empty v-if="scopes.length === 0" description="暂无搜索范围，请添加文件夹或文件" />
        
        <div v-else v-for="(scope, index) in scopes" :key="index" class="scope-card">
          <div class="scope-main">
            <!-- 搜索范围启用/禁用复选框 -->
            <el-tooltip :content="scope.active ? '点击禁用此范围' : '点击启用此范围'" placement="top">
              <el-checkbox 
                v-model="scope.active" 
                size="large" 
              />
            </el-tooltip>
            
            <!-- 批量索引选择复选框（仅未索引时显示） -->
            <el-checkbox
              v-if="scope.indexStatus === 'not_indexed'"
              :model-value="selectedForIndex.has(scope.path)"
              @change="toggleSelection(scope.path)"
              size="small"
              class="index-checkbox"
            >
              <span class="index-checkbox-label">选中索引</span>
            </el-checkbox>
            
            <el-icon :size="24" :color="scope.type === 'folder' ? '#409EFF' : '#67C23A'">
              <Folder v-if="scope.type === 'folder'" />
              <Document v-else />
            </el-icon>
            <div class="scope-info">
              <span class="scope-name">{{ formatPath(scope.path) }}</span>
              <span class="scope-full-path" :title="scope.path">{{ scope.path }}</span>
            </div>
          </div>
          
          <div class="scope-actions">
            <!-- 类型标签 -->
            <el-tag :type="scope.type === 'folder' ? 'info' : 'success'" size="small">
              {{ scope.type === 'folder' ? '文件夹' : '文件' }}
            </el-tag>
            
            <!-- 索引状态标签 -->
            <el-tag 
              v-if="scope.indexStatus === 'indexed'" 
              type="success" 
              size="small" 
              effect="light"
            >
              <el-icon class="tag-icon"><Check /></el-icon>
              已索引 ({{ scope.indexedCount }})
            </el-tag>
            <el-tag 
              v-else-if="scope.indexStatus === 'indexing'" 
              type="warning" 
              size="small" 
              effect="light"
            >
              索引中...
            </el-tag>
            <el-tag 
              v-else 
              type="danger" 
              size="small" 
              effect="light"
            >
              <el-icon class="tag-icon"><Warning /></el-icon>
              未索引
            </el-tag>
            
            <el-button-group size="small">
              <el-tooltip :content="scope.indexStatus === 'indexed' ? '更新索引' : '开始索引'" placement="top">
                <el-button 
                  :icon="RefreshRight" 
                  :loading="indexingPaths.has(scope.path)"
                  :type="scope.indexStatus === 'not_indexed' ? 'primary' : 'default'"
                  @click="handleSingleIndex(scope.path)"
                />
              </el-tooltip>
              <el-tooltip content="删除" placement="top">
                <el-button 
                  :icon="Delete" 
                  type="danger" 
                  @click="handleRemoveScope(scope)"
                />
              </el-tooltip>
            </el-button-group>
          </div>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<style scoped>
.scope-manager {
  padding: 10px 0;
}

.button-group {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.button-group .el-button {
  flex: 1;
}

.scope-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #f0f9ff;
  border-radius: 8px;
  color: #409EFF;
  font-size: 14px;
  margin-bottom: 16px;
}

.batch-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.scope-list {
  max-height: 450px;
  overflow-y: auto;
}

.scope-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 10px;
  margin-bottom: 12px;
  transition: all 0.3s;
}

.scope-card:hover {
  border-color: #409EFF;
  background: #fafafa;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.scope-main {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.scope-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  flex: 1;
}

.scope-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.scope-full-path {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.scope-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.tag-icon {
  margin-right: 4px;
  vertical-align: middle;
}

.index-checkbox {
  margin-left: -4px;
  padding: 2px 6px;
  background: #fef0f0;
  border-radius: 4px;
  border: 1px dashed #f56c6c;
}

.index-checkbox-label {
  font-size: 11px;
  color: #f56c6c;
}
</style>
