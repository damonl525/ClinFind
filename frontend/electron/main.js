const { app, BrowserWindow, Menu, shell, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');

let mainWindow;
let backendProcess;
const BACKEND_PORT = 8000;

// 版本更新历史
const VERSION_HISTORY = `
## v3.0.0 (2026-01-31)
🚀 全新架构重构
  • 前端：Vue 3 + Element Plus 现代化界面
  • 后端：Python FastAPI 高性能服务
  • 架构：前后端分离，Electron 桌面应用
✨ 新增功能
  • AI 智能搜索：集成多种 AI 服务商
  • 智能关键词扩展：AI 自动分析并扩展同义词
  • 搜索范围管理：支持多文件夹索引与增量更新
  • 逻辑搜索：支持 AND/OR 组合搜索

## v2.1 (2025-01-17)
  • 搜索精度大幅提升
  • 智能意外匹配检测

## v2.0 (2025-01-15)
  • Excel/Word/PDF/TXT 内容搜索
  • 重复文件检测
  • 现代化 GUI 界面

## v1.0 (2024-11)
  • 首次发布
`;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  const isDev = !app.isPackaged;

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    // 开发模式下不自动打开开发者工具，保持界面干净
    // 按 F12 仍可手动打开
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
    // Assuming running from frontend/ directory
    scriptPath = path.join(__dirname, '../../backend/main.py');
    cmd = 'python';
    args = [scriptPath, BACKEND_PORT.toString()];
    console.log('Starting backend (Dev):', cmd, args);
  } else {
    // Production: Run exe
    // backend.exe should be in resources/backend/backend.exe
    // or just resources/backend.exe depending on packaging
    const backendPath = path.join(process.resourcesPath, 'backend/main.exe');
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
    backendProcess.kill();
    backendProcess = null;
  }
}

app.whenReady().then(() => {
  // 先设置菜单，再创建窗口
  const menuTemplate = [
    {
      label: '帮助',
      submenu: [
        {
          label: '使用指南',
          click: () => {
            const isDev = !app.isPackaged;
            let readmePath;
            if (isDev) {
              readmePath = path.join(__dirname, '../../README.md');
            } else {
              readmePath = path.join(process.resourcesPath, 'README.md');
            }
            if (fs.existsSync(readmePath)) {
              shell.openPath(readmePath);
            } else {
              dialog.showMessageBox(mainWindow, {
                type: 'info',
                title: '使用指南',
                message: '请参阅项目目录下的 README.md 文件'
              });
            }
          }
        },
        { type: 'separator' },
        {
          label: '版本历史',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: '版本历史',
              message: 'ClinFind - 文件内容搜索工具',
              detail: VERSION_HISTORY
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);

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
