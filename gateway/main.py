from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Optional
import time
import uuid

from config import API_KEY, EMBEDDING_MODEL, CHAT_MODEL
from clients.ollama_client import OllamaClient
from schemas.embeddings import (
    EmbeddingRequest, EmbeddingResponse,
    EmbeddingData, EmbeddingUsage
)
from schemas.chat import (
    ChatRequest, ChatResponse, ChatMessage, ChatChoice, ChatUsage,
    StreamResponse, StreamChoice, StreamDelta
)

app = FastAPI(title="Ollama Gateway", version="1.0.0")
ollama = OllamaClient()


def verify_api_key(szc_api_key: Optional[str]) -> bool:
    """验证 API Key"""
    if not API_KEY:
        return True  # 未配置时跳过验证
    return szc_api_key == API_KEY


@app.post("/gateway/ti/qwen3-embedding/v1/embeddings")
async def create_embeddings(
    request: EmbeddingRequest,
    szc_api_key: Optional[str] = Header(None, alias="szc-api-key")
):
    """创建 Embedding"""
    if not verify_api_key(szc_api_key):
        raise HTTPException(status_code=401, detail="Invalid API Key")

    try:
        # 调用 Ollama 获取 embedding
        result = await ollama.get_embeddings(
            model=EMBEDDING_MODEL,
            input=request.input
        )

        # 构建响应
        embedding_data = EmbeddingData(
            index=0,
            embedding=result.get("embedding", [])
        )

        # 估算 token 数（简单估算）
        prompt_tokens = sum(len(text.split()) for text in request.input)

        response = EmbeddingResponse(
            id=f"embd-{uuid.uuid4().hex}",
            created=int(time.time()),
            model=request.model,
            data=[embedding_data],
            usage=EmbeddingUsage(
                prompt_tokens=prompt_tokens,
                total_tokens=prompt_tokens,
                completion_tokens=0
            )
        )

        return JSONResponse(content=response.model_dump())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/gateway/ti/qwen3-coder-30b/v1/chat/completions")
async def create_chat_completion(
    request: ChatRequest,
    szc_api_key: Optional[str] = Header(None, alias="szc-api-key")
):
    """创建对话完成"""
    if not verify_api_key(szc_api_key):
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # 构建 Ollama 选项
    options = {}
    if request.max_tokens:
        options["num_predict"] = request.max_tokens
    if request.top_p:
        options["top_p"] = request.top_p
    if request.temperature:
        options["temperature"] = request.temperature

    try:
        if request.stream:
            # 流式响应
            return StreamingResponse(
                generate_stream_response(request, options),
                media_type="text/event-stream"
            )
        else:
            # 非流式响应
            return await generate_non_stream_response(request, options)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def generate_stream_response(request: ChatRequest, options: dict):
    """生成流式响应"""
    chat_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    # 使用请求中的 model 参数，如果为空则使用默认值
    model = request.model if request.model else CHAT_MODEL

    async for chunk in ollama.chat(
        model=model,
        messages=messages,
        stream=True,
        options=options
    ):
        content = chunk.get("message", {}).get("content", "")
        done = chunk.get("done", False)

        if done:
            # 结束帧
            stream_choice = StreamChoice(
                index=0,
                delta=StreamDelta(content=""),
                finish_reason="stop"
            )
            stream_response = StreamResponse(
                id=chat_id,
                created=created,
                model=request.model,
                choices=[stream_choice]
            )
            yield f"data: {stream_response.model_dump_json()}\n\n"
            yield "data: [DONE]\n\n"
        else:
            stream_choice = StreamChoice(
                index=0,
                delta=StreamDelta(content=content),
                finish_reason=None
            )
            stream_response = StreamResponse(
                id=chat_id,
                created=created,
                model=request.model,
                choices=[stream_choice]
            )
            yield f"data: {stream_response.model_dump_json()}\n\n"


async def generate_non_stream_response(request: ChatRequest, options: dict):
    """生成非流式响应"""
    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    # 使用请求中的 model 参数，如果为空则使用默认值
    model = request.model if request.model else CHAT_MODEL

    # ollama.chat 始终返回异步生成器，需要用 async for 获取结果
    result = None
    async for chunk in ollama.chat(
        model=model,
        messages=messages,
        stream=False,
        options=options
    ):
        result = chunk
        break  # 非流式模式下只取第一个结果

    if not result:
        raise HTTPException(status_code=500, detail="Empty response from Ollama")

    chat_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())

    # 估算 token 数
    prompt_tokens = sum(len(m.content.split()) for m in request.messages)
    completion_tokens = len(result.get("message", {}).get("content", "").split())

    chat_message = ChatMessage(
        role="assistant",
        content=result.get("message", {}).get("content", "")
    )

    choice = ChatChoice(
        index=0,
        message=chat_message,
        finish_reason="stop"
    )

    response = ChatResponse(
        id=chat_id,
        created=created,
        model=request.model,
        choices=[choice],
        usage=ChatUsage(
            prompt_tokens=prompt_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            completion_tokens=completion_tokens
        )
    )

    return JSONResponse(content=response.model_dump())
