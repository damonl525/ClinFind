<script setup lang="ts">
import type { DebugStats } from '@/types'

const visible = defineModel<boolean>({ required: true })

defineProps<{
  stats: DebugStats | null
}>()
</script>

<template>
  <el-dialog v-model="visible" title="系统诊断信息" width="800px">
    <div v-if="stats">
      <el-descriptions :column="2" border size="large">
        <el-descriptions-item label="数据库路径">{{ stats.database.path }}</el-descriptions-item>
        <el-descriptions-item label="数据库大小">{{ stats.database.size_mb }} MB</el-descriptions-item>
        <el-descriptions-item label="索引文件数">{{ stats.statistics.index_count }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="stats.status === 'ok' ? 'success' : 'danger'" size="large">
            {{ stats.status }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </el-dialog>
</template>
