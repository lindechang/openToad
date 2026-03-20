import pytest
from datetime import datetime
from src.memory.types import MemoryItem, MemoryCategory, Identity, MemoryArchive


def test_memory_item_creation():
    item = MemoryItem(content="Test memory")
    assert item.id is not None
    assert item.content == "Test memory"
    assert item.category == MemoryCategory.CONTEXT
    assert item.weight == 0.5
    assert item.is_long_term is False


def test_memory_category_enum():
    assert MemoryCategory.IDENTITY.value == "identity"
    assert MemoryCategory.PREFERENCE.value == "preference"


def test_identity_defaults():
    identity = Identity()
    assert identity.name == ""
    assert identity.principles == []
    assert identity.discovered_traits == []


def test_memory_archive():
    archive = MemoryArchive(name="Test Project", archive_type="project")
    assert archive.id is not None
    assert archive.name == "Test Project"
    assert archive.items == []
