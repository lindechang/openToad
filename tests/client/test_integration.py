import pytest
import time
import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.client.service import InstanceService
from src.client.config import ClientConfig


def test_full_flow():
    config = ClientConfig()
    config.server_url = "http://localhost:8080"
    config.heartbeat_interval = 1
    config.command_poll_interval = 1
    
    commands_received = []
    
    def on_command(cmd):
        commands_received.append(cmd)
    
    with patch('src.client.instance.HttpClient') as MockInstanceClient, \
         patch('src.client.heartbeat.HttpClient') as MockHeartbeatClient, \
         patch('src.client.commander.HttpClient') as MockCommanderClient:
        mock_client = Mock()
        
        mock_client.post.side_effect = [
            {"id": "test-001", "version": "1.0.0", "status": "BOUND",
              "registeredAt": "2026-03-15T10:00:00", "lastHeartbeatAt": "2026-03-15T10:00:00",
              "boundAt": "2026-03-15T10:00:00"},
            None,
            None,
        ]
        
        mock_client.get.return_value = [
            {"id": "cmd-001", "instanceId": "test-001", "type": "UPDATE_CONFIG", 
             "payload": "{}", "status": "PENDING", "createdAt": "2026-03-15T10:00:00", "completedAt": None}
        ]
        
        MockInstanceClient.return_value = mock_client
        MockHeartbeatClient.return_value = mock_client
        MockCommanderClient.return_value = mock_client
        
        service = InstanceService(config, on_command)
        service.start()
        
        time.sleep(2)
        
        service.stop()
        
        assert len(commands_received) >= 1
        assert commands_received[0].type == "UPDATE_CONFIG"


def test_full_flow_with_command_completion():
    config = ClientConfig()
    config.server_url = "http://localhost:8080"
    config.heartbeat_interval = 1
    config.command_poll_interval = 1
    
    commands_received = []
    
    def on_command(cmd):
        commands_received.append(cmd)
        if cmd.status == "PENDING":
            service.commander_service.complete_command(cmd.id)
    
    with patch('src.client.instance.HttpClient') as MockInstanceClient, \
         patch('src.client.heartbeat.HttpClient') as MockHeartbeatClient, \
         patch('src.client.commander.HttpClient') as MockCommanderClient:
        mock_client = Mock()
        
        mock_client.post.side_effect = [
            {"id": "test-002", "version": "1.0.0", "status": "BOUND",
              "registeredAt": "2026-03-15T10:00:00", "lastHeartbeatAt": "2026-03-15T10:00:00",
              "boundAt": "2026-03-15T10:00:00"},
            None,
            None,
        ]
        
        mock_client.get.return_value = [
            {"id": "cmd-002", "instanceId": "test-002", "type": "RESTART", 
             "payload": "{}", "status": "PENDING", "createdAt": "2026-03-15T10:00:00", "completedAt": None}
        ]
        
        MockInstanceClient.return_value = mock_client
        MockHeartbeatClient.return_value = mock_client
        MockCommanderClient.return_value = mock_client
        
        service = InstanceService(config, on_command)
        service.start()
        
        time.sleep(2)
        
        service.stop()
        
        assert len(commands_received) >= 1
        assert commands_received[0].type == "RESTART"
        assert mock_client.post.call_count >= 1
