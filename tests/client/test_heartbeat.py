import pytest
import time
import threading
from unittest.mock import Mock, patch
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from client.config import ClientConfig
from client.heartbeat import HeartbeatService


class TestHeartbeatService:
    def test_start_sends_heartbeat(self):
        config = ClientConfig(
            server_url="http://localhost:8080",
            instance_id="test-instance-id",
            heartbeat_interval=1
        )
        
        with patch('client.heartbeat.HttpClient') as MockHttpClient:
            mock_client = Mock()
            MockHttpClient.return_value = mock_client
            
            service = HeartbeatService(config)
            service.start()
            
            time.sleep(0.5)
            
            mock_client.post.assert_called_once_with(
                "/instance/heartbeat",
                {"instanceId": "test-instance-id"}
            )
            
            service.stop()

    def test_stop_stops_thread(self):
        config = ClientConfig(
            server_url="http://localhost:8080",
            instance_id="test-instance-id",
            heartbeat_interval=1
        )
        
        service = HeartbeatService(config)
        service.start()
        service.stop()
        
        assert service._running is False
