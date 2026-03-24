import requests
from typing import Optional
from .types import LLMProvider, ChatOptions, ChatResponse, Message


class QianwenProvider:
    name = "qianwen"
    
    def __init__(self, api_key: str, base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"):
        from openai import OpenAI
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=60.0
        )
    
    def chat(self, options: ChatOptions) -> ChatResponse:
        response = self.client.chat.completions.create(
            model=options.model,
            messages=[{"role": m.role, "content": m.content} for m in options.messages],
            temperature=options.temperature if options.temperature is not None else 0.7,
            max_tokens=options.max_tokens if options.max_tokens is not None else 1024
        )
        
        return ChatResponse(
            content=response.choices[0].message.content or "",
            finish_reason=response.choices[0].finish_reason or "stop"
        )
    
    def chat_stream(self, options: ChatOptions, on_chunk: callable) -> ChatResponse:
        stream = self.client.chat.completions.create(
            model=options.model,
            messages=[{"role": m.role, "content": m.content} for m in options.messages],
            temperature=options.temperature if options.temperature is not None else 0.7,
            max_tokens=options.max_tokens if options.max_tokens is not None else 1024,
            stream=True
        )
        
        content = ""
        for chunk in stream:
            text = chunk.choices[0].delta.content or ""
            content += text
            on_chunk(text)
        
        return ChatResponse(content=content, finish_reason="stop")
    
    def list_models(self) -> list[str]:
        return ["qwen-turbo", "qwen-plus", "qwen-max", "qwen3.5-plus", "qwen3-max"]


class ErnieProvider:
    name = "ernie"
    
    def __init__(self, api_key: str, secret_key: str = ""):
        import base64
        import hmac
        import hashlib
        import time
        import json
        
        self.api_key = api_key
        self.secret_key = secret_key
        self._app_id = api_key
        
        def _create_token():
            now = time.time()
            expire = int(now + 1000)
            auth_str = f"app_id={self._app_id}&expire={expire}&timestamp={int(now)}"
            signature = hmac.new(self.secret_key.encode(), auth_str.encode(), hashlib.sha256).digest()
            return base64.b64encode(f"{auth_str}&signature={signature.decode()}".encode()).decode()
        
        self._get_token = _create_token
        self.access_token = None
    
    def _get_access_token(self):
        if self.access_token:
            return self.access_token
        
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        resp = requests.post(url, params=params, timeout=30)
        data = resp.json()
        self.access_token = data.get("access_token")
        return self.access_token
    
    def chat(self, options: ChatOptions) -> ChatResponse:
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{options.model}"
        params = {"access_token": self._get_access_token()}
        payload = {
            "messages": [{"role": m.role, "content": m.content} for m in options.messages],
            "temperature": options.temperature or 0.7,
            "max_output_tokens": options.max_tokens or 1024
        }
        resp = requests.post(url, json=payload, params=params, timeout=60)
        data = resp.json()
        
        if "result" in data:
            return ChatResponse(content=data["result"], finish_reason="stop")
        raise Exception(f"API error: {data}")
    
    def chat_stream(self, options: ChatOptions, on_chunk: callable) -> ChatResponse:
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{options.model}"
        params = {"access_token": self._get_access_token()}
        payload = {
            "messages": [{"role": m.role, "content": m.content} for m in options.messages],
            "temperature": options.temperature or 0.7,
            "max_output_tokens": options.max_tokens or 1024
        }
        
        with requests.post(url, json=payload, params=params, stream=True, timeout=60) as resp:
            content = ""
            for line in resp.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        import json
                        try:
                            chunk = json.loads(data)
                            if "result" in chunk:
                                text = chunk["result"]
                                content += text
                                on_chunk(text)
                        except:
                            pass
            return ChatResponse(content=content, finish_reason="stop")
    
    def list_models(self) -> list[str]:
        return ["ernie-bot", "ernie-bot-turbo", "ernie-bot-8k", "ernie-4.0-8k"]


class HunyuanProvider:
    name = "hunyuan"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def chat(self, options: ChatOptions) -> ChatResponse:
        url = "https://hunyuan.cloud.tencent.com/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": options.model,
            "messages": [{"role": m.role, "content": m.content} for m in options.messages],
            "temperature": options.temperature or 0.7,
            "max_tokens": options.max_tokens or 1024
        }
        
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        data = resp.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0]["message"]["content"]
            return ChatResponse(content=content, finish_reason="stop")
        raise Exception(f"API error: {data}")
    
    def chat_stream(self, options: ChatOptions, on_chunk: callable) -> ChatResponse:
        url = "https://hunyuan.cloud.tencent.com/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": options.model,
            "messages": [{"role": m.role, "content": m.content} for m in options.messages],
            "temperature": options.temperature or 0.7,
            "max_tokens": options.max_tokens or 1024,
            "stream": True
        }
        
        with requests.post(url, json=payload, headers=headers, stream=True, timeout=60) as resp:
            content = ""
            for line in resp.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        import json
                        try:
                            chunk = json.loads(data)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    text = delta["content"]
                                    content += text
                                    on_chunk(text)
                        except:
                            pass
            return ChatResponse(content=content, finish_reason="stop")
    
    def list_models(self) -> list[str]:
        return ["hunyuan-latest", "hunyuan-pro", "hunyuan-standard"]


