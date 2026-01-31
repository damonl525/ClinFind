import { ref, watch, computed } from 'vue'

export interface AIConfig {
    baseUrl: string
    apiKey: string
    model: string
    enabled: boolean
    currentProvider: string  // 当前选择的供应商名称
    expandPrompt: string     // AI 扩展搜索词的提示词
}

const CUSTOM_PROVIDERS_KEY = 'file_searcher_custom_providers'
const PROVIDER_CONFIGS_KEY = 'file_searcher_provider_configs'

export interface AIProvider {
    name: string
    baseUrl: string
    model: string
    placeholder?: string
    isCustom?: boolean
}

// 每个供应商的独立配置
export interface ProviderConfig {
    apiKey: string
    model: string
    baseUrl?: string  // 自定义供应商可能修改 baseUrl
}

// 预设的 AI 服务商配置
const BUILTIN_PRESETS: AIProvider[] = [
    {
        name: 'DeepSeek',
        baseUrl: 'https://api.deepseek.com/v1',
        model: 'deepseek-chat',
        placeholder: 'sk-...'
    },
    {
        name: 'OpenAI',
        baseUrl: 'https://api.openai.com/v1',
        model: 'gpt-3.5-turbo',
        placeholder: 'sk-...'
    },
    {
        name: '智谱 GLM',
        baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
        model: 'glm-4-flash',
        placeholder: '...'
    },
    {
        name: '阿里通义',
        baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        model: 'qwen-turbo',
        placeholder: 'sk-...'
    },
    {
        name: '心流 (iflow)',
        baseUrl: 'https://apis.iflow.cn/v1',
        model: '',
        placeholder: '...'
    }
]

const STORAGE_KEY = 'file_searcher_ai_config'

// 默认的 AI 扩展提示词
export const DEFAULT_EXPAND_PROMPT = `你是一个专业的文档搜索助手。请为以下搜索关键词生成 3-5 个最相关的扩展词，帮助用户找到更多相关文档。

搜索词：{{query}}

扩展规则：
1. 优先生成该词在**专业领域**中的同义词（如医学、统计、法律、金融等）
2. 包含该词的**中英文对应词**
3. 包含该词的**常见缩写或全称**
4. 不要生成过于宽泛或偏离原意的词
5. 不要包含原始搜索词本身

示例：
- "样本" → ["sample", "样本量", "sample size", "受试者", "n值"]
- "随机" → ["randomization", "随机化", "random", "随机分配", "RCT"]
- "盲法" → ["blinding", "双盲", "单盲", "double-blind", "设盲"]

请只返回 JSON 数组格式，如 ["词1", "词2", "词3"]，不要其他解释。`

// 默认配置
const defaultConfig: AIConfig = {
    baseUrl: '',
    apiKey: '',
    model: '',
    enabled: false,
    currentProvider: '',
    expandPrompt: DEFAULT_EXPAND_PROMPT
}

// 全局状态
const aiConfig = ref<AIConfig>(loadConfig())
const customProviders = ref<AIProvider[]>(loadCustomProviders())
const providerConfigs = ref<Record<string, ProviderConfig>>(loadProviderConfigs())

// 所有可用供应商 (预设 + 自定义)
const allProviders = computed(() => {
    return [...BUILTIN_PRESETS, ...customProviders.value, {
        name: '自定义',
        baseUrl: '',
        model: '',
        placeholder: ''
    }]
})

function loadConfig(): AIConfig {
    try {
        const saved = localStorage.getItem(STORAGE_KEY)
        if (saved) {
            return { ...defaultConfig, ...JSON.parse(saved) }
        }
    } catch (error) {
        console.error('Failed to load AI config:', error)
    }
    return { ...defaultConfig }
}

function loadCustomProviders(): AIProvider[] {
    try {
        const saved = localStorage.getItem(CUSTOM_PROVIDERS_KEY)
        if (saved) {
            return JSON.parse(saved)
        }
    } catch (error) {
        console.error('Failed to load custom providers:', error)
    }
    return []
}

function loadProviderConfigs(): Record<string, ProviderConfig> {
    try {
        const saved = localStorage.getItem(PROVIDER_CONFIGS_KEY)
        if (saved) {
            return JSON.parse(saved)
        }
    } catch (error) {
        console.error('Failed to load provider configs:', error)
    }
    return {}
}

function saveConfig() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(aiConfig.value))
    } catch (error) {
        console.error('Failed to save AI config:', error)
    }
}

