import anthropic
from typing import Optional
from .types import LLMProvider, ChatOptions, ChatResponse, Message


class AnthropicProvider:
    name = "anthropic"
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def chat(self, options: ChatOptions) -> ChatResponse:
        system_content = self._extract_system(options.messages)
        filtered_messages = self._filter_messages(options.messages)
        
        response = self.client.messages.create(
            model=options.model,
            system=system_content or "",
            messages=[{"role": m.role, "content": m.content} for m in filtered_messages],
            temperature=options.temperature,
            max_tokens=options.max_tokens or 1024
        )
        
        content_block = response.content[0]
        content = content_block.text if hasattr(content_block, 'text') else str(content_block)
        
        return ChatResponse(
            content=content,
            finish_reason="stop" if response.stop_reason == "end_turn" else "length"
        )
    
    def _extract_system(self, messages: list[Message]) -> Optional[str]:
        for msg in messages:
            if msg.role == "system":
                return msg.content
        return None
    
    def _filter_messages(self, messages: list[Message]) -> list[Message]:
        return [m for m in messages if m.role != "system"]
    
    def chat_stream(self, options: ChatOptions, on_chunk: callable) -> ChatResponse:
        system_content = self._extract_system(options.messages)
        filtered_messages = self._filter_messages(options.messages)
        
        with self.client.messages.stream(
            model=options.model,
            system=system_content or "",
            messages=[{"role": m.role, "content": m.content} for m in filtered_messages],
            temperature=options.temperature,
            max_tokens=options.max_tokens or 1024
        ) as stream:
            content = ""
            for text in stream.text_stream:
                content += text
                on_chunk(text)
            
            return ChatResponse(content=content, finish_reason="stop")
    
    def list_models(self) -> list[str]:
        return ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"]
