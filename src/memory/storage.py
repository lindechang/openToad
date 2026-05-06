import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import contextmanager

from .types import MemoryItem, MemoryArchive, Identity, MemoryCategory

try:
    from ..crypto.cipher import CryptoManager
except ImportError:
    CryptoManager = None


class MemoryStorage:
    def __init__(self, db_path: Optional[str] = None, crypto: Optional["CryptoManager"] = None, user_id: Optional[str] = None, memory_id: Optional[str] = None):
        # Use current directory instead of home directory to avoid permission issues
        current_dir = Path(".")
        
        if db_path is None:
            if user_id:
                if memory_id:
                    self.db_path = current_dir / f"memory_{user_id}_{memory_id}.db"
                else:
                    user_mem = current_dir / f"memory_{user_id}.db"
                    if user_mem.exists():
                        self.db_path = user_mem
                    else:
                        self.db_path = current_dir / "memory.db"
            else:
                self.db_path = current_dir / "memory.db"
        else:
            self.db_path = Path(db_path)
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._crypto = crypto
        self._encrypted = crypto is not None
        self._plain_path = self.db_path.with_suffix(self.db_path.suffix + ".plain")
        self._handle_encrypted_db()
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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS llm_configs (
                    id TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    api_key TEXT NOT NULL,
                    model TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_meta (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    memory_id TEXT NOT NULL UNIQUE,
                    name TEXT DEFAULT '',
                    description TEXT DEFAULT '',
                    bound_user_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_synced_at TEXT
                )
            """)
            conn.execute("""
                INSERT OR IGNORE INTO memory_meta (id, memory_id, name, description, bound_user_id, created_at, updated_at, last_synced_at)
                VALUES (1, ?, '', '', NULL, datetime('now'), datetime('now'), NULL)
            """, (str(uuid.uuid4()),))
            conn.commit()

    def _handle_encrypted_db(self):
        if not self._encrypted:
            return
        if self.db_path.exists() and self.db_path.stat().st_size > 0:
            self._crypto.decrypt_file(str(self.db_path), str(self._plain_path))
        elif self._plain_path.exists():
            pass
        else:
            self._plain_path.touch()

    def _encrypt_and_save(self):
        if not self._encrypted:
            return
        self._crypto.encrypt_file(str(self._plain_path), str(self.db_path))

    @contextmanager
    def _get_conn(self):
        path = str(self._plain_path if self._encrypted else self.db_path)
        conn = sqlite3.connect(path)
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
        self._encrypt_and_save()

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
        self._encrypt_and_save()
    
    def save_llm_config(self, config_id: str, provider: str, api_key: str, model: str) -> None:
        now = datetime.now().isoformat()
        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO llm_configs (id, provider, api_key, model, created_at, updated_at)
                VALUES (?, ?, ?, ?, COALESCE((SELECT created_at FROM llm_configs WHERE id = ?), ?), ?)
            """, (config_id, provider, api_key, model, config_id, now, now))
            conn.commit()
        self._encrypt_and_save()
    
    def get_llm_configs(self) -> list:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM llm_configs ORDER BY updated_at DESC").fetchall()
            return [
                {
                    "id": row["id"],
                    "provider": row["provider"],
                    "api_key": row["api_key"],
                    "model": row["model"]
                }
                for row in rows
            ]
    
    def delete_llm_config(self, config_id: str) -> None:
        with self._get_conn() as conn:
            conn.execute("DELETE FROM llm_configs WHERE id = ?", (config_id,))
            conn.commit()
        self._encrypt_and_save()
    
    def get_memory_info(self) -> Dict[str, Any]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM memory_meta WHERE id = 1").fetchone()
            if row:
                return {
                    "memory_id": row["memory_id"],
                    "name": row["name"] or "未命名记忆体",
                    "description": row["description"] or "",
                    "bound_user_id": row["bound_user_id"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "last_synced_at": row["last_synced_at"]
                }
            return {}
    
    def update_memory_info(self, name: str = None, description: str = None, bound_user_id: str = None) -> None:
        with self._get_conn() as conn:
            updates = []
            params = []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if bound_user_id is not None:
                updates.append("bound_user_id = ?")
                params.append(bound_user_id)
            updates.append("updated_at = datetime('now')")
            
            if updates:
                conn.execute(f"UPDATE memory_meta SET {', '.join(updates)} WHERE id = 1", params)
                conn.commit()
                self._encrypt_and_save()
    
    def bind_to_user(self, user_id: str) -> None:
        self.update_memory_info(bound_user_id=user_id)
    
    def unbind(self) -> None:
        self.update_memory_info(bound_user_id=None)
    
    @staticmethod
    def list_user_memories(user_id: str, crypto: "CryptoManager" = None, include_unbound: bool = True) -> list:
        home = Path.home()
        memories_dir = home / ".opentoad"
        memories = []
        
        for f in memories_dir.glob(f"memory_{user_id}*.db"):
            try:
                if f.stem == f"memory_{user_id}":
                    memory_id = None
                    name = "默认记忆体"
                    try:
                        temp_storage = MemoryStorage(db_path=str(f), crypto=crypto)
                        info = temp_storage.get_memory_info()
                        if info.get("name"):
                            name = info.get("name")
                        memory_id = info.get("memory_id")
                    except Exception:
                        pass
                else:
                    parts = f.stem.split("_", 2)
                    if len(parts) >= 3:
                        memory_id = parts[2]
                    else:
                        memory_id = None
                    name = "未命名"
                    try:
                        temp_storage = MemoryStorage(db_path=str(f), crypto=crypto)
                        info = temp_storage.get_memory_info()
                        if info.get("name"):
                            name = info.get("name")
                    except Exception:
                        pass
                
                memories.append({
                    "memory_id": memory_id,
                    "path": str(f),
                    "name": name,
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                    "bound_user_id": user_id,
                    "is_bound": True
                })
            except Exception:
                pass
        
        if include_unbound:
            shared_mem = memories_dir / "memory.db"
            if shared_mem.exists():
                try:
                    memory_id = None
                    name = "默认记忆体"
                    bound_user_id = None
                    try:
                        temp_storage = MemoryStorage(db_path=str(shared_mem), crypto=crypto)
                        info = temp_storage.get_memory_info()
                        if info.get("name"):
                            name = info.get("name")
                        memory_id = info.get("memory_id")
                        bound_user_id = info.get("bound_user_id")
                    except Exception:
                        pass
                    
                    memories.append({
                        "memory_id": memory_id,
                        "path": str(shared_mem),
                        "name": name,
                        "size": shared_mem.stat().st_size,
                        "modified": datetime.fromtimestamp(shared_mem.stat().st_mtime).isoformat(),
                        "is_shared": True,
                        "bound_user_id": bound_user_id,
                        "is_bound": bound_user_id is not None
                    })
                except Exception:
                    pass
        
        memories.sort(key=lambda x: x["modified"], reverse=True)
        return memories
    
    @staticmethod
    def create_memory(user_id: str, crypto: "CryptoManager" = None, name: str = None, bind_immediately: bool = True) -> "MemoryStorage":
        memory_id = str(uuid.uuid4())
        storage = MemoryStorage(user_id=user_id, memory_id=memory_id, crypto=crypto)
        if name:
            storage.update_memory_info(name=name)
        if bind_immediately:
            storage.bind_to_user(user_id)
        return storage
    
    @staticmethod
    def create_unbound_memory(name: str = "新记忆体") -> "MemoryStorage":
        import shutil
        home = Path.home()
        memories_dir = home / ".opentoad"
        memory_db = memories_dir / "memory.db"
        
        if memory_db.exists():
            memory_id = str(uuid.uuid4())
            new_path = memories_dir / f"memory_local_{memory_id}.db"
            shutil.move(str(memory_db), str(new_path))
            storage = MemoryStorage(db_path=str(new_path), crypto=None, user_id=None, memory_id=memory_id)
        else:
            storage = MemoryStorage(crypto=None, user_id=None, memory_id=None)
        
        storage.update_memory_info(name=name, bound_user_id=None)
        return storage
    
    @staticmethod
    def delete_memory(user_id: str, memory_id: str = None) -> bool:
        home = Path.home()
        if memory_id:
            db_path = home / ".opentoad" / f"memory_{user_id}_{memory_id}.db"
        else:
            db_path = home / ".opentoad" / f"memory_{user_id}.db"
        
        plain_path = db_path.with_suffix('.db.plain')
        
        if db_path.exists():
            db_path.unlink()
        if plain_path.exists():
            plain_path.unlink()
        return True
    
    @staticmethod
    def list_all_users() -> list:
        home = Path.home()
        memories_dir = home / ".opentoad"
        users = set()
        
        for f in memories_dir.glob("memory_*.db"):
            stem = f.stem
            if "_" in stem:
                parts = stem.split("_", 2)
                if len(parts) >= 2 and parts[1].isdigit():
                    users.add(parts[1])
        
        return list(users)
