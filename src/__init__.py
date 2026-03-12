"""OpenToad - Self-Sustainable AI Assistant"""
__version__ = "1.0.0"

from .providers import create_provider
from .agent import Agent, AgentConfig
from .tools import register_default_tools, global_tools
from .providers.types import ChatOptions, ChatResponse, Message, LLMProvider

__all__ = [
    "create_provider",
    "Agent",
    "AgentConfig",
    "register_default_tools",
    "global_tools",
    "ChatOptions",
    "ChatResponse",
    "Message",
    "LLMProvider"
]

