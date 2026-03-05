import httpx
import json
from typing import List, AsyncGenerator, Optional
from config import OLLAMA_BASE_URL


class OllamaClient:
    """Ollama API 客户端"""

    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url
        self.timeout = 300.0  # 5 分钟超时，给模型加载留足时间

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
        """对话接口（支持流式）- 使用 /api/generate 接口"""
        # 将 OpenAI 格式的消息转换为 prompt
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt += f"System: {content}\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n"
            else:  # user
                prompt += f"User: {content}\n"
        prompt += "Assistant: "

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        if options:
            payload["options"] = options

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if stream:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                # 转换为 chat 格式 - 优先使用 response 字段，如果没有则使用 thinking 字段
                                content = data.get("response", "") or data.get("thinking", "")
                                chunk = {
                                    "message": {"role": "assistant", "content": content},
                                    "done": data.get("done", False)
                                }
                                yield chunk
                            except json.JSONDecodeError:
                                continue
            else:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                # 转换为 chat 格式 - 优先使用 response 字段，如果没有则使用 thinking 字段
                content = data.get("response", "") or data.get("thinking", "")
                yield {
                    "message": {"role": "assistant", "content": content},
                    "done": True
                }
