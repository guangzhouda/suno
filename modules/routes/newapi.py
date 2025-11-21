"""
New API 路由 - 支持文本对话和图像生成
统一API接口：https://api.voct.top
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger
from typing import Optional, List, Dict
import json

from ..models.llm import ChatRequest, ChatMessage
from ..clients.llm import NewAPIClient
from pydantic import BaseModel, Field

# 创建路由器
router = APIRouter(prefix="/api/newapi", tags=["New API"])

# 全局客户端实例（懒加载）
_newapi_client: Optional[NewAPIClient] = None


# ==================== Pydantic模型 ====================

class ImageGenerationRequest(BaseModel):
    """图像生成请求模型"""
    prompt: str = Field(..., description="图像描述提示词")
    model: Optional[str] = Field(default=None, description="图像模型，不指定则使用默认")
    size: str = Field(default="1024x1024", description="图片尺寸")
    n: int = Field(default=1, ge=1, le=10, description="生成数量")
    quality: str = Field(default="standard", description="图片质量: standard, hd")
    style: str = Field(default="vivid", description="风格: vivid, natural")
    response_format: str = Field(default="url", description="响应格式: url, b64_json")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "一只可爱的小猫坐在窗台上，温暖的阳光照进来，温馨治愈的画风",
                "size": "1024x1024",
                "quality": "standard",
                "style": "vivid"
            }
        }


class LyricsGenerationRequest(BaseModel):
    """歌词生成请求模型"""
    theme: str = Field(..., description="歌曲主题")
    emotion: str = Field(default="治愈", description="情绪：治愈、悲伤、热血等")
    style: str = Field(default="流行", description="音乐风格")
    language: str = Field(default="zh", description="语言：zh中文, en英文")
    structure: bool = Field(default=True, description="是否输出结构化歌词")

    class Config:
        json_schema_extra = {
            "example": {
                "theme": "跨年前夜的独白",
                "emotion": "治愈",
                "style": "City Pop",
                "language": "zh"
            }
        }


class LyricsRewriteRequest(BaseModel):
    """歌词改写请求模型"""
    original_lyrics: str = Field(..., description="原始歌词")
    mode: str = Field(..., description="改写模式：change_theme, change_language")
    target_theme: Optional[str] = Field(default=None, description="目标主题（换主题时使用）")
    target_language: Optional[str] = Field(default=None, description="目标语言（换语言时使用）")

    class Config:
        json_schema_extra = {
            "example": {
                "original_lyrics": "原歌词内容...",
                "mode": "change_theme",
                "target_theme": "友情"
            }
        }


# ==================== 客户端管理 ====================

def get_newapi_client() -> NewAPIClient:
    """获取New API客户端（单例模式）"""
    global _newapi_client

    if _newapi_client is None:
        from config import get_config
        config = get_config()

        if not config.is_enabled('newapi'):
            raise HTTPException(
                status_code=503,
                detail="New API服务未启用，请在配置文件中启用并配置API密钥"
            )

        api_key = config.get('newapi.api_key')
        text_model = config.get('newapi.text_model', 'deepseek-ai/DeepSeek-V3')
        image_model = config.get('newapi.image_model', 'doubao-seedream-4-0-250828')

        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="New API配置错误：未找到API密钥"
            )

        try:
            _newapi_client = NewAPIClient(
                api_key=api_key,
                text_model=text_model,
                image_model=image_model
            )
            logger.info(f"New API客户端初始化成功")
            logger.info(f"  文本模型: {text_model}")
            logger.info(f"  图像模型: {image_model}")
        except Exception as e:
            logger.error(f"New API客户端初始化失败: {e}")
            raise HTTPException(status_code=500, detail=f"客户端初始化失败: {str(e)}")

    return _newapi_client


# ==================== API端点 ====================

@router.get("/health")
async def health_check():
    """健康检查"""
    try:
        client = get_newapi_client()
        is_healthy = client.health_check()

        return {
            "status": "ok" if is_healthy else "error",
            "provider": "newapi",
            "text_model": client.default_model,
            "image_model": client.image_model
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    文本对话接口
    支持标准OpenAI格式
    """
    try:
        client = get_newapi_client()

        # 转换Pydantic模型为字典
        messages = [msg.dict() for msg in request.messages]

        # 非流式输出
        if not request.stream:
            response = client.chat(
                messages=messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p
            )

            return {
                "code": 200,
                "data": response
            }
        else:
            # 流式输出
            async def generate():
                try:
                    for chunk in client.chat_stream(
                        messages=messages,
                        model=request.model,
                        temperature=request.temperature,
                        max_tokens=request.max_tokens
                    ):
                        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    logger.error(f"流式输出错误: {e}")
                    yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

            return StreamingResponse(
                generate(),
                media_type="text/event-stream"
            )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"对话请求失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image/generate")
