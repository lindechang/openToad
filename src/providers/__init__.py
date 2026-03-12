from typing import Optional
from .anthropic import AnthropicProvider
from .openai import OpenAIProvider
from .deepseek import DeepSeekProvider
from .ollama import OllamaProvider
from .types import LLMProvider, ChatOptions, ChatResponse, Message


def create_provider(type: str, api_key: str, base_url: Optional[str] = None) -> LLMProvider:
    providers = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "deepseek": DeepSeekProvider,
        "ollama": OllamaProvider,
    }
    if type not in providers:
        raise ValueError(f"Unknown provider: {type}")
    
    if type == "ollama":
        return OllamaProvider(api_key or "ollama", base_url or "http://localhost:11434/v1")
    return providers[type](api_key)


__all__ = [
    "create_provider",
    "LLMProvider",
    "ChatOptions",
    "ChatResponse",
    "Message",
    "AnthropicProvider",
    "OpenAIProvider",
    "DeepSeekProvider",
    "OllamaProvider",
]
