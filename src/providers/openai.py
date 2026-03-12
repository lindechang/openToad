from openai import OpenAI
from .types import LLMProvider, ChatOptions, ChatResponse, Message


class OpenAIProvider:
    name = "openai"
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def chat(self, options: ChatOptions) -> ChatResponse:
        response = self.client.chat.completions.create(
            model=options.model,
            messages=[{"role": m.role, "content": m.content} for m in options.messages],
            temperature=options.temperature,
            max_tokens=options.max_tokens
        )
        
        return ChatResponse(
            content=response.choices[0].message.content or "",
            finish_reason=response.choices[0].finish_reason or "stop"
        )
    
    def chat_stream(self, options: ChatOptions, on_chunk: callable) -> ChatResponse:
        stream = self.client.chat.completions.create(
            model=options.model,
            messages=[{"role": m.role, "content": m.content} for m in options.messages],
            temperature=options.temperature,
            max_tokens=options.max_tokens,
            stream=True
        )
        
        content = ""
        for chunk in stream:
            text = chunk.choices[0].delta.content or ""
            content += text
            on_chunk(text)
        
        return ChatResponse(content=content, finish_reason="stop")
    
    def list_models(self) -> list[str]:
        return [m.id for m in self.client.models.list()]
