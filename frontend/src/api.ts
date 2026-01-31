import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5分钟超时，支持大文件夹索引
});

export interface SearchResult {
  file_path: string;
  title: string;
  highlight: string;
  rank: number;
  match_type?: string;
  location_info?: string;
  source_query?: string;
  is_expanded?: boolean;
}

export interface SearchResponse {
  results: SearchResult[];
  total_count: number;
  has_more: boolean;
}

export interface IndexResponse {
  status: string;
  folder?: string;
  path?: string;
  indexed_count: number;
  total_count: number;
}

export interface AIConfig {
  base_url: string;
  api_key: string;
  model: string;
}

export interface AIExplainResponse {
  explanation: string;
}

export const searchFiles = async (
  query: string,
  limit: number = 50,
  precision: string = 'medium',
  paths?: string[],
  offset: number = 0
): Promise<SearchResponse> => {
  const response = await api.get<SearchResponse>('/search', {
    params: { q: query, limit, offset, precision, paths },
    paramsSerializer: {
      indexes: null // serialize arrays as paths=a&paths=b instead of paths[]=a
    }
  });
  return response.data;
};

export const indexFolder = async (folderPath: string): Promise<IndexResponse> => {
  const response = await api.post<IndexResponse>('/index/folder', {
    folder_path: folderPath,
  });
  return response.data;
};

export const indexPath = async (path: string): Promise<IndexResponse> => {
  const response = await api.post<IndexResponse>('/index/path', {
    path: path,
  });
  return response.data;
};

export const rebuildIndex = async (paths: string[]): Promise<any> => {
  const response = await api.post('/index/rebuild', {
    paths: paths,
  });
  return response.data;
};

// 查询索引状态
export interface IndexStatusResult {
  path: string;
  status: 'indexed' | 'not_indexed';
  indexed_count: number;
}

export const getIndexStatus = async (paths: string[]): Promise<IndexStatusResult[]> => {
  const response = await api.post<{ results: IndexStatusResult[] }>('/index/status', {
    paths: paths,
  });
  return response.data.results;
};

// 批量索引
export interface BatchIndexResponse {
  status: string;
  paths_processed: number;
  new_files_indexed: number;
  total_indexed: number;
}

export const batchIndex = async (paths: string[]): Promise<BatchIndexResponse> => {
  const response = await api.post<BatchIndexResponse>('/index/batch', {
    paths: paths,
  });
  return response.data;
};

// 删除索引数据
export interface DeleteIndexResponse {
  status: string;
  path: string;
  deleted_count: number;
}

export const deleteIndex = async (path: string): Promise<DeleteIndexResponse> => {
  const response = await api.post<DeleteIndexResponse>('/index/delete', {
    path: path,
  });
  return response.data;
};

export const explainCode = async (codeSnippet: string, context: string, config: AIConfig): Promise<AIExplainResponse> => {
  const response = await api.post<AIExplainResponse>('/ai/explain', {
    code_snippet: codeSnippet,
    context,
    config
  });
  return response.data;
};

export interface AIExpandResponse {
  original: string;
  expanded: string[];
}

export const expandQueryWithAI = async (query: string, config: AIConfig, prompt?: string): Promise<AIExpandResponse> => {
  const response = await api.post<AIExpandResponse>('/ai/expand', {
    query,
    config,
    prompt  // 可选的自定义 prompt
  });
  return response.data;
};

export const checkHealth = async (): Promise<any> => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Backend health check failed:', error);
    return null;
  }
};

export interface DebugStats {
  status: string;
  database: {
    path: string;
    size_mb: number;
    exists: boolean;
  };
  statistics: {
    file_count: number;
    index_count: number;
    file_types: Record<string, number>;
  };
  sample_paths: string[];
  error?: string;
}

export const getDebugStats = async (): Promise<DebugStats | null> => {
  try {
    const response = await api.get<DebugStats>('/debug/stats');
    return response.data;
  } catch (error) {
    console.error('Failed to get debug stats:', error);
    return null;
  }
};

export interface SearchSuggestion {
  text: string;
  type: 'filename' | 'content';
  source: string;
  preview?: string;
}

export const getSearchSuggestions = async (query: string): Promise<SearchSuggestion[]> => {
  try {
    if (!query || query.length < 2) return [];
    const response = await api.get<SearchSuggestion[]>('/search/suggestions', {
      params: { q: query }
    });
    return response.data;
  } catch (error) {
    console.error('Failed to get search suggestions:', error);
    return [];
  }
};

export interface RecentFile {
  file_path: string;
  title: string;
  last_modified: number;
  file_type: string;
}

export const getRecentFiles = async (limit: number = 10): Promise<RecentFile[]> => {
  try {
    const response = await api.get<RecentFile[]>('/files/recent', {
      params: { limit }
    });
    return response.data;
  } catch (error) {
    console.error('Failed to get recent files:', error);
    return [];
  }
};
