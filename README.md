# OpenToad 🐸

<p align="center">
  <strong>你的 AI 记忆分身</strong><br />
  独立执行 · 长期记忆 · 主动行动
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

***

## ⭐ 简介

**OpenToad – 你的 AI 记忆分身**

它不是笔记，不是提醒，而是可以**独立行动**的智能体。

OpenToad 是你的"第二个大脑"，更是你的执行分身。它能记住你的目标、习惯与意图，并在你授权下独立推进任务、执行计划、主动提醒与行动。

### 核心理念

> **最真实的人格 = 常年累月积累的记忆体**

### 它不只是记忆，更是执行

- 设定一个目标，OpenToad 会拆解步骤、主动推进
- 记录你的偏好与上下文，在执行任务时自动调用
- 支持类 OpenClaw 的智能体能力，但更聚焦"替你完成"

### 主要功能

| 功能 | 说明 |
| --- | --- |
| **独立执行任务** | 无需你持续干预，OpenToad 可按计划完成多步操作 |
| **长期记忆中枢** | 记住你的习惯、偏好、待办事项与项目上下文 |
| **主动式智能体** | 在合适的时间主动提出建议、执行动作或提醒 |
| **任务与计划管理** | 支持自然语言创建任务，由 AI 自动拆解与执行 |
| **与你协同进化** | 使用越久，越懂你的节奏与优先级 |

### 隐私优先

你的记忆与任务数据仅属于你。OpenToad 在设计上遵循**本地优先**与**可控授权**原则。

### 适合谁？

- 你希望有一个"能做事"的 AI，而不只是回答问题
- 你需要一个长期陪伴、记住上下文的智能伙伴
- 你熟悉 OpenClaw 类智能体，但希望它更像"另一个你"

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

| 类型  | 模型                                      |
| --- | --------------------------------------- |
| 海外  | Claude, GPT, Gemini                     |
| 国内  | 文心一言, 通义千问, 混元, ChatGLM, Kimi, DeepSeek |
| 自部署 | Ollama, LocalAI, LM Studio, vLLM        |

### 可扩展盈利

- 实例通讯：客户端自动注册、云端任务分发
- Token 经济：实例在线、任务执行赚取 Token
- 广告联盟、订阅系统、API 变现

### 手机直连 (Gateway)

- **WebSocket Gateway** - 手机 App 可直接与 OpenToad 终端通讯
- 无需经过远程 API 服务器
- InstanceID 认证，简单安全
- 支持流式响应

## 🔗 手机连接

OpenToad 支持手机 App 直接连接，实现真正的一对一私人 AI 助手。

### 连接方式

```
ws://<电脑IP>:18989/ws
```

### 认证消息

```json
{"type": "auth", "payload": {"instance_id": "你的instance_id"}}
```

### 发送消息

```json
{"type": "message", "payload": {"content": "你好", "stream": true}}
```

### 启用 Gateway

桌面应用：设置 → 📱 手机连接 → 勾选「启用 Gateway 服务」

或使用独立启动脚本：

```bash
python scripts/start_gateway.py --api-key your-key --model gpt-4o-mini
```

## 🚀 快速开始

### 环境要求

- Python 3.10+ (已完全兼容)
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
│   ├── client/        # 实例通讯客户端 (HTTP)
│   ├── gateway/        # WebSocket Gateway 服务 ⭐
│   │   ├── server.py     # Gateway 服务端
│   │   ├── ai_handler.py # AI 消息处理
│   │   ├── protocol.py    # 消息协议
│   │   └── config.py      # 配置
│   └── profile.py     # 用户画像
├── apps/              # 应用
│   └── desktop/       # 桌面应用 (PySide6)
├── scripts/           # 脚本
│   ├── start_gateway.py      # Gateway 启动脚本
│   └── test_gateway_client.py # 测试客户端
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

***

<p align="center">
  用 ❤️ 制作 · OpenToad Team
</p>
