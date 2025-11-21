"""
创意音乐工作流路由

整合 Suno 和 Doubao API，提供完整的音乐创作工作流：
1. 灵感写歌：Doubao生成歌词 + Suno生成音乐
2. 图片成歌：Doubao图像理解 + Doubao生成歌词 + Suno生成音乐
3. AI翻唱：上传音频 + Suno翻唱
4. MV生成：Suno音乐 + Doubao生成视频
"""

import tempfile
import pathlib
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

from modules.clients.suno import SunoClient
from modules.clients.doubao import DoubaoClient
from config import get_config

router = APIRouter(prefix="/api/creative", tags=["创意工作流"])


def get_suno_client() -> SunoClient:
    """获取 Suno 客户端"""
    try:
        return SunoClient()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suno 客户端初始化失败: {str(e)}")


def get_doubao_client() -> DoubaoClient:
    """获取 Doubao 客户端"""
    try:
        return DoubaoClient()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Doubao 客户端初始化失败: {str(e)}")


def _run_image_to_song_workflow(
    image_reference: str,
    additional_prompt: Optional[str],
    auto_generate: bool,
    model: str
) -> Dict[str, Any]:
    doubao = get_doubao_client()
    image_analysis = doubao.image_to_song_description(image_reference)

    lyrics_prompt = f"""
请根据以下图片分析结果创作一首完整的歌词：

【场景】
{image_analysis.get('scene', '未知')}

【情绪氛围】
{image_analysis.get('emotion', '未知')}

【色彩基调】
{image_analysis.get('color_tone', '未知')}

【推荐风格】
{image_analysis.get('style', '流行')}

【额外提示】
{additional_prompt or '无'}

要求：
1. 歌词要与图片的氛围高度契合
2. 运用图片中的视觉元素作为歌词意象
3. 情感表达要与图片传递的情绪一致
4. 结构完整（主歌、副歌、桥段）
5. 只输出歌词，不要额外说明
"""

    lyrics = doubao.generate_lyrics(
        prompt=lyrics_prompt,
        temperature=0.8
    )

    result = {
        "image_analysis": image_analysis,
        "lyrics": lyrics,
        "recommended_style": image_analysis.get('style', '流行')
    }

    if auto_generate:
        suno = get_suno_client()
        music_style = image_analysis.get('style', '流行')
        task_id = suno.generate_music(
            prompt=lyrics,
            customMode=True,
            style=music_style,
            title=f"图片创作 - {image_analysis.get('emotion', 'Untitled')[:20]}",
            instrumental=False,
            model=model
        )

        result["music_task_id"] = task_id
        result["message"] = "图片已分析，歌词已生成，音乐正在创作中"
    else:
        result["message"] = "图片已分析，歌词已生成"

    return result


# ==================== Pydantic 模型 ====================

class InspirationSongRequest(BaseModel):
    """灵感写歌请求"""
    inspiration: str = Field(..., description="创作灵感或主题")
    style: str = Field("流行", description="音乐风格")
    mood: Optional[str] = Field(None, description="情绪基调")
    instrumental: bool = Field(False, description="是否纯音乐")
    auto_generate: bool = Field(True, description="自动生成音乐")
    model: str = Field("V5", description="Suno模型版本")


class ImageToSongRequest(BaseModel):
    """图片成歌请求"""
    image_url: str = Field(..., description="图片URL")
    additional_prompt: Optional[str] = Field(None, description="额外的创作提示")
    auto_generate: bool = Field(True, description="自动生成音乐")
    model: str = Field("V5", description="Suno模型版本")


class CoverWorkflowRequest(BaseModel):
    """翻唱工作流请求"""
    audio_url: str = Field(..., description="原音频URL")
    target_style: str = Field(..., description="目标风格")
    new_title: Optional[str] = Field(None, description="新标题")
    new_lyrics: Optional[str] = Field(None, description="新歌词")
    model: str = Field("V5", description="Suno模型版本")


class MusicVideoRequest(BaseModel):
    """音乐MV生成请求"""
    music_url: Optional[str] = Field(None, description="音乐URL（如果已生成）")
    lyrics: str = Field(..., description="歌词")
    style: str = Field("流行", description="音乐风格")
    cover_image_url: Optional[str] = Field(None, description="封面图片URL")
    ratio: str = Field("16:9", description="视频比例")
    duration: int = Field(5, description="视频时长（秒）")


# ==================== 工作流端点 ====================

