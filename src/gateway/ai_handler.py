import logging
from typing import Optional, AsyncIterator
from ..providers import create_provider, LLMProvider, ChatOptions, Message
from ..profile import load_profile
from ..memory import MemoryCore
from ..agent.prompt import build_system_prompt

logger = logging.getLogger(__name__)


class AIHandler:
    def __init__(
        self,
        provider_type: str = "openai",
        api_key: str = "",
        model: str = "gpt-4o-mini",
        base_url: Optional[str] = None,
        stream: bool = True
    ):
        self.provider_type = provider_type
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.stream = stream
        self._provider: Optional[LLMProvider] = None
        self._memory = MemoryCore()

    def _get_provider(self) -> LLMProvider:
        if self._provider is None:
            self._provider = create_provider(
                self.provider_type,
                self.api_key,
                self.base_url
            )
        return self._provider

    def set_provider(
        self,
        provider_type: str,
        api_key: str,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.provider_type = provider_type
        self.api_key = api_key
        self.model = model or self.model
        self.base_url = base_url
        self._provider = None

    def _build_messages(self, user_input: str) -> list[Message]:
        profile = load_profile()
        profile_context = profile.to_prompt_context() if profile.name else ""
        memory_context = self._memory.to_context_string()
        system_prompt = build_system_prompt(profile_context, memory_context)

        return [
            Message(role="system", content=system_prompt),
            Message(role="user", content=user_input)
        ]

    async def chat(self, user_input: str) -> str:
        provider = self._get_provider()
        messages = self._build_messages(user_input)

        try:
            response = provider.chat(ChatOptions(
                model=self.model,
                messages=messages,
                temperature=0.7
            ))
            return response.content
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"抱歉，发生了错误: {str(e)}"

    async def chat_stream(self, user_input: str) -> AsyncIterator[str]:
        provider = self._get_provider()
        messages = self._build_messages(user_input)

        chunks = []

        def on_chunk(text: str):
            chunks.append(text)
            return text

        try:
            provider.chat_stream(
                ChatOptions(
                    model=self.model,
                    messages=messages,
                    temperature=0.7
                ),
                on_chunk
            )
            for chunk in chunks:
                yield chunk
        except Exception as e:
            logger.error(f"Chat stream error: {e}")
            yield f"抱歉，发生了错误: {str(e)}"

    async def handle_message(self, instance_id: str, content: str) -> AsyncIterator[str]:
        self._memory.add_memory(content, source="gateway")
        
        if self.stream:
            async for chunk in self.chat_stream(content):
                yield chunk
        else:
            response = await self.chat(content)
            yield response


def create_ai_handler(
    provider_type: str = "openai",
    api_key: str = "",
    model: str = "gpt-4o-mini",
    base_url: Optional[str] = None,
    stream: bool = True
) -> AIHandler:
    return AIHandler(
        provider_type=provider_type,
        api_key=api_key,
        model=model,
        base_url=base_url,
        stream=stream
    )
