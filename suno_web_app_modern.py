# -*- coding: utf-8 -*-
"""
Suno API Web 版 · 全量功能演示（FastAPI + 原生 HTML/JS，美化版）
Python 3.10+

依赖：
    pip install fastapi uvicorn requests python-multipart

环境变量：
    SUNO_API_KEY=你的Key

启动（任选其一）：
    # 方式A：直接运行（不热重载）
    python suno_web_app.py

    # 方式B：命令行热重载（推荐开发时）
    uvicorn suno_web_app:app --reload --port 8000

打开：
    http://localhost:8000
"""

import os
import re
import json
import time
import base64
import tempfile
import pathlib
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

import requests
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator

# ---------------- 基础常量与目录 ----------------
API_BASE = "https://api.sunoapi.org/api/v1"
UPLOAD_BASE = "https://sunoapiorg.redpandaai.co/api"  # 文档里的上传域（仅用于上传接口）
OUT_DIR = pathlib.Path("suno_outputs")
OUT_DIR.mkdir(exist_ok=True)

# ---------------- 小工具 ----------------
def _norm(d: Dict[str, Any] | None, *keys: str) -> Any:
    """兼容不同字段命名：依次取第一个存在的键"""
    for k in keys:
        if isinstance(d, dict) and k in d and d[k] is not None:
            return d[k]
    return None

def _slug(s: str, fallback: str = "file") -> str:
    s = (s or "").strip()
    s = re.sub(r"[^\w\s\.-]", "", s, flags=re.UNICODE)
    s = re.sub(r"\s+", "_", s)
    return s or fallback

def _guess_ext_from_url(url: str, default: str) -> str:
    p = urlparse(url)
    name = pathlib.Path(p.path).name
    if "." in name:
        ext = name.split(".")[-1].lower()
        if len(ext) <= 5:
            return "." + ext
    return default

def _download_to_media(url: str, basename: str, default_ext: str) -> str:
    """下载远程文件到 OUT_DIR，返回 /media/xxx 相对路径"""
    if not url:
        raise RuntimeError("下载URL为空")
    ext = _guess_ext_from_url(url, default_ext)
    fname = f"{_slug(basename)}{ext}"
    out_path = OUT_DIR / fname
    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(131072):
                if chunk:
                    f.write(chunk)
    return f"/media/{fname}"

