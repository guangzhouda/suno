"""
Suno API 路由

提供完整的 Suno 音乐生成 API 端点
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import tempfile
import pathlib

from modules.clients.suno import SunoClient
from config import get_config

router = APIRouter(prefix="/api/suno", tags=["Suno音乐"])


def get_suno_client() -> SunoClient:
    """获取 Suno 客户端实例"""
    try:
        return SunoClient()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suno 客户端初始化失败: {str(e)}")


# ==================== Pydantic 模型 ====================

class GenerateMusicRequest(BaseModel):
    """音乐生成请求"""
    prompt: str = Field(..., description="提示词或歌词")
    customMode: bool = Field(False, description="自定义模式")
    instrumental: bool = Field(False, description="是否纯音乐")
    model: str = Field("V5", description="模型版本")
    title: Optional[str] = Field(None, description="歌曲标题（customMode=true时必需）")
    style: Optional[str] = Field(None, description="音乐风格（customMode=true时必需）")
    callback: Optional[str] = Field(None, description="回调URL")


class CoverMusicRequest(BaseModel):
    """翻唱请求"""
    uploadUrl: str = Field(..., description="音频文件URL")
    customMode: bool = Field(True, description="自定义模式")
    instrumental: bool = Field(False, description="是否纯音乐")
    model: str = Field("V5", description="模型版本")
    prompt: Optional[str] = Field(None, description="新歌词")
    style: Optional[str] = Field(None, description="目标风格")
    title: Optional[str] = Field(None, description="新标题")
    callback: Optional[str] = Field(None, description="回调URL")


class ExtendMusicRequest(BaseModel):
    """延长音乐请求"""
    audio_id: str = Field(..., description="原音频ID")
    model: str = Field("V5", description="模型版本")
    continueAt: Optional[int] = Field(None, description="延长位置（秒）")
    defaultParamFlag: bool = Field(False, description="使用默认参数")
    title: Optional[str] = Field(None, description="标题")
    style: Optional[str] = Field(None, description="风格")
    prompt: Optional[str] = Field(None, description="续写提示")
    callback: Optional[str] = Field(None, description="回调URL")


class SeparateVocalsRequest(BaseModel):
    """人声分离请求"""
    task_id: str = Field(..., description="原任务ID")
    audio_id: str = Field(..., description="音频ID")
    sep_type: str = Field("separate_vocal", description="分离类型")
    callback: Optional[str] = Field(None, description="回调URL")


class LyricsRequest(BaseModel):
    """歌词生成请求"""
    prompt: str = Field(..., description="歌词创作提示")
    callback: Optional[str] = Field(None, description="回调URL")


# ==================== API 端点 ====================


def normalize_suno_task(raw: Dict[str, Any]) -> Dict[str, Any]:
    """标准化 Suno 任务响应，便于前端消费"""
    status = (raw or {}).get("status") or ""
    status_upper = status.upper()
    status_map = {
        "SUCCESS": "complete",
        "FINISH": "complete",
        "FAILED": "error",
        "FAIL": "error",
        "ERROR": "error",
    }
    normalized_status = status_map.get(status_upper, "processing")

    response = (raw or {}).get("response") or {}
    raw_tracks = response.get("sunoData") or raw.get("data") or []
    tracks = []
    for track in raw_tracks:
        if not isinstance(track, dict):
            continue
        tracks.append({
            "id": track.get("id"),
            "audio_url": track.get("audioUrl") or track.get("audio_url"),
            "stream_audio_url": track.get("streamAudioUrl") or track.get("stream_audio_url"),
            "image_url": track.get("imageUrl") or track.get("image_url"),
            "title": track.get("title"),
            "model_name": track.get("modelName") or track.get("model_name"),
            "tags": track.get("tags"),
            "duration": track.get("duration"),
            "created_at": track.get("createTime") or track.get("create_time"),
        })

    return {
        "task_id": raw.get("taskId") or response.get("taskId"),
        "status": normalized_status,
        "tracks": tracks,
        "raw_status": status,
        "message": raw.get("errorMessage") or raw.get("msg"),
        "error_code": raw.get("errorCode"),
        "error_message": raw.get("errorMessage"),
        "type": raw.get("type"),
    }

@router.get("/health")
async def health_check():
    """健康检查"""
    try:
        client = get_suno_client()
        credits = client.get_credits()
        return {
            "status": "ok",
            "service": "Suno API",
            "credits": credits
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/credits")
async def get_credits():
    """获取剩余积分"""
    client = get_suno_client()
    try:
        credits = client.get_credits()
        return {
            "code": 200,
            "data": {
                "credits": credits
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 音乐生成 ====================

@router.post("/generate")
async def generate_music(request: GenerateMusicRequest):
    """
    生成音乐

    支持两种模式：
    - customMode=false: 简单模式，只需提供 prompt
    - customMode=true: 自定义模式，需提供 style、title、prompt（歌词）
    """
    client = get_suno_client()

    try:
        task_id = client.generate_music(
            prompt=request.prompt,
            customMode=request.customMode,
            instrumental=request.instrumental,
            model=request.model,
            title=request.title,
            style=request.style,
            callback=request.callback
        )

        return {
            "code": 200,
            "message": "音乐生成任务已提交",
            "data": {
                "task_id": task_id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/{task_id}")
async def get_task_status(task_id: str):
    """查询音乐生成任务状态"""
    client = get_suno_client()

    try:
        raw_result = client.get_music_info(task_id)
        result = normalize_suno_task(raw_result)
        return {
            "code": 200,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 翻唱功能 ====================

@router.post("/cover")
async def cover_music(request: CoverMusicRequest):
    """
    AI 翻唱

    上传音频文件并进行翻唱：
    - 改变风格（民谣→摇滚）
    - 改变音色（男声→女声）
    - 多语言翻唱
    """
    client = get_suno_client()

    try:
        task_id = client.upload_cover(
            uploadUrl=request.uploadUrl,
            customMode=request.customMode,
            instrumental=request.instrumental,
            model=request.model,
            prompt=request.prompt,
            style=request.style,
            title=request.title,
            callback=request.callback
        )

        return {
            "code": 200,
            "message": "翻唱任务已提交",
            "data": {
                "task_id": task_id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 文件上传 ====================

@router.post("/upload/stream")
async def upload_audio_file(
    file: UploadFile = File(...),
    upload_path: str = Form("music")
):
    """
    上传音频文件（用于翻唱）

    返回可访问的文件 URL
    """
    client = get_suno_client()

    # 保存到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=pathlib.Path(file.filename).suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # 上传到 Suno
        file_url = client.upload_stream(
            file_path=tmp_path,
            upload_path=upload_path,
            file_name=file.filename
        )

        return {
            "code": 200,
            "message": "文件上传成功",
            "data": {
                "url": file_url,
                "filename": file.filename
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


@router.post("/upload/url")
async def upload_audio_from_url(
    file_url: str = Form(...),
    upload_path: str = Form("music"),
    file_name: Optional[str] = Form(None)
):
    """从 URL 上传音频文件"""
    client = get_suno_client()

    try:
        uploaded_url = client.upload_from_url(
            file_url=file_url,
            upload_path=upload_path,
            file_name=file_name
        )

        return {
            "code": 200,
            "message": "文件上传成功",
            "data": {
                "url": uploaded_url
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 延长音乐 ====================

@router.post("/extend")
async def extend_music(request: ExtendMusicRequest):
    """延长现有音乐"""
    client = get_suno_client()

    try:
        task_id = client.extend_music(
            audio_id=request.audio_id,
            model=request.model,
            continueAt=request.continueAt,
            defaultParamFlag=request.defaultParamFlag,
            title=request.title,
            style=request.style,
            prompt=request.prompt,
            callback=request.callback
        )

        return {
            "code": 200,
            "message": "延长任务已提交",
            "data": {
                "task_id": task_id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 人声处理 ====================

@router.post("/separate-vocals")
async def separate_vocals(request: SeparateVocalsRequest):
    """人声/伴奏分离"""
    client = get_suno_client()

    try:
        task_id = client.separate_vocals(
            task_id=request.task_id,
            audio_id=request.audio_id,
            sep_type=request.sep_type,
            callback=request.callback
        )

        return {
            "code": 200,
            "message": "人声分离任务已提交",
            "data": {
                "task_id": task_id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vocal-task/{task_id}")
async def get_vocal_task_status(task_id: str):
    """查询人声分离任务状态"""
    client = get_suno_client()

    try:
        result = client.get_vocal_info(task_id)
        return {
            "code": 200,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 歌词生成 ====================

@router.post("/lyrics")
async def create_lyrics(request: LyricsRequest):
    """生成歌词"""
    client = get_suno_client()

    try:
        task_id = client.create_lyrics(
            prompt=request.prompt,
            callback=request.callback
        )

        return {
            "code": 200,
            "message": "歌词生成任务已提交",
            "data": {
                "task_id": task_id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lyrics-task/{task_id}")
async def get_lyrics_task_status(task_id: str):
    """查询歌词生成任务状态"""
    client = get_suno_client()

    try:
        result = client.get_lyrics_info(task_id)
        return {
            "code": 200,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 工具功能 ====================

@router.post("/to-wav")
async def convert_to_wav(
    task_id: str = Form(...),
    audio_id: str = Form(...),
    callback: Optional[str] = Form(None)
):
    """转换为 WAV 格式"""
    client = get_suno_client()

    try:
        wav_task_id = client.convert_wav(
            task_id=task_id,
            audio_id=audio_id,
            callback=callback
        )

        return {
            "code": 200,
            "message": "WAV 转换任务已提交",
            "data": {
                "task_id": wav_task_id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wav-task/{task_id}")
async def get_wav_task_status(task_id: str):
    """查询 WAV 转换任务状态"""
    client = get_suno_client()

    try:
        result = client.get_wav_info(task_id)
        return {
            "code": 200,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Persona & Extend 功能 ====================

class GeneratePersonaRequest(BaseModel):
    """生成 Persona 请求"""
    taskId: str = Field(..., description="原始音乐生成任务ID")
    audioId: str = Field(..., description="音频ID")
    name: str = Field(..., description="Persona名称")
    description: str = Field(..., description="Persona描述")


class ExtendMusicRequest(BaseModel):
    """音乐扩展请求"""
    audioId: str = Field(..., description="要扩展的音频ID")
    defaultParamFlag: bool = Field(True, description="使用自定义参数")
    continueAt: int = Field(..., description="从第几秒开始扩展")
    prompt: str = Field(..., description="扩展提示词")
    style: str = Field(..., description="音乐风格")
    title: str = Field(..., description="标题")
    model: str = Field("V5", description="模型版本")
    personaId: Optional[str] = Field(None, description="Persona ID")


@router.post("/persona")
async def generate_persona(request: GeneratePersonaRequest):
    """
    生成 Persona

    基于已生成的音乐创建 Persona,赋予音乐独特的身份和特征
    """
    client = get_suno_client()

    try:
        result = client._post('/generate/generate-persona', json={
            "taskId": request.taskId,
            "audioId": request.audioId,
            "name": request.name,
            "description": request.description
        })

        if result.get('code') != 200:
            raise HTTPException(status_code=400, detail=result.get('msg', 'Persona 生成失败'))

        return {
            "code": 200,
            "msg": "success",
            "data": result['data']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extend")
async def extend_music(request: ExtendMusicRequest):
    """
    扩展音乐

    延长或修改现有音乐轨道
    """
    client = get_suno_client()

    try:
        payload = {
            "audioId": request.audioId,
            "defaultParamFlag": request.defaultParamFlag,
            "model": request.model,
            "callBackUrl": "https://example.invalid/extend"  # 占位URL
        }

        if request.defaultParamFlag:
            payload.update({
                "continueAt": request.continueAt,
                "prompt": request.prompt,
                "style": request.style,
                "title": request.title
            })

        if request.personaId:
            payload["personaId"] = request.personaId

        result = client._post('/generate/extend', json=payload)

        if result.get('code') != 200:
            raise HTTPException(status_code=400, detail=result.get('msg', '音乐扩展失败'))

        task_id = result['data']['taskId']
        return {
            "code": 200,
            "msg": "success",
            "data": task_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
