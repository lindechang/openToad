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
