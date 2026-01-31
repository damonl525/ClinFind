<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { CircleCheck, Warning, Plus, Delete } from '@element-plus/icons-vue'
import { useAIConfig } from '@/composables/useAIConfig'
import { ElMessage, ElMessageBox } from 'element-plus'

const visible = defineModel<boolean>({ required: true })

const { locale } = useI18n()
const { aiConfig, allProviders, applyPreset, saveAsPreset, deletePreset, isConfigValid, testConnection, resetPrompt } = useAIConfig()

// 测试状态
const testing = ref(false)
const testResult = ref<{ success: boolean; message: string } | null>(null)

// 当前选择的预设（从保存的配置初始化）
const selectedPreset = ref(aiConfig.value.currentProvider || '')

// 计算当前预设是否为自定义
const isCurrentPresetCustom = computed(() => {
  const preset = allProviders.value.find(p => p.name === selectedPreset.value)
  return preset?.isCustom
})

// 处理预设选择
const handlePresetChange = (presetName: string) => {
  applyPreset(presetName)
  selectedPreset.value = presetName
  testResult.value = null
}

// 保存当前配置为新预设
const handleSavePreset = async () => {
  try {
    const { value: name } = await ElMessageBox.prompt('请输入供应商名称', '保存配置', {
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputValue: selectedPreset.value === '自定义' ? '' : selectedPreset.value,
      inputPattern: /^.+$/,
      inputErrorMessage: '名称不能为空'
    })
    
    if (name) {
      saveAsPreset(name)
      selectedPreset.value = name
      ElMessage.success(`已保存供应商 "${name}"`)
    }
  } catch {
    // 用户取消
  }
}

// 删除当前预设
const handleDeletePreset = async () => {
  if (!selectedPreset.value) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除供应商 "${selectedPreset.value}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    deletePreset(selectedPreset.value)
    selectedPreset.value = '自定义'
    ElMessage.success('删除成功')
  } catch {
    // 取消
  }
}

// 测试 API 连接
const handleTest = async () => {
  if (!isConfigValid()) {
    ElMessage.warning('请先完成所有配置项')
    return
  }
  
  testing.value = true
  testResult.value = null
  
  try {
    testResult.value = await testConnection()
    if (testResult.value.success) {
      ElMessage.success('连接成功！')
    } else {
      ElMessage.error(testResult.value.message)
    }
  } catch (error) {
    testResult.value = { success: false, message: '测试失败' }
    ElMessage.error('测试失败')
  } finally {
    testing.value = false
  }
}

// 是否显示 API Key
const showApiKey = ref(false)

const emit = defineEmits<{
  openDebugPanel: []
}>()
</script>

