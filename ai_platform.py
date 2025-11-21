"""
AI创作平台 - 多功能AI服务集成Web应用
支持音乐生成、图片生成、视频生成、文字处理和音频处理

作者: AI Platform Team
版本: 2.0.0
日期: 2025-11-20
"""

import os
import json
import time
import asyncio
import pathlib
import tempfile
from typing import Optional, Dict, Any, List, Union
from abc import ABC, abstractmethod
from datetime import datetime

import requests
import aiohttp
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from loguru import logger

# 导入模块化路由
try:
    from modules.routes import music_workflow_router
    MUSIC_WORKFLOW_AVAILABLE = True
except ImportError:
    logger.warning("音乐创作工作流模块未找到，相关功能将不可用")
    MUSIC_WORKFLOW_AVAILABLE = False

try:
    from modules.routes import suno_router
    SUNO_ROUTER_AVAILABLE = True
except ImportError:
    logger.warning("Suno 路由模块未找到，相关功能将不可用")
    SUNO_ROUTER_AVAILABLE = False

try:
    from modules.routes import doubao_router
    DOUBAO_ROUTER_AVAILABLE = True
except ImportError:
    logger.warning("Doubao 路由模块未找到，相关功能将不可用")
    DOUBAO_ROUTER_AVAILABLE = False

try:
    from modules.routes import creative_workflow_router
    CREATIVE_WORKFLOW_AVAILABLE = True
except ImportError:
    logger.warning("创意工作流路由模块未找到，相关功能将不可用")
    CREATIVE_WORKFLOW_AVAILABLE = False

# ==================== 配置管理 ====================

