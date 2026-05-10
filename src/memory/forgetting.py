from datetime import datetime, timedelta
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .storage import MemoryStorage
    from .cache import MemoryCache


class MemoryForgettingManager:
    def __init__(
        self,
        storage: "MemoryStorage",
        cache: "MemoryCache",
        ttl_days: int = 7,
        normal_threshold: float = 2.0,
        storage_limit_percent: float = 0.8
    ):
        self.storage = storage
        self.cache = cache
        self.ttl_days = ttl_days
        self.normal_threshold = normal_threshold
        self.storage_limit_percent = storage_limit_percent
    
    def check_and_forget(self) -> List[str]:
        """检查并执行遗忘，返回被删除的记忆ID列表"""
        deleted = []
        
        deleted.extend(self._forget_expired_ttl())
        
        deleted.extend(self._forget_low_importance())
        
        self._forget_by_storage_pressure()
        
        return deleted
    
    def _forget_expired_ttl(self) -> List[str]:
        """遗忘超时的短期记忆"""
        cutoff = datetime.now() - timedelta(days=self.ttl_days)
        memories = self.storage.get_memories(long_term_only=False)
        
        deleted = []
        for mem in memories:
            if mem.last_accessed < cutoff and mem.importance_score < 5.0:
                self.storage.delete_memory(mem.id)
                self.cache.remove(mem.id)
                deleted.append(mem.id)
        return deleted
    
    def _forget_low_importance(self) -> List[str]:
        """遗忘低重要性的记忆"""
        memories = self.storage.get_memories(long_term_only=False)
        deleted = []
        for mem in memories:
            if mem.importance_score < self.normal_threshold:
                self.storage.delete_memory(mem.id)
                self.cache.remove(mem.id)
                deleted.append(mem.id)
        return deleted
    
    def _forget_by_storage_pressure(self):
        """存储压力过大时主动遗忘"""
        pass
