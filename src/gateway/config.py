from dataclasses import dataclass


@dataclass
class GatewayConfig:
    host: str = "0.0.0.0"
    port: int = 18989
    heartbeat_timeout: int = 60
    max_message_length: int = 1024 * 1024
