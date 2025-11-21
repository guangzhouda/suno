"""
LLM相关的Pydantic模型
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str = Field(..., description="角色: system, user, assistant")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """对话请求模型"""
    messages: List[ChatMessage] = Field(..., description="对话消息列表")
    model: Optional[str] = Field(default=None, description="模型名称，不指定则使用默认模型")
    temperature: float = Field(default=0.7, ge=0, le=2, description="温度参数 (0-2)")
    max_tokens: int = Field(default=2000, ge=1, le=32000, description="最大生成token数")
    top_p: float = Field(default=1.0, ge=0, le=1, description="核采样参数")
    stream: bool = Field(default=False, description="是否流式输出")
    presence_penalty: float = Field(default=0, ge=-2, le=2, description="存在惩罚")
    frequency_penalty: float = Field(default=0, ge=-2, le=2, description="频率惩罚")

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "system", "content": "你是一个有帮助的AI助手"},
                    {"role": "user", "content": "你好，请介绍一下自己"}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
        }


class CompletionRequest(BaseModel):
    """文本补全请求模型"""
    prompt: str = Field(..., description="提示文本")
    model: Optional[str] = Field(default=None, description="模型名称")
    temperature: float = Field(default=0.7, ge=0, le=2, description="温度参数")
    max_tokens: int = Field(default=2000, ge=1, le=32000, description="最大生成token数")
    top_p: float = Field(default=1.0, ge=0, le=1, description="核采样参数")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "从前有一座山，山里有座庙，庙里有个",
                "temperature": 0.8,
                "max_tokens": 100
            }
        }


class EmbeddingRequest(BaseModel):
    """向量嵌入请求模型"""
    input: str | List[str] = Field(..., description="输入文本（单个或列表）")
    model: Optional[str] = Field(default=None, description="嵌入模型名称")

    class Config:
        json_schema_extra = {
            "example": {
                "input": "这是一段需要向量化的文本",
                "model": "text-embedding-ada-002"
            }
        }
