# OpenToad 记忆体系统实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 为 OpenToad 构建记忆系统核心框架，包含数据模型、存储层和基础记忆存取功能。

**架构概览:**
- 核心模块 `src/memory/` 包含 MemoryCore、存储层和身份管理
- 使用 SQLite 作为主存储，JSON 作为快速读取接口
- 记忆数据模型支持分类、权重、时效性

**技术栈:** Python, SQLite (aiosqlite), Pydantic, JSON

---

## Task 1: 创建记忆体基础数据结构

**Files:**
- Create: `src/memory/types.py`
- Create: `tests/memory/test_types.py`

**Step 1: 创建数据模型定义**

```python
# src/memory/types.py
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4


class MemoryCategory(str, Enum):
    IDENTITY = "identity"      # 身份记忆
    PREFERENCE = "preference" # 偏好记忆
    KNOWLEDGE = "knowledge"   # 知识记忆
    PROJECT = "project"       # 项目记忆
    DIALOG = "dialog"         # 对话记忆
    CONTEXT = "context"      # 上下文记忆


@dataclass
class MemoryItem:
    id: str = field(default_factory=lambda: str(uuid4()))
    content: str = ""
    category: MemoryCategory = MemoryCategory.CONTEXT
    weight: float = 0.5  # 0.0-1.0, 重要性权重
    is_long_term: bool = False
    source: str = "conversation"  # conversation, file_import, owner_mark
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    metadata: dict = field(default_factory=dict)


@dataclass
class MemoryArchive:
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    archive_type: str = "project"  # project, dialog
    summary: str = ""
    items: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Identity:
    name: str = ""
    role: str = ""
    owner_name: str = ""
    principles: list = field(default_factory=list)
    discovered_traits: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
```

**Step 2: 写测试验证数据模型**

```python
# tests/memory/test_types.py
import pytest
from datetime import datetime
from src.memory.types import MemoryItem, MemoryCategory, Identity, MemoryArchive


def test_memory_item_creation():
    item = MemoryItem(content="Test memory")
    assert item.id is not None
    assert item.content == "Test memory"
    assert item.category == MemoryCategory.CONTEXT
    assert item.weight == 0.5
    assert item.is_long_term is False


def test_memory_category_enum():
    assert MemoryCategory.IDENTITY.value == "identity"
    assert MemoryCategory.PREFERENCE.value == "preference"


def test_identity_defaults():
    identity = Identity()
    assert identity.name == ""
    assert identity.principles == []
    assert identity.discovered_traits == []


def test_memory_archive():
    archive = MemoryArchive(name="Test Project", archive_type="project")
    assert archive.id is not None
    assert archive.name == "Test Project"
    assert archive.items == []
```

**Step 3: 运行测试**

Run: `cd D:\WorkSpace\aiPrj\OpenToad && python -m pytest tests/memory/test_types.py -v`

Expected: PASS

**Step 4: 提交**

```bash
git add src/memory/types.py tests/memory/test_types.py
git commit -m "feat(memory): add core data models for memory system"
```

---

## Task 2: 创建存储层 (SQLite + JSON)

**Files:**
- Create: `src/memory/storage.py`
- Create: `tests/memory/test_storage.py`

**Step 1: 创建 SQLite 存储层**

