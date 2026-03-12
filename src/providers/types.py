from dataclasses import dataclass
from typing import Protocol, runtime_checkable, Optional


@dataclass
class Message:
    role: str  # "user" | "assistant" | "system"
    content: str


@dataclass
class ChatOptions:
    model: str
    messages: list[Message]
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: bool = False


@dataclass
class ChatResponse:
    content: str
    finish_reason: str  # "stop" | "length" | "content_filter"


@runtime_checkable
class LLMProvider(Protocol):
    name: str
    
    def chat(self, options: ChatOptions) -> ChatResponse: ...
    
    def chat_stream(self, options: ChatOptions, on_chunk: callable) -> ChatResponse: ...
    
    def list_models(self) -> list[str]: ...
