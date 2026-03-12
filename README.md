# OpenToad 🐸

<p align="center">
  <strong>Self-Sustainable AI Assistant</strong><br />
  从零构建的 AI Agent 框架 | 多模型支持 | 可扩展盈利
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

支持 CLI 对话、ReAct 推理循环、Tool 系统、多模型接入，可扩展盈利模式。

## ✨ 特性

- **CLI 对话** - 终端直接交互，支持流式响应
- **ReAct 推理循环** - 思维链可视化，Tool 调用编排
- **Tool 系统** - Shell 执行、文件操作、网页搜索、计算器
- **多模型支持**
  - 海外：Claude, GPT, Gemini
  - 国内：文心一言、通义千问、混元、ChatGLM、Kimi、DeepSeek
  - 自部署：Ollama、LocalAI、LM Studio、vLLM
- **可扩展盈利** - 广告联盟、订阅系统、API 变现

## 🚀 快速开始

### 环境要求

- Node.js 22+
- pnpm 9+

### 安装

```bash
# 克隆仓库
git clone https://github.com/opentoad/opentoad.git
cd opentoad

# 安装依赖
pnpm install

# 构建
pnpm build
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

```bash
# 启动 CLI
pnpm start

# 或开发模式
pnpm dev
```

## 📖 文档

- [安装指南](docs/getting-started/installation.md)
- [配置说明](docs/configuration/README.md)
- [模型接入](docs/providers/README.md)
- [Tool 开发](docs/tools/README.md)

## 🏗️ 项目结构

```
opentoad/
├── src/
│   ├── cli/           # CLI 入口
│   ├── agent/         # Agent 推理核心
│   ├── tools/         # Tool 系统
│   │   └── impl/          # 内置 Tools
│   └── providers/    # LLM Provider
│       ├── anthropic.ts   # Claude
│       ├── openai.ts      # GPT
│       ├── deepseek.ts    # DeepSeek
│       └── ollama.ts      # 自部署
├── test/              # 测试
└── docs/              # 文档
```

## 🛠️ 开发

```bash
# 运行测试
pnpm test

# 代码检查
pnpm check

# 代码格式化
pnpm format
```

## 🤝 贡献

欢迎贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与。

## 📄 许可证

MIT 许可证 - 查看 [LICENSE](LICENSE) 文件。

---

<p align="center">
  用 ❤️ 制作 · OpenToad Team
</p>