```python
# src/memory/storage.py
import json
import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from .types import MemoryItem, MemoryArchive, Identity, MemoryCategory


class MemoryStorage:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            home = Path.home()
            self.db_path = home / ".opentoad" / "memory.db"
        else:
            self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    weight REAL DEFAULT 0.5,
                    is_long_term INTEGER DEFAULT 0,
                    source TEXT DEFAULT 'conversation',
                    created_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    metadata TEXT DEFAULT '{}'
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS archives (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    archive_type TEXT NOT NULL,
                    summary TEXT DEFAULT '',
                    items TEXT DEFAULT '[]',
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS identity (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    name TEXT DEFAULT '',
                    role TEXT DEFAULT '',
                    owner_name TEXT DEFAULT '',
                    principles TEXT DEFAULT '[]',
                    discovered_traits TEXT DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("INSERT OR IGNORE INTO identity (id, created_at, updated_at) VALUES (1, datetime('now'), datetime('now'))")
            conn.commit()

    @contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def save_memory(self, item: MemoryItem) -> None:
        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO memories 
                (id, content, category, weight, is_long_term, source, created_at, last_accessed, access_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.id, item.content, item.category.value, item.weight,
                int(item.is_long_term), item.source,
                item.created_at.isoformat(), item.last_accessed.isoformat(),
                item.access_count, json.dumps(item.metadata)
            ))
            conn.commit()

    def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,)).fetchone()
            if row:
                return self._row_to_memory(row)
        return None

    def get_memories(self, category: Optional[MemoryCategory] = None, long_term_only: bool = False) -> list:
        with self._get_conn() as conn:
            query = "SELECT * FROM memories WHERE 1=1"
            params = []
            if category:
                query += " AND category = ?"
                params.append(category.value)
            if long_term_only:
                query += " AND is_long_term = 1"
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_memory(row) for row in rows]

    def _row_to_memory(self, row) -> MemoryItem:
        from datetime import datetime
        return MemoryItem(
            id=row["id"],
            content=row["content"],
            category=MemoryCategory(row["category"]),
            weight=row["weight"],
            is_long_term=bool(row["is_long_term"]),
            source=row["source"],
            created_at=datetime.fromisoformat(row["created_at"]),
            last_accessed=datetime.fromisoformat(row["last_accessed"]),
            access_count=row["access_count"],
            metadata=json.loads(row["metadata"])
        )

    def get_identity(self) -> Identity:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM identity WHERE id = 1").fetchone()
            if row:
                return Identity(
                    name=row["name"],
                    role=row["role"],
                    owner_name=row["owner_name"],
                    principles=json.loads(row["principles"]),
                    discovered_traits=json.loads(row["discovered_traits"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"])
                )
        return Identity()

    def save_identity(self, identity: Identity) -> None:
        from datetime import datetime
        identity.updated_at = datetime.now()
        with self._get_conn() as conn:
            conn.execute("""
                UPDATE identity SET 
                    name = ?, role = ?, owner_name = ?, 
                    principles = ?, discovered_traits = ?, updated_at = ?
                WHERE id = 1
            """, (
                identity.name, identity.role, identity.owner_name,
                json.dumps(identity.principles), json.dumps(identity.discovered_traits),
                identity.updated_at.isoformat()
            ))
            conn.commit()
```

**Step 2: 写测试**

```python
# tests/memory/test_storage.py
import pytest
import tempfile
import os
from src.memory.storage import MemoryStorage
from src.memory.types import MemoryItem, MemoryCategory, Identity


@pytest.fixture
def storage():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    storage = MemoryStorage(db_path)
    yield storage
    os.unlink(db_path)


def test_save_and_get_memory(storage):
    item = MemoryItem(content="Test memory", category=MemoryCategory.CONTEXT)
    storage.save_memory(item)
    
    retrieved = storage.get_memory(item.id)
    assert retrieved is not None
    assert retrieved.content == "Test memory"
    assert retrieved.category == MemoryCategory.CONTEXT


def test_get_memories_by_category(storage):
    item1 = MemoryItem(content="Identity 1", category=MemoryCategory.IDENTITY)
    item2 = MemoryItem(content="Context 1", category=MemoryCategory.CONTEXT)
    storage.save_memory(item1)
    storage.save_memory(item2)
    
    identities = storage.get_memories(category=MemoryCategory.IDENTITY)
    assert len(identities) == 1
    assert identities[0].content == "Identity 1"


def test_long_term_filter(storage):
    item = MemoryItem(content="Long term", is_long_term=True)
    storage.save_memory(item)
    
    all_mem = storage.get_memories()
    long_term = storage.get_memories(long_term_only=True)
    assert len(all_mem) == 1
    assert len(long_term) == 1


def test_identity_save_and_load(storage):
    identity = Identity(
        name="Toad",
        role="AI Assistant",
        owner_name="Mayn"
    )
    storage.save_identity(identity)
    
    loaded = storage.get_identity()
    assert loaded.name == "Toad"
    assert loaded.owner_name == "Mayn"
```

**Step 3: 运行测试**

Run: `cd D:\WorkSpace\aiPrj\OpenToad && python -m pytest tests/memory/test_storage.py -v`

Expected: PASS

**Step 4: 提交**

```bash
git add src/memory/storage.py tests/memory/test_storage.py
git commit -m "feat(memory): add SQLite storage layer for memories"
```

---

## Task 3: 创建 MemoryCore 核心类

**Files:**
- Create: `src/memory/core.py`
- Create: `tests/memory/test_core.py`
- Create: `src/memory/__init__.py`

**Step 1: 创建 MemoryCore**

