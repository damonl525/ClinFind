<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Loading, Plus, Check, Close } from '@element-plus/icons-vue'

interface ExpandedTerm {
  original: string
  expanded: string[]
}

const props = defineProps<{
  visible: boolean
  loading: boolean
  originalQuery: string
  expandedTerms: ExpandedTerm[]
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  confirm: [terms: ExpandedTerm[]]
  cancel: []
}>()

// 本地编辑状态
const editableTerms = ref<ExpandedTerm[]>([])

// 当弹窗打开时，复制扩展词到本地编辑状态
watch(() => props.visible, (visible) => {
  if (visible && props.expandedTerms.length > 0) {
    editableTerms.value = props.expandedTerms.map(t => ({
      original: t.original,
      expanded: [...t.expanded]
    }))
  }
})

// 当扩展词更新时同步
watch(() => props.expandedTerms, (terms) => {
  if (terms.length > 0) {
    editableTerms.value = terms.map(t => ({
      original: t.original,
      expanded: [...t.expanded]
    }))
  }
}, { deep: true })

// 计算总扩展词数
const totalExpandedCount = computed(() => {
  return editableTerms.value.reduce((sum, t) => sum + t.expanded.length, 0)
})

// 删除单个扩展词
const removeExpanded = (termIndex: number, expandedIndex: number) => {
  editableTerms.value[termIndex].expanded.splice(expandedIndex, 1)
}

// 添加新搜索词（带输入框）
const addingToIndex = ref<number | null>(null)
const newExpandedInput = ref('')

const startAddingExpanded = (index: number) => {
  addingToIndex.value = index
  newExpandedInput.value = ''
}

const confirmAddExpanded = (termIndex: number) => {
  if (newExpandedInput.value.trim()) {
    editableTerms.value[termIndex].expanded.push(newExpandedInput.value.trim())
  }
  addingToIndex.value = null
  newExpandedInput.value = ''
}

const cancelAddExpanded = () => {
  addingToIndex.value = null
  newExpandedInput.value = ''
}

// 确认并开始搜索
const handleConfirm = () => {
  emit('confirm', editableTerms.value)
  emit('update:visible', false)
}

// 取消
const handleCancel = () => {
  emit('cancel')
  emit('update:visible', false)
}

const handleClose = () => {
  emit('update:visible', false)
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="handleClose"
    title="AI 智能扩展"
    width="600px"
    :close-on-click-modal="false"
    class="ai-expand-dialog"
  >
    <!-- 加载中状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="loading-icon" :size="48"><Loading /></el-icon>
      <p>AI 正在分析搜索词并生成扩展词...</p>
      <p class="loading-hint">这可能需要几秒钟</p>
    </div>

    <!-- 扩展结果 -->
    <div v-else class="expand-content">
      <div class="query-info">
        <span class="label">原始搜索词：</span>
        <span class="query">{{ originalQuery }}</span>
      </div>

      <el-divider />

      <div class="terms-section">
        <div class="section-header">
          <h4>扩展词列表</h4>
          <span class="count-badge">共 {{ totalExpandedCount }} 个扩展词</span>
        </div>

        <div v-for="(term, termIndex) in editableTerms" :key="termIndex" class="term-group">
          <div class="term-header">
            <el-tag type="primary" size="large">{{ term.original }}</el-tag>
            <span class="arrow">→</span>
          </div>
          
          <div class="expanded-tags">
            <el-tag
              v-for="(expanded, expIndex) in term.expanded"
              :key="expIndex"
              closable
              type="success"
              @close="removeExpanded(termIndex, expIndex)"
            >
              {{ expanded }}
            </el-tag>
            
            <!-- 添加新扩展词 -->
            <div v-if="addingToIndex === termIndex" class="add-input-wrapper">
              <el-input
                v-model="newExpandedInput"
                size="small"
                placeholder="输入扩展词"
                style="width: 120px"
                @keyup.enter="confirmAddExpanded(termIndex)"
              />
              <el-button size="small" type="primary" :icon="Check" @click="confirmAddExpanded(termIndex)" />
              <el-button size="small" :icon="Close" @click="cancelAddExpanded" />
            </div>
            <el-button
              v-else
              size="small"
              type="primary"
              plain
              :icon="Plus"
              @click="startAddingExpanded(termIndex)"
            >
              添加
            </el-button>
          </div>

          <el-alert
            v-if="term.expanded.length === 0"
            type="warning"
            :closable="false"
            show-icon
          >
            没有生成扩展词。您可以手动添加，或该词将只搜索原词。
          </el-alert>
        </div>
      </div>

      <el-divider />

      <div class="tips">
        <el-icon><Loading /></el-icon>
        <span>提示：您可以删除不相关的扩展词，或添加更多相关词来优化搜索结果</span>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">取消搜索</el-button>
        <el-button type="primary" @click="handleConfirm" :disabled="loading">
          <el-icon><Check /></el-icon>
          确认并搜索
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.loading-container {
  text-align: center;
  padding: 40px 20px;
}

.loading-icon {
  animation: spin 1s linear infinite;
  color: #409EFF;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-container p {
  margin: 16px 0 8px;
  font-size: 16px;
  color: #303133;
}

.loading-hint {
  color: #909399 !important;
  font-size: 14px !important;
}

.expand-content {
  padding: 0 10px;
}

.query-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.query-info .label {
  color: #909399;
  font-size: 14px;
}

.query-info .query {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.terms-section {
  margin: 16px 0;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-header h4 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.count-badge {
  background: #ecf5ff;
  color: #409EFF;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
}

.term-group {
  margin-bottom: 20px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.term-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.arrow {
  color: #909399;
  font-size: 18px;
}

.expanded-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.expanded-tags .el-tag {
  font-size: 14px;
}

.add-input-wrapper {
  display: flex;
  gap: 4px;
  align-items: center;
}

.tips {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f0f9eb;
  border-radius: 6px;
  color: #67c23a;
  font-size: 13px;
}

.tips .el-icon {
  animation: none;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
