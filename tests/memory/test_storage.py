import pytest
import tempfile
import os
from src.memory.storage import MemoryStorage
from src.memory.types import MemoryItem, MemoryCategory, Identity
from src.crypto.cipher import CryptoManager


@pytest.fixture
def storage():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    storage = MemoryStorage(db_path)
    yield storage
    os.unlink(db_path)


@pytest.fixture
def encrypted_storage():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    crypto = CryptoManager(CryptoManager.generate_key())
    storage = MemoryStorage(db_path, crypto=crypto)
    yield storage, crypto, db_path
    if os.path.exists(db_path):
        os.unlink(db_path)
    plain_path = db_path + ".plain"
    if os.path.exists(plain_path):
        os.unlink(plain_path)


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


def test_encrypted_storage_save_and_get_memory(encrypted_storage):
    storage, crypto, db_path = encrypted_storage
    item = MemoryItem(content="Encrypted memory", category=MemoryCategory.CONTEXT)
    storage.save_memory(item)
    
    assert os.path.exists(db_path)
    assert os.path.getsize(db_path) > 0
    
    retrieved = storage.get_memory(item.id)
    assert retrieved is not None
    assert retrieved.content == "Encrypted memory"


def test_encrypted_storage_identity(encrypted_storage):
    storage, crypto, db_path = encrypted_storage
    identity = Identity(name="Toad", role="AI Assistant")
    storage.save_identity(identity)
    
    loaded = storage.get_identity()
    assert loaded.name == "Toad"


def test_encrypted_storage_backward_compatible(storage):
    assert not storage._encrypted
    item = MemoryItem(content="Plain memory", category=MemoryCategory.CONTEXT)
    storage.save_memory(item)
    retrieved = storage.get_memory(item.id)
    assert retrieved.content == "Plain memory"