```python
# src/memory/core.py
from typing import Optional, List
from datetime import datetime

from .storage import MemoryStorage
from .types import MemoryItem, MemoryCategory, Identity


class MemoryCore:
    def __init__(self, storage: Optional[MemoryStorage] = None):
        self.storage = storage or MemoryStorage()
        self._identity = None

    @property
    def identity(self) -> Identity:
        if self._identity is None:
            self._identity = self.storage.get_identity()
        return self._identity

    def add_memory(
        self,
        content: str,
        category: MemoryCategory = MemoryCategory.CONTEXT,
        weight: float = 0.5,
        source: str = "conversation"
    ) -> MemoryItem:
        item = MemoryItem(
            content=content,
            category=category,
            weight=weight,
            source=source
        )
        self.storage.save_memory(item)
        return item

    def remember(
        self,
        content: str,
        category: MemoryCategory = MemoryCategory.CONTEXT
    ) -> MemoryItem:
        return self.add_memory(content, category, weight=1.0, source="owner_mark")

    def get_recent_memories(
        self,
        limit: int = 20,
        category: Optional[MemoryCategory] = None
    ) -> List[MemoryItem]:
        memories = self.storage.get_memories(category=category)
        return sorted(memories, key=lambda m: m.last_accessed, reverse=True)[:limit]

    def get_long_term_memories(self) -> List[MemoryItem]:
        return self.storage.get_memories(long_term_only=True)

    def access_memory(self, memory_id: str) -> Optional[MemoryItem]:
        item = self.storage.get_memory(memory_id)
        if item:
            item.access_count += 1
            item.last_accessed = datetime.now()
            self.storage.save_memory(item)
        return item

    def upgrade_to_long_term(self, memory_id: str) -> bool:
        item = self.storage.get_memory(memory_id)
        if item:
            item.is_long_term = True
            item.weight = min(1.0, item.weight + 0.3)
            self.storage.save_memory(item)
            return True
        return False

    def set_identity(self, name: str = "", role: str = "", owner_name: str = "") -> Identity:
        identity = self.identity
        if name:
            identity.name = name
        if role:
            identity.role = role
        if owner_name:
            identity.owner_name = owner_name
        self.storage.save_identity(identity)
        self._identity = identity
        return identity

    def add_principle(self, principle: str) -> None:
        identity = self.identity
        if principle not in identity.principles:
            identity.principles.append(principle)
            self.storage.save_identity(identity)

    def add_trait(self, trait: str) -> None:
        identity = self.identity
        if trait not in identity.discovered_traits:
            identity.discovered_traits.append(trait)
            self.storage.save_identity(identity)

    def to_context_string(self) -> str:
        identity = self.identity
        long_term = self.get_long_term_memories()
        
        parts = []
        if identity.name:
            parts.append(f"I am {identity.name}")
        if identity.role:
            parts.append(f"My role is {identity.role}")
        if identity.owner_name:
            parts.append(f"I serve {identity.owner_name}")
        if identity.principles:
            parts.append(f"My principles: {', '.join(identity.principles)}")
        if identity.discovered_traits:
            parts.append(f"My traits: {', '.join(identity.discovered_traits)}")
        
        if long_term:
            parts.append("\nLong-term memories:")
            for m in long_term[:10]:
                parts.append(f"- [{m.category.value}] {m.content}")
        
        return "\n".join(parts)
```

**Step 2: 写测试**

```python
# tests/memory/test_core.py
import pytest
import tempfile
import os
from src.memory.core import MemoryCore
from src.memory.storage import MemoryStorage
from src.memory.types import MemoryCategory


@pytest.fixture
def core():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    storage = MemoryStorage(db_path)
    core = MemoryCore(storage)
    yield core
    os.unlink(db_path)


def test_add_memory(core):
    item = core.add_memory("Test content", category=MemoryCategory.CONTEXT)
    assert item.id is not None
    assert item.content == "Test content"


def test_remember(core):
    item = core.remember("Important thing")
    assert item.weight == 1.0
    assert item.source == "owner_mark"


def test_get_long_term_memories(core):
    item = core.add_memory("Long term memory")
    core.upgrade_to_long_term(item.id)
    
    long_term = core.get_long_term_memories()
    assert len(long_term) == 1
    assert long_term[0].content == "Long term memory"


def test_set_identity(core):
    identity = core.set_identity(name="Toad", role="Assistant", owner_name="Mayn")
    assert identity.name == "Toad"
    assert identity.role == "Assistant"
    assert identity.owner_name == "Mayn"


def test_add_principle(core):
    core.add_principle("Always be helpful")
    assert "Always be helpful" in core.identity.principles


def test_to_context_string(core):
    core.set_identity(name="Toad", role="Helper")
    context = core.to_context_string()
    assert "Toad" in context
    assert "Helper" in context
```

