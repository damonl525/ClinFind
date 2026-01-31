// 搜索范围类型
export interface SearchScope {
    path: string
    type: 'folder' | 'file'
    active: boolean
    indexStatus?: 'indexed' | 'not_indexed' | 'indexing'  // 索引状态
    indexedCount?: number  // 已索引文件数
}

// 索引进度状态
export interface IndexingProgress {
    active: boolean
    currentFile: string
    totalFiles: number
    processedFiles: number
    folderPath: string
}

// 从 api.ts 重新导出类型
export type { SearchResult, DebugStats } from '@/api'
export type { IndexResponse as IndexResult } from '@/api'
