/**
 * Electron API composable
 * 封装与 Electron 主进程的交互
 */
import { ElMessage } from 'element-plus'

export function useElectron() {
    const isElectron = (): boolean => {
        return !!window.electronAPI
    }

    // 打开文件
    const openFile = async (filePath: string): Promise<void> => {
        if (window.electronAPI) {
            await window.electronAPI.openFile(filePath)
        } else {
            ElMessage.warning('浏览器模式下无法打开文件')
        }
    }

    // 打开文件所在文件夹
    const openFolder = async (filePath: string): Promise<void> => {
        if (window.electronAPI) {
            const folderPath = filePath.substring(0, filePath.lastIndexOf('\\'))
            await window.electronAPI.openFile(folderPath)
        } else {
            ElMessage.warning('浏览器模式下无法打开文件夹')
        }
    }

    // 选择目录
    const selectDirectory = async (): Promise<string | null> => {
        if (window.electronAPI) {
            return await window.electronAPI.selectDirectory()
        }
        ElMessage.warning('浏览器模式下无法选择目录')
        return null
    }

    // 选择文件
    const selectFile = async (): Promise<string | null> => {
        if (window.electronAPI) {
            return await window.electronAPI.selectFile()
        }
        ElMessage.warning('浏览器模式下无法选择文件')
        return null
    }

    // 复制到剪贴板
    const copyToClipboard = async (text: string): Promise<boolean> => {
        try {
            await navigator.clipboard.writeText(text)
            ElMessage.success('路径已复制')
            return true
        } catch {
            ElMessage.error('复制失败')
            return false
        }
    }

    return {
        isElectron,
        openFile,
        openFolder,
        selectDirectory,
        selectFile,
        copyToClipboard
    }
}
