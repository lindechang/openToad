# OpenToad 实例通讯客户端实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现客户端通讯模块，支持实例注册、心跳、指令接收与执行

**Architecture:** 采用 HTTP 轮询模式，在后台线程运行心跳和指令轮询

**Tech Stack:** Python 标准库 (uuid, json, threading, requests)

---

### Task 1: 配置管理模块 (config.py)

**Files:**
- Create: `src/client/config.py`
- Test: `tests/client/test_config.py`

**Step 1: 创建测试文件**

```python
# tests/client/test_config.py
import pytest
import json
import tempfile
import os
from src.client.config import ClientConfig

def test_load_default_config():
    config = ClientConfig()
    assert config.server_url == "http://localhost:8080"
    assert config.instance_version == "1.0.0"
    assert config.heartbeat_interval == 30

def test_generate_instance_id():
    config = ClientConfig()
    assert config.instance_id is not None
    assert len(config.instance_id) == 36  # UUID format
```

**Step 2: 运行测试验证失败**

Run: `python -m pytest tests/client/test_config.py -v`
Expected: FAIL - module not found

**Step 3: 实现配置模块**

```python
# src/client/config.py
import json
import uuid
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

DEFAULT_CONFIG = {
    "server_url": "http://localhost:8080",
    "instance_id": None,
    "instance_version": "1.0.0",
    "heartbeat_interval": 30,
    "command_poll_interval": 5,
    "http_timeout": 10
}

CONFIG_FILE = "config.json"

@dataclass
class ClientConfig:
    server_url: str = "http://localhost:8080"
    instance_id: Optional[str] = None
    instance_version: str = "1.0.0"
    heartbeat_interval: int = 30
    command_poll_interval: int = 5
    http_timeout: int = 10

    def __post_init__(self):
        if self.instance_id is None:
            self.instance_id = str(uuid.uuid4())
        self._load_from_file()

    def _load_from_file(self):
        config_path = Path(CONFIG_FILE)
        if config_path.exists():
            with open(config_path, 'r') as f:
                data = json.load(f)
                for key, value in DEFAULT_CONFIG.items():
                    if key in data:
                        setattr(self, key, data[key])
                if self.instance_id is None:
                    self.instance_id = str(uuid.uuid4())

    def save(self):
        config_path = Path(CONFIG_FILE)
        data = asdict(self)
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)

    @property
    def api_base(self) -> str:
        return f"{self.server_url}/api/instance"
```

**Step 4: 运行测试验证通过**

Run: `python -m pytest tests/client/test_config.py -v`
Expected: PASS

**Step 5: Commit**

---

### Task 2: HTTP 客户端封装 (http_client.py)

**Files:**
- Create: `src/client/http_client.py`
- Test: `tests/client/test_http_client.py`

**Step 1: 创建测试文件**

```python
# tests/client/test_http_client.py
import pytest
from unittest.mock import Mock, patch
from src.client.http_client import HttpClient

def test_get_request():
    client = HttpClient("http://localhost:8080", timeout=10)
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"status": "ok"}
        result = client.get("/api/test")
        assert result == {"status": "ok"}

def test_post_request():
    client = HttpClient("http://localhost:8080", timeout=10)
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {"id": "123"}
        result = client.post("/api/register", {"key": "value"})
        assert result == {"id": "123"}
```

**Step 2: 运行测试验证失败**

Run: `python -m pytest tests/client/test_http_client.py -v`
Expected: FAIL - module not found

**Step 3: 实现 HTTP 客户端**

```python
# src/client/http_client.py
import requests
from typing import Any, Dict, Optional

class HttpClient:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()

    def _build_url(self, endpoint: str) -> str:
        return f"{self.base_url}{endpoint}"

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        url = self._build_url(endpoint)
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json() if response.content else None

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        url = self._build_url(endpoint)
        response = self.session.post(url, json=data, timeout=self.timeout)
        response.raise_for_status()
        return response.json() if response.content else None
```

**Step 4: 运行测试验证通过**

Run: `python -m pytest tests/client/test_http_client.py -v`
Expected: PASS

**Step 5: Commit**

---

