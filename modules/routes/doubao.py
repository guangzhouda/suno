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
import requests
import pathlib

from modules.clients.doubao import DoubaoClient
from config import get_config

router = APIRouter(prefix="/api/doubao", tags=["豆包AI"])


def get_doubao_client() -> DoubaoClient:
    """获取 Doubao 客户端实例"""
    try:
        return DoubaoClient()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Doubao 客户端初始化失败: {str(e)}")


def _safe_name(text: str) -> str:
    """简易文件名清洗"""
    bad = r'\\/:*?"<>|'
    for ch in bad:
        text = text.replace(ch, "_")
    return text.strip() or "untitled"


def _ext_from_content_type(ct: str, kind: str) -> str:
    if not ct:
        return ".bin"
    if "png" in ct:
        return ".png"
    if "jpeg" in ct or "jpg" in ct:
        return ".jpg"
    if "mp4" in ct:
        return ".mp4"
    if "gif" in ct:
        return ".gif"
    if kind == "video":
        return ".mp4"
    return ".png"


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


class ImageLyricsRequest(BaseModel):
    """图片生成歌词请求"""
    image_url: str = Field(..., description="图片URL")
    prompt: Optional[str] = Field("", description="额外要求或风格提示")
    model: Optional[str] = Field(None, description="视觉模型ID")


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


class CoverFromSavedRequest(BaseModel):
    """基于已保存歌曲生成封面"""
    folder: str = Field(..., description="downloads 下的文件夹名（歌曲名或附带 task 前缀）")
    style: Optional[str] = Field(None, description="封面风格")
    title: Optional[str] = Field(None, description="歌曲标题（可选）")


class SaveMediaRequest(BaseModel):
    """保存图片/视频到本地"""
    url: str = Field(..., description="媒体URL")
    folder: str = Field(..., description="目标文件夹（downloads 下）")
    kind: str = Field("image", description="媒体类型 image|video")


class VideoTaskRequest(BaseModel):
    """视频任务状态查询"""
    task_id: str = Field(..., description="豆包视频任务ID")


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
        system_prompt = request.system_prompt or (
            "你是一位专业的中文歌曲作词人，擅长流行/民谣/摇滚等多种风格，"
            "请直接输出完整歌词文本，保留段落标签（如 [Verse] [Chorus]），不要解释。"
        )
        lyrics = client.generate_lyrics(
            prompt=request.prompt,
            system_prompt=system_prompt,
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


@router.post("/image/lyrics")
async def image_to_lyrics(request: ImageLyricsRequest):
    """
    图片生成歌词
    """
    client = get_doubao_client()

    try:
        result = client.image_to_lyrics(
            image_url=request.image_url,
            prompt=request.prompt,
            model=request.model
        )

        return {
            "code": 200,
            "data": {
                "lyrics": result.get("lyrics"),
                "title": result.get("title"),
                "description": result.get("description"),
                "raw": result.get("raw")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/video/task/{task_id}")
async def get_video_task(task_id: str):
    """
    查询视频任务状态
    """
    client = get_doubao_client()
    try:
        result = client.get_video_task(task_id)
        return {
            "code": 200,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image/cover-from-saved")
async def cover_from_saved(request: CoverFromSavedRequest):
    """
    基于 downloads/{folder}/lyrics.txt 生成封面
    """
    base_dir = pathlib.Path("downloads") / request.folder
    lyrics_file = base_dir / "lyrics.txt"
    if not lyrics_file.exists():
        alt = pathlib.Path("downloads") / _safe_name(request.folder) / "lyrics.txt"
        if alt.exists():
            lyrics_file = alt
        else:
            raise HTTPException(status_code=404, detail=f"未找到歌词文件: {lyrics_file}")

    try:
        lyrics_text = lyrics_file.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取歌词失败: {e}")

    prompt = f"根据以下歌词生成一张专辑封面，突出情绪和意境：\\n{lyrics_text}\\n风格：{request.style or '流行'}"
    client = get_doubao_client()
    try:
        result = client.generate_image(
            prompt=prompt,
            size="2K",
            model=None,
            watermark=False,
            response_format="url"
        )
        return {
            "code": 200,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/media/save")
async def save_media(request: SaveMediaRequest):
    """
    下载图片/视频到 downloads/{folder}
    """
    folder = pathlib.Path("downloads") / _safe_name(request.folder)
    folder.mkdir(parents=True, exist_ok=True)

    try:
        r = requests.get(request.url, timeout=300)
        r.raise_for_status()
        ext = _ext_from_content_type(r.headers.get("content-type", ""), request.kind)
        fname = folder / f"{request.kind}_{_safe_name(pathlib.Path(request.url).stem)}{ext}"
        with open(fname, "wb") as f:
            f.write(r.content)
        return {
            "code": 200,
            "data": {
                "path": str(fname)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
