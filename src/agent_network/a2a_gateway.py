# src/agent_network/a2a_gateway.py
"""
A2A Gateway 服务
整合 Gateway Server 和 A2A Message Handler，实现网络 Agent 协作
"""
import json
import logging
import asyncio
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime

from ..gateway.protocol import MessageType, WSMessage, create_a2a_message, create_error, create_response
from ..gateway.server import GatewayServer
from .protocol import A2AMessage, A2AMessageType, create_discovery_request, create_discovery_response
from .role import AgentInfo, AgentRole
from .a2a_handler import A2AMessageHandler, A2AConnection

logger = logging.getLogger(__name__)


@dataclass
class NetworkAgent:
    """网络 Agent 信息"""
    agent_id: str
    name: str
    role: AgentRole
    instance_id: str  # Gateway 实例 ID
    is_local: bool = True
    capabilities: List[Any] = None
    last_seen: datetime = None

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.last_seen is None:
            self.last_seen = datetime.utcnow()


class A2AGatewayService:
    """A2A Gateway 服务"""

    def __init__(self, gateway_config=None):
        self._gateway: Optional[GatewayServer] = None
        self._gateway_config = gateway_config
        self._a2a_handler = A2AMessageHandler()
        self._agent_registry: Dict[str, NetworkAgent] = {}
        self._instance_id_to_agent: Dict[str, str] = {}
        self._running = False
        self._lock = asyncio.Lock()

    async def start(self, background: bool = False):
        """启动 A2A Gateway"""
        if self._running:
            logger.warning("A2A Gateway already running")
            return

        from ..gateway.config import GatewayConfig

        config = self._gateway_config or GatewayConfig()

        async def a2a_message_handler(instance_id: str, msg: WSMessage):
            return await self._handle_gateway_message(instance_id, msg)

        self._gateway = GatewayServer(
            config=config,
            on_message=a2a_message_handler
        )

        self._running = True
        logger.info(f"Starting A2A Gateway on {config.host}:{config.port}")

        if background:
            import threading
            self._thread = threading.Thread(target=self._run_sync, daemon=True)
            self._thread.start()
        else:
            await self._gateway.start_async()

    def _run_sync(self):
        """同步运行（用于后台线程）"""
        import asyncio
        asyncio.run(self._gateway.start_async())

    async def stop(self):
        """停止 A2A Gateway"""
        if self._gateway:
            self._gateway.stop()
        self._running = False
        logger.info("A2A Gateway stopped")

    async def _handle_gateway_message(self, instance_id: str, msg: WSMessage) -> str:
        """处理 Gateway 消息"""
        try:
            if msg.type == MessageType.A2A.value:
                return await self._handle_a2a_message(instance_id, msg)
            elif msg.type == MessageType.MESSAGE.value:
                return await self._handle_chat_message(instance_id, msg)
            else:
                return json.dumps(create_error("UNSUPPORTED", f"Unsupported message type: {msg.type}").to_dict())
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return json.dumps(create_error("INTERNAL_ERROR", str(e)).to_dict())

    async def _handle_a2a_message(self, instance_id: str, msg: WSMessage) -> str:
        """处理 A2A 消息"""
        try:
            a2a_payload = msg.payload
            a2a_msg = A2AMessage.from_dict(a2a_payload)

            # 处理消息
            response = await self._a2a_handler.handle_message(a2a_msg)

            if response:
                return json.dumps(create_a2a_message(response.to_dict()).to_dict())
            else:
                return json.dumps(create_response("A2A message processed", done=True).to_dict())

        except Exception as e:
            logger.error(f"Error handling A2A message: {e}")
            return json.dumps(create_error("A2A_ERROR", str(e)).to_dict())

    async def _handle_chat_message(self, instance_id: str, msg: WSMessage) -> str:
        """处理聊天消息（简单的 echo）"""
        content = msg.payload.get("content", "")
        return json.dumps(create_response(f"A2A Gateway: Received message '{content[:50]}...'", done=True).to_dict())

    async def register_agent(self, agent_info: AgentInfo, instance_id: str) -> bool:
        """注册一个 Agent"""
        async with self._lock:
            network_agent = NetworkAgent(
                agent_id=agent_info.agent_id,
                name=agent_info.name,
                role=agent_info.role,
                instance_id=instance_id,
                is_local=False,
                capabilities=agent_info.capabilities
            )
            self._agent_registry[agent_info.agent_id] = network_agent
            self._instance_id_to_agent[instance_id] = agent_info.agent_id

            # 在 A2A Handler 中注册连接
            # 注意：这里需要 WebSocket 连接，实际使用时需要传入
            logger.info(f"Agent registered: {agent_info.agent_id} ({agent_info.role.value})")
            return True

    async def unregister_agent(self, agent_id: str) -> bool:
        """注销一个 Agent"""
        async with self._lock:
            if agent_id in self._agent_registry:
                agent = self._agent_registry[agent_id]
                self._instance_id_to_agent.pop(agent.instance_id, None)
                del self._agent_registry[agent_id]
                await self._a2a_handler.unregister_connection(agent_id)
                logger.info(f"Agent unregistered: {agent_id}")
                return True
            return False

    async def discover_agents(self, timeout: float = 3.0) -> List[NetworkAgent]:
        """发现所有在线 Agent"""
        discovery_request = create_discovery_request(from_agent_id="local_gateway")

        # 广播发现请求
        sent_count = await self._a2a_handler.broadcast_to_role("coordinator", discovery_request)

        if not sent_count:
            logger.info("No agents to discover")

        # 等待响应
        await asyncio.sleep(timeout)

        # 返回所有注册的 Agent
        async with self._lock:
            return list(self._agent_registry.values())

    async def assign_task_to_agent(
        self,
        agent_id: str,
        task_data: dict
    ) -> bool:
        """分配任务给指定的 Agent"""
        task_assign = create_task_assign(
            from_agent_id="gateway",
            to_agent_id=agent_id,
            task=task_data
        )

        return await self._a2a_handler.send_to_agent(agent_id, task_assign)

    def get_agents(self) -> List[NetworkAgent]:
        """获取所有注册的 Agent"""
        return list(self._agent_registry.values())

    def get_agent_by_id(self, agent_id: str) -> Optional[NetworkAgent]:
        """根据 ID 获取 Agent"""
        return self._agent_registry.get(agent_id)

    def get_agents_by_role(self, role: AgentRole) -> List[NetworkAgent]:
        """根据角色获取 Agent"""
        return [
            agent for agent in self._agent_registry.values()
            if agent.role == role
        ]


# 全局单例
_a2a_gateway_instance: Optional[A2AGatewayService] = None


def get_a2a_gateway() -> A2AGatewayService:
    """获取全局 A2A Gateway 实例"""
    global _a2a_gateway_instance
    if _a2a_gateway_instance is None:
        _a2a_gateway_instance = A2AGatewayService()
    return _a2a_gateway_instance


async def start_a2a_gateway(background: bool = False, port: int = 18990):
    """启动 A2A Gateway"""
    gateway = get_a2a_gateway()

    from ..gateway.config import GatewayConfig
    gateway._gateway_config = GatewayConfig(port=port)

    await gateway.start(background=background)
    return gateway


async def stop_a2a_gateway():
    """停止 A2A Gateway"""
    gateway = get_a2a_gateway()
    await gateway.stop()
