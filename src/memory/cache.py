from collections import OrderedDict
from typing import Optional, List
from datetime import datetime

from .types import MemoryItem


class MemoryCache:
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._cache: OrderedDict[str, MemoryItem] = OrderedDict()
        self._hit_count = 0
        self._miss_count = 0
    
    def get(self, memory_id: str) -> Optional[MemoryItem]:
        if memory_id in self._cache:
            self._cache.move_to_end(memory_id)
            self._hit_count += 1
            return self._cache[memory_id]
        self._miss_count += 1
        return None
    
    def put(self, memory_id: str, item: MemoryItem):
        if memory_id in self._cache:
            self._cache.move_to_end(memory_id)
        self._cache[memory_id] = item
        if len(self._cache) > self.max_size:
            self._cache.popitem(last=False)
    
    def get_by_location(self, location: str) -> List[MemoryItem]:
        return [item for item in self._cache.values() 
                if item.location.startswith(location)]
    
    def get_hot_memories(self, limit: int = 10) -> List[MemoryItem]:
        return sorted(self._cache.values(), 
                     key=lambda x: x.access_count, 
                     reverse=True)[:limit]
    
    @property
    def hit_rate(self) -> float:
        total = self._hit_count + self._miss_count
        return self._hit_count / total if total > 0 else 0.0
    
    def remove(self, memory_id: str) -> None:
        self._cache.pop(memory_id, None)
