import axios from 'axios';

// Get backend port from Electron context bridge, or default to 8000
const port = window.electronAPI ? window.electronAPI.getBackendPort() : 8000;
const baseURL = `http://localhost:${port}`;

const api = axios.create({
    baseURL: baseURL,
    timeout: 10000,
});

export const searchFiles = async (query) => {
    try {
        const response = await api.get('/search', {
            params: { q: query }
        });
        return response.data;
    } catch (error) {
        console.error('Search failed:', error);
        return [];
    }
};

export const indexFolder = async (folderPath) => {
    try {
        const response = await api.post('/index/folder', {
            folder_path: folderPath
        });
        return response.data;
    } catch (error) {
        console.error('Indexing failed:', error);
        throw error;
    }
};

export const checkHealth = async () => {
    try {
        const response = await api.get('/health');
        return response.data;
    } catch (error) {
        console.error('Health check failed:', error);
        return { status: 'error' };
    }
};
