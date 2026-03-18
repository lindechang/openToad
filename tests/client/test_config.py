import pytest
import uuid
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from client.config import ClientConfig, DEFAULT_CONFIG


class TestClientConfig:
    def test_default_config_values(self):
        config = ClientConfig()
        
        assert config.server_url == "http://localhost:8080"
        assert config.instance_version == "1.0.0"
        assert config.heartbeat_interval == 30
        assert config.command_poll_interval == 5
        assert config.http_timeout == 10

    def test_auto_generate_instance_id(self):
        config = ClientConfig()
        
        assert config.instance_id is not None
        uuid.UUID(config.instance_id)

    def test_api_base_property(self):
        config = ClientConfig(server_url="http://localhost:8080")
        
        assert config.api_base == "http://localhost:8080/api"
