import httpx
import json
from typing import List, AsyncGenerator, Optional
from config import OLLAMA_BASE_URL


class OllamaClient:
    """Ollama API 客户端"""

    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url
        self.timeout = 120.0

    async def get_embeddings(
        self,
        model: str,
        input: List[str]
    ) -> dict:
        """获取 embedding"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": model,
                    "prompt": input[0] if len(input) == 1 else "\n".join(input)
                }
            )
            response.raise_for_status()
            return response.json()

    async def chat(
        self,
        model: str,
        messages: List[dict],
        stream: bool = False,
        options: Optional[dict] = None
    ) -> AsyncGenerator[dict, None]:
        """对话接口（支持流式）"""
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        if options:
            payload["options"] = options

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if stream:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json=payload
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                yield json.loads(line)
                            except json.JSONDecodeError:
                                continue
            else:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                yield response.json()
