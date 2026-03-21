import asyncio
import logging
from typing import Optional, Dict
from .config import GatewayConfig
from .protocol import MessageType, WSMessage, create_error

logger = logging.getLogger(__name__)


class GatewayService:
    def __init__(
        self,
        config: Optional[GatewayConfig] = None,
        on_message: Optional[callable] = None
    ):
        self.config = config or GatewayConfig()
        self.on_message = on_message
        self._server = None
        self._running = False

    async def handle_message(self, instance_id: str, content: str) -> str:
        if self.on_message:
            return await self.on_message(instance_id, content)
        
        async def default_handler(instance_id: str, content: str) -> str:
            return "Gateway is running. Configure an AI handler to enable chat."
        
        return await default_handler(instance_id, content)

    async def start_async(self):
        from .server import GatewayServer
        
        async def wrapped_handler(instance_id: str, content: str) -> str:
            result = await self.handle_message(instance_id, content)
            return result

        self._server = GatewayServer(
            config=self.config,
            on_message=wrapped_handler
        )
        self._running = True
        logger.info(f"Gateway service starting on {self.config.host}:{self.config.port}")
        await self._server.start_async()

    def start(self, background: bool = False):
        from .server import GatewayServer
        
        async def wrapped_handler(instance_id: str, content: str) -> str:
            return await self.handle_message(instance_id, content)

        self._server = GatewayServer(
            config=self.config,
            on_message=wrapped_handler
        )
        self._server.start(background=background)
        self._running = True

    def stop(self):
        if self._server:
            self._server.stop()
        self._running = False
        logger.info("Gateway service stopped")

    @property
    def running(self) -> bool:
        return self._running
