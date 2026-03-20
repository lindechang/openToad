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
