# ClinFind v3.0 - 智能文件搜索工具

<p align="center">
  <img src="https://img.shields.io/badge/版本-3.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/平台-Windows-green" alt="Platform">
  <img src="https://img.shields.io/badge/许可证-MIT-orange" alt="License">
</p>

一个强大的本地文件全文搜索工具，支持 **AI 智能扩展搜索**，适用于 PDF、Word、Excel、PowerPoint 等多种文件格式。专为需要在海量文档中快速定位信息的专业人士设计。Clin代表临床，是本人从事的行业，所以是纯小白用AI搓出来自我方便用的工具。

---

## ✨ 核心特性

### 🔍 多模式搜索
| 模式 | 说明 |
|------|------|
| **精确匹配** | 严格匹配您输入的关键词 |
| **模糊匹配** | 智能匹配相近词汇 |
| **AI 智能搜索** | 🆕 自动扩展同义词、中英文对照词，大幅提升召回率 |

### 🤖 AI 智能搜索（v3.0 新增）
- **扩展词确认弹窗**：AI 生成扩展词后，用户可查看、编辑、添加或删除，确认后再执行搜索
- **自定义 Prompt**：在设置中可自由修改 AI 扩展提示词，适配不同专业领域
- **多 AI 服务商支持**：兼容 DeepSeek、OpenAI、智谱 GLM、阿里通义、心流 iflow 等

### 📄 文档格式支持
- PDF (`.pdf`)
- Word (`.docx`)
- Excel (`.xlsx`)
- PowerPoint (`.pptx`)
- 纯文本 (`.txt`, `.md`, `.csv`)

### ⚡ 其他亮点
- **快速索引**：基于 SQLite FTS5 全文搜索引擎
- **精确定位**：显示匹配内容的具体位置（页码、幻灯片、工作表）
- **分页加载**：搜索结果支持"加载更多"，不遗漏任何结果
- **拖拽添加**：直接拖拽文件夹到窗口即可添加搜索范围
- **现代界面**：Vue 3 + Element Plus，美观易用

---

## 🚀 快速开始

### 方式一：使用安装包（推荐）
1. 下载 `ClinFind Setup 3.0.0.exe`
2. 双击运行安装程序
3. 启动应用，开始使用

### 方式二：开发模式
```bash
# 1. 克隆仓库
git clone https://github.com/damonl525/ClinFind.git

# 2. 安装前端依赖
cd ClinFind/frontend
npm install

# 3. 启动开发服务器
npm run dev
```

---

## 📖 使用说明

### 基本搜索流程
1. **添加搜索范围**：点击「管理搜索范围」或直接拖拽文件夹
2. **等待索引完成**：系统自动扫描并索引文件内容
3. **输入关键词**：在搜索框输入，支持 `AND` / `OR` 逻辑操作符
4. **查看结果**：点击结果查看详情，双击打开原文件

### AI 智能搜索使用
1. 进入「设置」→「AI 智能搜索」
2. 选择 AI 服务商，填写 API Key
3. 点击「测试连接」确认配置成功
4. 启用 AI 智能匹配开关
5. 搜索时选择「AI 智能」模式
6. 在弹窗中确认或修改扩展词，点击「确认并搜索」

---

## 🛠️ 技术栈

### 后端
- **FastAPI** - 高性能 Python Web 框架
- **SQLite FTS5** - 全文搜索引擎
- **PyPDF2 / python-docx / openpyxl / python-pptx** - 文档解析

### 前端
- **Vue 3** + **TypeScript** - 现代前端框架
- **Element Plus** - UI 组件库
- **Electron** - 桌面应用框架
- **Vite** - 极速构建工具

---

## 📁 项目结构

```
ClinFind/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── core/              # 数据库模块
│   │   └── services/          # 业务逻辑（索引、搜索、AI客户端）
│   └── main.py                # FastAPI 入口
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/        # Vue 组件
│   │   │   ├── dialogs/       # 弹窗组件（设置、AI扩展确认等）
│   │   │   ├── search/        # 搜索相关组件
│   │   │   └── layout/        # 布局组件
│   │   ├── composables/       # 组合式函数（AI配置、搜索历史等）
│   │   ├── api.ts             # API 接口
│   │   └── App.vue            # 主界面
│   ├── electron/              # Electron 配置
│   └── dist_release/          # 打包输出
├── .gitignore
├── CHANGELOG.md               # 更新日志
└── README.md                  # 本文件
```

---

## 📝 更新日志

### v3.0.0 (2026-01-31)
- ✨ **AI 扩展词确认弹窗**：搜索前可查看和编辑 AI 生成的扩展词
- ✨ **自定义 AI Prompt**：在设置中可编辑扩展提示词
- ✨ **搜索结果分页**：支持"加载更多"，显示全部结果
- 🐛 修复了多个搜索相关的问题

### v2.x
- 基础全文搜索功能
- 多格式文档支持
- Electron 桌面应用

---

## 🐛 问题排查

| 问题 | 解决方案 |
|------|----------|
| 搜索无结果 | 确认已添加文件夹并完成索引 |
| AI 扩展无效 | 检查 API Key 配置，测试连接是否成功 |
| 后端无法启动 | 检查端口 8000 是否被占用 |
| 前端连接失败 | 确认后端已启动，访问 http://localhost:8000/health |

---

## 📄 许可证

[MIT License](LICENSE)

## 👨‍💻 作者

**Liangjianlin** (damonl525)

---

<p align="center">
  <b>享受高效搜索的乐趣！</b> 🎉
</p>