### Task 3: 实例管理器 (instance.py)

**Files:**
- Create: `src/client/instance.py`
- Modify: `src/client/__init__.py`
- Test: `tests/client/test_instance.py`

**Step 1: 创建测试文件**

```python
# tests/client/test_instance.py
import pytest
from unittest.mock import Mock, patch
from src.client.instance import InstanceManager
from src.client.config import ClientConfig

def test_register_instance():
    config = ClientConfig()
    config.server_url = "http://localhost:8080"
    
    with patch('src.client.http_client.HttpClient') as MockClient:
        mock_client = Mock()
        mock_client.post.return_value = {
            "id": "test-001",
            "version": "1.0.0",
            "status": "UNBOUND"
        }
        MockClient.return_value = mock_client
        
        manager = InstanceManager(config)
        result = manager.register()
        
        assert result["id"] == "test-001"
        mock_client.post.assert_called_once()
```

**Step 2: 运行测试验证失败**

Run: `python -m pytest tests/client/test_instance.py -v`
Expected: FAIL

**Step 3: 实现实例管理器**

```python
# src/client/instance.py
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from src.client.http_client import HttpClient
from src.client.config import ClientConfig

@dataclass
class InstanceInfo:
    id: str
    version: str
    user_id: Optional[int]
    bound_at: Optional[datetime]
    registered_at: datetime
    last_heartbeat_at: datetime
    status: str

class InstanceManager:
    def __init__(self, config: ClientConfig):
        self.config = config
        self.http_client = HttpClient(config.server_url, config.http_timeout)
        self._info: Optional[InstanceInfo] = None

    def register(self) -> Dict[str, Any]:
        data = {
            "instanceId": self.config.instance_id,
            "version": self.config.instance_version
        }
        result = self.http_client.post("/instance/register", data)
        self._info = self._parse_instance(result)
        return result

    def bind_user(self, user_id: int) -> Dict[str, Any]:
        data = {
            "instanceId": self.config.instance_id,
            "userId": user_id
        }
        result = self.http_client.post("/instance/bind", data)
        self._info = self._parse_instance(result)
        return result

    def get_status(self) -> Optional[InstanceInfo]:
        if not self.config.instance_id:
            return None
        result = self.http_client.get("/instance/status", {"instanceId": self.config.instance_id})
        self._info = self._parse_instance(result)
        return self._info

    def _parse_instance(self, data: Dict) -> InstanceInfo:
        return InstanceInfo(
            id=data["id"],
            version=data["version"],
            user_id=data.get("userId"),
            bound_at=self._parse_datetime(data.get("boundAt")),
            registered_at=self._parse_datetime(data["registeredAt"]),
            last_heartbeat_at=self._parse_datetime(data["lastHeartbeatAt"]),
            status=data["status"]
        )

    @staticmethod
    def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
```

**Step 4: 修改 __init__.py**

```python
# src/client/__init__.py
from src.client.config import ClientConfig
from src.client.http_client import HttpClient
from src.client.instance import InstanceManager, InstanceInfo

__all__ = ['ClientConfig', 'HttpClient', 'InstanceManager', 'InstanceInfo']
```

**Step 5: 运行测试验证通过**

Run: `python -m pytest tests/client/test_instance.py -v`
Expected: PASS

**Step 6: Commit**

---

### Task 4: 心跳模块 (heartbeat.py)

**Files:**
- Create: `src/client/heartbeat.py`
- Test: `tests/client/test_heartbeat.py`

**Step 1: 创建测试文件**

```python
# tests/client/test_heartbeat.py
import pytest
import time
from unittest.mock import Mock, patch, call
from src.client.heartbeat import HeartbeatService
from src.client.config import ClientConfig

def test_heartbeat_sends_request():
    config = ClientConfig()
    config.server_url = "http://localhost:8080"
    config.heartbeat_interval = 1
    
    with patch('src.client.http_client.HttpClient') as MockClient:
        mock_client = Mock()
        MockClient.return_value = mock_client
        
        service = HeartbeatService(config)
        service.start()
        time.sleep(2.5)  # 等待至少2次心跳
        service.stop()
        
        assert mock_client.post.call_count >= 2
```

