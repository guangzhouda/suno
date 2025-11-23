"""
Suno API 客户端

提供完整的 Suno 音乐生成 API 功能：
- 音乐生成
- 翻唱功能（上传音频）
- 延长音乐
- 人声分离
- 添加人声/伴奏
- WAV 转换
等
"""

import os
import json
import time
import pathlib
from typing import Optional, Dict, Any
import requests


class SunoClient:
    """Suno API 客户端"""

    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        # 先初始化，避免后续属性访问报缺失
        self.api_key = api_key

        # 优先级：参数 > 配置文件 > 环境变量
        if not self.api_key:
            # 尝试从 config.json 读取
            config_file = pathlib.Path("config.json")
            if config_file.exists():
                try:
                    with open(config_file, encoding="utf-8-sig") as f:  # 兼容 BOM
                        config = json.load(f)
                        suno_config = config.get("suno", {})
                        self.api_key = suno_config.get("api_key")
                except Exception as e:
                    print(f"警告：读取 config.json 失败: {e}")

            # 从环境变量读取
            if not self.api_key:
                self.api_key = os.getenv("SUNO_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "缺少 Suno API Key！请在 config.json 中配置 suno.api_key "
                "或设置环境变量 SUNO_API_KEY"
            )

        self.api_base = api_base or "https://api.sunoapi.org/api/v1"
        self.upload_base = "https://sunoapiorg.redpandaai.co/api"

        # 设置请求头
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.json_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    # ==================== 基础请求方法 ====================

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET 请求"""
        url = f"{self.api_base}{endpoint}"
        for _ in range(3):  # 重试3次
            try:
                r = requests.get(url, headers=self.headers, params=params, timeout=60)
                if r.status_code >= 500:
                    time.sleep(1)
                    continue
                r.raise_for_status()
                return r.json()
            except requests.exceptions.RequestException:
                if _ == 2:  # 最后一次重试
                    raise
                time.sleep(1)
        return {}

    def _post(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """POST 请求"""
        url = f"{self.api_base}{endpoint}"
        for _ in range(3):  # 重试3次
            try:
                r = requests.post(url, headers=self.json_headers, json=json, timeout=60)
                if r.status_code >= 500:
                    time.sleep(1)
                    continue
                r.raise_for_status()
                return r.json()
            except requests.exceptions.RequestException:
                if _ == 2:  # 最后一次重试
                    raise
                time.sleep(1)
        return {}

    # ==================== 账户管理 ====================

    def get_credits(self) -> int:
        """获取剩余积分"""
        res = self._get("/generate/credit")
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]

    # ==================== 音乐生成 ====================

    def generate_music(
        self,
        *,
        prompt: str,
        customMode: bool = False,
        instrumental: bool = False,
        model: str = "V5",
        title: Optional[str] = None,
        style: Optional[str] = None,
        callback: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        生成音乐

        Args:
            prompt: 提示词（customMode=False）或歌词（customMode=True）
            customMode: 自定义模式
            instrumental: 是否纯音乐
            model: 模型版本 (V3_5, V4, V4_5, V4_5PLUS, V5)
            title: 歌曲标题（customMode=True 时必需）
            style: 音乐风格（customMode=True 时必需）
            callback: 回调URL
            **kwargs: 其他参数（negativeTags, vocalGender, styleWeight等）

        Returns:
            任务ID
        """
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
        else:
            payload["prompt"] = prompt

        # 添加其他可选参数
        for key in ["negativeTags", "vocalGender", "personaId"]:
            if key in kwargs and kwargs[key] is not None:
                payload[key] = kwargs[key]

        for key in ["styleWeight", "weirdnessConstraint", "audioWeight"]:
            if key in kwargs and kwargs[key] is not None:
                payload[key] = float(kwargs[key])

        res = self._post("/generate", json=payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    def get_music_info(self, task_id: str) -> Dict[str, Any]:
        """获取音乐生成任务状态"""
        res = self._get("/generate/record-info", params={"taskId": task_id})
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]

    # ==================== 翻唱功能 ====================

    def upload_cover(
        self,
        *,
        uploadUrl: str,
        customMode: bool = True,
        instrumental: bool = False,
        model: str = "V5",
        prompt: Optional[str] = None,
        style: Optional[str] = None,
        title: Optional[str] = None,
        callback: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        上传音频并翻唱

        Args:
            uploadUrl: 音频文件URL（需要先上传获得）
            customMode: 自定义模式
            instrumental: 是否纯音乐
            model: 模型版本
            prompt: 歌词（customMode=True 且 instrumental=False 时）
            style: 目标风格（customMode=True 时必需）
            title: 新标题（customMode=True 时必需）
            callback: 回调URL
            **kwargs: 其他参数

        Returns:
            任务ID
        """
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

        # 添加其他可选参数
        for key in ["negativeTags", "vocalGender"]:
            if key in kwargs and kwargs[key] is not None:
                payload[key] = kwargs[key]

        for key in ["styleWeight", "weirdnessConstraint", "audioWeight"]:
            if key in kwargs and kwargs[key] is not None:
                payload[key] = float(kwargs[key])

        res = self._post("/generate/upload-cover", json=payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    # ==================== 文件上传 ====================

    def upload_stream(self, file_path: str, upload_path: str = "music", file_name: Optional[str] = None) -> str:
        if not file_name:
            file_name = pathlib.Path(file_path).name

        with open(file_path, "rb") as f:
            files = {"file": (file_name, f)}
            data = {"uploadPath": upload_path, "fileName": file_name}
            headers = {"Authorization": f"Bearer {self.api_key}"}
            r = requests.post(
                f"{self.upload_base}/file-stream-upload",
                headers=headers,
                files=files,
                data=data,
                timeout=300
            )

        r.raise_for_status()
        result = r.json()

        if result.get("code") != 200:
            raise RuntimeError(result.get("msg", "上传失败"))

        data = result.get("data") or {}
        # Suno 官方字段名：downloadUrl
        url = data.get("downloadUrl")
        if not url:
            raise RuntimeError(f"上传成功但返回中缺少 downloadUrl 字段: {result}")

        return url

    def upload_fileobj(self, fileobj, upload_path: str = "music", file_name: Optional[str] = None) -> str:
        """
        直接上传文件对象，返回公网 URL（给豆包图片理解用）
        """
        if not file_name:
            file_name = getattr(fileobj, "name", "upload.bin")

        files = {"file": (file_name, fileobj)}
        data = {"uploadPath": upload_path, "fileName": file_name}
        headers = {"Authorization": f"Bearer {self.api_key}"}

        r = requests.post(
            f"{self.upload_base}/file-stream-upload",
            headers=headers,
            files=files,
            data=data,
            timeout=300
        )
        r.raise_for_status()
        result = r.json()

        if result.get("code") != 200:
            raise RuntimeError(result.get("msg", "上传失败"))

        data = result.get("data") or {}
        url = data.get("downloadUrl")
        if not url:
            raise RuntimeError(f"上传成功但返回中缺少 downloadUrl 字段: {result}")

        return url

    def upload_from_url(self, file_url: str, upload_path: str = "music", file_name: Optional[str] = None) -> str:
        if not file_name:
            file_name = pathlib.Path(file_url).name

        payload = {
            "fileUrl": file_url,
            "uploadPath": upload_path,
            "fileName": file_name
        }

        r = requests.post(
            f"{self.upload_base}/file-url-upload",
            headers=self.json_headers,
            json=payload,
            timeout=120
        )

        r.raise_for_status()
        result = r.json()

        if result.get("code") != 200:
            raise RuntimeError(result.get("msg", "上传失败"))

        data = result.get("data") or {}
        url = data.get("downloadUrl")
        if not url:
            raise RuntimeError(f"上传成功但返回中缺少 downloadUrl 字段: {result}")

        return url

    # ==================== 延长音乐 ====================

    def extend_music(
        self,
        audio_id: str,
        *,
        model: str = "V5",
        continueAt: Optional[int] = None,
        defaultParamFlag: bool = False,
        title: Optional[str] = None,
        style: Optional[str] = None,
        prompt: Optional[str] = None,
        callback: Optional[str] = None,
    ) -> str:
        """
        延长现有音乐

        Args:
            audio_id: 原音频ID
            model: 模型版本
            continueAt: 延长位置（秒）
            defaultParamFlag: 是否使用默认参数
            title: 标题（defaultParamFlag=True 时必需）
            style: 风格（defaultParamFlag=True 时必需）
            prompt: 续写提示
            callback: 回调URL

        Returns:
            任务ID
        """
        payload: Dict[str, Any] = {
            "audioId": audio_id,
            "model": model,
            "defaultParamFlag": defaultParamFlag,
            "callBackUrl": callback or "https://example.invalid/extend",
        }

        if defaultParamFlag:
            if continueAt is None or not title or not style:
                raise ValueError("defaultParamFlag=True 时必须提供 continueAt/title/style")
            payload.update({
                "continueAt": continueAt,
                "title": title,
                "style": style
            })
            if prompt:
                payload["prompt"] = prompt

        res = self._post("/generate/extend", json=payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    # ==================== 人声处理 ====================

    def separate_vocals(
        self,
        task_id: str,
        audio_id: str,
        sep_type: str = "separate_vocal",
        callback: Optional[str] = None
    ) -> str:
        """
        人声/伴奏分离

        Args:
            task_id: 原任务ID
            audio_id: 音频ID
            sep_type: 分离类型 (separate_vocal 或其他)
            callback: 回调URL

        Returns:
            任务ID
        """
        payload = {
            "taskId": task_id,
            "audioId": audio_id,
            "type": sep_type,
            "callBackUrl": callback or "https://example.invalid/vocal",
        }

        res = self._post("/vocal-removal/generate", json=payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    def get_vocal_info(self, task_id: str) -> Dict[str, Any]:
        """获取人声分离任务状态"""
        res = self._get("/vocal-removal/record-info", params={"taskId": task_id})
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]

    def add_vocals(
        self,
        uploadUrl: str,
        *,
        prompt: str,
        title: str,
        style: str,
        negativeTags: str = "",
        model: Optional[str] = None,
        callback: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        为伴奏添加人声

        Args:
            uploadUrl: 伴奏文件URL
            prompt: 歌词
            title: 标题
            style: 风格
            negativeTags: 负面标签
            model: 模型版本
            callback: 回调URL
            **kwargs: 其他参数

        Returns:
            任务ID
        """
        payload: Dict[str, Any] = {
            "uploadUrl": uploadUrl,
            "prompt": prompt,
            "title": title,
            "style": style,
            "negativeTags": negativeTags,
            "callBackUrl": callback or "https://example.invalid/add-vocals",
        }

        if model:
            payload["model"] = model

        for key in ["vocalGender", "styleWeight", "weirdnessConstraint", "audioWeight"]:
            if key in kwargs and kwargs[key] is not None:
                if key in ["styleWeight", "weirdnessConstraint", "audioWeight"]:
                    payload[key] = float(kwargs[key])
                else:
                    payload[key] = kwargs[key]

        res = self._post("/generate/add-vocals", json=payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    def add_instrumental(
        self,
        uploadUrl: str,
        *,
        title: str,
        tags: str,
        negativeTags: str = "",
        model: Optional[str] = None,
        callback: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        为清唱添加伴奏

        Args:
            uploadUrl: 清唱文件URL
            title: 标题
            tags: 标签
            negativeTags: 负面标签
            model: 模型版本
            callback: 回调URL
            **kwargs: 其他参数

        Returns:
            任务ID
        """
        payload: Dict[str, Any] = {
            "uploadUrl": uploadUrl,
            "title": title,
            "tags": tags,
            "negativeTags": negativeTags,
            "callBackUrl": callback or "https://example.invalid/add-instrumental",
        }

        if model:
            payload["model"] = model

        for key in ["vocalGender", "styleWeight", "weirdnessConstraint", "audioWeight"]:
            if key in kwargs and kwargs[key] is not None:
                if key in ["styleWeight", "weirdnessConstraint", "audioWeight"]:
                    payload[key] = float(kwargs[key])
                else:
                    payload[key] = kwargs[key]

        res = self._post("/generate/add-instrumental", json=payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    # ==================== 歌词生成 ====================

    def create_lyrics(self, prompt: str, callback: Optional[str] = None) -> str:
        """
        生成歌词

        Args:
            prompt: 歌词创作提示
            callback: 回调URL

        Returns:
            任务ID
        """
        payload = {
            "prompt": prompt,
            "callBackUrl": callback or "https://example.invalid/lyrics"
        }

        res = self._post("/lyrics", json=payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    def get_lyrics_info(self, task_id: str) -> Dict[str, Any]:
        """获取歌词生成任务状态"""
        res = self._get("/lyrics/record-info", params={"taskId": task_id})
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]

    # ==================== 工具方法 ====================

    def convert_wav(self, task_id: str, audio_id: str, callback: Optional[str] = None) -> str:
        """转换为WAV格式"""
        payload = {
            "taskId": task_id,
            "audioId": audio_id,
            "callBackUrl": callback or "https://example.invalid/wav"
        }

        res = self._post("/wav/generate", json=payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    def get_wav_info(self, task_id: str) -> Dict[str, Any]:
        """获取WAV转换任务状态"""
        res = self._get("/wav/record-info", params={"taskId": task_id})
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]
