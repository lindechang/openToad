# OpenToad Web

OpenToad 的 Web 端应用，提供浏览器访问界面。

## 📁 目录结构

```
web/
├── backend/              # FastAPI 后端
│   ├── main.py          # 主服务
│   └── requirements.txt  # Python 依赖
└── frontend/            # 前端静态文件
    └── index.html      # 单页应用
```

## 🚀 快速开始

### 1. 启动后端服务

```bash
# 进入后端目录
cd apps/web/backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

后端服务将在 http://localhost:8000 启动

### 2. 访问 Web 界面

打开浏览器访问：

- **主界面**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws/{session_id}

### 3. 开发模式（热重载）

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## ✨ 功能特性

### 聊天功能
- 实时消息发送
- 流式响应（WebSocket）
- 会话管理
- 快捷消息

### Agent Network
- 查看所有在线 Agent
- Agent 角色和能力展示
- 任务状态追踪
- 协作可视化

### 设置
- 主题切换
- 账户管理
- Agent 配置

## 🛠️ API 接口

### 会话管理

```bash
# 创建会话
POST /api/sessions
Body: { "title": "新会话" }

# 获取所有会话
GET /api/sessions

# 获取指定会话
GET /api/sessions/{session_id}

# 删除会话
DELETE /api/sessions/{session_id}
```

### 聊天

```bash
# 发送消息（非流式）
POST /api/chat
Body: { "message": "你好", "session_id": "xxx" }
```

### Agent Network

```bash
# 获取 Agent 列表
GET /api/agents

# 获取任务列表
GET /api/tasks

# 获取工作区列表
GET /api/workspaces
```

## 📱 响应式设计

Web 端采用响应式设计，支持：

- 💻 桌面端 (1920px+)
- 💻 笔记本 (1024px - 1919px)
- 📱 平板 (768px - 1023px)
- 📱 手机 (320px - 767px)

## 🔧 技术栈

### 后端
- **框架**: FastAPI
- **异步**: uvicorn
- **验证**: Pydantic

### 前端
- **HTML5**: 语义化标签
- **CSS3**: CSS Variables, Flexbox, Grid
- **JavaScript**: ES6+, Fetch API, WebSocket

## 📦 部署

### Docker 部署

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## 🔮 未来功能

- [ ] 用户认证系统
- [ ] 记忆体同步
- [ ] 真实 LLM 集成
- [ ] 文件上传
- [ ] 主题定制
- [ ] 移动端适配
- [ ] PWA 支持

## 📄 许可证

MIT License
