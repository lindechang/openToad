import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import sys
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from client.config import ClientConfig
from client.commander import CommanderService, Command


class TestCommanderService:
    def test_fetch_commands(self):
        config = ClientConfig(
            server_url="http://localhost:8080",
            instance_id="test-instance-id",
            command_poll_interval=5
        )

        mock_response = [
            {
                "id": "cmd-1",
                "instanceId": "test-instance-id",
                "type": "ACTION",
                "payload": '{"action": "test"}',
                "status": "PENDING",
                "createdAt": "2026-01-01T00:00:00Z",
                "completedAt": None
            }
        ]

        with patch('client.commander.HttpClient') as MockHttpClient:
            mock_client = Mock()
            mock_client.get.return_value = mock_response
            MockHttpClient.return_value = mock_client

            service = CommanderService(config)
            commands = service.fetch_commands()

            assert len(commands) == 1
            assert commands[0].id == "cmd-1"
            assert commands[0].type == "ACTION"
            assert commands[0].status == "PENDING"

            mock_client.get.assert_called_once_with(
                "/instance/commands",
                {"instanceId": "test-instance-id"}
            )

    def test_fetch_commands_empty(self):
        config = ClientConfig(
            server_url="http://localhost:8080",
            instance_id="test-instance-id",
            command_poll_interval=5
        )

        with patch('client.commander.HttpClient') as MockHttpClient:
            mock_client = Mock()
            mock_client.get.return_value = None
            MockHttpClient.return_value = mock_client

            service = CommanderService(config)
            commands = service.fetch_commands()

            assert commands == []
