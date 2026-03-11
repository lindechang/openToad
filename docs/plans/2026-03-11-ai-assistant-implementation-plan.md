# OpenToad 自负盈亏 AI 助手实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 基于 OpenClaw 开发支持多渠道接入和多元化盈利模式的 AI 助手系统

**Architecture:** 
- 以 OpenClaw 为核心框架
- 新增微信 channel、盈利模块、广告系统
- 支持 SaaS 云端部署和用户自部署

**Tech Stack:** TypeScript, Node.js, Docker, PostgreSQL, Redis, pnpm

---

## 阶段一：基础环境搭建

### Task 1: 初始化项目结构

**Files:**
- 创建: `opentoad/package.json`
- 创建: `opentoad/pnpm-workspace.yaml`
- 创建: `opentoad/tsconfig.json`
- 创建: `opentoad/openclaw` (符号链接或 submodule)

**Step 1: 创建项目目录和 package.json**

```json
{
  "name": "opentoad",
  "version": "1.0.0",
  "private": true,
  "description": "自负盈亏 AI 助手",
  "scripts": {
    "dev": "openclaw gateway run",
    "build": "openclaw build",
    "test": "vitest"
  },
  "packageManager": "pnpm@9.0.0"
}
```

**Step 2: 创建 pnpm-workspace.yaml**

```yaml
packages:
  - 'openclaw'
  - 'packages/*'
  - 'extensions/*'
```

**Step 3: 创建 tsconfig.json**

```json
{
  "extends": "./openclaw/tsconfig.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"]
}
```

**Step 4: 初始化 git 仓库**

```bash
git init
git add .
git commit -m "chore: init opentoad project"
```

---

### Task 2: 运行 OpenClaw 本地开发环境

**Files:**
- 修改: `opentoad/openclaw/.env`
- 修改: `opentoad/openclaw/src/config/index.ts`

**Step 1: 复制环境配置**

```bash
cp openclaw/.env.example openclaw/.env
```

**Step 2: 配置必要的环境变量**

```bash
# 至少配置 ANTHROPIC_API_KEY 或 OPENAI_API_KEY
ANTHROPIC_API_KEY=your-key-here
```

**Step 3: 安装依赖并验证运行**

```bash
cd openclaw && pnpm install
pnpm build
pnpm openclaw --help
```

**Step 4: 提交更改**

```bash
git add openclaw/.env.example
git commit -m "chore: add openclaw as dependency"
```

---

## 阶段二：多渠道接入模块

### Task 3: 添加微信 channel 支持

**Files:**
- 创建: `extensions/wechat/src/index.ts`
- 创建: `extensions/wechat/package.json`
- 创建: `extensions/wechat/tsconfig.json`

**Step 1: 创建 wechat extension**

```bash
mkdir -p extensions/wechat/src
```

**Step 2: 实现微信 channel**

```typescript
// extensions/wechat/src/index.ts
import { ChannelPlugin } from 'openclaw/plugin-sdk';

export const wechatChannel: ChannelPlugin = {
  name: 'wechat',
  async send(message, channel) {
    // 调用微信 API 发送消息
  },
  async startPolling(credentials, handler) {
    // 轮询微信消息
  }
};
```

**Step 3: 注册到 OpenClaw**

```bash
pnpm openclaw extensions install wechat
```

**Step 4: 测试连接**

```bash
pnpm openclaw channels add wechat
pnpm openclaw channels status
```

---

### Task 4: 添加 Web Widget 支持

**Files:**
- 创建: `extensions/web-widget/src/index.ts`
- 创建: `ui/web-widget/index.html`
- 创建: `ui/web-widget/embed.js`

**Step 1: 创建 Web Widget 前端**

```html
<!-- ui/web-widget/index.html -->
<div id="opentoad-widget">
  <button id="opentoad-toggle">🤖</button>
  <div id="opentoad-chat" style="display:none">
    <div id="opentoad-messages"></div>
    <input id="opentoad-input" placeholder="发送消息..." />
  </div>
</div>
```

