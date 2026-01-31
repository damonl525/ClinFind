const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');

let mainWindow;
let backendProcess;
const BACKEND_PORT = 8000;

function setupIPC() {
  ipcMain.handle('select-directory', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openDirectory']
    });
    if (result.canceled) {
      return null;
    }
    return result.filePaths[0];
  });

  ipcMain.handle('select-file', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openFile'],
      filters: [
        { name: 'Excel Files', extensions: ['xlsx', 'xls', 'xlsm'] },
        { name: 'All Files', extensions: ['*'] }
      ]
    });
    if (result.canceled) {
      return null;
    }
    return result.filePaths[0];
  });

  ipcMain.handle('open-file', async (event, filePath) => {
    await shell.openPath(filePath);
  });
  
  ipcMain.handle('open-external', async (event, url) => {
    await shell.openExternal(url);
  });

  ipcMain.handle('restart-backend', async () => {
    console.log('[IPC] Restarting backend requested...');
    stopBackend();
    // Wait a bit for process to exit and ports to clear
    setTimeout(() => {
      startBackend();
    }, 2000);
    return true;
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false, // 开发模式下禁用web安全策略
    },
  });

  const isDev = !app.isPackaged;
  
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
    
    // 设置CSP以允许localhost连接
    mainWindow.webContents.session.webRequest.onHeadersReceived((details, callback) => {
      callback({
        responseHeaders: {
          ...details.responseHeaders,
          'Content-Security-Policy': ["default-src 'self' 'unsafe-inline' 'unsafe-eval' http://localhost:* ws://localhost:* data: blob:"]
        }
      })
    })
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }
}

function startBackend() {
  const isDev = !app.isPackaged;
  let scriptPath;
  let cmd;
  let args;

  if (isDev) {
    // Development: Run python script
    // Assuming running from frontend/ directory, so backend is at ../backend
    scriptPath = path.join(__dirname, '../../backend/main.py');
    cmd = 'python';
    args = [scriptPath, BACKEND_PORT.toString()];
    console.log('Starting backend (Dev):', cmd, args);
  } else {
    // Production: Run exe
    // In production, resources path contains extraResources
    const backendPath = path.join(process.resourcesPath, 'backend/backend.exe');
    cmd = backendPath;
    args = [BACKEND_PORT.toString()];
    console.log('Starting backend (Prod):', cmd);
  }

  backendProcess = spawn(cmd, args);

  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend stdout: ${data}`);
  });

  backendProcess.stderr.on('data', (data) => {
    console.error(`Backend stderr: ${data}`);
  });

  backendProcess.on('close', (code) => {
    console.log(`Backend exited with code ${code}`);
  });
}

function stopBackend() {
  if (backendProcess) {
    console.log(`[Backend] Stopping process ${backendProcess.pid}...`);
    try {
      if (process.platform === 'win32') {
        exec(`taskkill /pid ${backendProcess.pid} /T /F`, (err, stdout, stderr) => {
           if (err) console.error('[Backend] Taskkill failed:', err);
           else console.log('[Backend] Taskkill success:', stdout);
        });
      } else {
        backendProcess.kill();
      }
    } catch (e) {
      console.error('[Backend] Error stopping process:', e);
    }
    backendProcess = null;
  }
}

app.whenReady().then(() => {
  setupIPC();
  startBackend();
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    stopBackend();
    app.quit();
  }
});

app.on('before-quit', () => {
  stopBackend();
});