<template>
  <el-dialog v-model="visible" title="设置" width="650px">
    <el-tabs type="border-card">
      <!-- 基本设置 -->
      <el-tab-pane label="基本设置">
        <el-form label-position="top" size="large">
          <el-form-item label="语言">
            <el-select v-model="locale" style="width: 100%">
              <el-option label="简体中文" value="zh-CN" />
              <el-option label="English" value="en-US" />
            </el-select>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" size="large" @click="emit('openDebugPanel')">
              查看系统诊断信息
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <!-- AI 配置 -->
      <el-tab-pane label="AI 智能搜索">
        <el-form label-position="top" size="large">
          <!-- 启用开关 -->
          <el-form-item>
            <div class="ai-enable-row">
              <span class="ai-label">启用 AI 智能匹配</span>
              <el-switch 
                v-model="aiConfig.enabled" 
                :disabled="!isConfigValid()"
                active-text="开"
                inactive-text="关"
              />
            </div>
            <div class="ai-hint">
              启用后，搜索时 AI 会自动扩展关键词，找到更多相关结果
            </div>
          </el-form-item>
          
          <el-divider />
          
          <!-- 服务商选择 -->
          <el-form-item label="AI 服务商">
            <div class="provider-row">
              <el-select 
                v-model="selectedPreset" 
                @change="handlePresetChange"
                placeholder="选择服务商或自定义"
                style="width: 100%"
              >
                <el-option 
                  v-for="preset in allProviders" 
                  :key="preset.name" 
                  :label="preset.name" 
                  :value="preset.name"
                >
                  <span style="float: left">{{ preset.name }}</span>
                  <span v-if="preset.isCustom" style="float: right; color: #8492a6; font-size: 13px">自定义</span>
                </el-option>
              </el-select>
              
              <el-tooltip content="保存为自定义供应商" placement="top">
                <el-button :icon="Plus" @click="handleSavePreset" />
              </el-tooltip>
              
              <el-tooltip v-if="isCurrentPresetCustom" content="删除此供应商" placement="top">
                <el-button :icon="Delete" type="danger" plain @click="handleDeletePreset" />
              </el-tooltip>
            </div>
          </el-form-item>
          
          <!-- API Base URL -->
          <el-form-item label="API Base URL">
            <el-input 
              v-model="aiConfig.baseUrl" 
              placeholder="https://api.example.com/v1"
            />
          </el-form-item>
          
          <!-- API Key -->
          <el-form-item label="API Key">
            <el-input 
              v-model="aiConfig.apiKey" 
              :type="showApiKey ? 'text' : 'password'"
              placeholder="sk-..."
            >
              <template #suffix>
                <el-button 
                  text 
                  size="small" 
                  @click="showApiKey = !showApiKey"
                >
                  {{ showApiKey ? '隐藏' : '显示' }}
                </el-button>
              </template>
            </el-input>
          </el-form-item>
          
          <!-- 模型名称 -->
          <el-form-item label="模型名称">
            <el-input 
              v-model="aiConfig.model" 
              placeholder="gpt-3.5-turbo / deepseek-chat / glm-4-flash"
            />
          </el-form-item>
          
          <!-- 测试按钮 -->
          <el-form-item>
            <div class="test-row">
              <el-button 
                type="primary" 
                :loading="testing"
                :disabled="!isConfigValid()"
                @click="handleTest"
              >
                测试连接
              </el-button>
              
              <div v-if="testResult" class="test-result">
                <el-icon v-if="testResult.success" color="#67C23A"><CircleCheck /></el-icon>
                <el-icon v-else color="#F56C6C"><Warning /></el-icon>
                <span :class="testResult.success ? 'success' : 'error'">
                  {{ testResult.message }}
                </span>
              </div>
            </div>
          </el-form-item>
          
          <!-- 费用提示 -->
          <div class="cost-hint">
            <el-icon><Warning /></el-icon>
            <span>
              AI 智能匹配会消耗少量 API 配额，每次搜索约使用 100-200 token（约 ¥0.0001-0.001）
            </span>
          </div>
          
          <el-divider />
          
          <!-- AI 扩展提示词 -->
          <el-form-item>
            <template #label>
              <div class="prompt-label-row">
                <span>AI 扩展提示词</span>
                <el-button size="small" text type="primary" @click="resetPrompt">
                  恢复默认
                </el-button>
              </div>
            </template>
            <el-input
              v-model="aiConfig.expandPrompt"
              type="textarea"
              :rows="10"
              placeholder="输入 AI 扩展搜索词时使用的提示词..."
            />
            <div class="prompt-hint">
              <p>使用 <code v-pre>{{query}}</code> 作为搜索词占位符。AI 将根据此提示词生成扩展搜索词。</p>
            </div>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </el-dialog>
</template>

<style scoped>
.ai-enable-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.ai-label {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.ai-hint {
  font-size: 13px;
  color: #909399;
  margin-top: 8px;
}

.provider-row {
  display: flex;
  gap: 8px;
  width: 100%;
}

.test-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.test-result {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.test-result .success {
  color: #67C23A;
}

.test-result .error {
  color: #F56C6C;
}

.cost-hint {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 16px;
  background: #fdf6ec;
  border-radius: 8px;
  color: #E6A23C;
  font-size: 13px;
}

.cost-hint .el-icon {
  margin-top: 2px;
  flex-shrink: 0;
}

.prompt-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.prompt-hint {
  margin-top: 8px;
  font-size: 13px;
  color: #909399;
}

.prompt-hint code {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  color: #409EFF;
  font-family: monospace;
}
</style>