class ZhipuProvider:
    name = "zhipu"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def chat(self, options: ChatOptions) -> ChatResponse:
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": options.model,
            "messages": [{"role": m.role, "content": m.content} for m in options.messages],
            "temperature": options.temperature or 0.7,
            "max_tokens": options.max_tokens or 1024
        }
        
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        data = resp.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0]["message"]["content"]
            return ChatResponse(content=content, finish_reason="stop")
        raise Exception(f"API error: {data}")
    
    def chat_stream(self, options: ChatOptions, on_chunk: callable) -> ChatResponse:
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": options.model,
            "messages": [{"role": m.role, "content": m.content} for m in options.messages],
            "temperature": options.temperature or 0.7,
            "max_tokens": options.max_tokens or 1024,
            "stream": True
        }
        
        with requests.post(url, json=payload, headers=headers, stream=True, timeout=60) as resp:
            content = ""
            for line in resp.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        import json
                        try:
                            chunk = json.loads(data)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    text = delta["content"]
                                    content += text
                                    on_chunk(text)
                        except:
                            pass
            return ChatResponse(content=content, finish_reason="stop")
    
    def list_models(self) -> list[str]:
        return ["glm-4", "glm-4-flash", "glm-4-plus", "glm-3-turbo"]


class KimiProvider:
    name = "kimi"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def chat(self, options: ChatOptions) -> ChatResponse:
        url = "https://api.moonshot.cn/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": options.model,
            "messages": [{"role": m.role, "content": m.content} for m in options.messages],
            "temperature": options.temperature or 0.7,
            "max_tokens": options.max_tokens or 1024
        }
        
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        data = resp.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0]["message"]["content"]
            return ChatResponse(content=content, finish_reason="stop")
        raise Exception(f"API error: {data}")
    
    def chat_stream(self, options: ChatOptions, on_chunk: callable) -> ChatResponse:
        url = "https://api.moonshot.cn/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": options.model,
            "messages": [{"role": m.role, "content": m.content} for m in options.messages],
            "temperature": options.temperature or 0.7,
            "max_tokens": options.max_tokens or 1024,
            "stream": True
        }
        
        with requests.post(url, json=payload, headers=headers, stream=True, timeout=60) as resp:
            content = ""
            for line in resp.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        import json
                        try:
                            chunk = json.loads(data)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    text = delta["content"]
                                    content += text
                                    on_chunk(text)
                        except:
                            pass
            return ChatResponse(content=content, finish_reason="stop")
    
    def list_models(self) -> list[str]:
        return ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]


class GeminiProvider:
    name = "gemini"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def chat(self, options: ChatOptions) -> ChatResponse:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{options.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
        contents = []
        for m in options.messages:
            if m.role == "user":
                role = "user"
            elif m.role == "assistant":
                role = "model"
            else:
                continue
            contents.append({"role": role, "parts": [{"text": m.content}]})
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": options.temperature or 0.7,
                "maxOutputTokens": options.max_tokens or 1024
            }
        }
        
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        data = resp.json()
        
        if "candidates" in data and len(data["candidates"]) > 0:
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            return ChatResponse(content=content, finish_reason="stop")
        raise Exception(f"API error: {data}")
    
    def chat_stream(self, options: ChatOptions, on_chunk: callable) -> ChatResponse:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{options.model}:streamGenerateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
        contents = []
        for m in options.messages:
            if m.role == "user":
                role = "user"
            elif m.role == "assistant":
                role = "model"
            else:
                continue
            contents.append({"role": role, "parts": [{"text": m.content}]})
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": options.temperature or 0.7,
                "maxOutputTokens": options.max_tokens or 1024
            }
        }
        
        content = ""
        with requests.post(url, json=payload, headers=headers, stream=True, timeout=60) as resp:
            for line in resp.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        import json
                        try:
                            chunk = json.loads(data)
                            if "candidates" in chunk and len(chunk["candidates"]) > 0:
                                part = chunk["candidates"][0]["content"]["parts"][0]
                                if "text" in part:
                                    text = part["text"]
                                    content += text
                                    on_chunk(text)
                        except:
                            pass
        return ChatResponse(content=content, finish_reason="stop")
    
    def list_models(self) -> list[str]:
        return ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