**Step 2: 实现 Web Channel 后端**

```typescript
// extensions/web-widget/src/index.ts
import { ChannelPlugin, WebServer } from 'openclaw/plugin-sdk';

export const webChannel: ChannelPlugin = {
  name: 'web',
  async startPolling(credentials, handler) {
    const server = new WebServer(8080);
    server.on('message', handler);
    await server.start();
  }
};
```

---

## 阶段三：盈利系统

### Task 5: 广告联盟模块

**Files:**
- 创建: `packages/monetization/src/ad-plugins/admob.ts`
- 创建: `packages/monetization/src/ad-plugins/union.ts`
- 创建: `packages/monetization/src/index.ts`
- 创建: `packages/monetization/package.json`

**Step 1: 创建 monetization 包**

```bash
mkdir -p packages/monetization/src/ad-plugins
```

**Step 2: 实现广告插件接口**

```typescript
// packages/monetization/src/ad-plugins/admob.ts
export interface AdProvider {
  name: string;
  loadAd(config: AdConfig): Promise<AdUnit>;
  showAd(unit: AdUnit): Promise<void>;
}

export interface AdConfig {
  appId: string;
  adUnitId: string;
}

export interface AdUnit {
  id: string;
  type: 'banner' | 'interstitial' | 'rewarded';
}
```

**Step 3: 实现广告管理器**

```typescript
// packages/monetization/src/index.ts
export class AdManager {
  private providers: Map<string, AdProvider> = new Map();
  
  registerProvider(provider: AdProvider): void {
    this.providers.set(provider.name, provider);
  }
  
  async showAd(providerName: string, config: AdConfig): Promise<void> {
    const provider = this.providers.get(providerName);
    if (!provider) throw new Error(`Provider ${providerName} not found`);
    
    const ad = await provider.loadAd(config);
    await provider.showAd(ad);
  }
}
```

**Step 4: 测试广告加载**

```bash
cd packages/monetization
pnpm test
```

---

### Task 6: 任务市场模块

**Files:**
- 创建: `packages/monetization/src/task-market/index.ts`
- 创建: `packages/monetization/src/task-market/types.ts`
- 创建: `packages/monetization/src/task-market/db.ts`

**Step 1: 定义任务类型**

```typescript
// packages/monetization/src/task-market/types.ts
export interface Task {
  id: string;
  type: 'survey' | 'purchase' | 'booking';
  title: string;
  description: string;
  reward: number;
  status: 'pending' | 'completed' | 'failed';
  userId: string;
  metadata: Record<string, unknown>;
}

export interface TaskSubmission {
  taskId: string;
  answers?: Record<string, string>;
  proof?: string;
}
```

**Step 2: 实现任务市场服务**

```typescript
// packages/monetization/src/task-market/index.ts
import { db } from './db';

export class TaskMarket {
  async listTasks(userId: string): Promise<Task[]> {
    return db.tasks.findMany({ where: { userId } });
  }
  
  async submitTask(submission: TaskSubmission): Promise<Task> {
    // 验证并更新任务状态
  }
  
  async getReward(taskId: string): Promise<number> {
    // 计算收益
  }
}
```

---

### Task 7: 订阅系统

**Files:**
- 创建: `packages/monetization/src/subscription/index.ts`
- 创建: `packages/monetization/src/subscription/plans.ts`
- 创建: `packages/monetization/src/subscription/payment.ts`

**Step 1: 定义订阅计划**

```typescript
// packages/monetization/src/subscription/plans.ts
export const subscriptionPlans = {
  free: {
    name: '免费版',
    price: 0,
    features: ['基础 AI 对话', '广告展示'],
    limits: { messagesPerDay: 50 }
  },
  premium: {
    name: '高级版',
    price: 9.9,
    features: ['无限制对话', '无广告', '高级插件'],
    limits: {}
  }
};
```

