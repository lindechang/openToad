import threading
import time
import logging
from typing import List, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
from src.client.http_client import HttpClient
from src.client.config import ClientConfig

logger = logging.getLogger(__name__)

@dataclass
class Command:
    id: str
    instance_id: str
    type: str
    payload: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

class CommanderService:
    def __init__(self, config: ClientConfig, on_command: Optional[Callable] = None):
        self.config = config
        self.http_client = HttpClient(config.api_base, config.http_timeout)
        self.on_command = on_command
        self._running = False
        self._thread: threading.Thread = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("Commander service started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Commander service stopped")

    def fetch_commands(self) -> List[Command]:
        params = {"instanceId": self.config.instance_id}
        data = self.http_client.get("/instance/commands", params)
        return [self._parse_command(c) for c in data] if data else []

    def complete_command(self, command_id: str):
        self.http_client.post("/instance/command/complete", {"commandId": command_id})
        logger.info(f"Command {command_id} marked as completed")

    def _run(self):
        while self._running:
            try:
                commands = self.fetch_commands()
                for cmd in commands:
                    if cmd.status == "PENDING" and self.on_command:
                        self.on_command(cmd)
            except Exception as e:
                logger.error(f"Failed to fetch commands: {e}")
            time.sleep(self.config.command_poll_interval)

    def _parse_command(self, data: dict) -> Command:
        return Command(
            id=data["id"],
            instance_id=data["instanceId"],
            type=data["type"],
            payload=data["payload"],
            status=data["status"],
            created_at=datetime.fromisoformat(data["createdAt"].replace('Z', '+00:00')),
            completed_at=datetime.fromisoformat(data["completedAt"].replace('Z', '+00:00')) if data.get("completedAt") else None
        )
