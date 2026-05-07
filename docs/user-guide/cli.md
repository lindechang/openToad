# OpenToad CLI 使用说明

## 📖 简介

OpenToad CLI 是一个强大的命令行界面，提供完整的 AI 助手功能，包括对话、记忆管理、工具调用等。

## 🚀 快速开始

### 基本启动

```bash
# 方式 1: 使用启动脚本（推荐）
./opentoad.sh  # macOS/Linux
opentoad.bat   # Windows

# 方式 2: 直接运行
python3 run_opentoad.py  # macOS/Linux
python run_opentoad.py   # Windows
```

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|
| `--web` | 启动 Web 服务器模式 | - |
| `--host` | Web 服务器主机地址 | 0.0.0.0 |
| `--port` | Web 服务器端口 | 8000 |
| `--stream` | 启用流式输出 | - |
| `--no-stream` | 禁用流式输出 | - |

### 示例

```bash
# 标准 CLI 模式
python3 run_opentoad.py

# Web 模式
python3 run_opentoad.py --web

# 自定义 Web 配置
python3 run_opentoad.py --web --host 127.0.0.1 --port 3000

# 禁用流式输出
python3 run_opentoad.py --no-stream
```

## 💬 交互命令

在 CLI 对话模式下，可以使用以下命令：

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助信息 |
| `/history` | 显示对话历史 |
| `/clear` | 清空对话历史 |
| `/config` | 显示当前配置 |
| `/models` | 列出可用模型 |
| `/tools` | 列出可用工具 |
| `/identity` | 查看 AI 身份信息 |
| `/memories` | 查看记忆列表 |
| `/remember <内容>` | 添加重要记忆（长期记忆） |
| `/exit` 或 `/quit` | 退出程序 |

### 命令详解

#### `/identity` - 查看 AI 身份

显示当前 AI 的名字、角色、主人信息、原则和特征。

```
🐸 AI Identity:
  名字: Toad
  角色: AI Assistant
  主人: 你的名字
  原则: Safety, Loyalty
```

#### `/memories` - 查看记忆列表

显示最近的记忆和长期记忆。

```
🐸 Long-term Memories:
  1. [KNOWLEDGE] 重要的生日是1月1日 (weight: 1.0

🐸 Recent Memories:
  1. [DIALOG] User: 你好 (weight: 0.5)
  2. [DIALOG] Toad: 你好! (weight: 0.5)
```

#### `/remember` - 添加重要记忆

将内容标记为长期记忆，永久保存。

```
/remember 我的生日是1月1日
✓ Remembered: 我的生日是1月1日
```

## 🧠 记忆系统

### 首次启动

第一次运行时，会引导你设置 AI 身份：

```
🐸 初次见面，让我们先设置一下 AI 的身份...

请输入 AI 名字 [Toad]: 
请输入 AI 角色 [AI Assistant]: 
你的名字: 张三

✓ 身份设置完成！
  名字: Toad
  角色: AI Assistant
  主人: 张三
```

### 记忆分类

| 类别 | 说明 |
|------|------|
| **IDENTITY** | 身份记忆 |
| **PREFERENCE** | 偏好记忆 |
| **KNOWLEDGE** | 知识记忆 |
| **PROJECT** | 项目记忆 |
| **DIALOG** | 对话记忆 |
| **CONTEXT** | 上下文记忆 |

## ⚙️ 配置管理

### 首次配置

第一次运行会提示选择 LLM 提供商：

```
Found saved configuration:
  Provider: anthropic
  Model: claude-3-5-sonnet-20241022
  API Key: ************
Use saved configuration? [Y/n]:
```

### 选择提供商

可用的 LLM 提供商：

| 选项 | 提供商 | 模型示例 |
|------|--------|
| 1 | Anthropic | claude-3-5-sonnet-20241022 |
| 2 | OpenAI | gpt-4o |
| 3 | DeepSeek | deepseek-chat |
| 4 | Qianwen | qwen-turbo |
| 5 | Ernie | ernie-bot |
| 6 | Hunyuan | hunyuan-latest |
| 7 | Zhipu | glm-4 |
| 8 | Kimi | moonshot-v1-8k |
| 9 | Gemini | gemini-1.5-flash |
| 10 | Ollama | llama2 |

## 🛠️ 内置工具

OpenToad CLI 支持以下工具：

| 工具 | 说明 |
|------|------|
| Shell | 执行 shell 命令 |
| Filesystem | 文件读写操作 |
| Web Search | 网页搜索 |
| Calculator | 数学计算 |
| Profile Tools | 画像工具 |

## 📝 对话示例

### 基本对话

```
You >> 你好
🤖 AI >> 你好！我是 Toad，你的 AI 助手。有什么我可以帮助你的吗？
```

### 使用工具

```
You >> 帮我查看当前目录的文件
🤖 AI >> 好的，让我帮你查看一下...
[使用工具执行 ls 命令
```

## 🎯 提示

- `/help` - 显示帮助
- `/identity` - 查看身份
- `/memories` - 查看记忆
- `/remember` - 记住重要事情
- `/exit` - 退出