class Config:
    """全局配置管理类"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            logger.warning(f"配置文件 {self.config_path} 不存在，使用环境变量")
            return self._load_from_env()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"成功加载配置文件: {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return self._load_from_env()

    def _load_from_env(self) -> Dict[str, Any]:
        """从环境变量加载配置"""
        return {
            "suno": {
                "api_key": os.getenv("SUNO_API_KEY", ""),
                "api_base": "https://api.sunoapi.org/api/v1",
                "upload_base": "https://sunoapiorg.redpandaai.co/api",
                "enabled": True
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "output_dir": "outputs",
                "max_upload_size_mb": 50,
                "poll_interval_seconds": 8,
                "max_poll_timeout_seconds": 900
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    def is_enabled(self, service: str) -> bool:
        """检查服务是否启用"""
        return self.get(f"{service}.enabled", False)


# 全局配置实例
config = Config()

# ==================== API客户端基类 ====================

class BaseAPIClient(ABC):
    """API客户端基类"""

    def __init__(self, api_key: str, api_base: str, service_name: str):
        self.api_key = api_key
        self.api_base = api_base.rstrip('/')
        self.service_name = service_name
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """通用请求方法，带重试机制"""
        url = f"{self.api_base}{endpoint}"
        max_retries = 3

        # 设置默认超时时间（图片生成需要更长时间）
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 180  # 3分钟超时

        for attempt in range(max_retries):
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout as e:
                if attempt < max_retries - 1:
                    logger.warning(f"{self.service_name} 请求超时，重试 {attempt + 1}/{max_retries}")
                    time.sleep(2 ** attempt)
                    continue
                logger.error(f"{self.service_name} 请求超时: {e}")
                raise HTTPException(status_code=504, detail="请求超时，请稍后重试")
            except requests.exceptions.HTTPError as e:
                error_detail = f"状态码: {response.status_code}"
                try:
                    error_detail += f", 响应: {response.text[:200]}"
                except:
                    pass

                if response.status_code >= 500 and attempt < max_retries - 1:
                    logger.warning(f"{self.service_name} 请求失败 ({error_detail})，重试 {attempt + 1}/{max_retries}")
                    time.sleep(2 ** attempt)
                    continue
                logger.error(f"{self.service_name} HTTP错误: {error_detail}")
                raise HTTPException(status_code=response.status_code, detail=error_detail)
            except Exception as e:
                logger.error(f"{self.service_name} 请求异常: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        raise HTTPException(status_code=500, detail=f"{self.service_name} 请求失败")

    def _get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """GET请求"""
        return self._request('GET', endpoint, **kwargs)

    def _post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """POST请求"""
        return self._request('POST', endpoint, **kwargs)

    @abstractmethod
    def health_check(self) -> bool:
        """健康检查"""
        pass


# ==================== Suno音乐生成客户端 ====================

class SunoClient(BaseAPIClient):
    """Suno音乐生成API客户端"""

    def __init__(self):
        api_key = config.get('suno.api_key')
        api_base = config.get('suno.api_base')
        if not api_key:
            raise ValueError("Suno API Key未配置")

        super().__init__(api_key, api_base, "Suno")
        self.upload_base = config.get('suno.upload_base', '').rstrip('/')
        self.output_dir = pathlib.Path(config.get('server.output_dir', 'outputs'))
        self.output_dir.mkdir(exist_ok=True)

    def health_check(self) -> bool:
        """健康检查"""
        try:
            credits = self.get_credits()
            return credits >= 0
        except:
            return False

    def get_credits(self) -> int:
        """查询剩余积分"""
        res = self._get('/generate/credit')
        if res.get('code') != 200:
            raise HTTPException(status_code=400, detail=res.get('msg', '查询积分失败'))
        return res['data']

    def generate_music(self,
                      prompt: str,
                      model: str = "V4_5",
                      custom: bool = False,
                      style: str = "",
                      title: str = "",
                      instrumental: bool = False,
                      wait: bool = True) -> Dict[str, Any]:
        """生成音乐"""
        payload = {
            "prompt": prompt,
            "model": model,
            "customMode": custom
        }

        if custom:
            payload.update({
                "tags": style,
                "title": title,
                "instrumental": instrumental
            })

        res = self._post('/generate', json=payload)
        if res.get('code') != 200:
            raise HTTPException(status_code=400, detail=res.get('msg', '生成音乐失败'))

        task_id = res['data']
        logger.info(f"音乐生成任务已创建: {task_id}")

        if wait:
            return self._poll_task(task_id)

        return {"task_id": task_id, "status": "processing"}

    def generate_lyrics(self, prompt: str, wait: bool = True) -> Dict[str, Any]:
        """生成歌词"""
        # Suno API要求必须提供callBackUrl参数
        payload = {
            "prompt": prompt,
            "callBackUrl": "https://example.invalid/lyrics"  # 占位URL
        }
        res = self._post('/lyrics', json=payload)

        if res.get('code') != 200:
            raise HTTPException(status_code=400, detail=res.get('msg', '生成歌词失败'))

        task_id = res['data'].get('taskId') if isinstance(res['data'], dict) else res['data']
        logger.info(f"歌词生成任务已创建: {task_id}")

        if wait:
            return self._poll_task(task_id, task_type='lyrics')

        return {"task_id": task_id, "status": "processing"}

    def extend_music(self,
                    audio_id: str,
                    model: str = "V4_5",
                    default_param: bool = False,
                    continue_at: int = 0,
                    title: str = "",
                    style: str = "",
                    prompt: str = "",
                    wait: bool = True) -> Dict[str, Any]:
        """延长音乐"""
        payload = {
            "audioId": audio_id,
            "model": model,
            "defaultParamFlag": default_param
        }

        if default_param:
            payload.update({
                "continueAt": continue_at,
                "title": title,
                "tags": style,
                "prompt": prompt
            })

        res = self._post('/generate/extend', json=payload)
        if res.get('code') != 200:
            raise HTTPException(status_code=400, detail=res.get('msg', '延长音乐失败'))

        task_id = res['data']
        logger.info(f"音乐延长任务已创建: {task_id}")

        if wait:
            return self._poll_task(task_id)

        return {"task_id": task_id, "status": "processing"}

    def _poll_task(self, task_id: str, task_type: str = 'generate') -> Dict[str, Any]:
        """轮询任务状态

        Args:
            task_id: 任务ID
            task_type: 任务类型，可选值: 'generate', 'lyrics', 'separate', 'wav', 'mp4'
        """
        poll_interval = config.get('server.poll_interval_seconds', 8)
        max_timeout = config.get('server.max_poll_timeout_seconds', 900)
        start_time = time.time()

        # 根据任务类型选择不同的查询端点
        endpoint_map = {
            'generate': '/generate/record-info',
            'lyrics': '/lyrics/record-info',
            'separate': '/generate/record-info',  # 使用相同的端点
            'wav': '/generate/record-info',
            'mp4': '/generate/record-info'
        }

        endpoint = endpoint_map.get(task_type, '/generate/record-info')
        logger.info(f"开始轮询任务: {task_id} (类型: {task_type})")

        while time.time() - start_time < max_timeout:
            try:
                res = self._get(f'{endpoint}?taskId={task_id}')

                if res.get('code') != 200:
                    logger.error(f"查询任务失败: {res.get('msg')}")
                    time.sleep(poll_interval)
                    continue

                data = res['data']
                status = data.get('status')

                logger.debug(f"任务 {task_id} 状态: {status}")

                if status == 'SUCCESS':
                    logger.success(f"任务 {task_id} 完成")
                    return data
                elif status == 'FAIL':
                    raise HTTPException(status_code=400, detail="任务执行失败")

                time.sleep(poll_interval)

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"轮询异常: {e}")
                time.sleep(poll_interval)

        raise HTTPException(status_code=408, detail="任务超时")

    def get_task_info(self, task_id: str) -> Dict[str, Any]:
        """查询任务信息"""
        res = self._get(f'/generate/record-info?taskId={task_id}')
        if res.get('code') != 200:
            raise HTTPException(status_code=400, detail=res.get('msg', '查询任务失败'))
        return res['data']


# ==================== 图片生成客户端 ====================

class ImageGenerationClient(BaseAPIClient):
    """图片生成API客户端（支持多种服务）"""

    def __init__(self):
        if not config.is_enabled('image_generation'):
            raise ValueError("图片生成服务未启用")

        api_key = config.get('image_generation.api_key')
        api_base = config.get('image_generation.api_base')
        provider = config.get('image_generation.provider', 'stable-diffusion')

        super().__init__(api_key, api_base, f"ImageGen-{provider}")
        self.provider = provider
        self.default_model = config.get('image_generation.default_model')

    def health_check(self) -> bool:
        """健康检查"""
        # 不同provider可能有不同的健康检查endpoint
        return True

    def generate(self,
                prompt: str,
                model: Optional[str] = None,
                size: str = "1024x1024",
                **kwargs) -> Dict[str, Any]:
        """生成图片"""
        model = model or self.default_model

        # 根据不同provider使用不同的API格式
        if self.provider == 'newapi':
            # New API 使用 OpenAI 兼容格式
            payload = {
                "model": model,
                "prompt": prompt,
                "n": 1,
                "size": size,
                "response_format": "url",
                **kwargs
            }
            logger.info(f"发起图片生成请求 (New API): {prompt[:50]}...")
            res = self._post('/images/generations', json=payload)
        else:
            # 其他provider的通用格式
            payload = {
                "prompt": prompt,
                "model": model,
                "size": size,
                **kwargs
            }
            logger.info(f"发起图片生成请求: {prompt[:50]}...")
            res = self._post('/generate', json=payload)

        return res


# ==================== 视频生成客户端 ====================

class VideoGenerationClient(BaseAPIClient):
    """视频生成API客户端（即梦等）"""

    def __init__(self):
        if not config.is_enabled('video_generation'):
            raise ValueError("视频生成服务未启用")

        api_key = config.get('video_generation.api_key')
        api_base = config.get('video_generation.api_base')
        provider = config.get('video_generation.provider', 'jimeng')

        super().__init__(api_key, api_base, f"VideoGen-{provider}")
        self.provider = provider
        self.default_model = config.get('video_generation.default_model')

    def health_check(self) -> bool:
        """健康检查"""
        return True

    def generate(self,
                prompt: str,
                model: Optional[str] = None,
                duration: int = 5,
                **kwargs) -> Dict[str, Any]:
        """生成视频"""
        model = model or self.default_model

        payload = {
            "prompt": prompt,
            "model": model,
            "duration": duration,
            **kwargs
        }

        logger.info(f"发起视频生成请求: {prompt[:50]}...")
        res = self._post('/generate', json=payload)
        return res


# ==================== 文字处理客户端 ====================

class TextProcessingClient(BaseAPIClient):
    """文字处理API客户端（DeepSeek等）"""

    def __init__(self):
        if not config.is_enabled('text_processing'):
            raise ValueError("文字处理服务未启用")

        api_key = config.get('text_processing.api_key')
        api_base = config.get('text_processing.api_base')
        provider = config.get('text_processing.provider', 'deepseek')

        super().__init__(api_key, api_base, f"TextProcess-{provider}")
        self.provider = provider
        self.default_model = config.get('text_processing.default_model')

    def health_check(self) -> bool:
        """健康检查"""
        return True

    def chat(self,
            messages: List[Dict[str, str]],
            model: Optional[str] = None,
            **kwargs) -> Dict[str, Any]:
        """对话接口"""
        model = model or self.default_model

        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }

        logger.info(f"发起文字处理请求")
        res = self._post('/chat/completions', json=payload)
        return res


# ==================== 音频处理客户端 ====================

class AudioProcessingClient(BaseAPIClient):
    """音频处理API客户端"""

    def __init__(self):
        if not config.is_enabled('audio_processing'):
            raise ValueError("音频处理服务未启用")

        api_key = config.get('audio_processing.api_key')
        api_base = config.get('audio_processing.api_base')
        provider = config.get('audio_processing.provider', 'custom')

        super().__init__(api_key, api_base, f"AudioProcess-{provider}")
        self.provider = provider
        self.default_model = config.get('audio_processing.default_model')

    def health_check(self) -> bool:
        """健康检查"""
        return True

    def process(self,
               audio_url: str,
               task_type: str,
               model: Optional[str] = None,
               **kwargs) -> Dict[str, Any]:
        """处理音频"""
        model = model or self.default_model

        payload = {
            "audio_url": audio_url,
            "task_type": task_type,
            "model": model,
            **kwargs
        }

        logger.info(f"发起音频处理请求: {task_type}")
        res = self._post('/process', json=payload)
        return res


# ==================== Pydantic模型定义 ====================

class MusicGenerateRequest(BaseModel):
    prompt: str = Field(..., description="音乐生成提示词")
    model: str = Field(default="V4_5", description="模型版本")
    custom: bool = Field(default=False, description="是否自定义模式")
    style: str = Field(default="", description="音乐风格")
    title: str = Field(default="", description="音乐标题")
    instrumental: bool = Field(default=False, description="是否纯器乐")
    wait: bool = Field(default=True, description="是否等待完成")


class LyricsGenerateRequest(BaseModel):
    prompt: str = Field(..., description="歌词生成提示词")
    wait: bool = Field(default=True, description="是否等待完成")


class MusicExtendRequest(BaseModel):
    audio_id: str = Field(..., description="音频ID")
    model: str = Field(default="V4_5", description="模型版本")
    default_param: bool = Field(default=False, description="是否使用自定义参数")
    continue_at: int = Field(default=0, description="延长起始位置（秒）")
    title: str = Field(default="", description="标题")
    style: str = Field(default="", description="风格")
    prompt: str = Field(default="", description="提示词")
    wait: bool = Field(default=True, description="是否等待完成")


class ImageGenerateRequest(BaseModel):
    prompt: str = Field(..., description="图片生成提示词")
    model: Optional[str] = Field(default=None, description="模型名称")
    size: str = Field(default="1024x1024", description="图片尺寸")
    negative_prompt: str = Field(default="", description="负面提示词")


class VideoGenerateRequest(BaseModel):
    prompt: str = Field(..., description="视频生成提示词")
    model: Optional[str] = Field(default=None, description="模型名称")
    duration: int = Field(default=5, description="视频时长（秒）")


class TextChatRequest(BaseModel):
    messages: List[Dict[str, str]] = Field(..., description="对话消息列表")
    model: Optional[str] = Field(default=None, description="模型名称")
    temperature: float = Field(default=0.7, description="温度参数")
    max_tokens: int = Field(default=2000, description="最大token数")


class AudioProcessRequest(BaseModel):
    audio_url: str = Field(..., description="音频URL")
    task_type: str = Field(..., description="任务类型: transcribe, enhance, separate等")
    model: Optional[str] = Field(default=None, description="模型名称")


# ==================== FastAPI应用 ====================

app = FastAPI(
    title="AI创作平台",
    description="集成音乐、图片、视频、文字、音频处理的多功能AI平台",
    version="2.0.0"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
output_dir = pathlib.Path(config.get('server.output_dir', 'outputs'))
output_dir.mkdir(exist_ok=True)
app.mount("/outputs", StaticFiles(directory=str(output_dir)), name="outputs")

# 注册模块化路由
if MUSIC_WORKFLOW_AVAILABLE:
    app.include_router(music_workflow_router)
    logger.info("✅ 音乐创作工作流模块已加载")

if SUNO_ROUTER_AVAILABLE:
    app.include_router(suno_router)
    logger.info("✅ Suno API 路由模块已加载")

if DOUBAO_ROUTER_AVAILABLE:
    app.include_router(doubao_router)
    logger.info("✅ Doubao AI 路由模块已加载")

if CREATIVE_WORKFLOW_AVAILABLE:
    app.include_router(creative_workflow_router)
    logger.info("✅ 创意工作流路由模块已加载")

# 初始化客户端（懒加载）
_suno_client: Optional[SunoClient] = None
_image_client: Optional[ImageGenerationClient] = None
_video_client: Optional[VideoGenerationClient] = None
_text_client: Optional[TextProcessingClient] = None
_audio_client: Optional[AudioProcessingClient] = None


def get_suno_client() -> SunoClient:
    """获取Suno客户端"""
    global _suno_client
    if _suno_client is None:
        _suno_client = SunoClient()
    return _suno_client


def get_image_client() -> ImageGenerationClient:
    """获取图片生成客户端"""
    global _image_client
    if _image_client is None:
        _image_client = ImageGenerationClient()
    return _image_client


def get_video_client() -> VideoGenerationClient:
    """获取视频生成客户端"""
    global _video_client
    if _video_client is None:
        _video_client = VideoGenerationClient()
    return _video_client


def get_text_client() -> TextProcessingClient:
    """获取文字处理客户端"""
    global _text_client
    if _text_client is None:
        _text_client = TextProcessingClient()
    return _text_client


def get_audio_client() -> AudioProcessingClient:
    """获取音频处理客户端"""
    global _audio_client
    if _audio_client is None:
        _audio_client = AudioProcessingClient()
    return _audio_client


# ==================== Web UI ====================

def get_creative_ui_html() -> str:
    """生成创意工作流UI的HTML"""
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI创作平台 - 音乐创作工作流</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; color: white; margin-bottom: 40px; }
        .header h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .status-bar {
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 15px 25px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
        }
        .status-item { display: flex; align-items: center; gap: 10px; }
        .status-dot { width: 10px; height: 10px; background: #4ade80; border-radius: 50%; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .workflow-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 25px; margin-bottom: 30px; }
        .workflow-card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .workflow-card:hover { transform: translateY(-5px); box-shadow: 0 15px 40px rgba(0,0,0,0.3); }
        .workflow-card h2 { color: #667eea; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; font-size: 1.8em; }
        .workflow-card .description { color: #666; margin-bottom: 20px; line-height: 1.6; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: #333; font-weight: 500; }
        .form-group input[type="text"], .form-group textarea, .form-group select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1em;
            transition: border-color 0.3s;
            font-family: inherit;
        }
        .form-group input:focus, .form-group textarea:focus, .form-group select:focus { outline: none; border-color: #667eea; }
        .form-group textarea { min-height: 120px; resize: vertical; }
        .form-group input[type="file"] { padding: 10px; }
        .checkbox-group { display: flex; align-items: center; gap: 10px; margin-top: 15px; }
        .checkbox-group input[type="checkbox"] { width: 20px; height: 20px; cursor: pointer; }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
            margin-top: 10px;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
        .btn:active { transform: translateY(0); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .result-box {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            display: none;
        }
        .result-box.show { display: block; animation: slideDown 0.3s ease-out; }
        @keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
        .result-box h3 { color: #667eea; margin-bottom: 10px; }
        .result-box pre {
            background: white;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            line-height: 1.6;
        }
        .loading { display: none; text-align: center; padding: 20px; color: #667eea; }
        .loading.show { display: block; }
        .spinner { border: 3px solid #f3f3f3; border-top: 3px solid #667eea; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 10px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .tag { display: inline-block; background: #667eea; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8em; margin-left: 10px; }
        .error { background: #fee; border-left-color: #f44; color: #c33; }
        .success { background: #efe; border-left-color: #4a4; color: #363; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 AI创作平台</h1>
            <p>Suno 音乐生成 + Doubao AI 智能创作</p>
        </div>
        <div class="status-bar">
            <div class="status-item"><div class="status-dot"></div><span>服务运行中</span></div>
            <div class="status-item"><span>Suno 积分: <strong id="credits">加载中...</strong></span></div>
            <div class="status-item"><span>Doubao: <strong>✓ 已连接</strong></span></div>
        </div>
        <div class="workflow-grid">
            <div class="workflow-card">
                <h2>💡 灵感写歌<span class="tag">推荐</span></h2>
                <p class="description">输入你的创作灵感，AI 会自动生成歌词并创作音乐</p>
                <form id="inspirationForm">
                    <div class="form-group">
                        <label>创作灵感 *</label>
                        <textarea name="inspiration" placeholder="例如：夏日海边的回忆，夕阳西下的温柔..." required></textarea>
                    </div>
                    <div class="form-group">
                        <label>音乐风格</label>
                        <select name="style">
                            <option value="流行">流行</option>
                            <option value="民谣">民谣</option>
                            <option value="摇滚">摇滚</option>
                            <option value="说唱">说唱</option>
                            <option value="电子">电子</option>
                            <option value="古风">古风</option>
                            <option value="爵士">爵士</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>情绪基调</label>
                        <input type="text" name="mood" placeholder="例如：温暖、忧伤、激昂..." />
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="autoGenerate1" name="auto_generate" checked />
                        <label for="autoGenerate1">自动生成音乐</label>
                    </div>
                    <button type="submit" class="btn">✨ 开始创作</button>
                </form>
                <div class="loading" id="loading1"><div class="spinner"></div><p>AI 正在创作中...</p></div>
                <div class="result-box" id="result1"></div>
            </div>
            <div class="workflow-card">
                <h2>🖼️ 图片成歌<span class="tag">特色</span></h2>
                <p class="description">上传一张图片，AI 会分析图片的氛围并创作相应的音乐</p>
                <form id="imageForm">
                    <div class="form-group">
                        <label>图片URL *</label>
                        <input type="url" name="image_url" placeholder="https://example.com/image.jpg" required />
                    </div>
                    <div class="form-group">
                        <label>额外提示（可选）</label>
                        <textarea name="additional_prompt" placeholder="告诉 AI 你希望强调图片中的哪些元素..."></textarea>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="autoGenerate2" name="auto_generate" checked />
                        <label for="autoGenerate2">自动生成音乐</label>
                    </div>
                    <button type="submit" class="btn">🎨 开始创作</button>
                </form>
                <div class="loading" id="loading2"><div class="spinner"></div><p>分析图片并创作中...</p></div>
                <div class="result-box" id="result2"></div>
            </div>
            <div class="workflow-card">
                <h2>🎤 AI翻唱<span class="tag">高级</span></h2>
                <p class="description">上传音频文件，AI 会改变风格、音色或语言进行翻唱</p>
                <form id="coverForm">
                    <div class="form-group">
                        <label>上传音频文件 *</label>
                        <input type="file" name="file" accept="audio/*" required />
                    </div>
                    <div class="form-group">
                        <label>目标风格 *</label>
                        <input type="text" name="target_style" placeholder="例如：摇滚、民谣、电子..." required />
                    </div>
                    <div class="form-group">
                        <label>新标题（可选）</label>
                        <input type="text" name="new_title" placeholder="翻唱版标题" />
                    </div>
                    <div class="form-group">
                        <label>新歌词（可选）</label>
                        <textarea name="new_lyrics" placeholder="如果要改变歌词，请在这里输入..."></textarea>
                    </div>
                    <button type="submit" class="btn">🎵 开始翻唱</button>
                </form>
                <div class="loading" id="loading3"><div class="spinner"></div><p>上传并处理中...</p></div>
                <div class="result-box" id="result3"></div>
            </div>
            <div class="workflow-card">
                <h2>🎬 完整创作流<span class="tag">一站式</span></h2>
                <p class="description">从灵感到音乐、封面、MV，一站式完成全部创作</p>
                <form id="fullWorkflowForm">
                    <div class="form-group">
                        <label>创作主题 *</label>
                        <input type="text" name="inspiration" placeholder="例如：青春校园、追梦之旅..." required />
                    </div>
                    <div class="form-group">
                        <label>音乐风格</label>
                        <select name="style">
                            <option value="流行">流行</option>
                            <option value="民谣">民谣</option>
                            <option value="摇滚">摇滚</option>
                            <option value="说唱">说唱</option>
                            <option value="电子">电子</option>
                        </select>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="createCover" name="create_cover" />
                        <label for="createCover">生成专辑封面</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="createVideo" name="create_video" />
                        <label for="createVideo">生成音乐MV</label>
                    </div>
                    <button type="submit" class="btn">🚀 启动完整创作</button>
                </form>
                <div class="loading" id="loading4"><div class="spinner"></div><p>完整创作流程启动中...</p></div>
                <div class="result-box" id="result4"></div>
            </div>
        </div>
    </div>
    <script>
        async function loadCredits() {
            try {
                const res = await fetch('/api/suno/credits');
                const data = await res.json();
                document.getElementById('credits').textContent = data.data.credits;
            } catch (e) {
                document.getElementById('credits').textContent = '加载失败';
            }
        }
        loadCredits();
        function handleFormSubmit(formId, endpoint, loadingId, resultId, isFormData) {
            const form = document.getElementById(formId);
            const loading = document.getElementById(loadingId);
            const result = document.getElementById(resultId);
            const btn = form.querySelector('button[type="submit"]');
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                loading.classList.add('show');
                result.classList.remove('show');
                btn.disabled = true;
                try {
                    let body;
                    if (isFormData) {
                        body = new FormData(form);
                    } else {
                        const formData = new FormData(form);
                        const data = {};
                        formData.forEach((value, key) => {
                            if (key === 'auto_generate' || key === 'create_cover' || key === 'create_video') {
                                data[key] = form.querySelector(`[name="${key}"]`).checked;
                            } else {
                                data[key] = value;
                            }
                        });
                        body = JSON.stringify(data);
                    }
                    const options = { method: 'POST', body: body };
                    if (!isFormData) options.headers = { 'Content-Type': 'application/json' };
                    const res = await fetch(endpoint, options);
                    const responseData = await res.json();
                    loading.classList.remove('show');
                    btn.disabled = false;
                    result.classList.add('show');
                    if (res.ok) {
                        result.classList.remove('error');
                        result.classList.add('success');
                        if (responseData.data.lyrics) {
                            result.innerHTML = `<h3>✅ 创作成功！</h3><h4>📝 生成的歌词：</h4><pre>${responseData.data.lyrics}</pre>${responseData.data.music_task_id ? `<p><strong>🎵 音乐任务ID:</strong> ${responseData.data.music_task_id}</p>` : ''}<p style="margin-top: 15px; color: #666;">使用任务ID查询生成状态：<code>/api/suno/task/{task_id}</code></p>`;
                        } else {
                            result.innerHTML = `<h3>✅ 创作成功！</h3><pre>${JSON.stringify(responseData.data, null, 2)}</pre>`;
                        }
                        loadCredits();
                    } else {
                        result.classList.remove('success');
                        result.classList.add('error');
                        result.innerHTML = `<h3>❌ 创作失败</h3><pre>${JSON.stringify(responseData, null, 2)}</pre>`;
                    }
                } catch (error) {
                    loading.classList.remove('show');
                    btn.disabled = false;
                    result.classList.add('show', 'error');
                    result.innerHTML = `<h3>❌ 请求失败</h3><pre>${error.message}</pre>`;
                }
            });
        }
        handleFormSubmit('inspirationForm', '/api/creative/inspiration-song', 'loading1', 'result1');
        handleFormSubmit('imageForm', '/api/creative/image-to-song', 'loading2', 'result2');
        handleFormSubmit('coverForm', '/api/creative/upload-cover', 'loading3', 'result3', true);
        handleFormSubmit('fullWorkflowForm', '/api/creative/full-workflow', 'loading4', 'result4', true);
    </script>
</body>
</html>
"""

