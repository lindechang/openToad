# OpenToad 功能清单

## 📋 功能概览

| 模块 | 功能 | 状态 |
|------|------|------|
| **记忆体系统** | 多记忆体管理 | ✅ 已完成 |
| | 记忆体加密 | ✅ 已完成 |
| | 账号绑定记忆体 | ✅ 已完成 |
| | 本地/在线记忆体 | ✅ 已完成 |
| **LLM 配置** | 多模型支持 | ✅ 已完成 |
| | API Key 管理 | ✅ 已完成 |
| | 模型选择 | ✅ 已完成 |
| **桌面应用** | PySide6 GUI | ✅ 已完成 |
| | 会话管理 | ✅ 已完成 |
| | 侧边栏导航 | ✅ 已完成 |
| **账号系统** | 用户注册/登录 | ✅ 已完成 |
| | 加密密钥派生 | ✅ 已完成 |
| **Gateway** | WebSocket 服务 | ✅ 已完成 |
| | 手机直连 | ✅ 已完成 |

---

## 🧠 记忆体系统

### 核心功能

| 功能 | 说明 |
|------|------|
| **多记忆体管理** | 可创建和管理多个独立的记忆体，每个记忆体有唯一的 UUID |
| **记忆体加密** | 支持 AES-256 加密，密钥由用户密码派生 |
| **账号绑定** | 记忆体可绑定到用户账号，实现云端同步 |
| **独立存储** | 每个记忆体独立存储在单独文件中，格式：`memory_{user_id}_{memory_id}.db` |
| **LLM 配置** | 每个记忆体可独立配置 LLM API Key 和模型 |

### 记忆体类型

| 类型 | 说明 |
|------|------|
| **未绑定记忆体** | 本地使用，无需登录账号 |
| **已绑定记忆体** | 绑定到账号，支持加密保护 |
| **拉取在线记忆体** | 从云端下载已存在的记忆体 |

### 数据表结构

```sql
-- 记忆体元数据表
CREATE TABLE memory_meta (
    memory_id TEXT PRIMARY KEY,      -- UUID
    name TEXT NOT NULL,              -- 记忆体名称
    bound_user_id TEXT,              -- 绑定用户ID（NULL表示未绑定）
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- LLM 配置表
CREATE TABLE llm_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,          -- deepseek, openai, qianwen 等
    api_key TEXT NOT NULL,           -- 加密存储
    model TEXT NOT NULL,             -- 模型名称
    temperature REAL DEFAULT 0.7,
    max_tokens INTEGER,
    created_at TIMESTAMP
);
```

---

## 🤖 LLM 配置

### 支持的模型提供商

| 类型 | 提供商 | 模型 |
|------|--------|------|
| 海外 | DeepSeek | deepseek-chat, deepseek-coder |
| 海外 | OpenAI | GPT-4o, GPT-4o-mini, GPT-4 |
| 海外 | Anthropic | Claude 3.5, Claude 3 |
| 国内 | 通义千问 (Qianwen) | qwen-turbo, qwen-plus, qwen-max |
| 国内 | 文心一言 | ernie-bot |
| 国内 | 混元 | hunyuan |
| 国内 | ChatGLM | chatglm3 |
| 国内 | Kimi | moonshot-v1 |
| 本地 | Ollama | 支持所有 Ollama 模型 |

### 配置方式

- API Key 存储在记忆体数据库中（加密）
- 不在 `settings.json` 中存储敏感信息
- 支持温度、最大 token 等参数配置

---

## 💻 桌面应用 (PySide6)

### UI 布局

```
┌─────┬──────────┬─────────────────────────────────┐
│ 65px│  180px   │                                 │
│图标栏│ 会话列表  │         主聊天区域               │
│     │          │                                 │
│🔍   │🌰 记忆体  │                                 │
│ +   │▼         │                                 │
│     │─────────│                                 │
│🤖   │+ 新建会话 │                                 │
│⚙️   │─────────│                                 │
│🔐   │会话      │                                 │
│ℹ️   │ 当前会话  │                                 │
│     │ 会话 2   │                                 │
│     │ 会话 3   │                                 │
└─────┴──────────┴─────────────────────────────────┘
```

### 功能模块

| 模块 | 功能 |
|------|------|
| **图标栏** | 搜索、新建记忆体、LLM配置、设置、账号、关于 |
| **会话列表** | 多会话管理、右键删除、新建会话 |
| **聊天区域** | 消息显示、输入框、流式响应 |
| **记忆体选择** | 下拉切换当前记忆体 |

---

## 🔐 账号系统

### 功能

| 功能 | 说明 |
|------|------|
| **用户注册** | 邮箱 + 密码 + 昵称 |
| **用户登录** | 邮箱 + 密码登录 |
| **密钥派生** | PBKDF2 派生加密密钥 |
| **记忆体绑定** | 登录后可绑定记忆体到账号 |

### 安全特性

- 密码使用 PBKDF2 + salt 哈希存储
- API Key 使用 AES-256 加密
- 加密密钥从用户密码派生，不明文存储

---

## 📱 Gateway 服务

### 功能

| 功能 | 说明 |
|------|------|
| **WebSocket 服务** | 支持手机 App 直连 |
| **InstanceID 认证** | 简单的设备认证机制 |
| **流式响应** | 支持 Server-Sent Events |

### 配置

```python
GatewayConfig(
    host="0.0.0.0",
    port=18989
)
```

---

## 🚀 待开发功能

- [ ] 记忆体云端同步
- [ ] 记忆体导入/导出
- [ ] 多设备登录
- [ ] 记忆体分享功能
- [ ] 插件系统
- [ ] 任务计划执行
