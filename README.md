# OpenToad 🐸

<p align="center">
  <img src="assets/logo.png" alt="OpenToad" width="200" />
</p>

<p align="center">
  <strong>Self-Sustainable AI Assistant</strong><br />
  基于 OpenClaw Fork | 多渠道接入 | 多元化盈利
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

OpenToad 是基于 [OpenClaw](https://github.com/openclaw/openclaw) Fork 开发的**自负盈亏 AI 助手**。保留 OpenClaw 全部核心功能（Gateway、Agent、Tools、Memory、Skills），并新增微信接入和盈利模块。

不同于传统 AI 助手，OpenToad 致力于打造可持续盈利的个人 AI 助手，支持广告变现、任务市场、订阅会员等多种商业模式。

## ✨ 特性

### 来自 OpenClaw 的核心功能

- **Gateway** - 会话管理、认证、消息路由、WebSocket
- **多渠道接入** - Telegram、Discord、Slack、WhatsApp、Signal 等
- **Agent** - ReAct 推理循环、多模型支持
- **Tools** - Shell、浏览器自动化、文件系统
- **Memory** - 持久化会话、上下文管理
- **Skills** - 按需加载的专业技能

### OpenToad 新增功能

- **微信接入** - 微信消息平台支持
- **盈利系统**
  - 广告联盟（展示/点击计费）
  - 任务市场（调查问卷、抢购等）
  - 订阅会员（去广告+高级功能）
- **部署支持** - Docker 一键部署

## 🚀 快速开始

### 环境要求

- Node.js 22+
- pnpm 9+
- Docker (可选)

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

# 编辑配置文件，添加 API Key
# ANTHROPIC_API_KEY=your-key-here
# OPENAI_API_KEY=your-key-here
```

### 运行

```bash
# 启动网关
pnpm openclaw gateway run
```

### 首次设置

```bash
# 运行向导
pnpm openclaw onboard

# 添加渠道
pnpm openclaw channels add telegram
pnpm openclaw channels add discord
pnpm openclaw channels add wechat
```

## 📖 文档

- [安装指南](docs/getting-started/installation.md)
- [配置说明](docs/configuration/README.md)
- [渠道接入](docs/channels/README.md)
- [盈利系统](docs/monetization/README.md)
- [部署指南](docs/deployment/README.md)

## 🏗️ 项目结构

```
opentoad/
├── src/
│   ├── gateway/          # Gateway 核心
│   ├── channels/         # 消息渠道
│   ├── agents/           # Agent 推理循环
│   ├── tools/            # 工具集
│   ├── memory/           # 持久化
│   ├── wechat/           # 微信接入
│   └── monetization/     # 盈利系统
│       ├── ads/              # 广告联盟
│       ├── subscription/     # 订阅系统
│       └── task-market/     # 任务市场
├── docker/               # Docker 配置
└── docs/                # 文档
```

## 💻 使用

### 消息渠道

| 渠道 | 状态 | 说明 |
|------|------|------|
| Telegram | ✅ | 官方支持 |
| Discord | ✅ | 官方支持 |
| Slack | ✅ | 官方支持 |
| WhatsApp | ✅ | OpenClaw 原生 |
| Signal | ✅ | OpenClaw 原生 |
| 微信 | 🆕 | OpenToad 新增 |

### 盈利功能

```bash
# 查看订阅计划
pnpm openclaw subscription plans

# 创建订阅
pnpm openclaw subscription create --plan premium

# 开启广告
pnpm openclaw monetization ads enable --provider admob

# 查看任务
pnpm openclaw tasks list
```

## 🛠️ 开发

### 开发环境

```bash
# 安装开发依赖
pnpm install

# 运行测试
pnpm test

# 代码检查
pnpm check

# 代码格式化
pnpm format
```

### Docker 部署

```bash
# 构建镜像
docker build -t opentoad:latest .

# 使用 docker-compose 启动
docker-compose up -d
```

## 🤝 贡献

欢迎贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件。

## ⚠️ 免责声明

- 本项目基于 [OpenClaw](https://github.com/openclaw/openclaw) 开源项目开发
- 使用广告和任务变现功能时请遵守当地法律法规
- 请勿用于任何违法用途
- 用户需自行承担使用过程中的一切风险

## 🔗 相关链接

- [OpenClaw 官网](https://openclaw.ai)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [Discord 社区](https://discord.gg/opentoad)

---

<p align="center">
  用 ❤️ 制作 · OpenToad Team
</p>
