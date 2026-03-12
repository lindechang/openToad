from typing import Optional
from .anthropic import AnthropicProvider
from .openai import OpenAIProvider
from .deepseek import DeepSeekProvider
from .ollama import OllamaProvider
from .chinese import (
    QianwenProvider,
    ErnieProvider,
    HunyuanProvider,
    ZhipuProvider,
    KimiProvider,
    GeminiProvider,
)
from .types import LLMProvider, ChatOptions, ChatResponse, Message


def create_provider(type: str, api_key: str, base_url: Optional[str] = None) -> LLMProvider:
    providers = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "deepseek": DeepSeekProvider,
        "ollama": OllamaProvider,
        "qianwen": QianwenProvider,
        "ernie": ErnieProvider,
        "hunyuan": HunyuanProvider,
        "zhipu": ZhipuProvider,
        "kimi": KimiProvider,
        "gemini": GeminiProvider,
    }
    if type not in providers:
        raise ValueError(f"Unknown provider: {type}")
    
    if type == "ollama":
        return OllamaProvider(api_key or "ollama", base_url or "http://localhost:11434/v1")
    if type == "ernie":
        secret_key = base_url or ""
        return ErnieProvider(api_key, secret_key)
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
    "QianwenProvider",
    "ErnieProvider",
    "HunyuanProvider",
    "ZhipuProvider",
    "KimiProvider",
    "GeminiProvider",
]
