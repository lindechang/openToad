# OpenToad 实例通讯客户端设计

## 概述

为 OpenToad 客户端实现与 API 服务端的通讯模块，支持实例注册、心跳保活、指令接收与执行。

## 功能需求

1. **实例注册** - 启动时自动注册到服务端
2. **心跳保活** - 定期发送心跳维持在线状态
3. **指令轮询** - 定期获取待执行指令
4. **指令执行** - 执行服务端下发的指令并反馈结果
5. **配置管理** - 支持服务端配置更新

## 技术方案

### HTTP 轮询模式

- 心跳间隔：30秒
- 指令轮询间隔：5秒
- 超时设置：10秒

### 模块设计

```
src/client/
├── __init__.py
├── config.py          # 配置管理
├── http_client.py     # HTTP 客户端封装
├── instance.py        # 实例管理器
├── heartbeat.py       # 心跳线程
├── commander.py       # 指令处理器
└── service.py        # 统一入口
```

### API 对应关系

| 服务端 API | 客户端模块 |
|------------|------------|
| POST /api/instance/register | instance.py |
| POST /api/instance/heartbeat | heartbeat.py |
| GET /api/instance/commands | commander.py |
| POST /api/instance/command/complete | commander.py |
| POST /api/instance/bind | instance.py |

### 数据结构

```python
@dataclass
class InstanceInfo:
    id: str
    version: str
    user_id: Optional[int]
    bound_at: Optional[datetime]
    registered_at: datetime
    last_heartbeat_at: datetime
    status: str  # UNBOUND, ONLINE, OFFLINE

@dataclass
class Command:
    id: str
    instance_id: str
    type: str  # UPDATE_CONFIG, etc.
    payload: str
    status: str  # PENDING, COMPLETED, FAILED
    created_at: datetime
    completed_at: Optional[datetime]
```

## 配置项

```json
{
  "server_url": "http://localhost:8080",
  "instance_id": null,
  "instance_version": "1.0.0",
  "heartbeat_interval": 30,
  "command_poll_interval": 5,
  "http_timeout": 10
}
```

## 实现顺序

1. config.py - 配置管理
2. http_client.py - HTTP 封装
3. instance.py - 实例注册/绑定
4. heartbeat.py - 心跳循环
5. commander.py - 指令处理
6. service.py - 统一入口