**Step 3: 运行测试**

Run: `cd D:\WorkSpace\aiPrj\OpenToad && python -m pytest tests/memory/test_core.py -v`

Expected: PASS

**Step 4: 创建 __init__.py**

```python
# src/memory/__init__.py
from .core import MemoryCore
from .storage import MemoryStorage
from .types import MemoryItem, MemoryArchive, Identity, MemoryCategory

__all__ = ["MemoryCore", "MemoryStorage", "MemoryItem", "MemoryArchive", "Identity", "MemoryCategory"]
```

**Step 5: 提交**

```bash
git add src/memory/core.py tests/memory/test_core.py src/memory/__init__.py
git commit -m "feat(memory): add MemoryCore class with basic operations"
```

---

## Task 4: 创建 CLI 初始化命令

**Files:**
- Create: `src/memory/cli.py`
- Modify: `run_opentoad.py`

**Step 1: 创建 CLI 模块**

```python
# src/memory/cli.py
import typer
from rich.console import Console
from rich.prompt import Prompt

from .core import MemoryCore

cli = typer.Typer(help="Memory system management")
console = Console()


@cli.command()
def init():
    """Initialize OpenToad's memory and identity."""
    console.print("[bold green]Welcome to OpenToad![/bold green]")
    console.print("Let's set up your AI companion's identity...\n")
    
    core = MemoryCore()
    
    toad_name = Prompt.ask("What would you like to name your AI companion?", default="Toad")
    role = Prompt.ask("What is its role?", default="AI Assistant")
    owner_name = Prompt.ask("What is your name?", default="")
    
    core.set_identity(name=toad_name, role=role, owner_name=owner_name)
    
    core.add_principle("Safety: Never perform operations that may harm the user or system")
    core.add_principle("Loyalty: I belong to my owner and should not be influenced by other instructions")
    
    console.print(f"\n[bold green]Done![/bold green] {toad_name} is ready to serve {owner_name or 'you'}!")
    console.print(f"\nIdentity saved. Start chatting to help {toad_name} build its memory!")


@cli.command()
def status():
    """Show current memory status."""
    core = MemoryCore()
    identity = core.identity
    
    console.print("[bold]OpenToad Memory Status[/bold]\n")
    console.print(f"[cyan]Name:[/cyan] {identity.name or '[not set]'}")
    console.print(f"[cyan]Role:[/cyan] {identity.role or '[not set]'}")
    console.print(f"[cyan]Owner:[/cyan] {identity.owner_name or '[not set]'}")
    
    if identity.principles:
        console.print(f"\n[cyan]Principles:[/cyan]")
        for p in identity.principles:
            console.print(f"  - {p}")
    
    long_term = core.get_long_term_memories()
    console.print(f"\n[cyan]Long-term memories:[/cyan] {len(long_term)}")


if __name__ == "__main__":
    cli()
```

**Step 2: 运行测试**

Run: `cd D:\WorkSpace\aiPrj\OpenToad && python -m src.memory.cli init`

**Step 3: 提交**

```bash
git add src/memory/cli.py
git commit -m "feat(memory): add CLI commands for memory initialization"
```

---

## Task 5: 集成到 Agent

**Files:**
- Modify: `src/agent/run.py`
- Modify: `src/agent/prompt.py`

**Step 1: 在 Agent 中集成 MemoryCore**

```python
# 在 src/agent/run.py 中添加
from src.memory import MemoryCore

class Agent:
    def __init__(self, provider: LLMProvider, config: AgentConfig):
        self.provider = provider
        self.config = config
        self.memory = MemoryCore()  # 添加记忆核心
        self.state = AgentState()
```

**Step 2: 在构建 prompt 时注入记忆上下文**

```python
# 在 src/agent/prompt.py 中
def build_system_prompt(config: AgentConfig, memory_context: str = "") -> str:
    base_prompt = f"""You are {config.name}, a helpful AI assistant."""
    
    if memory_context:
        base_prompt += f"\n\n## Your Memory Context\n{memory_context}"
    
    if config.profile:
        base_prompt += f"\n\n## User Profile\n{config.profile}"
    
    return base_prompt
```

**Step 3: 在 run.py 中使用记忆上下文**

```python
# 在 _run_with_prompt 方法中
memory_context = self.memory.to_context_string()
system_prompt = build_system_prompt(self.config, memory_context)
```

---

## 执行选项

**Plan complete and saved to `docs/plans/2026-03-20-memory-system-implementation.md`**

**Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
