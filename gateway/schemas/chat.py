from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any


class Message(BaseModel):
    """对话消息"""
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    """对话请求体"""
    model: str = Field(default="Qwen3-Coder-30B", description="模型名称")
    messages: List[Message] = Field(..., description="会话列表")
    stream: bool = Field(default=False, description="是否流式输出")
    max_tokens: Optional[int] = Field(default=None, description="最大 token 数")
    top_p: Optional[float] = Field(default=None, description="核采样参数")
    temperature: Optional[float] = Field(default=None, description="温度参数")


class ChatMessage(BaseModel):
    """对话响应消息"""
    role: str = "assistant"
    content: str
    refusal: Optional[Any] = None
    annotations: Optional[Any] = None
    audio: Optional[Any] = None
    function_call: Optional[Any] = None
    tool_calls: List = Field(default_factory=list)
    reasoning_content: Optional[Any] = None


class ChatChoice(BaseModel):
    """对话选择"""
    index: int = 0
    message: ChatMessage
    logprobs: Optional[Any] = None
    finish_reason: str = "stop"
    stop_reason: Optional[Any] = None


class ChatUsage(BaseModel):
    """使用量统计"""
    prompt_tokens: int
    total_tokens: int
    completion_tokens: int
    prompt_tokens_details: Optional[Any] = None


class ChatResponse(BaseModel):
    """对话响应体"""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    service_tier: Optional[Any] = None
    system_fingerprint: Optional[Any] = None
    usage: ChatUsage
    prompt_logprobs: Optional[Any] = None
    kv_transfer_params: Optional[Any] = None


# 流式响应相关
class StreamDelta(BaseModel):
    """流式增量内容"""
    role: Optional[str] = None
    content: Optional[str] = None


class StreamChoice(BaseModel):
    """流式选择"""
    index: int = 0
    delta: StreamDelta
    logprobs: Optional[Any] = None
    finish_reason: Optional[str] = None
    stop_reason: Optional[Any] = None


class StreamResponse(BaseModel):
    """流式响应体"""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[StreamChoice]
