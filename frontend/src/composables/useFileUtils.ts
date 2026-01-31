/**
 * 文件工具函数 composable
 * 提供文件名、路径、类型相关的工具函数
 */

// 获取文件扩展名
export const getFileExtension = (filePath: string): string => {
    const ext = filePath.split('.').pop()?.toLowerCase() || ''
    return ext
}

// 获取文件名
export const getFileName = (filePath: string): string => {
    return filePath.split('\\').pop() || filePath
}

// 获取文件类型标签颜色
export const getFileTypeColor = (filePath: string): string => {
    const ext = getFileExtension(filePath)
    const colorMap: Record<string, string> = {
        'pdf': '#E74C3C',
        'docx': '#3498DB',
        'doc': '#3498DB',
        'xlsx': '#27AE60',
        'xls': '#27AE60',
        'pptx': '#E67E22',
        'ppt': '#E67E22',
        'txt': '#95A5A6',
    }
    return colorMap[ext] || '#909399'
}

// 获取文件类型名称
export const getFileTypeName = (filePath: string): string => {
    const ext = getFileExtension(filePath)
    const nameMap: Record<string, string> = {
        'pdf': 'PDF',
        'docx': 'Word',
        'doc': 'Word',
        'xlsx': 'Excel',
        'xls': 'Excel',
        'pptx': 'PPT',
        'ppt': 'PPT',
        'txt': 'TXT',
    }
    return nameMap[ext] || ext.toUpperCase()
}

// 提取高亮文本中的位置信息
export const extractLocation = (highlight: string): string | null => {
    const metaPattern = /<span class="meta">\[(.*?)\]<\/span>/
    const match = highlight.match(metaPattern)
    return match ? match[1] : null
}

// 清理高亮文本中的元数据标签
export const cleanHighlight = (highlight: string): string => {
    return highlight.replace(/<span class="meta">\[.*?\]<\/span>/g, '')
}

// 格式化位置信息
export const formatLocation = (location: string | null): string => {
    if (!location) return ''

    const parts = location.split(':')
    if (parts.length < 2) return location

    const type = parts[0]
    const value = parts.slice(1).join(':')

    const typeMap: Record<string, string> = {
        'Page': '页码',
        'Sheet': '工作表',
        'Row': '行',
        'Col': '列',
        'Slide': '幻灯片',
        'Para': '段落',
        'Table': '表格'
    }

    return `${typeMap[type] || type}: ${value}`
}

// 复合 composable 导出
export function useFileUtils() {
    return {
        getFileExtension,
        getFileName,
        getFileTypeColor,
        getFileTypeName,
        extractLocation,
        cleanHighlight,
        formatLocation
    }
}
