"""
OpenToad Web - FastAPI 后端服务
复用 src/agent_network 核心模块
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import asyncio

from src.agent_network import (
    AgentInfo, AgentRole, LocalAgentRegistry,
    TaskOrchestrator, WorkspaceManager,
    get_evolution_engine, init_evolution_system
)

app = FastAPI(
    title="OpenToad Web API",
    description="OpenToad AI 分身助手 Web API - 复用核心模块",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    stream: bool = True


class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None


class WorkspaceCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


agent_registry = LocalAgentRegistry()
task_orchestrator = TaskOrchestrator(agent_registry)
workspace_manager = WorkspaceManager()
evolution_engine = init_evolution_system()

chat_history: Dict[str, List[Dict]] = {}


def init_demo_agents():
    """初始化演示用 Agent"""
    demo_agents = [
        AgentInfo(
            agent_id="coordinator-1",
            name="Coordinator Agent",
            role=AgentRole.COORDINATOR,
            capabilities=["task_assignment", "result_aggregation", "coordination"]
        ),
        AgentInfo(
            agent_id="worker-1",
            name="Worker Agent 1",
            role=AgentRole.WORKER,
            capabilities=["task_execution", "coding", "testing"]
        ),
        AgentInfo(
            agent_id="worker-2",
            name="Worker Agent 2",
            role=AgentRole.WORKER,
            capabilities=["task_execution", "documentation"]
        ),
        AgentInfo(
            agent_id="researcher-1",
            name="Researcher Agent",
            role=AgentRole.RESEARCHER,
            capabilities=["research", "analysis", "data_collection"]
        ),
        AgentInfo(
            agent_id="writer-1",
            name="Writer Agent",
            role=AgentRole.WRITER,
            capabilities=["writing", "documentation", "translation"]
        ),
    ]

    for agent in demo_agents:
        agent_registry.register(agent)


init_demo_agents()


@app.get("/")
async def root():
    return {
        "name": "OpenToad Web API",
        "version": "2.0.0",
        "core_modules": "agent_network, memory, evolution",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agents_count": len(agent_registry.list_agents()),
        "tasks_count": len(task_orchestrator.tasks)
    }


@app.get("/api/agents")
async def list_agents():
    agents = agent_registry.list_agents()
    return {
        "agents": [
            {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "role": agent.role.value if hasattr(agent.role, 'value') else str(agent.role),
                "status": "online",
                "capabilities": agent.capabilities
            }
            for agent in agents
        ]
    }


@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    agent = agent_registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {
        "agent_id": agent.agent_id,
        "name": agent.name,
        "role": agent.role.value if hasattr(agent.role, 'value') else str(agent.role),
        "capabilities": agent.capabilities
    }


@app.get("/api/tasks")
async def list_tasks():
    return {
        "tasks": [
            {
                "task_id": task.task_id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value if hasattr(task.status, 'value') else str(task.status),
                "assigned_to": task.assigned_to,
                "progress": 0,
                "created_at": task.created_at.isoformat() if hasattr(task, 'created_at') else None
            }
            for task in task_orchestrator.tasks.values()
        ]
    }


@app.post("/api/tasks")
async def create_task(request: TaskCreateRequest):
    task = task_orchestrator.create_task(
        title=request.title,
        description=request.description or "",
        assigned_to=request.assigned_to
    )
    return {
        "task_id": task.task_id,
        "title": task.title,
        "status": task.status.value if hasattr(task.status, 'value') else str(task.status)
    }


@app.get("/api/workspaces")
async def list_workspaces():
    workspaces = workspace_manager.list_workspaces()
    return {
        "workspaces": [
            {
                "workspace_id": ws.id,
                "name": ws.name,
                "description": ws.description,
                "participants": list(ws.participants),
                "notes_count": len(ws.notes),
                "files_count": len(ws.files)
            }
            for ws in workspaces
        ]
    }


@app.post("/api/workspaces")
async def create_workspace(request: WorkspaceCreateRequest):
    workspace = workspace_manager.create_workspace(
        name=request.name,
        description=request.description or ""
    )
    return {
        "workspace_id": workspace.id,
        "name": workspace.name
    }


@app.get("/api/workspaces/{workspace_id}")
async def get_workspace(workspace_id: str):
    workspace = workspace_manager.get_workspace(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {
        "workspace_id": workspace.id,
        "name": workspace.name,
        "description": workspace.description,
        "participants": list(workspace.participants),
        "notes": [
            {
                "note_id": note.note_id,
                "author_id": note.author_id,
                "content": note.content,
                "tags": note.tags
            }
            for note in workspace.notes.values()
        ],
        "files": [
            {
                "file_id": f.file_id,
                "name": f.name,
                "size": f.size
            }
            for f in workspace.files.values()
        ]
    }


@app.post("/api/workspaces/{workspace_id}/notes")
async def add_note(workspace_id: str, author_id: str, content: str, tags: List[str] = None):
    workspace = workspace_manager.get_workspace(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    note = workspace.add_note(author_id, content, tags or [])
    return {
        "note_id": note.note_id,
        "content": note.content
    }


@app.get("/api/evolution/summary")
async def get_evolution_summary():
    return evolution_engine.get_evolution_summary()


@app.post("/api/chat")
async def chat(request: ChatRequest):
    session_id = request.session_id or "default"

    if session_id not in chat_history:
        chat_history[session_id] = []

    user_message = {
        "role": "user",
        "content": request.message,
        "timestamp": datetime.utcnow().isoformat()
    }
    chat_history[session_id].append(user_message)

    evolution_engine.record_metric("chat_messages", 1.0)
    evolution_engine.record_metric("task_execution_time", 2.5)
    evolution_engine.record_metric("task_success_rate", 0.95)

    response = await generate_response(request.message, session_id)

    assistant_message = {
        "role": "assistant",
        "content": response,
        "timestamp": datetime.utcnow().isoformat()
    }
    chat_history[session_id].append(assistant_message)

    return {
        "session_id": session_id,
        "response": assistant_message,
        "stats": {
            "agents_online": len(agent_registry.list_agents()),
            "total_tasks": len(task_orchestrator.tasks),
            "total_workspaces": len(workspace_manager.list_workspaces())
        }
    }


async def generate_response(message: str, session_id: str) -> str:
    """生成 AI 响应 - 复用核心模块"""
    message_lower = message.lower()

    if any(word in message_lower for word in ["agent", "代理", "协作"]):
        agents = agent_registry.list_agents()
        agent_list = "\n".join([f"- {a.name} ({a.role})" for a in agents])
        return f"🤖 **当前在线 Agent**:\n{agent_list}\n\n你可以创建任务并分配给它们！"

    if any(word in message_lower for word in ["任务", "task", "工作"]):
        tasks = task_orchestrator.list_tasks()
        if not tasks:
            return "📋 目前没有活跃任务。你可以创建一个新任务。"
        task_list = "\n".join([f"- {t.title} ({t.status})" for t in tasks])
        return f"📋 **当前任务**:\n{task_list}"

    if any(word in message_lower for word in ["工作区", "workspace", "协作"]):
        workspaces = workspace_manager.list_workspaces()
        if not workspaces:
            return "🏠 目前没有工作区。你可以创建一个新工作区来开始协作。"
        ws_list = "\n".join([f"- {ws.name} ({len(ws.participants)}人参与)" for ws in workspaces])
        return f"🏠 **当前工作区**:\n{ws_list}"

    if any(word in message_lower for word in ["进化", "evolution", "学习"]):
        summary = evolution_engine.get_evolution_summary()
        return f"🧬 **系统进化状态**:\n- 提案数: {summary['total_proposed']}\n- 已部署: {summary['total_deployed']}\n- 知识库: {summary['knowledge_count']} 条"

    responses = [
        f"我收到了: {message}\n\n作为 OpenToad AI 分身，我可以帮你:\n• 管理 Agent 网络\n• 创建和分配任务\n• 协调多 Agent 协作\n• 追踪系统进化",
        f"你说得对！让我帮你处理: {message}\n\n当前系统状态:\n• {len(agent_registry.list_agents())} 个 Agent 在线\n• {len(task_orchestrator.tasks)} 个任务进行中\n• {len(workspace_manager.list_workspaces())} 个工作区活跃",
        f"我理解你的需求。{message}\n\n你可以尝试:\n1. 说「查看 Agent」- 查看所有在线 Agent\n2. 说「创建任务」- 创建新任务\n3. 说「打开工作区」- 进入协作工作区"
    ]
    import random
    return random.choice(responses)


@app.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message_data = eval(data) if isinstance(data, str) else data

            if message_data.get("type") == "message":
                content = message_data.get("content", "")

                if session_id not in chat_history:
                    chat_history[session_id] = []

                chat_history[session_id].append({
                    "role": "user",
                    "content": content,
                    "timestamp": datetime.utcnow().isoformat()
                })

                await websocket.send_json({
                    "type": "received",
                    "content": content
                })

                response = await generate_response(content, session_id)

                for i in range(0, len(response), 10):
                    await websocket.send_json({
                        "type": "stream",
                        "content": response[i:i+10]
                    })
                    await asyncio.sleep(0.02)

                await websocket.send_json({
                    "type": "done",
                    "content": response
                })

                chat_history[session_id].append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.utcnow().isoformat()
                })

    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
