import pytest
import uuid
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from client.config import ClientConfig
from client.instance import InstanceManager, InstanceInfo


class TestInstanceManager:
    def test_register_instance(self):
        config = ClientConfig()
        manager = InstanceManager(config)
        
        assert manager.config == config
        assert manager._info is None
