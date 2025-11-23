"""
Suno API 路由

提供完整的 Suno 音乐生成 API 端点
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import tempfile
import pathlib
import requests
from pathlib import Path

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

class CoverFromSavedRequest(BaseModel):
    """基于已保存歌曲文件发起翻唱"""
    dir: str = Field(..., description="downloads 下的目录名或完整路径")
    track_index: int = Field(0, description="使用第几个音轨，默认0")
    prompt: Optional[str] = Field(None, description="歌词/提示")
    style: Optional[str] = Field(None, description="目标风格")
    title: Optional[str] = Field(None, description="新标题")


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

class SaveSongRequest(BaseModel):
    """保存歌曲与歌词请求"""
    task_id: str = Field(..., description="Suno 任务ID")
    lyrics_text: Optional[str] = Field(None, description="歌词文本")
    title: Optional[str] = Field(None, description="歌曲标题")
    style: Optional[str] = Field(None, description="歌曲风格")


def _safe_name(text: str) -> str:
    """简易文件名清洗"""
    bad = r'\\/:*?"<>|'
    for ch in bad:
        text = text.replace(ch, "_")
    return text.strip() or "untitled"

def _load_meta(dir_path: Path) -> Dict[str, Any]:
    meta_file = dir_path / "meta.json"
    if not meta_file.exists():
        return {}
    try:
        import json
        return json.loads(meta_file.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}


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
            "audio_id": track.get("audioId") or track.get("audio_id"),
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


@router.post("/save")
async def save_song(request: SaveSongRequest):
    """
    保存歌曲音频与歌词到本地 downloads/{task_id}

    - 自动获取 Suno 任务信息，下载 audio_url
    - 将歌词写入 lyrics.txt
    """
    client = get_suno_client()
    try:
        raw = client.get_music_info(request.task_id)
        info = normalize_suno_task(raw)
        tracks = info.get("tracks", [])
        if not tracks:
            raise HTTPException(status_code=400, detail="任务无可下载音频")

        # 以歌曲名作为目录名，避免任务ID命名
        title_from_track = tracks[0].get("title") if tracks else None
        title_final = request.title or title_from_track or f"song_{request.task_id[:6]}"
        folder_name = _safe_name(title_final)
        base_dir = Path("downloads") / folder_name
        # 若同名目录已存在，附加任务ID前缀避免覆盖，但仍以歌名为前缀
        if base_dir.exists() and base_dir.is_dir():
            base_dir = Path("downloads") / f"{folder_name}_{request.task_id[:8]}"
        base_dir.mkdir(parents=True, exist_ok=True)

        saved_files = []
        meta = {
            "task_id": request.task_id,
            "title": title_final,
            "style": request.style,
            "tracks": [],
        }
        for idx, t in enumerate(tracks, 1):
            url = t.get("audio_url") or t.get("stream_audio_url")
            if not url:
                continue
            resp = requests.get(url, timeout=300)
            resp.raise_for_status()
            fname = base_dir / f"{idx:02d}_{_safe_name(t.get('title') or 'track')}.mp3"
            with open(fname, "wb") as f:
                f.write(resp.content)
            saved_files.append(str(fname))
            meta["tracks"].append({
                "title": t.get("title"),
                "audio_id": t.get("audio_id") or t.get("id"),
                "audio_url": url,
                "stream_audio_url": t.get("stream_audio_url"),
                "file": str(fname)
            })

        # 写歌词
        if request.lyrics_text:
            lyric_file = base_dir / "lyrics.txt"
            with open(lyric_file, "w", encoding="utf-8") as f:
                f.write(request.lyrics_text)
            saved_files.append(str(lyric_file))
            meta["lyrics_file"] = str(lyric_file)

        # 写 meta
        try:
            meta_file = base_dir / "meta.json"
            meta_file.write_text(
                __import__("json").dumps(meta, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            saved_files.append(str(meta_file))
        except Exception:
            pass

        return {
            "code": 200,
            "data": {
                "saved": saved_files,
                "dir": str(base_dir)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


@router.get("/saved")
async def list_saved_songs():
    """
    列出 downloads 下保存的歌曲（基于 meta.json）
    """
    base = Path("downloads")
    items = []
    if not base.exists():
        return {"code": 200, "data": []}
    for folder in base.iterdir():
        if not folder.is_dir():
            continue
        meta_file = folder / "meta.json"
        if not meta_file.exists():
            continue
        try:
            meta = __import__("json").loads(meta_file.read_text(encoding="utf-8", errors="ignore"))
            items.append({
                "dir": str(folder),
                "task_id": meta.get("task_id"),
                "title": meta.get("title") or folder.name,
                "style": meta.get("style"),
                "tracks": meta.get("tracks") or [],
            })
        except Exception:
            continue
    return {"code": 200, "data": items}


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


class CoverFromSavedRequest(BaseModel):
    """基于已保存歌曲文件发起翻唱"""
    dir: str = Field(..., description="downloads 下的目录名或完整路径")
    track_index: int = Field(0, description="使用第几个音轨，默认0")
    prompt: Optional[str] = Field(None, description="歌词/提示")
    style: Optional[str] = Field(None, description="目标风格")
    title: Optional[str] = Field(None, description="新标题")


@router.post("/cover-from-saved")
async def cover_from_saved(request: CoverFromSavedRequest):
    """
    基于 downloads 下已保存的歌曲文件发起翻唱
    """
    base_dir = Path(request.dir)
    if not base_dir.exists():
        base_dir = Path("downloads") / request.dir
    if not base_dir.exists():
        raise HTTPException(status_code=404, detail=f"未找到目录: {request.dir}")

    meta = _load_meta(base_dir)
    tracks = meta.get("tracks") or []
    if not tracks:
        raise HTTPException(status_code=400, detail="目录中缺少 meta.json 或 tracks 为空")
    idx = max(0, min(request.track_index, len(tracks) - 1))
    track = tracks[idx]
    file_path = Path(track.get("file") or "")
    if not file_path.exists():
        # 尝试目录下匹配 mp3
        candidates = list(base_dir.glob("*.mp3"))
        if not candidates:
            raise HTTPException(status_code=404, detail="未找到可用的音频文件")
        file_path = candidates[idx % len(candidates)]

    client = get_suno_client()
    try:
        upload_url = client.upload_stream(str(file_path), upload_path="music", file_name=file_path.name)
        task_id = client.upload_cover(
            uploadUrl=upload_url,
            customMode=True,
            instrumental=False,
            model="V5",
            prompt=request.prompt,
            style=request.style or meta.get("style") or "Pop",
            title=request.title or meta.get("title") or file_path.stem,
            callback=None
        )
        return {
            "code": 200,
            "message": "翻唱任务已提交（基于本地已保存歌曲）",
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
