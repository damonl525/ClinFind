<script setup lang="ts">
import { ref } from 'vue'
import { Search, Setting, Folder, RefreshRight, QuestionFilled, Document, InfoFilled } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

defineProps<{
  backendConnected: boolean
}>()

const emit = defineEmits<{
  openScopeManager: []
  checkBackend: []
  openSettings: []
}>()

// 版本历史
const VERSION_HISTORY = `
v3.0.0 (2026-01-31)
━━━━━━━━━━━━━━━━━━━━
🚀 全新架构重构
  • 前端：Vue 3 + Element Plus 现代化界面
  • 后端：Python FastAPI 高性能服务
  • 架构：前后端分离，Electron 桌面应用
✨ 新增功能
  • 🧠 AI 智能搜索：集成多种 AI 服务商（DeepSeek、OpenAI、智谱GLM、阿里通义等）
  • 🔍 智能关键词扩展：AI 自动分析并扩展同义词和相关词
  • 📂 搜索范围管理：支持多文件夹索引与增量更新
  • 🔄 实时索引状态：可视化显示索引进度与文件数量
  • 💡 逻辑搜索：支持 AND/OR 组合搜索
  • ⚙️ 供应商配置独立保存：每个 AI 供应商的 API Key 和模型独立保存
🎨 界面优化
  • 现代化卡片式搜索结果展示
  • 文件类型图标与颜色区分
  • 深色/浅色主题支持
  • 响应式布局适配

v2.1 (2025-01-17)
━━━━━━━━━━━━━━━━━━━━
🎯 搜索精度大幅提升
  • 解决拼音缩写误匹配问题
  • 分层评分系统：精确匹配 > 部分匹配 > 语义匹配
✨ 智能意外匹配检测
  • 自动识别并降低拼音/英文缩写的意外高分匹配
  • 优先考虑词首匹配和完整词边界匹配

v2.0 (2025-01-15)
━━━━━━━━━━━━━━━━━━━━
✨ 新增功能
  • 文件名搜索（支持模糊匹配）
  • Excel/Word/PDF/TXT 内容搜索
  • 重复文件检测
  • 搜索精度控制
  • 现代化 GUI 界面
🔧 技术优化
  • 无 pandas 依赖，启动更快

v1.1 (2024-12)
━━━━━━━━━━━━━━━━━━━━
🐛 修复文件搜索稳定性问题
🚀 优化 GUI 响应速度

v1.0 (2024-11)
━━━━━━━━━━━━━━━━━━━━
🎉 首次发布
  • 基础文件搜索功能
  • 简单 GUI 界面
  • 支持基本文档格式
`

// 帮助下拉菜单状态
const showHelpMenu = ref(false)

// 显示版本历史
const showVersionHistory = () => {
  showHelpMenu.value = false
  ElMessageBox.alert(VERSION_HISTORY, '版本历史', {
    confirmButtonText: '知道了',
    customClass: 'version-dialog'
  })
}

// 打开使用指南
const openUserGuide = () => {
  showHelpMenu.value = false
  // 显示内置指南
  ElMessageBox.alert(`
<h3>🔍 基本搜索</h3>
<p>在搜索框输入关键词，按回车搜索</p>

<h3>📂 搜索范围</h3>
<p>点击【管理搜索范围】添加文件夹，系统会自动建立索引</p>

<h3>🧠 AI 智能搜索</h3>
<p>切换到【AI 智能】模式，系统会自动扩展同义词</p>

<h3>💡 逻辑搜索</h3>
<p>• <code>词1 AND 词2</code> - 同时包含两个词</p>
<p>• <code>词1 OR 词2</code> - 包含任意一个词</p>

<h3>⚙️ AI 配置</h3>
<p>点击右上角【设置】配置 API 地址和密钥</p>
  `, '使用指南', {
    confirmButtonText: '知道了',
    dangerouslyUseHTMLString: true,
    customClass: 'guide-dialog'
  })
}
</script>

<template>
  <div class="top-bar">
    <div class="top-bar-left">
      <el-icon :size="28" color="#409EFF"><Search /></el-icon>
      <span class="app-title">ClinFind</span>
      <el-tag :type="backendConnected ? 'success' : 'danger'" size="small" class="status-tag">
        {{ backendConnected ? '已连接' : '未连接' }}
      </el-tag>
    </div>
    
    <div class="top-bar-right">
      <el-button :icon="Folder" @click="emit('openScopeManager')" size="large">
        管理搜索范围
      </el-button>
      <el-button :icon="RefreshRight" circle @click="emit('checkBackend')" size="large" />
      <el-button :icon="Setting" circle @click="emit('openSettings')" size="large" />
      
      <!-- 帮助下拉菜单 -->
      <el-dropdown trigger="click" @command="(cmd: string) => cmd === 'guide' ? openUserGuide() : showVersionHistory()">
        <el-button :icon="QuestionFilled" circle size="large" />
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="guide">
              <el-icon><Document /></el-icon>
              使用指南
            </el-dropdown-item>
            <el-dropdown-item command="version" divided>
              <el-icon><InfoFilled /></el-icon>
              版本历史
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<style scoped>
.top-bar {
  height: 70px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  z-index: 100;
}

.top-bar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.app-title {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  letter-spacing: 0.5px;
}

.status-tag {
  font-size: 13px;
}

.top-bar-right {
  display: flex;
  gap: 12px;
  align-items: center;
}
</style>

<style>
/* 全局样式 - 版本对话框 */
.version-dialog .el-message-box__message {
  white-space: pre-line;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.8;
}

/* 全局样式 - 指南对话框 */
.guide-dialog .el-message-box__message {
  font-size: 14px;
  line-height: 1.6;
}

.guide-dialog .el-message-box__message h3 {
  margin: 16px 0 8px 0;
  color: #409EFF;
  font-size: 15px;
}

.guide-dialog .el-message-box__message h3:first-child {
  margin-top: 0;
}

.guide-dialog .el-message-box__message p {
  margin: 4px 0;
  color: #606266;
}

.guide-dialog .el-message-box__message code {
  background: #f4f4f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', monospace;
  color: #e6a23c;
}
</style>
