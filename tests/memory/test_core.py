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