**Step 2: 实现订阅服务**

```typescript
// packages/monetization/src/subscription/index.ts
export class SubscriptionService {
  async checkAccess(userId: string, feature: string): Promise<boolean> {
    const sub = await this.getSubscription(userId);
    // 检查权限
  }
  
  async createCheckoutSession(userId: string, planId: string): Promise<string> {
    // 创建支付会话
  }
}
```

---

## 阶段四：数据层

### Task 8: 数据库设计

**Files:**
- 创建: `packages/database/prisma/schema.prisma`
- 创建: `packages/database/src/index.ts`

**Step 1: 创建 Prisma schema**

```prisma
// packages/database/prisma/schema.prisma
model User {
  id            String    @id @default(cuid())
  email         String    @unique
  subscription  Subscription?
  tasks         Task[]
  createdAt     DateTime  @default(now())
}

model Subscription {
  id        String   @id @default(cuid())
  userId    String   @unique
  plan      String
  expiresAt DateTime
  user      User     @relation(fields: [userId], references: [id])
}

model Task {
  id          String   @id @default(cuid())
  userId      String
  type        String
  reward      Float
  status      String
  user        User     @relation(fields: [userId], references: [id])
  createdAt   DateTime @default(now())
}
```

**Step 2: 初始化数据库**

```bash
cd packages/database
pnpm prisma migrate dev --name init
```

---

## 阶段五：部署系统

### Task 9: Docker 镜像构建

**Files:**
- 创建: `docker/Dockerfile.saaS`
- 创建: `docker/docker-compose.saaS.yml`
- 创建: `docker/docker-compose.selfhosted.yml`

**Step 1: 创建 SaaS Docker 配置**

```dockerfile
# docker/Dockerfile.saaS
FROM node:22-alpine

WORKDIR /app
COPY packages ./packages
COPY extensions ./extensions
COPY openclaw ./openclaw

RUN npm install -g pnpm@9
RUN pnpm install
RUN pnpm build

EXPOSE 18789
CMD ["pnpm", "openclaw", "gateway", "run"]
```

**Step 2: 创建 docker-compose SaaS**

```yaml
# docker/docker-compose.saaS.yml
version: '3.8'
services:
  gateway:
    build:
      context: ..
      dockerfile: docker/Dockerfile.saaS
    ports:
      - "18789:18789"
    env_file:
      - .env.saaS
  postgres:
    image: postgres:16
  redis:
    image: redis:7
```

**Step 3: 测试构建**

```bash
docker build -f docker/Dockerfile.saaS -t opentoad:saas .
```

---

### Task 10: 自部署版本

**Files:**
- 创建: `scripts/package-selfhosted.sh`
- 创建: `.env.selfhosted.example`

**Step 1: 创建打包脚本**

```bash
#!/bin/bash
# scripts/package-selfhosted.sh
pnpm install
pnpm build
tar -czf opentoad-selfhosted.tar.gz \
  dist/ \
  openclaw/ \
  extensions/ \
  packages/
```

**Step 2: 创建自部署配置示例**

```bash
cp .env.example .env.selfhosted
```

---

## 阶段六：集成测试

### Task 11: 端到端测试

**Files:**
- 创建: `test/e2e/monetization.test.ts`
- 创建: `test/e2e/channels.test.ts`

**Step 1: 编写 E2E 测试**

```typescript
// test/e2e/monetization.test.ts
import { test, expect } from 'vitest';

test('subscription flow', async () => {
  const user = await createTestUser();
  const checkout = await subscriptionService.createCheckoutSession(user.id, 'premium');
  expect(checkout).toBeDefined();
});
```

**Step 2: 运行测试**

```bash
pnpm test:e2e
```

---

## 执行选项

**Plan complete and saved to `docs/plans/2026-03-11-ai-assistant-design.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
