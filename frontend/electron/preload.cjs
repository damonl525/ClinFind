const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  getBackendPort: () => 8000,
  openFile: (path) => ipcRenderer.invoke('open-file', path),
  selectDirectory: () => ipcRenderer.invoke('select-directory'),
  selectFile: () => ipcRenderer.invoke('select-file'),
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  restartBackend: () => ipcRenderer.invoke('restart-backend')
});
