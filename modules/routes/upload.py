"""
简单的图片上传到 Suno 上传接口，返回公网 URL（复用 /api/suno/upload/stream）。
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from modules.clients.suno import SunoClient

router = APIRouter(prefix="/api/upload", tags=["上传"])


def get_suno_client() -> SunoClient:
    try:
        return SunoClient()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suno 客户端初始化失败: {str(e)}")


@router.post("/image")
async def upload_image(file: UploadFile = File(...), upload_path: str = Form("music")):
    """
    上传图片到 Suno 存储，获取公网 URL（用于豆包图片理解/生成）
    """
    client = get_suno_client()
    try:
        # 直接上传文件对象，返回公网 URL
        url = client.upload_fileobj(fileobj=file.file, upload_path=upload_path, file_name=file.filename)
        return {"code": 200, "data": {"url": url}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
