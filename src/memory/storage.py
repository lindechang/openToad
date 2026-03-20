import json
import sqlite3
from datetime import datetime
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
