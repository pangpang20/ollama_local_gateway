from pydantic import BaseModel, Field
from typing import List, Optional, Any


class EmbeddingRequest(BaseModel):
    """Embedding 请求体"""
    model: str = Field(..., description="模型名称")
    input: List[str] = Field(..., description="向量字符串列表")


class EmbeddingData(BaseModel):
    """单个 embedding 数据"""
    index: int
    object: str = "embedding"
    embedding: List[float]


class EmbeddingUsage(BaseModel):
    """使用量统计"""
    prompt_tokens: int
    total_tokens: int
    completion_tokens: int = 0
    prompt_tokens_details: Optional[Any] = None


class EmbeddingResponse(BaseModel):
    """Embedding 响应体"""
    id: str
    object: str = "list"
    created: int
    model: str
    data: List[EmbeddingData]
    usage: EmbeddingUsage