**Step 2: 运行测试验证失败**

Run: `python -m pytest tests/client/test_heartbeat.py -v`
Expected: FAIL

**Step 3: 实现心跳模块**

```python
# src/client/heartbeat.py
import threading
import time
import logging
from src.client.http_client import HttpClient
from src.client.config import ClientConfig

logger = logging.getLogger(__name__)

class HeartbeatService:
    def __init__(self, config: ClientConfig):
        self.config = config
        self.http_client = HttpClient(config.server_url, config.http_timeout)
        self._running = False
        self._thread: threading.Thread = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("Heartbeat service started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Heartbeat service stopped")

    def _run(self):
        while self._running:
            try:
                self._send_heartbeat()
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
            time.sleep(self.config.heartbeat_interval)

    def _send_heartbeat(self):
        data = {"instanceId": self.config.instance_id}
        self.http_client.post("/instance/heartbeat", data)
        logger.debug("Heartbeat sent")
```

**Step 4: 运行测试验证通过**

Run: `python -m pytest tests/client/test_heartbeat.py -v`
Expected: PASS

**Step 5: Commit**

---

### Task 5: 指令处理模块 (commander.py)

**Files:**
- Create: `src/client/commander.py`
- Test: `tests/client/test_commander.py`

**Step 1: 创建测试文件**

```python
# tests/client/test_commander.py
import pytest
import time
from unittest.mock import Mock, patch
from src.client.commander import CommanderService, Command
from src.client.config import ClientConfig

def test_fetch_commands():
    config = ClientConfig()
    config.server_url = "http://localhost:8080"
    config.command_poll_interval = 1
    
    with patch('src.client.http_client.HttpClient') as MockClient:
        mock_client = Mock()
        mock_client.get.return_value = [
            {"id": "cmd-001", "type": "UPDATE_CONFIG", "payload": "{}", "status": "PENDING"}
        ]
        MockClient.return_value = mock_client
        
        commander = CommanderService(config)
        commands = commander.fetch_commands()
        
        assert len(commands) == 1
        assert commands[0].id == "cmd-001"
```

**Step 2: 运行测试验证失败**

Run: `python -m pytest tests/client/test_commander.py -v`
Expected: FAIL

**Step 3: 实现指令处理模块**

```python
# src/client/commander.py
import threading
import time
import json
import logging
from typing import List, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
from src.client.http_client import HttpClient
from src.client.config import ClientConfig

logger = logging.getLogger(__name__)

@dataclass
class Command:
    id: str
    instance_id: str
    type: str
    payload: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

class CommanderService:
    def __init__(self, config: ClientConfig, on_command: Optional[Callable] = None):
        self.config = config
        self.http_client = HttpClient(config.server_url, config.http_timeout)
        self.on_command = on_command
        self._running = False
        self._thread: threading.Thread = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("Commander service started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Commander service stopped")

    def fetch_commands(self) -> List[Command]:
        params = {"instanceId": self.config.instance_id}
        data = self.http_client.get("/instance/commands", params)
        return [self._parse_command(c) for c in data]

    def complete_command(self, command_id: str):
        self.http_client.post("/instance/command/complete", {"commandId": command_id})
        logger.info(f"Command {command_id} marked as completed")

    def _run(self):
        while self._running:
            try:
                commands = self.fetch_commands()
                for cmd in commands:
                    if cmd.status == "PENDING" and self.on_command:
                        self.on_command(cmd)
            except Exception as e:
                logger.error(f"Failed to fetch commands: {e}")
            time.sleep(self.config.command_poll_interval)

    def _parse_command(self, data: dict) -> Command:
        return Command(
            id=data["id"],
            instance_id=data["instanceId"],
            type=data["type"],
            payload=data["payload"],
            status=data["status"],
            created_at=datetime.fromisoformat(data["createdAt"].replace('Z', '+00:00')),
            completed_at=datetime.fromisoformat(data["completedAt"].replace('Z', '+00:00')) if data.get("completedAt") else None
        )
```

**Step 4: 运行测试验证通过**

Run: `python -m pytest tests/client/test_commander.py -v`
Expected: PASS

