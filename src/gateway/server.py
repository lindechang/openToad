import asyncio
import json
import logging
from typing import Dict, Optional, Callable, Awaitable

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from .config import GatewayConfig
from .protocol import (
    MessageType, WSMessage, create_auth_response, 
    create_response, create_pong, create_error
)

logger = logging.getLogger(__name__)


class GatewayServer:
    def __init__(
        self, 
        config: Optional[GatewayConfig] = None,
        on_message: Optional[Callable[[str, str], Awaitable[str]]] = None
    ):
        self.config = config or GatewayConfig()
        self.on_message = on_message
        self.clients: Dict[str, WebSocket] = {}
        self.authenticated: Dict[str, bool] = {}
        self.app = FastAPI()
        self._setup_routes()
        self._running = False

    def _setup_routes(self):
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            instance_id: Optional[str] = None

            try:
                while True:
                    data = await websocket.receive_text()
                    try:
                        msg = WSMessage.from_dict(json.loads(data))
                    except (json.JSONDecodeError, KeyError):
                        await self._send(websocket, create_error("INVALID_FORMAT", "Invalid JSON format"))
                        continue

                    if msg.type == MessageType.AUTH.value:
                        instance_id = await self._handle_auth(websocket, msg)
                    elif msg.type == MessageType.MESSAGE.value:
                        if not self._is_authenticated(instance_id):
                            await self._send(websocket, create_error("NOT_AUTHENTICATED", "Please authenticate first"))
                            continue
                        await self._handle_message(websocket, instance_id, msg)
                    elif msg.type == MessageType.PING.value:
                        await self._send(websocket, create_pong())
                    else:
                        await self._send(websocket, create_error("UNKNOWN_TYPE", f"Unknown message type: {msg.type}"))

            except WebSocketDisconnect:
                logger.info(f"Client disconnected: {instance_id}")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            finally:
                if instance_id:
                    self._remove_client(instance_id)

    async def _handle_auth(self, websocket: WebSocket, msg: WSMessage) -> Optional[str]:
        instance_id = msg.payload.get("instance_id", "")
        
        if not instance_id:
            await self._send(websocket, create_auth_response(False, error="Missing instance_id"))
            return None

        existing = self.clients.get(instance_id)
        if existing:
            try:
                await existing.close()
            except Exception:
                pass

        self.clients[instance_id] = websocket
        self.authenticated[instance_id] = True
        logger.info(f"Client authenticated: {instance_id}")
        await self._send(websocket, create_auth_response(True, instance_id=instance_id))
        return instance_id

    async def _handle_message(self, websocket: WebSocket, instance_id: Optional[str], msg: WSMessage):
        if not instance_id:
            await self._send(websocket, create_error("INTERNAL_ERROR", "Missing instance_id"))
            return
        content = msg.payload.get("content", "")
        stream = msg.payload.get("stream", True)

        if self.on_message:
            try:
                result = self.on_message(instance_id, content)
                if stream:
                    if hasattr(result, '__anext__'):
                        async for chunk in result:
                            await self._send(websocket, create_response(chunk, done=False))
                    else:
                        for chunk in result:
                            await self._send(websocket, create_response(chunk, done=False))
                await self._send(websocket, create_response("", done=True))
            except Exception as e:
                logger.error(f"Message handling error: {e}")
                await self._send(websocket, create_error("PROCESSING_ERROR", str(e)))
        else:
            await self._send(websocket, create_response("Gateway is running but no message handler configured.", done=True))
            await self._send(websocket, create_response("", done=True))

    def _is_authenticated(self, instance_id: Optional[str]) -> bool:
        if not instance_id:
            return False
        return self.authenticated.get(instance_id, False)

    def _remove_client(self, instance_id: str):
        self.clients.pop(instance_id, None)
        self.authenticated.pop(instance_id, None)
        logger.info(f"Client removed: {instance_id}")

    async def _send(self, websocket: WebSocket, msg: WSMessage):
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_text(json.dumps(msg.to_dict()))
            except Exception as e:
                logger.error(f"Failed to send message: {e}")

    def start(self, background: bool = False):
        config = uvicorn.Config(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        if background:
            import threading
            thread = threading.Thread(target=server.run, daemon=True)
            thread.start()
            self._running = True
            logger.info(f"Gateway started on {self.config.host}:{self.config.port}")
        else:
            self._running = True
            logger.info(f"Starting Gateway on {self.config.host}:{self.config.port}")
            server.run()

    async def start_async(self):
        config = uvicorn.Config(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        self._running = True
        logger.info(f"Starting Gateway on {self.config.host}:{self.config.port}")
        await server.serve()

    def stop(self):
        self._running = False
        for instance_id in list(self.clients.keys()):
            self._remove_client(instance_id)
        logger.info("Gateway stopped")


def create_gateway(
    host: str = "0.0.0.0",
    port: int = 18989,
    on_message: Optional[Callable[[str, str], Awaitable[str]]] = None
) -> GatewayServer:
    config = GatewayConfig(host=host, port=port)
    return GatewayServer(config=config, on_message=on_message)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    gateway = create_gateway()
    gateway.start()
