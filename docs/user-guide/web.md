# OpenToad Web 端使用说明

## 📖 简介

OpenToad Web 提供一个美观的浏览器界面，可以通过网页访问 AI 助手功能，支持对话、记忆管理和 Agent 协作。

## 🚀 快速开始

### 启动 Web 服务

```bash
# 使用 CLI 启动 Web 模式（推荐）
python3 run_opentoad.py --web

# 自定义端口
python3 run_opentoad.py --web --port 3000

# 仅本地访问
python3 run_opentoad.py --web --host 127.0.0.1
```

### 访问 Web 界面

启动成功后，在浏览器中打开：

```
http://localhost:8000
```

## 🌐 界面说明

### 侧边栏导航

| 图标 | 功能 | 说明 |
|------|------|
| 💬 | 聊天 | 主要对话界面 |
| 🤖 | Agent Network | Agent 协作面板 |
| ⚙️ | 设置 | 系统设置 |

### 主聊天区域

- **聊天标题** - 当前会话名称
- **消息列表** - 显示用户和 AI 消息
- **输入框** - 发送消息的输入区域
- **发送按钮** - 点击发送消息，或按 Enter 键

### Agent Network 面板

- **Agent 列表** - 显示所有在线 Agent
- **任务列表** - 显示当前任务和进度

## 💬 使用说明

### 开始对话

1. 在输入框中输入你的消息
2. 按 Enter 键或点击发送按钮
3. AI 会实时回复（支持流式输出）

### 快速操作

Web 界面提供几个快速操作按钮：

| 按钮 | 说明 |
|------|
| 🔍 研究 AI 技术 | 发送研究相关请求 |
| 💻 写爬虫代码 | 发送编程相关请求 |
| 🤖 A2A 协作 | 查看 Agent 协作功能 |

## 🤖 Agent Network

### 查看 Agent

1. 点击侧边栏的 "🤖 Agent Network"
2. 在 Agent Network 面板中查看所有在线 Agent
3. 每个 Agent 显示：
   - 名字
   - 角色
   - 状态（在线/离线）
   - 能力

### Agent 角色

| 角色 | 图标 | 职责 |
|------|------|
| Coordinator | 🎯 | 协调任务分配和结果汇总 |
| Worker | ⚙️ | 执行具体任务 |
| Researcher | 🔍 | 进行研究和分析 |
| Writer | ✍️ | 撰写文档和内容 |
| Reviewer | 👁️ | 审查和评估结果 |

### 任务管理

任务面板显示：

- **任务标题** - 当前任务名称
- **任务状态** - 待处理/进行中/已完成
- **进度条** - 任务完成百分比
- **进度文本** - 具体进度数值

## ⚙️ 设置

### 账户设置

- **登录状态** - 显示是否已登录
- **登录开关** - 切换登录/登出

### 外观设置

| 选项 | 说明 |
|------|------|
| 深色主题 | 启用/禁用深色配色方案 |
| 流式输出 | 实时显示 AI 回复 |

### Agent 设置

| 选项 | 说明 |
|------|------|
| 自动启动 Agent | 启动时自动初始化 Agent |
| 协作模式 | 允许多 Agent 协作 |

## 🔌 API 接口

### 基础信息

```bash
# 健康检查
curl http://localhost:8000/health

# 获取 AI 身份
curl http://localhost:8000/api/identity

# 获取记忆列表
curl http://localhost:8000/api/memories
```

### 聊天接口

```bash
# 发送聊天消息
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好",
    "session_id": "my-session",
    "stream": true
  }'
```

### 添加重要记忆

```bash
# 记住重要内容
curl -X POST "http://localhost:8000/api/remember?content=重要信息&category=KNOWLEDGE"
```

## 📱 WebSocket

### 连接 WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/my-session-id');

ws.onopen = () => {
  console.log('WebSocket 连接已建立');
};
```

### 发送消息

```javascript
ws.send(JSON.stringify({
  type: 'message',
  content: '你好'
}));
```

### 接收响应

```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'done') {
    console.log('AI 回复:', data.content);
  }
};
```

## 🎯 提示

- 确保在 CLI 模式下先配置好 LLM 提供商和 API Key
- Web 模式和 CLI 模式共享相同的记忆系统
- 可以使用自定义端口避免冲突
- WebSocket 支持实时流式输出