async def generate_image(request: ImageGenerationRequest):
    """
    图像生成接口
    使用doubao-seedream模型
    """
    try:
        client = get_newapi_client()

        response = client.generate_image(
            prompt=request.prompt,
            size=request.size,
            n=request.n,
            quality=request.quality,
            style=request.style,
            response_format=request.response_format
        )

        return {
            "code": 200,
            "data": response
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"图像生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lyrics/generate")
async def generate_lyrics(request: LyricsGenerationRequest):
    """
    歌词生成接口
    根据主题、情绪、风格生成结构化歌词
    """
    try:
        client = get_newapi_client()

        # 构建系统提示
        system_prompt = """你是一名专业作词人，会根据用户提供的主题和风格创作歌词。
输出统一使用 JSON 格式，包含以下字段：
- title: 歌曲标题
- language: 语言代码
- emotion: 情绪
- style: 音乐风格
- lyrics: 歌词对象，包含 verse_1, pre_chorus, chorus, verse_2, bridge 等段落

歌词要求：
1. 按 Verse / Chorus / Bridge 分段
2. 保持稳定的行数和节奏结构，便于谱曲
3. 用词精炼，少用过长句子
4. 根据情绪选择合适的用词和画面感
"""

        # 构建用户请求
        user_prompt = f"""请创作一首歌词，要求如下：
主题：{request.theme}
情绪：{request.emotion}
风格：{request.style}
语言：{request.language}

请输出JSON格式的结构化歌词。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # 调用对话接口
        response = client.chat(
            messages=messages,
            temperature=0.8,
            max_tokens=2000
        )

        # 提取歌词内容
        content = response['choices'][0]['message']['content']

        # 尝试解析JSON
        try:
            lyrics_data = json.loads(content)
        except json.JSONDecodeError:
            # 如果不是JSON，返回原始文本
            lyrics_data = {
                "title": "生成的歌词",
                "content": content
            }

        return {
            "code": 200,
            "data": lyrics_data
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"歌词生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lyrics/rewrite")
async def rewrite_lyrics(request: LyricsRewriteRequest):
    """
    歌词改写接口
    支持换主题、换语言等改写模式
    """
    try:
        client = get_newapi_client()

        # 构建系统提示
        system_prompt = """你是一名专业作词人，擅长在保留节奏结构的前提下改写歌词。

改写要求：
1. 保留每段的行数和大致节奏（音节数差不多）
2. 如果是换主题，要用新的意象，但不抄原句
3. 如果是换语言，要忠实传达情绪，同时考虑唱起来顺口

输出 JSON 格式：
- mode: 改写模式
- target_theme 或 target_language: 目标主题或语言
- rewritten_lyrics: 改写后的歌词（保留段落结构）
- notes: 改写思路说明
"""

        # 构建用户请求
        mode_text = {
            "change_theme": f"换主题到：{request.target_theme}",
            "change_language": f"翻译为：{request.target_language}"
        }.get(request.mode, "改写")

        user_prompt = f"""请改写以下歌词：

【原歌词】
{request.original_lyrics}

【改写要求】
模式：{mode_text}

请输出JSON格式的改写结果。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # 调用对话接口
        response = client.chat(
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )

        # 提取改写内容
        content = response['choices'][0]['message']['content']

        # 尝试解析JSON
        try:
            rewritten_data = json.loads(content)
        except json.JSONDecodeError:
            rewritten_data = {
                "mode": request.mode,
                "content": content
            }

        return {
            "code": 200,
            "data": rewritten_data
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"歌词改写失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models():
    """获取可用模型列表"""
    try:
        client = get_newapi_client()

        return {
            "code": 200,
            "data": {
                "provider": "newapi",
                "text_model": client.default_model,
                "image_model": client.image_model,
                "available_text_models": [
                    {
                        "id": "deepseek-ai/DeepSeek-V3",
                        "name": "DeepSeek V3",
                        "description": "强大的文本生成模型"
                    }
                ],
                "available_image_models": [
                    {
                        "id": "doubao-seedream-4-0-250828",
                        "name": "Doubao SeedDream",
                        "description": "高质量图像生成模型"
                    }
                ]
            }
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"获取模型列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
