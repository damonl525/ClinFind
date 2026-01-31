# FileSearcher V3 - 文件搜索神器

一个强大的本地文件全文搜索工具，支持 PDF、Word、Excel、PowerPoint 等多种文件格式。

## ✨ 主要特性

- 🔍 **全文搜索**: 支持文件内容全文检索
- 📄 **多格式支持**: PDF、DOCX、XLSX、PPTX、TXT 等
- 🎯 **精确定位**: 显示匹配内容的具体位置（页码、幻灯片、工作表等）
- ⚡ **快速索引**: 使用 SQLite FTS5 全文搜索引擎
- 🎨 **现代界面**: 基于 Vue 3 + Element Plus 的美观界面
- 🖥️ **桌面应用**: Electron 打包，跨平台支持

## 🚀 快速开始

### 方式1: 一键启动（推荐）

双击运行 `start_dev.bat`，会自动启动后端和前端服务。

### 方式2: 分步启动

1. **启动后端**
   ```bash
   cd backend
   python main.py
   ```

2. **启动前端**（新开终端）
   ```bash
   cd frontend
   npm run dev
   ```

3. **启动 Electron**（新开终端）
   ```bash
   cd frontend
   npm run electron:dev
   ```

## 📖 使用说明

1. **添加文件夹**: 点击"管理搜索范围"按钮，添加要搜索的文件夹
2. **等待索引**: 系统会自动索引文件夹中的所有支持格式的文件
3. **开始搜索**: 在搜索框输入关键词，按回车搜索
4. **查看结果**: 点击结果可以查看详情，双击打开文件

## 🛠️ 技术栈

### 后端
- **FastAPI**: 现代化的 Python Web 框架
- **SQLite FTS5**: 全文搜索引擎
- **PyPDF2**: PDF 解析
- **python-docx**: Word 文档解析
- **openpyxl**: Excel 文档解析
- **python-pptx**: PowerPoint 解析

### 前端
- **Vue 3**: 渐进式 JavaScript 框架
- **Element Plus**: Vue 3 组件库
- **Electron**: 跨平台桌面应用框架
- **TypeScript**: 类型安全的 JavaScript

## 📁 项目结构

```
FileSearcherV3/
├── backend/              # 后端服务
│   ├── app/
│   │   ├── core/        # 核心模块（数据库）
│   │   └── services/    # 业务逻辑（索引、搜索、解析）
│   └── main.py          # 后端入口
├── frontend/            # 前端应用
│   ├── src/
│   │   ├── App.vue      # 主界面
│   │   └── api.ts       # API 接口
│   └── electron/        # Electron 配置
├── start_dev.bat        # 一键启动脚本
└── README.md            # 本文件
```

## 🔧 开发工具

### 测试索引功能
```bash
python test_indexer_direct.py
```

### 测试搜索功能
```bash
python test_search.py
```

### 清理临时文件
```bash
cleanup_project.bat
```

## 📝 更多文档

- [快速开始指南](QUICK_START.md)
- [启动说明](HOW_TO_START.md)
- [部署指南](DEPLOYMENT_GUIDE.md)
- [版本说明](RELEASE_NOTES_V3.1.md)

## 🐛 问题排查

### 搜索无结果
1. 确认已添加文件夹并完成索引
2. 检查数据库是否有数据：运行 `test_indexer_direct.py`
3. 查看后端日志是否有错误

### 后端无法启动
1. 确认 Python 环境已安装所有依赖
2. 检查端口 8000 是否被占用
3. 查看终端错误信息

### 前端无法连接后端
1. 确认后端已启动（访问 http://localhost:8000/health）
2. 检查防火墙设置
3. 确认端口配置正确

## 📄 许可证

MIT License

## 👨‍💻 作者

Liangjianlin

---

**享受搜索的乐趣！** 🎉