function saveCustomProviders() {
    try {
        localStorage.setItem(CUSTOM_PROVIDERS_KEY, JSON.stringify(customProviders.value))
    } catch (error) {
        console.error('Failed to save custom providers:', error)
    }
}

function saveProviderConfigs() {
    try {
        localStorage.setItem(PROVIDER_CONFIGS_KEY, JSON.stringify(providerConfigs.value))
    } catch (error) {
        console.error('Failed to save provider configs:', error)
    }
}

// 保存当前供应商的配置
function saveCurrentProviderConfig() {
    const currentProvider = aiConfig.value.currentProvider
    if (currentProvider) {
        providerConfigs.value[currentProvider] = {
            apiKey: aiConfig.value.apiKey,
            model: aiConfig.value.model,
            baseUrl: aiConfig.value.baseUrl
        }
        saveProviderConfigs()
    }
}

// 监听变化自动保存
watch(aiConfig, saveConfig, { deep: true })
watch(customProviders, saveCustomProviders, { deep: true })

// 当 apiKey 或 model 变化时，保存到当前供应商的配置中
watch(() => [aiConfig.value.apiKey, aiConfig.value.model, aiConfig.value.baseUrl], () => {
    saveCurrentProviderConfig()
})

export function useAIConfig() {
    // 更新配置
    const updateConfig = (config: Partial<AIConfig>) => {
        aiConfig.value = { ...aiConfig.value, ...config }
    }

    // 应用预设（切换供应商时调用）
    const applyPreset = (presetName: string) => {
        // 先保存当前供应商的配置
        saveCurrentProviderConfig()

        const preset = allProviders.value.find(p => p.name === presetName)
        if (preset) {
            // 获取该供应商保存的配置
            const savedConfig = providerConfigs.value[presetName]

            // 应用供应商的 baseUrl
            aiConfig.value.baseUrl = savedConfig?.baseUrl || preset.baseUrl

            // 恢复该供应商保存的 apiKey 和 model，如果没有则使用预设的 model
            aiConfig.value.apiKey = savedConfig?.apiKey || ''
            aiConfig.value.model = savedConfig?.model || preset.model

            // 更新当前供应商
            aiConfig.value.currentProvider = presetName
        }
    }

    // 保存当前配置为新预设
    const saveAsPreset = (name: string) => {
        if (!name.trim()) return

        // 保存当前的 apiKey 和 model 到供应商配置
        providerConfigs.value[name] = {
            apiKey: aiConfig.value.apiKey,
            model: aiConfig.value.model,
            baseUrl: aiConfig.value.baseUrl
        }
        saveProviderConfigs()

        // 如果已存在同名自定义预设，则更新
        const existingIndex = customProviders.value.findIndex(p => p.name === name)
        if (existingIndex >= 0) {
            customProviders.value[existingIndex] = {
                name,
                baseUrl: aiConfig.value.baseUrl,
                model: aiConfig.value.model,
                isCustom: true
            }
        } else {
            customProviders.value.push({
                name,
                baseUrl: aiConfig.value.baseUrl,
                model: aiConfig.value.model,
                isCustom: true
            })
        }

        // 更新当前供应商
        aiConfig.value.currentProvider = name
    }

    // 删除自定义预设
    const deletePreset = (name: string) => {
        customProviders.value = customProviders.value.filter(p => p.name !== name)

        // 同时删除该供应商的配置
        if (providerConfigs.value[name]) {
            delete providerConfigs.value[name]
            saveProviderConfigs()
        }
    }

    // 检查配置是否有效
    const isConfigValid = (): boolean => {
        return !!(aiConfig.value.baseUrl && aiConfig.value.apiKey && aiConfig.value.model)
    }

    // 测试连接
    const testConnection = async (): Promise<{ success: boolean; message: string }> => {
        if (!isConfigValid()) {
            return { success: false, message: '请先完成 API 配置' }
        }

        try {
            const response = await fetch('http://localhost:8000/ai/test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    base_url: aiConfig.value.baseUrl,
                    api_key: aiConfig.value.apiKey,
                    model: aiConfig.value.model
                })
            })

            const data = await response.json()
            return data
        } catch (error) {
            return { success: false, message: '连接失败: ' + error }
        }
    }

    // 重置提示词为默认值
    const resetPrompt = () => {
        aiConfig.value.expandPrompt = DEFAULT_EXPAND_PROMPT
        saveConfig()
    }

    return {
        aiConfig,
        allProviders,
        updateConfig,
        applyPreset,
        saveAsPreset,
        deletePreset,
        isConfigValid,
        testConnection,
        resetPrompt,
        DEFAULT_EXPAND_PROMPT
    }
}
