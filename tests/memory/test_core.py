import pytest
import tempfile
import os
from unittest.mock import MagicMock, patch
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


class TestAuthIntegration:
    def test_no_auth_service_non_encrypted_storage(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        storage = MemoryStorage(db_path)
        core = MemoryCore(storage, auth_service=None)
        item = core.add_memory("Test")
        assert item.content == "Test"
        os.unlink(db_path)

    def test_auth_service_not_logged_in_encrypted_storage_raises(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        mock_crypto = MagicMock()
        storage = MemoryStorage(db_path, crypto=mock_crypto)
        mock_auth = MagicMock()
        mock_auth.is_logged_in = False
        core = MemoryCore(storage, auth_service=mock_auth)
        
        with pytest.raises(PermissionError, match="Authentication required"):
            core.add_memory("Test")
        
        os.unlink(db_path)

    def test_auth_service_logged_in_encrypted_storage_works(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        mock_crypto = MagicMock()
        storage = MemoryStorage(db_path, crypto=mock_crypto)
        mock_auth = MagicMock()
        mock_auth.is_logged_in = True
        core = MemoryCore(storage, auth_service=mock_auth)
        
        item = core.add_memory("Test")
        assert item.content == "Test"
        
        os.unlink(db_path)

    def test_get_identity_encrypted_not_logged_in_raises(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        mock_crypto = MagicMock()
        storage = MemoryStorage(db_path, crypto=mock_crypto)
        mock_auth = MagicMock()
        mock_auth.is_logged_in = False
        core = MemoryCore(storage, auth_service=mock_auth)
        
        with pytest.raises(PermissionError, match="Authentication required"):
            _ = core.identity
        
        os.unlink(db_path)
