import { ref, watch } from 'vue'

export interface SearchHistoryItem {
    query: string
    timestamp: number
    resultCount?: number
}

const STORAGE_KEY = 'file_searcher_search_history'
const MAX_HISTORY_ITEMS = 20

// 全局状态
const searchHistory = ref<SearchHistoryItem[]>([])

// 加载历史记录
const loadHistory = () => {
    try {
        const saved = localStorage.getItem(STORAGE_KEY)
        if (saved) {
            searchHistory.value = JSON.parse(saved)
        }
    } catch (error) {
        console.error('Failed to load search history:', error)
        searchHistory.value = []
    }
}

// 保存历史记录
const saveHistory = () => {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(searchHistory.value))
    } catch (error) {
        console.error('Failed to save search history:', error)
    }
}

// 初始化
loadHistory()

// 监听变化自动保存
watch(searchHistory, saveHistory, { deep: true })

export function useSearchHistory() {
    // 添加搜索记录
    const addToHistory = (query: string, resultCount?: number) => {
        if (!query.trim()) return

        // 移除重复项
        searchHistory.value = searchHistory.value.filter(
            item => item.query.toLowerCase() !== query.toLowerCase()
        )

        // 添加到开头
        searchHistory.value.unshift({
            query: query.trim(),
            timestamp: Date.now(),
            resultCount
        })

        // 限制数量
        if (searchHistory.value.length > MAX_HISTORY_ITEMS) {
            searchHistory.value = searchHistory.value.slice(0, MAX_HISTORY_ITEMS)
        }
    }

    // 移除单条记录
    const removeFromHistory = (query: string) => {
        searchHistory.value = searchHistory.value.filter(
            item => item.query !== query
        )
    }

    // 清空历史
    const clearHistory = () => {
        searchHistory.value = []
    }

    // 获取匹配的历史记录
    const getMatchingHistory = (query: string): SearchHistoryItem[] => {
        if (!query.trim()) return searchHistory.value.slice(0, 8)

        const lowerQuery = query.toLowerCase()
        return searchHistory.value
            .filter(item => item.query.toLowerCase().includes(lowerQuery))
            .slice(0, 8)
    }

    // 格式化时间
    const formatTime = (timestamp: number): string => {
        const now = Date.now()
        const diff = now - timestamp

        if (diff < 60000) return '刚刚'
        if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
        if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`

        return new Date(timestamp).toLocaleDateString('zh-CN')
    }

    return {
        searchHistory,
        addToHistory,
        removeFromHistory,
        clearHistory,
        getMatchingHistory,
        formatTime
    }
}