# ---------------- Suno 客户端 ----------------
class SunoClient:
    def __init__(self, api_key: Optional[str] = None, poll_interval: int = 8, timeout: int = 900):
        # 多种方式读取 API Key，优先级：参数 > 配置文件 > 环境变量
        if api_key:
            self.api_key = api_key
        else:
            # 尝试从 config.json 读取
            config_file = pathlib.Path("config.json")
            if config_file.exists():
                try:
                    with open(config_file, encoding="utf-8") as f:
                        config = json.load(f)
                        self.api_key = config.get("SUNO_API_KEY")
                except Exception as e:
                    print(f"警告：读取 config.json 失败: {e}")

            # 从环境变量读取
            if not self.api_key:
                self.api_key = os.getenv("SUNO_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "缺少 API Key！请使用以下任一方式配置：\n"
                "1. 在程序目录创建 config.json 文件，内容：{\"SUNO_API_KEY\": \"your-key\"}\n"
                "2. 设置环境变量 SUNO_API_KEY\n"
                "3. 复制 config.example.json 为 config.json 并填入你的 Key"
            )
        self.poll_interval = poll_interval
        self.timeout = timeout
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.json_headers = dict(self.headers)
        self.json_headers["Content-Type"] = "application/json"

    # ---- 基础请求（含简单重试） ----
    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{API_BASE}{path}"
        for _ in range(3):
            r = requests.get(url, headers=self.headers, params=params, timeout=60)
            if r.status_code >= 500:
                time.sleep(1)
                continue
            r.raise_for_status()
            return r.json()
        r.raise_for_status()
        return {}

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{API_BASE}{path}"
        for _ in range(3):
            r = requests.post(url, headers=self.json_headers, json=payload, timeout=60)
            if r.status_code >= 500:
                time.sleep(1)
                continue
            r.raise_for_status()
            return r.json()
        r.raise_for_status()
        return {}

    # ---- 账户 ----
    def get_credits(self) -> int:
        res = self._get("/generate/credit")
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]

    # ---- 歌词 ----
    def create_lyrics(self, prompt: str, callback: Optional[str] = None) -> str:
        payload = {"prompt": prompt, "callBackUrl": callback or "https://example.invalid/lyrics"}
        res = self._post("/lyrics", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    def get_lyrics_info(self, task_id: str) -> Dict[str, Any]:
        res = self._get("/lyrics/record-info", params={"taskId": task_id})
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]

    def get_timestamped_lyrics(self, task_id: str, audio_id: str) -> Dict[str, Any]:
        payload = {"taskId": task_id, "audioId": audio_id}
        res = self._post("/generate/get-timestamped-lyrics", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]

    # ---- 生成音乐 ----
    def generate_music(
        self,
        *,
        prompt: str,
        customMode: bool,
        instrumental: bool,
        model: str = "V4_5",
        title: Optional[str] = None,
        style: Optional[str] = None,
        callback: Optional[str] = None,
        personaId: Optional[str] = None,
        negativeTags: Optional[str] = None,
        vocalGender: Optional[str] = None,
        styleWeight: Optional[float] = None,
        weirdnessConstraint: Optional[float] = None,
        audioWeight: Optional[float] = None,
    ) -> str:
        payload: Dict[str, Any] = {
            "customMode": customMode,
            "instrumental": instrumental,
            "model": model,
            "callBackUrl": callback or "https://example.invalid/music",
        }
        if customMode:
            if not style or not title:
                raise ValueError("customMode=True 时必须提供 style 和 title")
            payload.update({"style": style, "title": title})
            if not instrumental:
                payload["prompt"] = prompt
            if personaId:
                payload["personaId"] = personaId
        else:
            payload["prompt"] = prompt

        if negativeTags is not None: payload["negativeTags"] = negativeTags
        if vocalGender is not None:  payload["vocalGender"] = vocalGender
        if styleWeight is not None:  payload["styleWeight"] = float(styleWeight)
        if weirdnessConstraint is not None: payload["weirdnessConstraint"] = float(weirdnessConstraint)
        if audioWeight is not None:  payload["audioWeight"] = float(audioWeight)

        res = self._post("/generate", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    def get_music_info(self, task_id: str) -> Dict[str, Any]:
        res = self._get("/generate/record-info", params={"taskId": task_id})
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]

    # ---- 延长音乐 ----
    def extend_music(
        self,
        audio_id: str,
        *,
        model: str,
        continueAt: Optional[int] = None,
        defaultParamFlag: bool = False,
        title: Optional[str] = None,
        style: Optional[str] = None,
        prompt: Optional[str] = None,
        callback: Optional[str] = None,
    ) -> str:
        payload: Dict[str, Any] = {
            "audioId": audio_id,
            "model": model,
            "defaultParamFlag": defaultParamFlag,
            "callBackUrl": callback or "https://example.invalid/extend",
        }
        if defaultParamFlag:
            if continueAt is None or not title or not style:
                raise ValueError("defaultParamFlag=True 时必须提供 continueAt/title/style")
            payload.update({"continueAt": continueAt, "title": title, "style": style})
            if prompt:
                payload["prompt"] = prompt
        res = self._post("/generate/extend", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    # ---- 上传并扩展 ----
    def upload_and_extend(
        self,
        *,
        uploadUrl: str,
        model: str,
        defaultParamFlag: bool,
        instrumental: Optional[bool] = None,
        prompt: Optional[str] = None,
        style: Optional[str] = None,
        title: Optional[str] = None,
        continueAt: Optional[int] = None,
        personaId: Optional[str] = None,
        negativeTags: Optional[str] = None,
        vocalGender: Optional[str] = None,
        styleWeight: Optional[float] = None,
        weirdnessConstraint: Optional[float] = None,
        audioWeight: Optional[float] = None,
        callback: Optional[str] = None,
    ) -> str:
        payload: Dict[str, Any] = {
            "uploadUrl": uploadUrl,
            "model": model,
            "defaultParamFlag": defaultParamFlag,
            "callBackUrl": callback or "https://example.invalid/upload-extend",
        }
        if instrumental is not None:
            payload["instrumental"] = bool(instrumental)
        if defaultParamFlag:
            if continueAt is None or not title or not style:
                raise ValueError("defaultParamFlag=True 时必须提供 continueAt/title/style")
            payload.update({"continueAt": continueAt, "title": title, "style": style})
            if prompt:
                payload["prompt"] = prompt

        if personaId is not None: payload["personaId"] = personaId
        if negativeTags is not None: payload["negativeTags"] = negativeTags
        if vocalGender is not None:  payload["vocalGender"] = vocalGender
        if styleWeight is not None:  payload["styleWeight"] = float(styleWeight)
        if weirdnessConstraint is not None: payload["weirdnessConstraint"] = float(weirdnessConstraint)
        if audioWeight is not None:  payload["audioWeight"] = float(audioWeight)

        res = self._post("/generate/upload-extend", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    # ---- 人声/伴奏分离 ----
    def separate_vocals(self, task_id: str, audio_id: str, sep_type: str = "separate_vocal",
                        callback: Optional[str] = None) -> str:
        payload = {
            "taskId": task_id,
            "audioId": audio_id,
            "type": sep_type,
            "callBackUrl": callback or "https://example.invalid/vocal",
        }
        res = self._post("/vocal-removal/generate", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    def get_vocal_info(self, task_id: str) -> Dict[str, Any]:
        res = self._get("/vocal-removal/record-info", params={"taskId": task_id})
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]

    # ---- WAV 转换 ----
    def convert_wav(self, task_id: str, audio_id: str, callback: Optional[str] = None) -> str:
        payload = {"taskId": task_id, "audioId": audio_id, "callBackUrl": callback or "https://example.invalid/wav"}
        res = self._post("/wav/generate", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    def get_wav_info(self, task_id: str) -> Dict[str, Any]:
        res = self._get("/wav/record-info", params={"taskId": task_id})
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]

    # ---- 生成音乐视频 MP4 ----
    def create_music_video(self, task_id: str, audio_id: str,
                           author: Optional[str] = None, domainName: Optional[str] = None,
                           callback: Optional[str] = None) -> str:
        payload = {"taskId": task_id, "audioId": audio_id, "callBackUrl": callback or "https://example.invalid/mp4"}
        if author:
            payload["author"] = author
        if domainName:
            payload["domainName"] = domainName
        res = self._post("/mp4/generate", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    def get_mp4_info(self, task_id: str) -> Dict[str, Any]:
        res = self._get("/mp4/record-info", params={"taskId": task_id})
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]

    # ---- 上传三件套 ----
    def upload_base64(self, b64: str, upload_path: str, file_name: str) -> Dict[str, Any]:
        payload = {"base64": b64, "uploadPath": upload_path, "fileName": file_name}
        r = requests.post(f"{UPLOAD_BASE}/file-base64-upload", headers=self.json_headers, json=payload, timeout=120)
        r.raise_for_status()
        return r.json()

    def upload_stream(self, file_path: str, upload_path: str, file_name: str) -> Dict[str, Any]:
        with open(file_path, "rb") as f:
            files = {"file": (file_name, f)}
            data = {"uploadPath": upload_path, "fileName": file_name}
            r = requests.post(f"{UPLOAD_BASE}/file-stream-upload", headers=self.headers, files=files, data=data, timeout=300)
        r.raise_for_status()
        return r.json()

    def upload_from_url(self, file_url: str, upload_path: str, file_name: str) -> Dict[str, Any]:
        payload = {"fileUrl": file_url, "uploadPath": upload_path, "fileName": file_name}
        r = requests.post(f"{UPLOAD_BASE}/file-url-upload", headers=self.json_headers, json=payload, timeout=120)
        r.raise_for_status()
        return r.json()

    # ---- 上传并翻唱（cover） ----
    def upload_cover(
        self,
        *,
        uploadUrl: str,
        customMode: bool,
        instrumental: bool,
        model: str = "V4_5",
        prompt: Optional[str] = None,
        style: Optional[str] = None,
        title: Optional[str] = None,
        negativeTags: Optional[str] = None,
        vocalGender: Optional[str] = None,
        styleWeight: Optional[float] = None,
        weirdnessConstraint: Optional[float] = None,
        audioWeight: Optional[float] = None,
        callback: Optional[str] = None,
    ) -> str:
        payload: Dict[str, Any] = {
            "uploadUrl": uploadUrl,
            "customMode": customMode,
            "instrumental": instrumental,
            "model": model,
            "callBackUrl": callback or "https://example.invalid/cover",
        }
        if customMode:
            if not style or not title:
                raise ValueError("customMode=True 需要 style 和 title")
            payload.update({"style": style, "title": title})
            if not instrumental:
                if not prompt:
                    raise ValueError("customMode=True 且 instrumental=False 时需要 prompt（歌词）")
                payload["prompt"] = prompt
        else:
            if not prompt:
                raise ValueError("customMode=False 时必须提供 prompt（创作提示）")
            payload["prompt"] = prompt

        if negativeTags is not None: payload["negativeTags"] = negativeTags
        if vocalGender is not None:  payload["vocalGender"] = vocalGender
        if styleWeight is not None:  payload["styleWeight"] = float(styleWeight)
        if weirdnessConstraint is not None: payload["weirdnessConstraint"] = float(weirdnessConstraint)
        if audioWeight is not None:  payload["audioWeight"] = float(audioWeight)

        res = self._post("/generate/upload-cover", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    # ---- 添加乐器 / 添加人声 ----
    def add_instrumental(self, uploadUrl: str, *, title: str, tags: str, negativeTags: str,
                         model: Optional[str] = None, vocalGender: Optional[str] = None,
                         styleWeight: Optional[float] = None, weirdnessConstraint: Optional[float] = None,
                         audioWeight: Optional[float] = None, callback: Optional[str] = None) -> str:
        payload: Dict[str, Any] = {
            "uploadUrl": uploadUrl,
            "title": title,
            "tags": tags,
            "negativeTags": negativeTags,
            "callBackUrl": callback or "https://example.invalid/add-instrumental",
        }
        if model: payload["model"] = model
        if vocalGender is not None: payload["vocalGender"] = vocalGender
        if styleWeight is not None: payload["styleWeight"] = float(styleWeight)
        if weirdnessConstraint is not None: payload["weirdnessConstraint"] = float(weirdnessConstraint)
        if audioWeight is not None: payload["audioWeight"] = float(audioWeight)
        res = self._post("/generate/add-instrumental", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    def add_vocals(self, uploadUrl: str, *, prompt: str, title: str, style: str, negativeTags: str,
                   model: Optional[str] = None, vocalGender: Optional[str] = None,
                   styleWeight: Optional[float] = None, weirdnessConstraint: Optional[float] = None,
                   audioWeight: Optional[float] = None, callback: Optional[str] = None) -> str:
        payload: Dict[str, Any] = {
            "uploadUrl": uploadUrl, "prompt": prompt, "title": title, "style": style,
            "negativeTags": negativeTags, "callBackUrl": callback or "https://example.invalid/add-vocals",
        }
        if model: payload["model"] = model
        if vocalGender is not None: payload["vocalGender"] = vocalGender
        if styleWeight is not None: payload["styleWeight"] = float(styleWeight)
        if weirdnessConstraint is not None: payload["weirdnessConstraint"] = float(weirdnessConstraint)
        if audioWeight is not None: payload["audioWeight"] = float(audioWeight)
        res = self._post("/generate/add-vocals", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    # ---- 风格增强（同步） ----
    def style_generate(self, content: str) -> Dict[str, Any]:
        res = self._post("/style/generate", {"content": content})
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]

    # ---- 封面 ----
    def create_cover(self, task_id: str, callback: Optional[str] = None) -> str:
        payload = {"taskId": task_id, "callBackUrl": callback or "https://example.invalid/cover-art"}
        res = self._post("/suno/cover/generate", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    def get_cover_info(self, task_id: str) -> Dict[str, Any]:
        res = self._get("/suno/cover/record-info", params={"taskId": task_id})
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]

    # ---- 局部重写 ----
    def replace_section(self, *, taskId: str, audioId: str, prompt: str, tags: str, title: str,
                        negativeTags: str, infillStartS: float, infillEndS: float,
                        model: Optional[str] = None, callback: Optional[str] = None) -> str:
        payload: Dict[str, Any] = {
            "taskId": taskId, "audioId": audioId, "prompt": prompt, "tags": tags, "title": title,
            "negativeTags": negativeTags, "infillStartS": float(infillStartS), "infillEndS": float(infillEndS),
            "callBackUrl": callback or "https://example.invalid/replace-section",
        }
        if model: payload["model"] = model
        res = self._post("/generate/replace-section", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    # ---- Persona（同步返回） ----
    def generate_persona(self, task_id: str, audio_id: str, *, name: str, description: str) -> Dict[str, Any]:
        payload = {"taskId": task_id, "audioId": audio_id, "name": name, "description": description}
        res = self._post("/generate/generate-persona", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]


# ---------------- FastAPI app ----------------
app = FastAPI(title="Suno API Web Demo (Full+Styled)", version="1.2.0")

# CORS（本地开发更方便）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

# 静态资源：媒体文件
app.mount("/media", StaticFiles(directory=str(OUT_DIR), html=False), name="media")

def get_client() -> SunoClient:
    try:
        return SunoClient()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- Pydantic 请求模型 ----------------
class GenerateReq(BaseModel):
    prompt: str = Field(..., description="提示词：非自定义为创作提示，自定义为演唱歌词")
    customMode: bool = Field(False, description="自定义模式")
    instrumental: bool = Field(False, description="是否仅器乐")
    style: Optional[str] = Field(None, description="customMode=True 需要：风格")
    title: Optional[str] = Field(None, description="customMode=True 需要：标题")
    model: str = Field("V4_5", description="模型：V3_5/V4/V4_5/V4_5PLUS/V5")

    @model_validator(mode="after")
    def _check_custom(self):
        if self.customMode and (not self.style or not self.title):
            raise ValueError("customMode=True 时必须提供 style 和 title")
        return self

class UploadExtendReq(BaseModel):
    uploadUrl: str
    model: str = "V4_5"
    defaultParamFlag: bool = False
    instrumental: Optional[bool] = None
    prompt: Optional[str] = None
    style: Optional[str] = None
    title: Optional[str] = None
    continueAt: Optional[int] = None

    @model_validator(mode="after")
    def _check_default(self):
        if self.defaultParamFlag:
            if not self.style or not self.title or self.continueAt is None:
                raise ValueError("defaultParamFlag=True 时必须提供 continueAt/title/style")
        return self

# -------------- 首页：现代化完整功能界面 --------------
INDEX_HTML = """<!doctype html>
<html lang="zh">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Suno AI 音乐生成平台 · 完整版</title>
  <style>
    :root {
      --bg: #0a0e1a;
      --bg-soft: #11161f;
      --bg-elevated: #1a1f2e;
      --card: #141927;
      --txt: #f0f2f7;
      --txt-secondary: #b4bcd0;
      --muted: #6b7280;
      --primary: #6366f1;
      --primary-hover: #7c3aed;
      --primary-light: rgba(99, 102, 241, 0.1);
      --accent: #10b981;
      --accent-light: rgba(16, 185, 129, 0.1);
      --warning: #f59e0b;
      --danger: #ef4444;
      --radius: 16px;
      --radius-sm: 12px;
      --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
      --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.4);
      --transition: all 0.2s ease;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
      background: var(--bg);
      color: var(--txt);
      line-height: 1.6;
      min-height: 100vh;
    }

    .navbar {
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(10, 14, 26, 0.95);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      padding: 0 2rem;
    }

    .nav-container {
      max-width: 1600px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 70px;
    }

    .logo {
      font-size: 1.5rem;
      font-weight: 700;
      background: linear-gradient(135deg, var(--primary), var(--primary-hover));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .nav-actions {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .credits-badge {
      background: var(--primary-light);
      color: var(--primary);
      padding: 0.5rem 1rem;
      border-radius: 999px;
      font-weight: 600;
      font-size: 0.875rem;
      cursor: pointer;
      transition: var(--transition);
    }

    .credits-badge:hover {
      background: rgba(99, 102, 241, 0.2);
    }

    .container {
      max-width: 1600px;
      margin: 0 auto;
      padding: 2rem;
    }

    .tabs {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 2rem;
      background: var(--bg-soft);
      padding: 0.5rem;
      border-radius: var(--radius);
      overflow-x: auto;
      flex-wrap: wrap;
    }

    .tab {
      padding: 0.75rem 1.25rem;
      border: none;
      background: transparent;
      color: var(--txt-secondary);
      border-radius: var(--radius-sm);
      cursor: pointer;
      font-weight: 500;
      transition: var(--transition);
      white-space: nowrap;
      font-size: 0.9rem;
    }

    .tab:hover {
      background: rgba(255, 255, 255, 0.05);
      color: var(--txt);
    }

    .tab.active {
      background: linear-gradient(135deg, var(--primary), var(--primary-hover));
      color: white;
    }

    .tab-content {
      display: none;
    }

    .tab-content.active {
      display: block;
      animation: fadeIn 0.3s ease;
    }

    .card {
      background: var(--card);
      border-radius: var(--radius);
      padding: 1.5rem;
      box-shadow: var(--shadow);
      margin-bottom: 1.5rem;
      border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .card-title {
      font-size: 1.125rem;
      font-weight: 600;
      margin-bottom: 1.25rem;
      color: var(--txt);
    }

    .form-group {
      margin-bottom: 1.25rem;
    }

    .form-label {
      display: block;
      font-size: 0.875rem;
      font-weight: 500;
      color: var(--txt-secondary);
      margin-bottom: 0.5rem;
    }

    .form-input, .form-select, .form-textarea {
      width: 100%;
      padding: 0.75rem 1rem;
      background: var(--bg-soft);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-sm);
      color: var(--txt);
      font-size: 0.9375rem;
      transition: var(--transition);
    }

    .form-input:focus, .form-select:focus, .form-textarea:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px var(--primary-light);
    }

    .form-textarea {
      min-height: 100px;
      resize: vertical;
      font-family: inherit;
    }

    .form-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1rem;
    }

    .checkbox-group {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem;
      background: var(--bg-soft);
      border-radius: var(--radius-sm);
      cursor: pointer;
    }

    .checkbox-group input[type="checkbox"] {
      width: 1.125rem;
      height: 1.125rem;
      cursor: pointer;
    }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      padding: 0.75rem 1.5rem;
      border: none;
      border-radius: var(--radius-sm);
      font-weight: 600;
      font-size: 0.9375rem;
      cursor: pointer;
      transition: var(--transition);
    }

    .btn-primary {
      background: linear-gradient(135deg, var(--primary), var(--primary-hover));
      color: white;
      box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }

    .btn-primary:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
    }

    .btn-secondary {
      background: var(--bg-elevated);
      color: var(--txt);
      border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .btn-secondary:hover:not(:disabled) {
      background: var(--bg-soft);
      border-color: rgba(255, 255, 255, 0.2);
    }

    .btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .status-message {
      padding: 1rem;
      border-radius: var(--radius-sm);
      font-size: 0.875rem;
      margin-top: 1rem;
      display: none;
    }

    .status-message.show {
      display: block;
      animation: slideDown 0.3s ease;
    }

    .status-success {
      background: var(--accent-light);
      color: var(--accent);
      border: 1px solid var(--accent);
    }

    .status-error {
      background: rgba(239, 68, 68, 0.1);
      color: var(--danger);
      border: 1px solid var(--danger);
    }

    .status-loading {
      background: rgba(245, 158, 11, 0.1);
      color: var(--warning);
      border: 1px solid var(--warning);
    }

    .media-container {
      display: none;
      margin-top: 2rem;
    }

    .media-container.show {
      display: block;
    }

    .media-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1.5rem;
    }

    .media-item {
      background: var(--bg-elevated);
      border-radius: var(--radius);
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .media-item audio, .media-item video, .media-item img {
      width: 100%;
      display: block;
    }

    .json-output {
      background: var(--bg-soft);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-sm);
      padding: 1rem;
      margin-top: 1rem;
      font-family: monospace;
      font-size: 0.875rem;
      max-height: 300px;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-all;
      display: none;
    }

    .json-output.show {
      display: block;
    }

    .spinner {
      display: inline-block;
      width: 1rem;
      height: 1rem;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-top-color: currentColor;
      border-radius: 50%;
      animation: spin 0.6s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideDown {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 768px) {
      .container { padding: 1rem; }
      .navbar { padding: 0 1rem; }
      .nav-container { height: 60px; }
      .card { padding: 1.25rem; }
      .form-row { grid-template-columns: 1fr; }
      .tabs { padding: 0.25rem; }
      .tab { padding: 0.5rem 1rem; font-size: 0.85rem; }
    }
  </style>
</head>
<body>
  <nav class="navbar">
    <div class="nav-container">
      <div class="logo">🎵 Suno AI 音乐平台</div>
      <div class="nav-actions">
        <div class="credits-badge" id="credits" onclick="loadCredits()">💳 查询余额</div>
      </div>
    </div>
  </nav>

  <div class="container">
    <div class="tabs">
      <button class="tab active" onclick="switchTab(event, 'generate')">🎵 生成音乐</button>
      <button class="tab" onclick="switchTab(event, 'lyrics')">📝 生成歌词</button>
      <button class="tab" onclick="switchTab(event, 'extend')">⏩ 延长音乐</button>
      <button class="tab" onclick="switchTab(event, 'upload-extend')">⬆️ 上传并扩展</button>
      <button class="tab" onclick="switchTab(event, 'separate')">🎼 人声分离</button>
      <button class="tab" onclick="switchTab(event, 'convert')">🔄 格式转换</button>
      <button class="tab" onclick="switchTab(event, 'cover')">🎤 AI翻唱</button>
      <button class="tab" onclick="switchTab(event, 'add')">➕ 添加音轨</button>
      <button class="tab" onclick="switchTab(event, 'tools')">🛠️ 辅助工具</button>
      <button class="tab" onclick="switchTab(event, 'query')">🔍 查询任务</button>
    </div>

    <!-- 生成音乐 -->
    <div id="tab-generate" class="tab-content active">
      <div class="card">
        <h2 class="card-title">生成音乐</h2>
        <div class="form-group">
          <label class="form-label">提示词（Prompt）</label>
          <textarea id="gen_prompt" class="form-textarea" placeholder="描述您想要的音乐风格，例如：80年代合成器音乐，夜间驾驶，电影感"></textarea>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">模型</label>
            <select id="gen_model" class="form-select">
              <option>V3_5</option>
              <option>V4</option>
              <option selected>V4_5</option>
              <option>V4_5PLUS</option>
              <option>V5</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="checkbox-group">
            <input type="checkbox" id="gen_custom" onchange="toggleCustom()">
            <label>自定义模式</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="gen_instr">
            <label>仅器乐（无人声）</label>
          </div>
        </div>
        <div id="custom_fields" style="display:none">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">风格 (Style)</label>
              <input id="gen_style" class="form-input" placeholder="Pop, Rock, Folk">
            </div>
            <div class="form-group">
              <label class="form-label">标题 (Title)</label>
              <input id="gen_title" class="form-input" placeholder="歌曲标题">
            </div>
          </div>
        </div>
        <button class="btn btn-primary" onclick="submitGenerate()">🎵 开始生成</button>
        <div id="gen_status" class="status-message"></div>
        <div id="gen_json" class="json-output"></div>
        <div id="gen_media" class="media-container"></div>
      </div>
    </div>

    <!-- 生成歌词 -->
    <div id="tab-lyrics" class="tab-content">
      <div class="card">
        <h2 class="card-title">生成歌词</h2>
        <div class="form-group">
          <label class="form-label">歌词主题</label>
          <input id="lyr_prompt" class="form-input" placeholder="输入歌词主题或关键词">
        </div>
        <button class="btn btn-primary" onclick="createLyrics()">📝 生成歌词</button>
        <div id="lyr_status" class="status-message"></div>
        <div id="lyr_json" class="json-output"></div>
      </div>

      <div class="card">
        <h2 class="card-title">获取时间戳歌词</h2>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">任务 ID</label>
            <input id="ts_task" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">音频 ID</label>
            <input id="ts_audio" class="form-input">
          </div>
        </div>
        <button class="btn btn-primary" onclick="tsLyrics()">🎵 获取时间戳歌词</button>
        <div id="ts_status" class="status-message"></div>
        <div id="ts_json" class="json-output"></div>
      </div>
    </div>

    <!-- 延长音乐 -->
    <div id="tab-extend" class="tab-content">
      <div class="card">
        <h2 class="card-title">延长音乐</h2>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">原音频 ID</label>
            <input id="ex_audio" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">模型</label>
            <select id="ex_model" class="form-select">
              <option selected>V4_5</option>
              <option>V4_5PLUS</option>
              <option>V5</option>
            </select>
          </div>
        </div>
        <div class="checkbox-group" style="margin-bottom:1rem">
          <input type="checkbox" id="ex_default" onchange="toggleExtendParams()">
          <label>使用自定义参数 (defaultParamFlag)</label>
        </div>
        <div id="extend_params" style="display:none">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">继续时间点 (秒)</label>
              <input id="ex_continue" class="form-input" type="number">
            </div>
            <div class="form-group">
              <label class="form-label">标题 (Title)</label>
              <input id="ex_title" class="form-input">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">风格 (Style)</label>
              <input id="ex_style" class="form-input">
            </div>
            <div class="form-group">
              <label class="form-label">提示词 (可选)</label>
              <input id="ex_prompt" class="form-input">
            </div>
          </div>
        </div>
        <button class="btn btn-primary" onclick="extendMusic()">⏩ 延长音乐</button>
        <div id="ex_status" class="status-message"></div>
        <div id="ex_json" class="json-output"></div>
        <div id="ex_media" class="media-container"></div>
      </div>
    </div>

    <!-- 上传并扩展 -->
    <div id="tab-upload-extend" class="tab-content">
      <div class="card">
        <h2 class="card-title">上传音频文件</h2>
        <div class="form-group">
          <label class="form-label">选择文件</label>
          <input type="file" id="upext_file" class="form-input" accept="audio/*">
        </div>
        <div class="form-group">
          <label class="form-label">或输入公网 URL</label>
          <input id="upext_url" class="form-input" placeholder="https://...">
        </div>
        <button class="btn btn-secondary" onclick="doUploadForExtend()">⬆️ 上传并获取 URL</button>
        <div id="upext_upload_status" class="status-message"></div>
      </div>

      <div class="card">
        <h2 class="card-title">上传并扩展音乐</h2>
        <div class="form-group">
          <label class="form-label">上传后的 URL（或从上面获取）</label>
          <input id="upext_uploadUrl" class="form-input">
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">模型</label>
            <select id="upext_model" class="form-select">
              <option selected>V4_5</option>
              <option>V4_5PLUS</option>
              <option>V5</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="checkbox-group">
            <input type="checkbox" id="upext_default" onchange="toggleUpExtParams()">
            <label>使用自定义参数</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="upext_instr">
            <label>仅器乐</label>
          </div>
        </div>
        <div id="upext_params" style="display:none">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">继续时间点 (秒)</label>
              <input id="upext_continue" class="form-input" type="number">
            </div>
            <div class="form-group">
              <label class="form-label">标题</label>
              <input id="upext_title" class="form-input">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">风格</label>
              <input id="upext_style" class="form-input">
            </div>
            <div class="form-group">
              <label class="form-label">提示词 (可选)</label>
              <input id="upext_prompt" class="form-input">
            </div>
          </div>
        </div>
        <button class="btn btn-primary" onclick="submitUploadExtend()">🚀 开始扩展</button>
        <div id="upext_status" class="status-message"></div>
        <div id="upext_json" class="json-output"></div>
        <div id="upext_media" class="media-container"></div>
      </div>
    </div>

    <!-- 人声分离 -->
    <div id="tab-separate" class="tab-content">
      <div class="card">
        <h2 class="card-title">人声/伴奏分离</h2>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">原任务 ID</label>
            <input id="sep_task" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">音频 ID</label>
            <input id="sep_audio" class="form-input">
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">分离类型</label>
          <select id="sep_type" class="form-select">
            <option value="separate_vocal">分离人声</option>
            <option value="split_stem">分离音轨</option>
          </select>
        </div>
        <button class="btn btn-primary" onclick="separateVocals()">🎼 开始分离</button>
        <div id="sep_status" class="status-message"></div>
        <div id="sep_json" class="json-output"></div>
        <div id="sep_media" class="media-container"></div>
      </div>
    </div>

    <!-- 格式转换 -->
    <div id="tab-convert" class="tab-content">
      <div class="card">
        <h2 class="card-title">转换为 WAV 格式</h2>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">任务 ID</label>
            <input id="wav_task" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">音频 ID</label>
            <input id="wav_audio" class="form-input">
          </div>
        </div>
        <button class="btn btn-primary" onclick="convertToWav()">🔄 转换为 WAV</button>
        <div id="wav_status" class="status-message"></div>
        <div id="wav_json" class="json-output"></div>
        <div id="wav_media" class="media-container"></div>
      </div>

      <div class="card">
        <h2 class="card-title">生成 MP4 视频</h2>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">任务 ID</label>
            <input id="mp4_task" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">音频 ID</label>
            <input id="mp4_audio" class="form-input">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">作者 (可选)</label>
            <input id="mp4_author" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">域名 (可选)</label>
            <input id="mp4_domain" class="form-input">
          </div>
        </div>
        <button class="btn btn-primary" onclick="generateMp4()">📹 生成视频</button>
        <div id="mp4_status" class="status-message"></div>
        <div id="mp4_json" class="json-output"></div>
        <div id="mp4_media" class="media-container"></div>
      </div>
    </div>

    <!-- AI翻唱 -->
    <div id="tab-cover" class="tab-content">
      <div class="card">
        <h2 class="card-title">AI 翻唱 (Cover)</h2>
        <div class="form-group">
          <label class="form-label">上传 URL</label>
          <input id="cov_uploadUrl" class="form-input">
        </div>
        <div class="form-row">
          <div class="checkbox-group">
            <input type="checkbox" id="cov_custom">
            <label>自定义模式</label>
          </div>
          <div class="checkbox-group">
            <input type="checkbox" id="cov_instr">
            <label>仅器乐</label>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">模型</label>
            <select id="cov_model" class="form-select">
              <option selected>V4_5</option>
              <option>V4_5PLUS</option>
              <option>V5</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">提示词/歌词</label>
            <input id="cov_prompt" class="form-input">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">风格</label>
            <input id="cov_style" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">标题</label>
            <input id="cov_title" class="form-input">
          </div>
        </div>
        <button class="btn btn-primary" onclick="uploadCover()">🎤 开始翻唱</button>
        <div id="cov_status" class="status-message"></div>
        <div id="cov_json" class="json-output"></div>
        <div id="cov_media" class="media-container"></div>
      </div>
    </div>

    <!-- 添加音轨 -->
    <div id="tab-add" class="tab-content">
      <div class="card">
        <h2 class="card-title">添加乐器</h2>
        <div class="form-group">
          <label class="form-label">上传 URL</label>
          <input id="ai_uploadUrl" class="form-input">
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">标题</label>
            <input id="ai_title" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">标签</label>
            <input id="ai_tags" class="form-input">
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">负面标签</label>
          <input id="ai_neg" class="form-input">
        </div>
        <button class="btn btn-primary" onclick="addInstrumental()">➕ 添加乐器</button>
        <div id="ai_status" class="status-message"></div>
        <div id="ai_json" class="json-output"></div>
        <div id="ai_media" class="media-container"></div>
      </div>

      <div class="card">
        <h2 class="card-title">添加人声</h2>
        <div class="form-group">
          <label class="form-label">上传 URL</label>
          <input id="av_uploadUrl" class="form-input">
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">歌词</label>
            <input id="av_prompt" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">标题</label>
            <input id="av_title" class="form-input">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">风格</label>
            <input id="av_style" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">负面标签</label>
            <input id="av_neg" class="form-input">
          </div>
        </div>
        <button class="btn btn-primary" onclick="addVocals()">➕ 添加人声</button>
        <div id="av_status" class="status-message"></div>
        <div id="av_json" class="json-output"></div>
        <div id="av_media" class="media-container"></div>
      </div>
    </div>

    <!-- 辅助工具 -->
    <div id="tab-tools" class="tab-content">
      <div class="card">
        <h2 class="card-title">风格增强</h2>
        <div class="form-group">
          <label class="form-label">风格描述</label>
          <input id="sg_content" class="form-input" placeholder="例如: Pop, Mysterious">
        </div>
        <button class="btn btn-primary" onclick="styleGenerate()">✨ 增强风格</button>
        <div id="sg_status" class="status-message"></div>
        <div id="sg_json" class="json-output"></div>
      </div>

      <div class="card">
        <h2 class="card-title">生成封面</h2>
        <div class="form-group">
          <label class="form-label">父任务 ID</label>
          <input id="cover_task" class="form-input">
        </div>
        <button class="btn btn-primary" onclick="createCoverArt()">🎨 生成封面</button>
        <div id="cover_status" class="status-message"></div>
        <div id="cover_json" class="json-output"></div>
        <div id="cover_media" class="media-container"></div>
      </div>

      <div class="card">
        <h2 class="card-title">局部替换音乐片段</h2>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">任务 ID</label>
            <input id="rs_task" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">音频 ID</label>
            <input id="rs_audio" class="form-input">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">提示词</label>
            <input id="rs_prompt" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">标签</label>
            <input id="rs_tags" class="form-input">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">标题</label>
            <input id="rs_title" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">负面标签</label>
            <input id="rs_neg" class="form-input">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">开始时间 (秒)</label>
            <input id="rs_start" class="form-input" type="number" step="0.1">
          </div>
          <div class="form-group">
            <label class="form-label">结束时间 (秒)</label>
            <input id="rs_end" class="form-input" type="number" step="0.1">
          </div>
        </div>
        <button class="btn btn-primary" onclick="replaceSection()">✂️ 替换片段</button>
        <div id="rs_status" class="status-message"></div>
        <div id="rs_json" class="json-output"></div>
        <div id="rs_media" class="media-container"></div>
      </div>

      <div class="card">
        <h2 class="card-title">生成 Persona</h2>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">任务 ID</label>
            <input id="ps_task" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">音频 ID</label>
            <input id="ps_audio" class="form-input">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">名称</label>
            <input id="ps_name" class="form-input">
          </div>
          <div class="form-group">
            <label class="form-label">描述</label>
            <input id="ps_desc" class="form-input">
          </div>
        </div>
        <button class="btn btn-primary" onclick="generatePersona()">👤 生成 Persona</button>
        <div id="ps_status" class="status-message"></div>
        <div id="ps_json" class="json-output"></div>
      </div>
    </div>

    <!-- 查询任务 -->
    <div id="tab-query" class="tab-content">
      <div class="card">
        <h2 class="card-title">查询任务状态</h2>
        <div class="form-group">
          <label class="form-label">任务 ID</label>
          <input id="q_task" class="form-input" placeholder="输入任务ID">
        </div>
        <button class="btn btn-primary" onclick="queryTask()">🔍 查询</button>
        <div id="q_status" class="status-message"></div>
        <div id="q_json" class="json-output"></div>
        <div id="q_media" class="media-container"></div>
      </div>
    </div>
  </div>

  <script>
    const POLL_MS = 10000;

    function switchTab(event, tabName) {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      event.target.classList.add('active');
      document.getElementById(`tab-${tabName}`).classList.add('active');
    }

    async function loadCredits() {
      try {
        const r = await fetch('/api/credits');
        const j = await r.json();
        document.getElementById('credits').textContent = r.ok ? `💳 余额：${j.credits}` : '💳 查询失败';
      } catch(e) {
        document.getElementById('credits').textContent = '💳 查询失败';
      }
    }

    function toggleCustom() {
      document.getElementById('custom_fields').style.display =
        document.getElementById('gen_custom').checked ? 'block' : 'none';
    }

    function toggleExtendParams() {
      document.getElementById('extend_params').style.display =
        document.getElementById('ex_default').checked ? 'block' : 'none';
    }

    function toggleUpExtParams() {
      document.getElementById('upext_params').style.display =
        document.getElementById('upext_default').checked ? 'block' : 'none';
    }

    function showStatus(id, message, type) {
      const el = document.getElementById(id);
      el.className = `status-message show status-${type}`;
      el.textContent = message;
    }

    function hideStatus(id) {
      document.getElementById(id).classList.remove('show');
    }

    function showJSON(id, data) {
      const el = document.getElementById(id);
      el.classList.add('show');
      el.textContent = JSON.stringify(data, null, 2);
    }

    function renderMedia(containerId, cached) {
      const el = document.getElementById(containerId);
      el.classList.add('show');
      el.innerHTML = '<div class="media-grid"></div>';
      const grid = el.querySelector('.media-grid');

      if (cached.images && cached.images.length) {
        cached.images.forEach((u, idx) => {
          grid.innerHTML += `<div class="media-item">
            <div style="padding:1rem;font-size:0.875rem;color:var(--txt-secondary);">封面 ${idx + 1}</div>
            <img src="${u}" alt="封面${idx + 1}"/>
          </div>`;
        });
      }
      if (cached.audio && cached.audio.length) {
        cached.audio.forEach((u, idx) => {
          grid.innerHTML += `<div class="media-item">
            <div style="padding:1rem;font-size:0.875rem;color:var(--txt-secondary);">🎵 歌曲 ${idx + 1}</div>
            <audio controls src="${u}"></audio>
            <div style="padding:1rem;"><a href="${u}" download style="color:var(--primary);text-decoration:none;">📥 下载</a></div>
          </div>`;
        });
      }
      if (cached.video) {
        grid.innerHTML += `<div class="media-item">
          <div style="padding:1rem;font-size:0.875rem;color:var(--txt-secondary);">📹 视频</div>
          <video controls src="${cached.video}"></video>
          <div style="padding:1rem;"><a href="${cached.video}" download style="color:var(--primary);text-decoration:none;">📥 下载</a></div>
        </div>`;
      }
    }

    async function cacheMediaFromInfo(info, kind) {
      let res = info.response || info;
      let sd = (res.sunoData) || info.data || [];
      let payload = { title: 'song', audio: [], images: [], video: null };

      if (sd && sd.length) {
        // 处理所有返回的歌曲（Suno 通常返回2首）
        sd.forEach((tr, index) => {
          const au = tr.audioUrl || tr.audio_url;
          const im = tr.imageUrl || tr.image_url;
          if (au) payload.audio.push(au);
          if (im) payload.images.push(im);
        });
        payload.title = sd[0].title || 'song';
      }

      const iv = res.instrumentalUrl || res.instrumental_url;
      const vv = res.vocalUrl || res.vocal_url;
      if (iv) payload.audio.push(iv);
      if (vv) payload.audio.push(vv);

      const wav = res.wavUrl || res.url;
      if (kind==='wav' && wav) payload.audio.push(wav);

      const vurl = res.videoUrl || res.url;
      if (kind==='mp4' && vurl) payload.video = vurl;

      if (Array.isArray(res.images)) payload.images = res.images;

      const r = await fetch('/api/cache-media', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      return await r.json();
    }

    async function pollTask(taskId, statusId, jsonId, mediaId, kind=null) {
      showStatus(statusId, `🔄 任务 ${taskId} 正在处理中...`, 'loading');

      const endpointMap = {
        lyrics: '/api/lyrics/',
        separate: '/api/vocal-separation/',
        wav: '/api/wav/',
        mp4: '/api/mp4/',
        cover: '/api/cover-info/'
      };
      const endpoint = endpointMap[kind || ''] || '/api/generate/';

      while(true) {
        await new Promise(r => setTimeout(r, POLL_MS));
        const r = await fetch(endpoint + taskId);
        const info = await r.json();
        const status = info.status ?? info.successFlag;

        if (status === 'SUCCESS' || status === 1) {
          showStatus(statusId, '✅ 任务完成！', 'success');
          showJSON(jsonId, info);
          try {
            const cached = await cacheMediaFromInfo(info, kind);
            renderMedia(mediaId, cached);
          } catch(e) { console.error(e); }
          break;
        }

        if (['FAILED','CREATE_TASK_FAILED','GENERATE_AUDIO_FAILED','GENERATE_LYRICS_FAILED','GENERATE_MP4_FAILED'].includes(status)) {
          showStatus(statusId, `❌ 任务失败：${status}`, 'error');
          showJSON(jsonId, info);
          break;
        }
      }
    }

    async function pollLyricsTask(taskId, statusId, jsonId) {
      showStatus(statusId, `🔄 任务 ${taskId} 正在处理中...`, 'loading');

      while(true) {
        await new Promise(r => setTimeout(r, POLL_MS));
        const r = await fetch('/api/lyrics/' + taskId);
        const info = await r.json();
        const status = info.status;

        if (status === 'SUCCESS') {
          showStatus(statusId, '✅ 歌词生成完成！', 'success');
          showJSON(jsonId, info);
          
          // 显示歌词内容
          const lyricsData = info.response?.data || [];
          if (lyricsData.length > 0) {
            let lyricsHtml = '<div style="margin-top:1rem;">';
            lyricsData.forEach((item, idx) => {
              lyricsHtml += `
                <div style="background:var(--bg-elevated);padding:1.5rem;border-radius:var(--radius);margin-bottom:1rem;">
                  <h3 style="color:var(--primary);margin-bottom:1rem;">📝 ${item.title || '歌词 ' + (idx+1)}</h3>
                  <pre style="white-space:pre-wrap;line-height:1.8;color:var(--txt);">${item.text || '无内容'}</pre>
                </div>
              `;
            });
            lyricsHtml += '</div>';
            document.getElementById(jsonId).insertAdjacentHTML('afterend', lyricsHtml);
          }
          break;
        }

        if (['CREATE_TASK_FAILED','GENERATE_LYRICS_FAILED','SENSITIVE_WORD_ERROR'].includes(status)) {
          showStatus(statusId, `❌ 生成失败：${status}`, 'error');
          showJSON(jsonId, info);
          break;
        }
      }
    }

    // 生成音乐
    async function submitGenerate() {
      const body = {
        prompt: document.getElementById('gen_prompt').value.trim(),
        customMode: document.getElementById('gen_custom').checked,
        instrumental: document.getElementById('gen_instr').checked,
        model: document.getElementById('gen_model').value
      };

      if (body.customMode) {
        body.style = document.getElementById('gen_style').value.trim();
        body.title = document.getElementById('gen_title').value.trim();
      }

      showStatus('gen_status', '⏳ 正在提交...', 'loading');
      const r = await fetch('/api/generate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body)
      });
      const j = await r.json();

      if (r.ok) {
        pollTask(j.task_id, 'gen_status', 'gen_json', 'gen_media');
      } else {
        showStatus('gen_status', `❌ ${j.detail || '提交失败'}`, 'error');
      }
    }

    // 生成歌词
    async function createLyrics() {
      const prompt = document.getElementById('lyr_prompt').value.trim();
      if (!prompt) {
        showStatus('lyr_status', '❌ 请输入歌词主题', 'error');
        return;
      }

      showStatus('lyr_status', '⏳ 正在生成...', 'loading');
      const r = await fetch('/api/lyrics', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({prompt})
      });
      const j = await r.json();

      if (r.ok) {
        pollLyricsTask(j.task_id, 'lyr_status', 'lyr_json');
      } else {
        showStatus('lyr_status', `❌ ${j.detail || '失败'}`, 'error');
      }
    }

    // 时间戳歌词
    async function tsLyrics() {
      const payload = {
        taskId: document.getElementById('ts_task').value.trim(),
        audioId: document.getElementById('ts_audio').value.trim()
      };

      showStatus('ts_status', '⏳ 正在获取...', 'loading');
      const r = await fetch('/api/ts-lyrics', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const j = await r.json();

      if (r.ok) {
        showStatus('ts_status', '✅ 获取成功', 'success');
        showJSON('ts_json', j);
      } else {
        showStatus('ts_status', `❌ ${j.detail || '失败'}`, 'error');
      }
    }

    // 延长音乐
    async function extendMusic() {
      const payload = {
        audioId: document.getElementById('ex_audio').value.trim(),
        model: document.getElementById('ex_model').value,
        defaultParamFlag: document.getElementById('ex_default').checked
      };

      if (payload.defaultParamFlag) {
        payload.continueAt = parseInt(document.getElementById('ex_continue').value || '0');
        payload.title = document.getElementById('ex_title').value.trim();
        payload.style = document.getElementById('ex_style').value.trim();
        const p = document.getElementById('ex_prompt').value.trim();
        if (p) payload.prompt = p;
      }

      showStatus('ex_status', '⏳ 正在提交...', 'loading');
      const r = await fetch('/api/extend', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const j = await r.json();

      if (r.ok) {
        pollTask(j.task_id, 'ex_status', 'ex_json', 'ex_media');
      } else {
        showStatus('ex_status', `❌ ${j.detail || '失败'}`, 'error');
      }
    }

    // 上传文件用于扩展
    async function doUploadForExtend() {
      showStatus('upext_upload_status', '⏳ 正在上传...', 'loading');

      const file = document.getElementById('upext_file').files[0];
      const url = document.getElementById('upext_url').value.trim();

      let form = new FormData();
      if (file) form.append('file', file);
      if (url) form.append('url', url);

      const r = await fetch('/api/upload', {method: 'POST', body: form});
      const j = await r.json();

      if (r.ok) {
        showStatus('upext_upload_status', `✅ 上传成功`, 'success');
        document.getElementById('upext_uploadUrl').value = j.uploadUrl;
      } else {
        showStatus('upext_upload_status', `❌ ${j.detail || '失败'}`, 'error');
      }
    }

    // 上传并扩展
    async function submitUploadExtend() {
      const payload = {
        uploadUrl: document.getElementById('upext_uploadUrl').value.trim(),
        model: document.getElementById('upext_model').value,
        defaultParamFlag: document.getElementById('upext_default').checked,
        instrumental: document.getElementById('upext_instr').checked
      };

      if (payload.defaultParamFlag) {
        payload.continueAt = parseInt(document.getElementById('upext_continue').value || '0');
        payload.title = document.getElementById('upext_title').value.trim();
        payload.style = document.getElementById('upext_style').value.trim();
        const p = document.getElementById('upext_prompt').value.trim();
        if (p) payload.prompt = p;
      }

      showStatus('upext_status', '⏳ 正在提交...', 'loading');
      const r = await fetch('/api/upload-extend', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const j = await r.json();

      if (r.ok) {
        pollTask(j.task_id, 'upext_status', 'upext_json', 'upext_media');
      } else {
        showStatus('upext_status', `❌ ${j.detail || '失败'}`, 'error');
      }
    }

    // 人声分离
    async function separateVocals() {
      const payload = {
        taskId: document.getElementById('sep_task').value.trim(),
        audioId: document.getElementById('sep_audio').value.trim(),
        type: document.getElementById('sep_type').value
      };

      showStatus('sep_status', '⏳ 正在提交...', 'loading');
      const r = await fetch('/api/separate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const j = await r.json();

      if (r.ok) {
        pollTask(j.task_id, 'sep_status', 'sep_json', 'sep_media', 'separate');
      } else {
        showStatus('sep_status', `❌ ${j.detail || '失败'}`, 'error');
      }
    }

    // 转 WAV
    async function convertToWav() {
      const payload = {
        taskId: document.getElementById('wav_task').value.trim(),
        audioId: document.getElementById('wav_audio').value.trim()
      };

      showStatus('wav_status', '⏳ 正在提交...', 'loading');
      const r = await fetch('/api/wav', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const j = await r.json();

      if (r.ok) {
        pollTask(j.task_id, 'wav_status', 'wav_json', 'wav_media', 'wav');
      } else {
        showStatus('wav_status', `❌ ${j.detail || '失败'}`, 'error');
      }
    }

    // 生成 MP4
    async function generateMp4() {
      const payload = {
        taskId: document.getElementById('mp4_task').value.trim(),
        audioId: document.getElementById('mp4_audio').value.trim(),
        author: document.getElementById('mp4_author').value.trim() || undefined,
        domainName: document.getElementById('mp4_domain').value.trim() || undefined
      };

      showStatus('mp4_status', '⏳ 正在提交...', 'loading');
      const r = await fetch('/api/mp4', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const j = await r.json();

      if (r.ok) {
        pollTask(j.task_id, 'mp4_status', 'mp4_json', 'mp4_media', 'mp4');
      } else {
        showStatus('mp4_status', `❌ ${j.detail || '失败'}`, 'error');
      }
    }

    // AI 翻唱
    async function uploadCover() {
      const payload = {
        uploadUrl: document.getElementById('cov_uploadUrl').value.trim(),
        customMode: document.getElementById('cov_custom').checked,
        instrumental: document.getElementById('cov_instr').checked,
        model: document.getElementById('cov_model').value,
        prompt: document.getElementById('cov_prompt').value.trim() || undefined,
        style: document.getElementById('cov_style').value.trim() || undefined,
        title: document.getElementById('cov_title').value.trim() || undefined
      };

      showStatus('cov_status', '⏳ 正在提交...', 'loading');
      const r = await fetch('/api/cover', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const j = await r.json();

      if (r.ok) {
        pollTask(j.task_id, 'cov_status', 'cov_json', 'cov_media');
      } else {
        showStatus('cov_status', `❌ ${j.detail || '失败'}`, 'error');
      }
    }

    // 添加乐器
    async function addInstrumental() {
      const payload = {
        uploadUrl: document.getElementById('ai_uploadUrl').value.trim(),
        title: document.getElementById('ai_title').value.trim(),
        tags: document.getElementById('ai_tags').value.trim(),
        negativeTags: document.getElementById('ai_neg').value.trim()
      };

      showStatus('ai_status', '⏳ 正在提交...', 'loading');
      const r = await fetch('/api/add-instrumental', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const j = await r.json();

      if (r.ok) {
        pollTask(j.task_id, 'ai_status', 'ai_json', 'ai_media');
      } else {
        showStatus('ai_status', `❌ ${j.detail || '失败'}`, 'error');
      }
    }

    // 添加人声
    async function addVocals() {
      const payload = {
        uploadUrl: document.getElementById('av_uploadUrl').value.trim(),
        prompt: document.getElementById('av_prompt').value.trim(),
        title: document.getElementById('av_title').value.trim(),
        style: document.getElementById('av_style').value.trim(),
        negativeTags: document.getElementById('av_neg').value.trim()
      };

      showStatus('av_status', '⏳ 正在提交...', 'loading');
      const r = await fetch('/api/add-vocals', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const j = await r.json();

      if (r.ok) {
        pollTask(j.task_id, 'av_status', 'av_json', 'av_media');
      } else {
        showStatus('av_status', `❌ ${j.detail || '失败'}`, 'error');
      }
    }

    // 风格增强
    async function styleGenerate() {
      const content = document.getElementById('sg_content').value.trim();
      if (!content) return;

      showStatus('sg_status', '⏳ 正在处理...', 'loading');
      const r = await fetch('/api/style-generate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({content})
      });
      const j = await r.json();

      if (r.ok) {
        showStatus('sg_status', '✅ 完成', 'success');
        showJSON('sg_json', j);
      } else {
        showStatus('sg_status', `❌ ${j.detail || '失败'}`, 'error');
      }
    }

    // 生成封面
    async function createCoverArt() {
      const taskId = document.getElementById('cover_task').value.trim();

      showStatus('cover_status', '⏳ 正在提交...', 'loading');
      const r = await fetch('/api/cover-art', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({taskId})
      });
      const j = await r.json();

      if (r.ok) {
        pollTask(j.task_id, 'cover_status', 'cover_json', 'cover_media', 'cover');
      } else {
        showStatus('cover_status', `❌ ${j.detail || '失败'}`, 'error');
      }
    }

    // 局部替换
    async function replaceSection() {
      const payload = {
        taskId: document.getElementById('rs_task').value.trim(),
        audioId: document.getElementById('rs_audio').value.trim(),
        prompt: document.getElementById('rs_prompt').value.trim(),
        tags: document.getElementById('rs_tags').value.trim(),
        title: document.getElementById('rs_title').value.trim(),
        negativeTags: document.getElementById('rs_neg').value.trim(),
        infillStartS: parseFloat(document.getElementById('rs_start').value || '0'),
        infillEndS: parseFloat(document.getElementById('rs_end').value || '0')
      };

      showStatus('rs_status', '⏳ 正在提交...', 'loading');
      const r = await fetch('/api/replace-section', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const j = await r.json();

      if (r.ok) {
        pollTask(j.task_id, 'rs_status', 'rs_json', 'rs_media');
      } else {
        showStatus('rs_status', `❌ ${j.detail || '失败'}`, 'error');
      }
    }

    // 生成 Persona
    async function generatePersona() {
      const payload = {
        taskId: document.getElementById('ps_task').value.trim(),
        audioId: document.getElementById('ps_audio').value.trim(),
        name: document.getElementById('ps_name').value.trim(),
        description: document.getElementById('ps_desc').value.trim()
      };

      showStatus('ps_status', '⏳ 正在提交...', 'loading');
      const r = await fetch('/api/persona', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const j = await r.json();

      if (r.ok) {
        showStatus('ps_status', '✅ 完成', 'success');
        showJSON('ps_json', j);
      } else {
        showStatus('ps_status', `❌ ${j.detail || '失败'}`, 'error');
      }
    }

    // 查询任务
    async function queryTask() {
      const tid = document.getElementById('q_task').value.trim();
      if (!tid) return;

      showStatus('q_status', '⏳ 正在查询...', 'loading');
      const r = await fetch('/api/generate/' + tid);
      const info = await r.json();

      if (r.ok) {
        showStatus('q_status', '✅ 查询完成', 'success');
        showJSON('q_json', info);
        try {
          const cached = await cacheMediaFromInfo(info, null);
          renderMedia('q_media', cached);
        } catch(e) {}
      } else {
        showStatus('q_status', `❌ ${info.detail || '查询失败'}`, 'error');
      }
    }

    // 页面加载时查询余额
    loadCredits();
  </script>
</body>
</html>

"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(INDEX_HTML)

# ---------------- REST：账户 / 生成 / 查询 ----------------
@app.get("/api/credits")
def api_credits():
    cli = get_client()
    try:
        return {"credits": cli.get_credits()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
def api_generate(req: GenerateReq):
    cli = get_client()
    try:
        task_id = cli.generate_music(
            prompt=req.prompt, customMode=req.customMode, instrumental=req.instrumental,
            model=req.model, style=req.style, title=req.title
        )
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/generate/{task_id}")
def api_generate_info(task_id: str):
    cli = get_client()
    try:
        info = cli.get_music_info(task_id)
        return JSONResponse(info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------- REST：歌词 ----------------
class LyricsReq(BaseModel):
    prompt: str

@app.post("/api/lyrics")
def api_lyrics(req: LyricsReq):
    cli = get_client()
    try:
        tid = cli.create_lyrics(req.prompt)
        return {"task_id": tid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/lyrics/{task_id}")
def api_lyrics_info(task_id: str):
    cli = get_client()
    try:
        info = cli.get_lyrics_info(task_id)
        return JSONResponse(info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------- REST：延长 / 上传并扩展 ----------------
class ExtendReq(BaseModel):
    audioId: str
    model: str = "V4_5"
    defaultParamFlag: bool = False
    continueAt: Optional[int] = None
    title: Optional[str] = None
    style: Optional[str] = None
    prompt: Optional[str] = None

@app.post("/api/extend")
def api_extend(req: ExtendReq):
    cli = get_client()
    try:
        tid = cli.extend_music(
            audio_id=req.audioId, model=req.model, defaultParamFlag=req.defaultParamFlag,
            continueAt=req.continueAt, title=req.title, style=req.style, prompt=req.prompt
        )
        return {"task_id": tid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/upload-extend")
def api_upload_extend(req: UploadExtendReq):
    cli = get_client()
    try:
        tid = cli.upload_and_extend(
            uploadUrl=req.uploadUrl, model=req.model, defaultParamFlag=req.defaultParamFlag,
            instrumental=req.instrumental, prompt=req.prompt, style=req.style, title=req.title, continueAt=req.continueAt
        )
        return {"task_id": tid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------- REST：分离 / WAV / MP4 ----------------
class SepReq(BaseModel):
    taskId: str
    audioId: str
    type: str = "separate_vocal"

@app.post("/api/separate")
def api_separate(req: SepReq):
    cli = get_client()
    try:
        tid = cli.separate_vocals(req.taskId, req.audioId, sep_type=req.type)
        return {"task_id": tid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/vocal-separation/{task_id}")
def api_vocal_separation_info(task_id: str):
    cli = get_client()
    try:
        info = cli.get_vocal_info(task_id)
        return JSONResponse(info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class WavReq(BaseModel):
    taskId: str
    audioId: str

@app.post("/api/wav")
def api_wav(req: WavReq):
    cli = get_client()
    try:
        tid = cli.convert_wav(req.taskId, req.audioId)
        return {"task_id": tid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/wav/{task_id}")
def api_wav_info(task_id: str):
    cli = get_client()
    try:
        info = cli.get_wav_info(task_id)
        return JSONResponse(info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class Mp4Req(BaseModel):
    taskId: str
    audioId: str
    author: Optional[str] = None
    domainName: Optional[str] = None

@app.post("/api/mp4")
def api_mp4(req: Mp4Req):
    cli = get_client()
    try:
        tid = cli.create_music_video(req.taskId, req.audioId, author=req.author, domainName=req.domainName)
        return {"task_id": tid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/mp4/{task_id}")
def api_mp4_info(task_id: str):
    cli = get_client()
    try:
        info = cli.get_mp4_info(task_id)
        return JSONResponse(info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------- REST：上传（Base64/流/URL） ----------------
class UploadB64Req(BaseModel):
    b64: str
    path: str
    name: str

@app.post("/api/upload-b64")
def api_upload_b64(req: UploadB64Req):
    cli = get_client()
    try:
        return cli.upload_base64(req.b64, req.path, req.name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/upload-stream")
def api_upload_stream(file: UploadFile = File(...), path: str = Form(...), name: str = Form(...)):
    cli = get_client()
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        up = cli.upload_stream(tmp_path, path, name)
        try: os.remove(tmp_path)
        except: pass
        return up
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class UploadURLReq(BaseModel):
    url: str
    path: str
    name: str

@app.post("/api/upload-url")
def api_upload_url(req: UploadURLReq):
    cli = get_client()
    try:
        return cli.upload_from_url(req.url, req.path, req.name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/upload")
def api_upload(file: UploadFile | None = File(default=None), url: str | None = Form(default=None)):
    cli = get_client()
    try:
        if url:
            up = cli.upload_from_url(url, upload_path="files/url", file_name=os.path.basename(urlparse(url).path) or "upload_from_url.bin")
            upload_url = _norm(_norm(up, "data") or {}, "downloadUrl")
            if not upload_url:
                raise RuntimeError("URL 直传失败：未获得 downloadUrl")
            return {"uploadUrl": upload_url}
        if not file:
            raise HTTPException(status_code=400, detail="需要提供 file 或 url 之一")
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        up = cli.upload_stream(tmp_path, upload_path="files/stream", file_name=file.filename or "upload_stream.bin")
        try: os.remove(tmp_path)
        except: pass
        upload_url = _norm(_norm(up, "data") or {}, "downloadUrl")
        if not upload_url:
            raise RuntimeError("文件上传失败：未获得 downloadUrl")
        return {"uploadUrl": upload_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------- REST：Cover / Add-Inst / Add-Voc / Style / Replace / Persona / TS-Lyrics ----------------
class CoverReq(BaseModel):
    uploadUrl: str
    customMode: bool
    instrumental: bool
    model: str = "V4_5"
    prompt: Optional[str] = None
    style: Optional[str] = None
    title: Optional[str] = None
    negativeTags: Optional[str] = None
    vocalGender: Optional[str] = None
    styleWeight: Optional[float] = None
    weirdnessConstraint: Optional[float] = None
    audioWeight: Optional[float] = None

@app.post("/api/cover")
def api_cover(req: CoverReq):
    cli = get_client()
    try:
        tid = cli.upload_cover(
            uploadUrl=req.uploadUrl, customMode=req.customMode, instrumental=req.instrumental, model=req.model,
            prompt=req.prompt, style=req.style, title=req.title, negativeTags=req.negativeTags,
            vocalGender=req.vocalGender, styleWeight=req.styleWeight, weirdnessConstraint=req.weirdnessConstraint,
            audioWeight=req.audioWeight
        )
        return {"task_id": tid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class AddInstReq(BaseModel):
    uploadUrl: str
    title: str
    tags: str
    negativeTags: str
    model: Optional[str] = None

@app.post("/api/add-instrumental")
def api_add_instrumental(req: AddInstReq):
    cli = get_client()
    try:
        tid = cli.add_instrumental(uploadUrl=req.uploadUrl, title=req.title, tags=req.tags, negativeTags=req.negativeTags, model=req.model)
        return {"task_id": tid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class AddVocReq(BaseModel):
    uploadUrl: str
    prompt: str
    title: str
    style: str
    negativeTags: str
    model: Optional[str] = None

@app.post("/api/add-vocals")
def api_add_vocals(req: AddVocReq):
    cli = get_client()
    try:
        tid = cli.add_vocals(uploadUrl=req.uploadUrl, prompt=req.prompt, title=req.title, style=req.style, negativeTags=req.negativeTags, model=req.model)
        return {"task_id": tid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class StyleGenReq(BaseModel):
    content: str

@app.post("/api/style-generate")
def api_style_gen(req: StyleGenReq):
    cli = get_client()
    try:
        return cli.style_generate(req.content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class CoverArtReq(BaseModel):
    taskId: str

@app.post("/api/cover-art")
def api_cover_art(req: CoverArtReq):
    cli = get_client()
    try:
        tid = cli.create_cover(req.taskId)
        return {"task_id": tid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/cover-info/{task_id}")
def api_cover_info(task_id: str):
    cli = get_client()
    try:
        info = cli.get_cover_info(task_id)
        return JSONResponse(info)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class ReplaceReq(BaseModel):
    taskId: str
    audioId: str
    prompt: str
    tags: str
    title: str
    negativeTags: str
    infillStartS: float
    infillEndS: float
    model: Optional[str] = None

@app.post("/api/replace-section")
def api_replace(req: ReplaceReq):
    cli = get_client()
    try:
        tid = cli.replace_section(
            taskId=req.taskId, audioId=req.audioId, prompt=req.prompt, tags=req.tags, title=req.title,
            negativeTags=req.negativeTags, infillStartS=req.infillStartS, infillEndS=req.infillEndS, model=req.model
        )
        return {"task_id": tid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class PersonaReq(BaseModel):
    taskId: str
    audioId: str
    name: str
    description: str

@app.post("/api/persona")
def api_persona(req: PersonaReq):
    cli = get_client()
    try:
        data = cli.generate_persona(req.taskId, req.audioId, name=req.name, description=req.description)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class TSLyricReq(BaseModel):
    taskId: str
    audioId: str

@app.post("/api/ts-lyrics")
def api_ts_lyrics(req: TSLyricReq):
    cli = get_client()
    try:
        data = cli.get_timestamped_lyrics(req.taskId, req.audioId)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------- REST：媒体缓存（下载到本地再展示/播放） ----------------
class CacheMediaReq(BaseModel):
    title: str
    audio: List[str] = []
    images: List[str] = []
    video: Optional[str] = None

@app.post("/api/cache-media")
def api_cache_media(req: CacheMediaReq):
    try:
        title = req.title or "song"
        out = {"audio": [], "images": [], "video": None}
        for i, a in enumerate(req.audio or []):
            try:
                out["audio"].append(_download_to_media(a, f"{title}_{i+1}", ".mp3"))
            except Exception:
                pass
        for i, img in enumerate(req.images or []):
            try:
                out["images"].append(_download_to_media(img, f"{title}_cover_{i+1}", ".jpg"))
            except Exception:
                pass
        if req.video:
            try:
                out["video"] = _download_to_media(req.video, f"{title}_video", ".mp4")
            except Exception:
                pass
        return out
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------- 健康检查 ----------------
@app.get("/health")
def health():
    ok = bool(os.getenv("SUNO_API_KEY"))
    return {"ok": ok}

# ---------------- 直接运行入口 ----------------
if __name__ == "__main__":
    import uvicorn
    # 直接运行不开启 reload（若需热重载：uvicorn suno_web_app:app --reload）
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=False)
