# src/agent_network/a2a_handler.py
"""
A2A 消息处理器
处理 Agent-to-Agent 网络消息的发送、接收和路由
"""
import json
import logging
import asyncio
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from .protocol import A2AMessage, A2AMessageType, create_task_assign, create_task_result
from .role import AgentInfo
from .task import Task, TaskResult

logger = logging.getLogger(__name__)


@dataclass
class A2AConnection:
    """A2A 连接信息"""
    agent_id: str
    websocket: Any  # WebSocket 连接
    agent_info: AgentInfo
    connected_at: datetime = field(default_factory=datetime.utcnow)


class A2AMessageHandler:
    """A2A 消息处理器"""

    def __init__(self):
        self._connections: Dict[str, A2AConnection] = {}
        self._message_handlers: Dict[A2AMessageType, Callable] = {}
        self._lock = asyncio.Lock()
        self._pending_tasks: Dict[str, List[Callable]] = {}
        
        self._register_default_handlers()

    def _register_default_handlers(self):
        """注册默认的消息处理器"""
        self._message_handlers[A2AMessageType.DISCOVERY_REQUEST] = self._handle_discovery_request
        self._message_handlers[A2AMessageType.DISCOVERY_RESPONSE] = self._handle_discovery_response
        self._message_handlers[A2AMessageType.TASK_ASSIGN] = self._handle_task_assign
        self._message_handlers[A2AMessageType.TASK_RESULT] = self._handle_task_result

    async def register_connection(self, agent_id: str, websocket: Any, agent_info: AgentInfo):
        """注册一个 Agent 连接"""
        async with self._lock:
            connection = A2AConnection(
                agent_id=agent_id,
                websocket=websocket,
                agent_info=agent_info
            )
            self._connections[agent_id] = connection
            logger.info(f"Agent registered: {agent_id} ({agent_info.role.value})")

    async def unregister_connection(self, agent_id: str):
        """注销一个 Agent 连接"""
        async with self._lock:
            if agent_id in self._connections:
                del self._connections[agent_id]
                logger.info(f"Agent unregistered: {agent_id}")

    async def handle_message(self, message: A2AMessage) -> Optional[A2AMessage]:
        """处理 A2A 消息"""
        handler = self._message_handlers.get(message.type)
        if handler:
            try:
                return await handler(message)
            except Exception as e:
                logger.error(f"Error handling message {message.type}: {e}")
                return None
        else:
            logger.warning(f"No handler for message type: {message.type}")
            return None

    async def _handle_discovery_request(self, message: A2AMessage) -> Optional[A2AMessage]:
        """处理发现请求"""
        async with self._lock:
            agents = [
                {
                    "agent_id": conn.agent_id,
                    "name": conn.agent_info.name,
                    "role": conn.agent_info.role.value,
                    "capabilities": [
                        {"name": cap.name, "description": cap.description}
                        for cap in conn.agent_info.capabilities
                    ],
                    "is_local": conn.agent_info.is_local,
                    "network_address": conn.agent_info.network_address
                }
                for conn in self._connections.values()
            ]
        
        return create_discovery_response(from_agent_id="gateway", agents=agents)

    async def _handle_discovery_response(self, message: A2AMessage) -> Optional[A2AMessage]:
        """处理发现响应"""
        agents = message.payload.get("agents", [])
        logger.info(f"Received discovery response with {len(agents)} agents")
        
        # 触发等待的回调
        task_id = f"discovery_{message.message_id}"
        if task_id in self._pending_tasks:
            callbacks = self._pending_tasks.pop(task_id)
            for callback in callbacks:
                try:
                    callback(agents)
                except Exception as e:
                    logger.error(f"Error in discovery callback: {e}")
        
        return None

    async def _handle_task_assign(self, message: A2AMessage) -> Optional[A2AMessage]:
        """处理任务分配"""
        task_data = message.payload.get("task", {})
        target_agent_id = message.to_agent_id
        
        if not target_agent_id:
            logger.error("Task assign message missing target agent")
            return None
        
        # 查找目标 Agent
        connection = self._connections.get(target_agent_id)
        if not connection:
            logger.error(f"Target agent not found: {target_agent_id}")
            return None
        
        # 转发消息给目标 Agent
        try:
            await connection.websocket.send_text(json.dumps(message.to_dict()))
            logger.info(f"Task assigned to {target_agent_id}: {task_data.get('task_id')}")
        except Exception as e:
            logger.error(f"Failed to forward task to {target_agent_id}: {e}")
            return None
        
        return None

    async def _handle_task_result(self, message: A2AMessage) -> Optional[A2AMessage]:
        """处理任务结果"""
        # 转发结果给发送者
        sender_id = message.to_agent_id
        if not sender_id:
            return None
        
        connection = self._connections.get(sender_id)
        if not connection:
            return None
        
        try:
            await connection.websocket.send_text(json.dumps(message.to_dict()))
            logger.info(f"Task result forwarded to {sender_id}")
        except Exception as e:
            logger.error(f"Failed to forward result to {sender_id}: {e}")
        
        return None

    async def send_to_agent(self, target_agent_id: str, message: A2AMessage) -> bool:
        """发送消息给指定的 Agent"""
        connection = self._connections.get(target_agent_id)
        if not connection:
            logger.error(f"Agent not found: {target_agent_id}")
            return False
        
        try:
            await connection.websocket.send_text(json.dumps(message.to_dict()))
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {target_agent_id}: {e}")
            return False

    async def broadcast_to_role(self, role: str, message: A2AMessage) -> List[str]:
        """广播消息给特定角色的所有 Agent"""
        sent_to = []
        async with self._lock:
            for agent_id, connection in self._connections.items():
                if connection.agent_info.role.value == role:
                    try:
                        await connection.websocket.send_text(json.dumps(message.to_dict()))
                        sent_to.append(agent_id)
                    except Exception as e:
                        logger.error(f"Failed to broadcast to {agent_id}: {e}")
        
        return sent_to

    async def get_online_agents(self) -> List[AgentInfo]:
        """获取所有在线的 Agent"""
        async with self._lock:
            return [conn.agent_info for conn in self._connections.values()]

    def get_agent_by_id(self, agent_id: str) -> Optional[AgentInfo]:
        """根据 ID 获取 Agent"""
        connection = self._connections.get(agent_id)
        return connection.agent_info if connection else None

    async def get_agents_by_role(self, role: str) -> List[AgentInfo]:
        """根据角色获取 Agent"""
        async with self._lock:
            return [
                conn.agent_info
                for conn in self._connections.values()
                if conn.agent_info.role.value == role
            ]

    async def discover_remote_agents(self, timeout: float = 5.0) -> List[dict]:
        """发现远程 Agent（通过广播发现请求）"""
        discovery_request = create_discovery_request(from_agent_id="local_gateway")
        
        # 广播给所有连接的 Agent
        sent_to = await self.broadcast_to_role("coordinator", discovery_request)
        
        if not sent_to:
            logger.info("No agents to discover from")
            return []
        
        # 等待响应
        discovered = []
        task_id = f"discovery_{discovery_request.message_id}"
        
        def collect_agents(agents):
            discovered.extend(agents)
        
        if task_id not in self._pending_tasks:
            self._pending_tasks[task_id] = []
        self._pending_tasks[task_id].append(collect_agents)
        
        # 等待超时
        await asyncio.sleep(timeout)
        
        return discovered