**Step 5: Commit**

---

### Task 6: 统一服务入口 (service.py)

**Files:**
- Create: `src/client/service.py`
- Modify: `src/client/__init__.py`

**Step 1: 实现统一入口**

```python
# src/client/service.py
import logging
from typing import Optional, Callable, List
from src.client.config import ClientConfig
from src.client.instance import InstanceManager
from src.client.heartbeat import HeartbeatService
from src.client.commander import CommanderService, Command
from src.client.http_client import HttpClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstanceService:
    def __init__(self, config: Optional[ClientConfig] = None, on_command: Optional[Callable] = None):
        self.config = config or ClientConfig()
        self.instance_manager = InstanceManager(self.config)
        self.heartbeat_service = HeartbeatService(self.config)
        self.commander_service = CommanderService(self.config, on_command)
        self._started = False

    def start(self):
        if self._started:
            logger.warning("Service already started")
            return
        
        logger.info(f"Starting instance service for {self.config.instance_id}")
        
        # 注册实例
        self.instance_manager.register()
        logger.info(f"Instance registered: {self.config.instance_id}")
        
        # 启动心跳
        self.heartbeat_service.start()
        
        # 启动指令监听
        self.commander_service.start()
        
        self._started = True
        logger.info("Instance service started successfully")

    def stop(self):
        self.heartbeat_service.stop()
        self.commander_service.stop()
        self._started = False
        logger.info("Instance service stopped")

    def bind_user(self, user_id: int):
        return self.instance_manager.bind_user(user_id)

    def get_status(self):
        return self.instance_manager.get_status()

    @property
    def instance_id(self) -> str:
        return self.config.instance_id
```

**Step 2: 修改 __init__.py**

```python
# src/client/__init__.py 完整内容
from src.client.config import ClientConfig
from src.client.http_client import HttpClient
from src.client.instance import InstanceManager, InstanceInfo
from src.client.heartbeat import HeartbeatService
from src.client.commander import CommanderService, Command
from src.client.service import InstanceService

__all__ = [
    'ClientConfig', 
    'HttpClient', 
    'InstanceManager', 
    'InstanceInfo',
    'HeartbeatService',
    'CommanderService',
    'Command',
    'InstanceService'
]
```

**Step 3: 验证导入**

Run: `python -c "from src.client import InstanceService; print('OK')"`
Expected: OK

**Step 4: Commit**

---

### Task 7: 集成测试

**Files:**
- Test: `tests/client/test_integration.py`

**Step 1: 创建集成测试**

```python
# tests/client/test_integration.py
import pytest
from unittest.mock import Mock, patch
from src.client.service import InstanceService
from src.client.config import ClientConfig

def test_full_flow():
    config = ClientConfig()
    config.server_url = "http://localhost:8080"
    config.heartbeat_interval = 1
    config.command_poll_interval = 1
    
    commands_received = []
    
    def on_command(cmd):
        commands_received.append(cmd)
    
    with patch('src.client.http_client.HttpClient') as MockClient:
        mock_client = Mock()
        
        # 注册响应
        mock_client.post.side_effect = [
            {"id": "test-001", "version": "1.0.0", "status": "UNBOUND",
              "registeredAt": "2026-03-15T10:00:00", "lastHeartbeatAt": "2026-03-15T10:00:00"},
            None,  # heartbeat
            None,  # heartbeat
        ]
        
        # 获取指令响应
        mock_client.get.return_value = [
            {"id": "cmd-001", "instanceId": "test-001", "type": "UPDATE_CONFIG", 
             "payload": "{}", "status": "PENDING", "createdAt": "2026-03-15T10:00:00", "completedAt": None}
        ]
        
        MockClient.return_value = mock_client
        
        service = InstanceService(config, on_command)
        service.start()
        
        # 等待获取指令
        import time
        time.sleep(2)
        
        service.stop()
        
        assert len(commands_received) >= 1
        assert commands_received[0].type == "UPDATE_CONFIG"
```

**Step 2: 运行集成测试**

Run: `python -m pytest tests/client/test_integration.py -v`
Expected: PASS

**Step 3: Commit**

---

**Plan complete!**
