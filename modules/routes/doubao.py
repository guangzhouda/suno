"""
Doubao API 路由

提供豆包 AI 功能：
- 文本对话（歌词生成）
- 图像生成（专辑封面）
- 图像理解（图片成歌）
- 视频生成（音乐 MV）
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from modules.clients.doubao import DoubaoClient
from config import get_config

router = APIRouter(prefix="/api/doubao", tags=["豆包AI"])


def get_doubao_client() -> DoubaoClient:
    """获取 Doubao 客户端实例"""
    try:
        return DoubaoClient()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Doubao 客户端初始化失败: {str(e)}")


# ==================== Pydantic 模型 ====================

class ChatRequest(BaseModel):
    """文本对话请求"""
    messages: List[Dict[str, str]] = Field(..., description="对话消息列表")
    model: Optional[str] = Field(None, description="模型ID")
    temperature: float = Field(0.7, description="温度参数")
    max_tokens: int = Field(2000, description="最大token数")


class LyricsGenerateRequest(BaseModel):
    """歌词生成请求"""
    prompt: str = Field(..., description="歌词创作提示")
    system_prompt: Optional[str] = Field(None, description="系统提示")
    temperature: float = Field(0.7, description="温度参数")


class ImageGenerateRequest(BaseModel):
    """图像生成请求"""
    prompt: str = Field(..., description="图像描述")
    size: str = Field("2K", description="图像尺寸")
    model: Optional[str] = Field(None, description="模型ID")
    watermark: bool = Field(False, description="是否添加水印")
    response_format: str = Field("url", description="返回格式")


class ImageUnderstandRequest(BaseModel):
    """图像理解请求"""
    image_url: str = Field(..., description="图片URL")
    question: str = Field(
        "这是哪里？描述一下这张图片的内容、氛围和情绪。",
        description="询问内容"
    )
    model: Optional[str] = Field(None, description="模型ID")


class ImageToSongRequest(BaseModel):
    """图片成歌请求"""
    image_url: str = Field(..., description="图片URL")


class VideoGenerateRequest(BaseModel):
    """视频生成请求"""
    prompt: str = Field(..., description="视频描述")
    image_url: Optional[str] = Field(None, description="首帧图片URL")
    model: Optional[str] = Field(None, description="模型ID")
    ratio: Optional[str] = Field("16:9", description="视频比例")
    duration: Optional[int] = Field(5, description="视频时长（秒）")


class MusicVideoRequest(BaseModel):
    """音乐 MV 请求"""
    lyrics: str = Field(..., description="歌词")
    style: str = Field("流行", description="音乐风格")
    image_url: Optional[str] = Field(None, description="封面图片URL")


# ==================== API 端点 ====================

@router.get("/health")
async def health_check():
    """健康检查"""
    try:
        client = get_doubao_client()
        return {
            "status": "ok",
            "service": "Doubao API",
            "models": client.models
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


# ==================== 文本对话 ====================

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    文本对话

    支持通用对话和歌词生成
    """
    client = get_doubao_client()

    try:
        content = client.chat(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        return {
            "code": 200,
            "data": {
                "content": content
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lyrics")
async def generate_lyrics(request: LyricsGenerateRequest):
    """
    生成歌词

    使用 DeepSeek-V3 模型生成创意歌词
    """
    client = get_doubao_client()

    try:
        lyrics = client.generate_lyrics(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            temperature=request.temperature
        )

        return {
            "code": 200,
            "data": {
                "lyrics": lyrics
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 图像生成 ====================

@router.post("/image/generate")
async def generate_image(request: ImageGenerateRequest):
    """
    生成图像

    用于专辑封面、场景图等
    """
    client = get_doubao_client()

    try:
        result = client.generate_image(
            prompt=request.prompt,
            size=request.size,
            model=request.model,
            watermark=request.watermark,
            response_format=request.response_format
        )

        return {
            "code": 200,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 图像理解 ====================

@router.post("/image/understand")
async def understand_image(request: ImageUnderstandRequest):
    """
    图像理解

    分析图片内容、氛围、情绪等
    """
    client = get_doubao_client()

    try:
        description = client.understand_image(
            image_url=request.image_url,
            question=request.question,
            model=request.model
        )

        return {
            "code": 200,
            "data": {
                "description": description
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image/to-song")
async def image_to_song(request: ImageToSongRequest):
    """
    图片成歌

    分析图片并提取音乐创作元素：
    - 场景和元素
    - 氛围和情绪
    - 色彩基调
    - 音乐风格
    - 推荐乐器和节奏
    """
    client = get_doubao_client()

    try:
        elements = client.image_to_song_description(
            image_url=request.image_url
        )

        return {
            "code": 200,
            "data": elements
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 视频生成 ====================

@router.post("/video/generate")
async def generate_video(request: VideoGenerateRequest):
    """
    生成视频

    支持文生视频和图生视频
    """
    client = get_doubao_client()

    # 构建提示词，包含比例和时长参数
    prompt = request.prompt
    if request.ratio or request.duration:
        prompt += f"\n\n--ratio {request.ratio} --dur {request.duration}"

    try:
        result = client.generate_video(
            prompt=prompt,
            image_url=request.image_url,
            model=request.model
        )

        return {
            "code": 200,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video/music-video")
async def create_music_video(request: MusicVideoRequest):
    """
    创建音乐 MV

    根据歌词和风格生成匹配的 MV 视频
    """
    client = get_doubao_client()

    try:
        result = client.create_music_video(
            lyrics=request.lyrics,
            style=request.style,
            image_url=request.image_url
        )

        return {
            "code": 200,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