@router.get("/health")
async def health_check():
    """健康检查"""
    try:
        suno = get_suno_client()
        doubao = get_doubao_client()

        suno_credits = suno.get_credits()

        return {
            "status": "ok",
            "service": "Creative Workflow",
            "suno_credits": suno_credits,
            "doubao_models": doubao.models
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/inspiration-song")
async def create_inspiration_song(request: InspirationSongRequest):
    """
    灵感写歌工作流

    流程：
    1. 使用 Doubao DeepSeek-V3 根据灵感生成歌词
    2. 使用 Suno 根据歌词生成音乐

    返回生成的歌词和音乐任务ID
    """
    doubao = get_doubao_client()
    suno = get_suno_client()

    try:
        # Step 1: 生成歌词
        lyrics_prompt = f"""
请根据以下创作灵感创作一首完整的歌词：

【创作灵感】
{request.inspiration}

【音乐风格】
{request.style}

【情绪基调】
{request.mood or "自然流露"}

要求：
1. 歌词结构完整（主歌、副歌、桥段）
2. 符合{request.style}风格的特点
3. 情感表达真挚自然
4. 适合演唱的韵律和节奏
5. 不要添加任何额外的说明，只输出歌词本身
"""

        lyrics = doubao.generate_lyrics(
            prompt=lyrics_prompt,
            temperature=0.8
        )

        result = {
            "lyrics": lyrics,
            "inspiration": request.inspiration,
            "style": request.style
        }

        # Step 2: 自动生成音乐
        if request.auto_generate:
            task_id = suno.generate_music(
                prompt=lyrics,
                customMode=True,
                style=request.style,
                title=f"灵感创作 - {request.inspiration[:20]}",
                instrumental=request.instrumental,
                model=request.model
            )

            result["music_task_id"] = task_id
            result["message"] = "歌词已生成，音乐正在创作中"
        else:
            result["message"] = "歌词已生成，请调用 /api/suno/generate 生成音乐"

        return {
            "code": 200,
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image-to-song")
async def create_image_to_song(request: ImageToSongRequest):
    """
    图片成歌工作流

    流程：
    1. 使用 Doubao Vision 分析图片，提取音乐元素
    2. 使用 Doubao DeepSeek-V3 根据图片分析生成歌词
    3. 使用 Suno 生成音乐
    """
    try:
        result = _run_image_to_song_workflow(
            image_reference=request.image_url,
            additional_prompt=request.additional_prompt,
            auto_generate=request.auto_generate,
            model=request.model
        )

        return {"code": 200, "data": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image-to-song/upload")
async def create_image_to_song_from_upload(
    image_file: UploadFile = File(...),
    additional_prompt: Optional[str] = Form(None),
    auto_generate: bool = Form(True),
    model: str = Form("V5")
):
    """
    图片成歌（文件上传）
    """
    if not image_file.content_type or not image_file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="请上传图片文件")

    try:
        content = await image_file.read()
        if not content:
            raise HTTPException(status_code=400, detail="图片内容为空")

        suffix = pathlib.Path(image_file.filename or "").suffix or ".png"
        tmp_path: Optional[str] = None
        upload_url: Optional[str] = None

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            suno = get_suno_client()
            try:
                upload_url = suno.upload_stream(
                    file_path=tmp_path,
                    upload_path="images/image-to-song",
                    file_name=image_file.filename or pathlib.Path(tmp_path).name
                )
            except Exception as upload_exc:
                raise HTTPException(status_code=500, detail=f"图片上传失败: {upload_exc}") from upload_exc

        finally:
            if tmp_path:
                try:
                    pathlib.Path(tmp_path).unlink()
                except OSError:
                    pass

        if not upload_url:
            raise HTTPException(status_code=500, detail="图片上传失败：未获取可访问 URL")

        try:
            result = _run_image_to_song_workflow(
                image_reference=upload_url,
                additional_prompt=additional_prompt,
                auto_generate=auto_generate,
                model=model
            )
        except Exception as workflow_exc:
            raise HTTPException(status_code=500, detail=f"图片分析失败: {workflow_exc}") from workflow_exc

        return {"code": 200, "data": result}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cover-workflow")
async def create_cover(request: CoverWorkflowRequest):
    """
    翻唱工作流

    流程：
    1. 验证音频URL可访问
    2. 调用 Suno 翻唱功能

    支持：
    - 改变风格（民谣→摇滚）
    - 改变音色（男声→女声）
    - 多语言翻唱
    """
    suno = get_suno_client()

    try:
        # 调用 Suno 翻唱
        task_id = suno.upload_cover(
            uploadUrl=request.audio_url,
            customMode=True,
            instrumental=False,
            model=request.model,
            prompt=request.new_lyrics,
            style=request.target_style,
            title=request.new_title
        )

        return {
            "code": 200,
            "data": {
                "task_id": task_id,
                "target_style": request.target_style,
                "message": "翻唱任务已提交，请使用 task_id 查询进度"
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-cover")
async def upload_and_cover(
    file: UploadFile = File(...),
    target_style: str = Form(...),
    new_title: Optional[str] = Form(None),
    new_lyrics: Optional[str] = Form(None),
    model: str = Form("V5")
):
    """
    上传音频并翻唱

    先上传文件到 Suno，然后进行翻唱
    """
    suno = get_suno_client()

    # 保存到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=pathlib.Path(file.filename).suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # 上传文件
        file_url = suno.upload_stream(
            file_path=tmp_path,
            upload_path="music",
            file_name=file.filename
        )

        # 翻唱
        task_id = suno.upload_cover(
            uploadUrl=file_url,
            customMode=True,
            instrumental=False,
            model=model,
            prompt=new_lyrics,
            style=target_style,
            title=new_title
        )

        return {
            "code": 200,
            "data": {
                "uploaded_url": file_url,
                "task_id": task_id,
                "target_style": target_style,
                "message": "文件已上传，翻唱任务已提交"
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 清理临时文件
        try:
            pathlib.Path(tmp_path).unlink()
        except:
            pass


@router.post("/music-video")
async def create_music_video(request: MusicVideoRequest):
    """
    音乐MV生成工作流

    流程：
    1. 如果没有音乐URL，先生成音乐
    2. 使用 Doubao 根据歌词生成MV视频
    """
    doubao = get_doubao_client()
    suno = get_suno_client()

    try:
        result = {}

        # Step 1: 如果没有音乐，先生成
        if not request.music_url:
            music_task_id = suno.generate_music(
                prompt=request.lyrics,
                customMode=True,
                style=request.style,
                title=f"MV音乐 - {request.style}",
                instrumental=False,
                model="V5"
            )

            result["music_task_id"] = music_task_id
            result["music_status"] = "generating"

        # Step 2: 生成MV视频
        video_result = doubao.create_music_video(
            lyrics=request.lyrics,
            style=request.style,
            image_url=request.cover_image_url
        )

        result["video_task_id"] = video_result.get("task_id")
        result["video_status"] = "generating"
        result["message"] = "MV视频生成任务已提交"

        return {
            "code": 200,
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/full-workflow")
async def full_creative_workflow(
    inspiration: str = Form(...),
    style: str = Form("流行"),
    create_cover: bool = Form(False),
    create_video: bool = Form(False),
    cover_image_url: Optional[str] = Form(None)
):
    """
    完整创作工作流

    一站式完成：
    1. 生成歌词
    2. 生成音乐
    3. （可选）生成专辑封面
    4. （可选）生成MV视频
    """
    doubao = get_doubao_client()
    suno = get_suno_client()

    try:
        result = {}

        # Step 1: 生成歌词
        lyrics_prompt = f"根据'{inspiration}'创作一首{style}风格的完整歌词"
        lyrics = doubao.generate_lyrics(prompt=lyrics_prompt, temperature=0.8)
        result["lyrics"] = lyrics

        # Step 2: 生成音乐
        music_task_id = suno.generate_music(
            prompt=lyrics,
            customMode=True,
            style=style,
            title=f"{inspiration[:20]}",
            instrumental=False,
            model="V5"
        )
        result["music_task_id"] = music_task_id

        # Step 3: 生成封面（可选）
        if create_cover:
            cover_prompt = f"{style}风格专辑封面，主题：{inspiration}"
            cover_result = doubao.generate_image(prompt=cover_prompt, size="2K")
            result["cover_url"] = cover_result.get("url")

        # Step 4: 生成MV（可选）
        if create_video:
            video_result = doubao.create_music_video(
                lyrics=lyrics,
                style=style,
                image_url=cover_image_url or result.get("cover_url")
            )
            result["video_task_id"] = video_result.get("task_id")

        result["message"] = "完整创作流程已启动"

        return {
            "code": 200,
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
