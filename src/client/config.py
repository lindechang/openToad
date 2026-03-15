import json
import uuid
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

DEFAULT_CONFIG = {
    "server_url": "http://localhost:8080",
    "instance_id": None,
    "instance_version": "1.0.0",
    "heartbeat_interval": 30,
    "command_poll_interval": 5,
    "http_timeout": 10
}

CONFIG_FILE = "config.json"

@dataclass
class ClientConfig:
    server_url: str = "http://localhost:8080"
    instance_id: Optional[str] = None
    instance_version: str = "1.0.0"
    heartbeat_interval: int = 30
    command_poll_interval: int = 5
    http_timeout: int = 10

    def __post_init__(self):
        if self.instance_id is None:
            self.instance_id = str(uuid.uuid4())
        self._load_from_file()

    def _load_from_file(self):
        config_path = Path(CONFIG_FILE)
        if config_path.exists():
            with open(config_path, 'r') as f:
                data = json.load(f)
                for key, value in DEFAULT_CONFIG.items():
                    if key in data:
                        setattr(self, key, data[key])
                if self.instance_id is None:
                    self.instance_id = str(uuid.uuid4())

    def save(self):
        config_path = Path(CONFIG_FILE)
        data = asdict(self)
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)

    @property
    def api_base(self) -> str:
        return f"{self.server_url}/api/instance"
