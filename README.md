# OpenToad 🐸

<p align="center">
  <strong>Self-Sustainable AI Assistant</strong><br />
  从零构建的 AI Agent 框架 | 多模型支持 | 记忆体系统 | 可扩展盈利
</p>

<p align="center">
  <a href="https://opentoad.cn" target="_blank">
    <img src="https://img.shields.io/website?url=https%3A%2F%2Fopentoad.cn&label=官网" alt="官网" />
  </a>
</p>

<p align="center">
  <a href="#">
    <img src="https://img.shields.io/github/stars/opentoad/opentoad?style=flat" alt="stars" />
  </a>
  <a href="#">
    <img src="https://img.shields.io/github/forks/opentoad/opentoad?style=flat" alt="forks" />
  </a>
  <a href="#">
    <img src="https://img.shields.io/github/license/opentoad/opentoad?style=flat" alt="license" />
  </a>
  <a href="#">
    <img src="https://img.shields.io/github/v/release/opentoad/opentoad?style=flat" alt="version" />
  </a>
</p>

---

## ⭐ 简介

OpenToad 是从零构建的 **AI Agent 框架**，完全自主可控，不依赖任何现有框架。

OpenToad 不只是一个 AI 助手，而是**主人的记忆体分身**——从诞生的那一刻起，它会记住与主人的每一次交互，逐渐形成独特的性格和理解。

**核心理念**: 最真实的人格 = 常年累月积累的记忆体

## ✨ 特性

### 核心能力

- **记忆体系统** - 独特的长期记忆/短期记忆架构
  - 身份记忆：记住自己是谁、服务于谁
  - 偏好记忆：学习主人的代码风格、沟通习惯
  - 知识记忆：积累主人告诉的事实和知识
  - 项目记忆：跟踪项目进度和上下文
  - 封装记忆体：项目/对话完成后可打包存档，按需调用
- **渐进式自我认知** - 身份由被赋予到自我探索逐渐形成
- **智能遗忘机制** - 主人标记 + AI评估 + 使用频率，三重升级策略

### 对话与推理

- **CLI 对话** - 终端直接交互，支持流式响应
- **桌面应用** - 跨平台 GUI 界面，支持 Windows、macOS、Linux
- **ReAct 推理循环** - 思维链可视化，Tool 调用编排
- **Tool 系统** - Shell 执行、文件操作、网页搜索、计算器
- **流式支持** - 实时响应，提升用户体验

### 多模型支持

| 类型 | 模型 |
|------|------|
| 海外 | Claude, GPT, Gemini |
| 国内 | 文心一言, 通义千问, 混元, ChatGLM, Kimi, DeepSeek |
| 自部署 | Ollama, LocalAI, LM Studio, vLLM |

### 可扩展盈利

- 实例通讯：客户端自动注册、云端任务分发
- Token 经济：实例在线、任务执行赚取 Token
- 广告联盟、订阅系统、API 变现

## 🚀 快速开始

### 环境要求

- Python 3.9+ (已完全兼容)
- pip 20.0+

### 安装

```bash
# 克隆仓库
git clone https://github.com/opentoad/opentoad.git
cd opentoad

# 安装核心依赖
pip install -e .

# 安装桌面应用依赖
pip install -e apps/desktop
```

### 配置

```bash
# 复制环境配置
cp .env.example .env

# 编辑配置文件
# PROVIDER=anthropic
# API_KEY=your-key-here
# MODEL=claude-3-5-sonnet-20241022
```

### 运行

#### macOS / Linux
```bash
# 首次运行，初始化身份和记忆
python -m src.memory.cli init

# 启动 CLI (推荐，支持配置保存)
./opentoad.sh

# 启动 CLI (原始方式)
./bin/opentoad

# 启动桌面应用
python3 apps/desktop/src/main.py
```

#### Windows
```batch
# 首次运行，初始化身份和记忆
python -m src.memory.cli init

# 启动 CLI (推荐，支持配置保存)
opentoad.bat

# 启动桌面应用
python apps/desktop/src/main.py
```

### 配置保存功能

OpenToad 支持配置保存功能，首次运行时会提示您选择提供商、模型并输入 API key。

## 📖 文档

- [官网](https://opentoad.cn)
- [安装指南](docs/getting-started/installation.md)
- [配置说明](docs/configuration/README.md)
- [模型接入](docs/providers/README.md)
- [Tool 开发](docs/tools/README.md)
- [记忆体系统设计](docs/plans/2026-03-20-memory-system-design.md)
- [桌面应用](docs/desktop/README.md)

## 🏗️ 项目结构

```
opentoad/
├── src/                # 核心代码
│   ├── agent/         # Agent 推理核心 (ReAct 循环)
│   ├── memory/        # 记忆体系统 ⭐
│   │   ├── core.py       # MemoryCore 核心类
│   │   ├── storage.py    # SQLite 存储层
│   │   ├── types.py      # 数据模型
│   │   └── cli.py        # CLI 命令
│   ├── tools/         # Tool 系统
│   │   └── impl/         # 内置 Tools
│   ├── providers/     # LLM Provider
│   │   ├── anthropic.py  # Claude
│   │   ├── openai.py     # GPT
│   │   ├── deepseek.py   # DeepSeek
│   │   └── ollama.py     # 自部署
│   ├── client/        # 实例通讯客户端
│   └── profile.py     # 用户画像
├── apps/              # 应用
│   └── desktop/       # 桌面应用 (PySide6)
├── tests/             # 测试
└── docs/              # 文档
    └── plans/         # 设计文档
```

## 🛠️ 开发

```bash
# 运行测试
python -m pytest

# 代码检查
python -m mypy src/

# 代码格式化
python -m black src/
```

## 🤝 贡献

欢迎贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与。

## 📄 许可证

MIT 许可证 - 查看 [LICENSE](LICENSE) 文件。

---

<p align="center">
  用 ❤️ 制作 · OpenToad Team
</p>
