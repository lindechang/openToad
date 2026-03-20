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