# ==================== API路由 ====================

@app.get("/", response_class=HTMLResponse)
async def index():
    """主页：默认展示创意工作流 V2 UI"""
    return await creative_workflow_ui()


@app.get("/creative", response_class=HTMLResponse)
async def creative_workflow_ui():
    """创意工作流Web UI - V2版本"""
    html_path = pathlib.Path(__file__).parent / "templates" / "creative_ui_v2.html"
    if html_path.exists():
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()

    # 降级到增强版
    html_path = pathlib.Path(__file__).parent / "templates" / "creative_ui_enhanced.html"
    if html_path.exists():
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()

    return get_creative_ui_html()


@app.get("/api-docs")
async def api_docs_simple():
    """API 文档（简化版，不依赖 CDN）"""
    html_path = pathlib.Path(__file__).parent / "templates" / "api_docs_simple.html"
    if html_path.exists():
        with open(html_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>文档文件不存在</h1>")


@app.get("/api-docs-cdn")
async def api_docs_cdn():
    """API 文档（使用国内 CDN）"""
    html_path = pathlib.Path(__file__).parent / "templates" / "api_docs.html"
    if html_path.exists():
        with open(html_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>文档文件不存在</h1>")


@app.get("/favicon.ico")
async def favicon():
    """返回网站图标"""
    # 返回一个简单的SVG图标作为favicon
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <rect width="100" height="100" rx="15" fill="#6366f1"/>
        <text x="50" y="70" font-size="60" text-anchor="middle" fill="white">🎨</text>
    </svg>"""
    from fastapi.responses import Response
    return Response(content=svg_content, media_type="image/svg+xml")


@app.get("/api/health")
async def health_check():
    """健康检查"""
    services = {}

    if config.is_enabled('suno'):
        try:
            client = get_suno_client()
            services['suno'] = client.health_check()
        except:
            services['suno'] = False

    if config.is_enabled('image_generation'):
        try:
            client = get_image_client()
            services['image_generation'] = client.health_check()
        except:
            services['image_generation'] = False

    if config.is_enabled('video_generation'):
        try:
            client = get_video_client()
            services['video_generation'] = client.health_check()
        except:
            services['video_generation'] = False

    if config.is_enabled('text_processing'):
        try:
            client = get_text_client()
            services['text_processing'] = client.health_check()
        except:
            services['text_processing'] = False

    if config.is_enabled('audio_processing'):
        try:
            client = get_audio_client()
            services['audio_processing'] = client.health_check()
        except:
            services['audio_processing'] = False

    return {
        "status": "ok",
        "services": services,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/config/services")
async def get_enabled_services():
    """获取已启用的服务列表"""
    return {
        "suno": config.is_enabled('suno'),
        "image_generation": config.is_enabled('image_generation'),
        "video_generation": config.is_enabled('video_generation'),
        "text_processing": config.is_enabled('text_processing'),
        "audio_processing": config.is_enabled('audio_processing')
    }


# ==================== 音乐生成相关API ====================

@app.get("/api/suno/credits")
async def get_credits():
    """查询Suno积分"""
    try:
        client = get_suno_client()
        credits = client.get_credits()
        return {"code": 200, "data": {"credits": credits}}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"查询积分失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/suno/generate")
async def generate_music(request: MusicGenerateRequest):
    """生成音乐"""
    try:
        client = get_suno_client()
        result = client.generate_music(
            prompt=request.prompt,
            model=request.model,
            custom=request.custom,
            style=request.style,
            title=request.title,
            instrumental=request.instrumental,
            wait=request.wait
        )
        return {"code": 200, "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"生成音乐失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/suno/lyrics")
async def generate_lyrics(request: LyricsGenerateRequest):
    """生成歌词"""
    try:
        client = get_suno_client()
        result = client.generate_lyrics(
            prompt=request.prompt,
            wait=request.wait
        )
        return {"code": 200, "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"生成歌词失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/suno/extend")
async def extend_music(request: MusicExtendRequest):
    """延长音乐"""
    try:
        client = get_suno_client()
        result = client.extend_music(
            audio_id=request.audio_id,
            model=request.model,
            default_param=request.default_param,
            continue_at=request.continue_at,
            title=request.title,
            style=request.style,
            prompt=request.prompt,
            wait=request.wait
        )
        return {"code": 200, "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"延长音乐失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/suno/task/{task_id}")
async def get_task_info(task_id: str):
    """查询任务信息"""
    try:
        client = get_suno_client()
        result = client.get_task_info(task_id)
        return {"code": 200, "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"查询任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 图片生成相关API ====================

@app.post("/api/image/generate")
async def generate_image(request: ImageGenerateRequest):
    """生成图片"""
    try:
        client = get_image_client()
        result = client.generate(
            prompt=request.prompt,
            model=request.model,
            size=request.size,
            negative_prompt=request.negative_prompt
        )
        return {"code": 200, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"生成图片失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 视频生成相关API ====================

@app.post("/api/video/generate")
async def generate_video(request: VideoGenerateRequest):
    """生成视频"""
    try:
        client = get_video_client()
        result = client.generate(
            prompt=request.prompt,
            model=request.model,
            duration=request.duration
        )
        return {"code": 200, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"生成视频失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 文字处理相关API ====================

@app.post("/api/text/chat")
async def text_chat(request: TextChatRequest):
    """文字对话"""
    try:
        client = get_text_client()
        result = client.chat(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return {"code": 200, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"文字处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 音频处理相关API ====================

@app.post("/api/audio/process")
async def process_audio(request: AudioProcessRequest):
    """处理音频"""
    try:
        client = get_audio_client()
        result = client.process(
            audio_url=request.audio_url,
            task_type=request.task_type,
            model=request.model
        )
        return {"code": 200, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"音频处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 文件上传 ====================

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件"""
    try:
        # 保存文件到临时目录
        suffix = pathlib.Path(file.filename).suffix
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)

        content = await file.read()
        temp_file.write(content)
        temp_file.close()

        logger.info(f"文件已上传: {file.filename} -> {temp_file.name}")

        return {
            "code": 200,
            "data": {
                "filename": file.filename,
                "temp_path": temp_file.name,
                "size": len(content)
            }
        }
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 主程序入口 ====================

if __name__ == "__main__":
    import uvicorn

    host = config.get('server.host', '0.0.0.0')
    port = config.get('server.port', 8000)

    logger.info(f"启动AI创作平台服务器: http://{host}:{port}")
    logger.info(f"API文档: http://{host}:{port}/docs")
    logger.info(f"已启用服务: {[k for k, v in config.get('', {}).items() if isinstance(v, dict) and v.get('enabled')]}")

    uvicorn.run(
        "ai_platform:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
