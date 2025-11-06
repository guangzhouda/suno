
# -*- coding: utf-8 -*-
# filename: main.py
# Python 3.10+
import os
import json
import time
import base64
import pathlib
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

import argparse
import requests

API_BASE = "https://api.sunoapi.org/api/v1"
# 文档里的上传域（仅用于上传接口）
UPLOAD_BASE = "https://sunoapiorg.redpandaai.co/api"
OUT_DIR = pathlib.Path("suno_outputs")
OUT_DIR.mkdir(exist_ok=True)


def _norm(d: Dict[str, Any] | None, *keys: str) -> Any:
    """兼容不同字段命名：依次取第一个存在的键"""
    for k in keys:
        if isinstance(d, dict) and k in d and d[k] is not None:
            return d[k]
    return None


class SunoClient:
    def __init__(self, api_key: Optional[str] = None, poll_interval: int = 8, timeout: int = 900):
        self.api_key = api_key or os.getenv("SUNO_API_KEY")
        if not self.api_key:
            raise RuntimeError("缺少 API Key，请设置环境变量 SUNO_API_KEY。")
        self.poll_interval = poll_interval
        self.timeout = timeout
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.json_headers = dict(self.headers)
        self.json_headers["Content-Type"] = "application/json"

    # -------- 基础请求（含简单重试） --------
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

    def _download(self, url: str, filename: Optional[str] = None) -> pathlib.Path:
        if not url:
            raise ValueError("下载URL为空")
        name = filename or pathlib.Path(urlparse(url).path).name or "download.bin"
        out = OUT_DIR / name
        with requests.get(url, stream=True, timeout=300) as r:
            r.raise_for_status()
            with open(out, "wb") as f:
                for chunk in r.iter_content(131072):
                    if chunk:
                        f.write(chunk)
        print(f"[下载完成] {out}")
        return out

    def _wait_until(self, fetch_fn, task_id: str, ok_status: str = "SUCCESS") -> Dict[str, Any]:
        """统一轮询：直至状态==ok_status 或失败/超时"""
        start = time.time()
        while True:
            data = fetch_fn(task_id)
            # 不同接口字段可能不一致：status / successFlag
            status = _norm(data, "status", "successFlag")
            if status == ok_status or status == 1:  # 封面等接口 successFlag=1
                return data
            if status in {
                "FAILED",
                "CREATE_TASK_FAILED",
                "GENERATE_AUDIO_FAILED",
                "GENERATE_LYRICS_FAILED",
                "GENERATE_MP4_FAILED",
                "CALLBACK_EXCEPTION",
                "SENSITIVE_WORD_ERROR",
            }:
                raise RuntimeError(f"任务失败: {status} / {data.get('errorMessage')}")
            if time.time() - start > self.timeout:
                raise TimeoutError(f"轮询超时（{task_id}）")
            time.sleep(self.poll_interval)

    # -------- 账户 --------
    def get_credits(self) -> int:
        res = self._get("/generate/credit")
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]

    # -------- 歌词 --------
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
        """POST /generate/get-timestamped-lyrics（同步返回对齐结果）"""
        payload = {"taskId": task_id, "audioId": audio_id}
        res = self._post("/generate/get-timestamped-lyrics", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]

    # -------- 生成音乐 --------
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
                payload["prompt"] = prompt  # 自定义+演唱，需要明确歌词
            if personaId:
                payload["personaId"] = personaId
        else:
            payload["prompt"] = prompt  # 非自定义只要 prompt

        # 可选增强
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

    # -------- 延长音乐 --------
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
            # 文档要求 true 时必须带 continueAt/title/style（prompt 可选）
            if continueAt is None or not title or not style:
                raise ValueError("defaultParamFlag=True 时必须提供 continueAt/title/style")
            payload.update({"continueAt": continueAt, "title": title, "style": style})
            if prompt:
                payload["prompt"] = prompt

        res = self._post("/generate/extend", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    # NEW: 上传并扩展音乐
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
        """
        POST /generate/upload-extend
        - defaultParamFlag=true: 需 style/title/continueAt (+prompt 如果有演唱) + uploadUrl
        - defaultParamFlag=false: 仅需 uploadUrl (+prompt 可选)，其余参数默认沿用源音频
        """
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

        # 可选增强
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

    # -------- 人声/伴奏分离 --------
    def separate_vocals(self, task_id: str, audio_id: str, sep_type: str = "separate_vocal",
                        callback: Optional[str] = None) -> str:
        payload = {
            "taskId": task_id,
            "audioId": audio_id,
            "type": sep_type,  # "separate_vocal" 或 "split_stem"
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

    # -------- WAV 转换 --------
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

    # -------- 生成音乐视频 MP4 --------
    def create_music_video(self, task_id: str, audio_id: str,
                           author: Optional[str] = None, domainName: Optional[str] = None,
                           callback: Optional[str] = None) -> str:
        payload = {
            "taskId": task_id,
            "audioId": audio_id,
            "callBackUrl": callback or "https://example.invalid/mp4",
        }
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

    # -------- 上传（3种） --------
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

    # -------- 上传并翻唱音乐（cover） --------
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
        vocalGender: Optional[str] = None,  # "m" / "f" / "n"
        styleWeight: Optional[float] = None,
        weirdnessConstraint: Optional[float] = None,
        audioWeight: Optional[float] = None,
        callback: Optional[str] = None,
    ) -> str:
        """
        POST /api/v1/generate/upload-cover
        规则：
        - customMode=true:
            - instrumental=true:  需 style、title、uploadUrl
            - instrumental=false: 需 style、title、prompt(歌词)、uploadUrl
        - customMode=false: 需 prompt + uploadUrl
        生成文件通常保留 15 天；建议配合“获取音乐生成详情”轮询直至 SUCCESS。
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
                raise ValueError("customMode=True 时需要提供 style 和 title")
            payload.update({"style": style, "title": title})
            if not instrumental:
                if not prompt:
                    raise ValueError("customMode=True 且 instrumental=False 时需要提供 prompt（歌词）")
                payload["prompt"] = prompt
        else:
            if not prompt:
                raise ValueError("customMode=False 时必须提供 prompt（创作提示）")
            payload["prompt"] = prompt

        # 可选增强
        if negativeTags is not None: payload["negativeTags"] = negativeTags
        if vocalGender is not None:  payload["vocalGender"] = vocalGender  # "m"/"f"/"n"
        if styleWeight is not None:  payload["styleWeight"] = float(styleWeight)
        if weirdnessConstraint is not None: payload["weirdnessConstraint"] = float(weirdnessConstraint)
        if audioWeight is not None:  payload["audioWeight"] = float(audioWeight)

        res = self._post("/generate/upload-cover", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    # -------- 新增：添加乐器 / 添加人声 --------
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
            "uploadUrl": uploadUrl,
            "prompt": prompt,
            "title": title,
            "style": style,
            "negativeTags": negativeTags,
            "callBackUrl": callback or "https://example.invalid/add-vocals",
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

    # -------- 新增：风格增强 --------
    def style_generate(self, content: str) -> Dict[str, Any]:
        """POST /style/generate（同步返回）"""
        res = self._post("/style/generate", {"content": content})
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]

    # -------- 新增：生成封面 / 查询封面 --------
    def create_cover(self, task_id: str, callback: Optional[str] = None) -> str:
        """POST /suno/cover/generate"""
        payload = {"taskId": task_id, "callBackUrl": callback or "https://example.invalid/cover-art"}
        res = self._post("/suno/cover/generate", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    def get_cover_info(self, task_id: str) -> Dict[str, Any]:
        """GET /suno/cover/record-info"""
        res = self._get("/suno/cover/record-info", params={"taskId": task_id})
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]

    # -------- 新增：替换音乐分区（局部重写） --------
    def replace_section(self, *, taskId: str, audioId: str, prompt: str, tags: str, title: str,
                        negativeTags: str, infillStartS: float, infillEndS: float,
                        model: Optional[str] = None, callback: Optional[str] = None) -> str:
        payload: Dict[str, Any] = {
            "taskId": taskId,
            "audioId": audioId,
            "prompt": prompt,
            "tags": tags,
            "title": title,
            "negativeTags": negativeTags,
            "infillStartS": float(infillStartS),
            "infillEndS": float(infillEndS),
            "callBackUrl": callback or "https://example.invalid/replace-section",
        }
        if model:
            payload["model"] = model
        res = self._post("/generate/replace-section", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]["taskId"]

    # -------- 新增：生成 Persona（同步返回 personaId） --------
    def generate_persona(self, task_id: str, audio_id: str, *, name: str, description: str) -> Dict[str, Any]:
        payload = {"taskId": task_id, "audioId": audio_id, "name": name, "description": description}
        res = self._post("/generate/generate-persona", payload)
        if res.get("code") != 200:
            raise RuntimeError(res.get("msg"))
        return res["data"]


def run_cli():
    parser = argparse.ArgumentParser(
        description="Suno API 命令行 Demo（Python 3.10+）"
    )
    parser.add_argument("--api-key", help="可选：显式传入 API Key（默认读环境变量 SUNO_API_KEY）")
    parser.add_argument("--poll-interval", type=int, default=8, help="轮询间隔秒（默认8）")
    parser.add_argument("--timeout", type=int, default=900, help="任务总超时时间秒（默认900）")

    sub = parser.add_subparsers(dest="cmd", required=True)

    # 积分
    sub.add_parser("credits", help="查询积分余额")

    # 歌词
    p_lyr = sub.add_parser("lyrics", help="生成歌词（返回taskId并等待完成）")
    p_lyr.add_argument("--prompt", required=True, help="歌词提示词")
    p_lyr.add_argument("--callback", help="回调URL，可选")

    # 生成音乐
    p_gen = sub.add_parser("gen", help="生成音乐（自定义/非自定义）")
    p_gen.add_argument("--prompt", required=True, help="提示词：非自定义为创作提示，自定义为演唱歌词")
    p_gen.add_argument("--custom", action="store_true", help="自定义模式（customMode=true）")
    p_gen.add_argument("--instrumental", action="store_true", help="只生成器乐")
    p_gen.add_argument("--style", help="自定义模式需要：风格，如 流行/摇滚/民谣")
    p_gen.add_argument("--title", help="自定义模式需要：标题")
    p_gen.add_argument("--model", default="V4_5", help="模型：V3_5/V4/V4_5/V4_5PLUS/V5")
    p_gen.add_argument("--callback", help="回调URL，可选")
    p_gen.add_argument("--download", action="store_true", help="生成后自动下载mp3与封面")

    # 查询音乐任务
    p_qm = sub.add_parser("query-music", help="查询音乐任务状态")
    p_qm.add_argument("--task-id", required=True, help="音乐任务ID")

    # 延长音乐
    p_ext = sub.add_parser("extend", help="延长音乐")
    p_ext.add_argument("--audio-id", required=True, help="原音乐audioId")
    p_ext.add_argument("--model", default="V4_5")
    p_ext.add_argument("--default-param", action="store_true", help="defaultParamFlag=true 走自定义续写")
    p_ext.add_argument("--continue-at", type=int, help="defaultParam=true 必填：从何处续写（秒）")
    p_ext.add_argument("--title", help="defaultParam=true 必填：新标题")
    p_ext.add_argument("--style", help="defaultParam=true 必填：风格")
    p_ext.add_argument("--prompt", help="defaultParam=true 可选：歌词/描述")
    p_ext.add_argument("--callback", help="回调URL，可选")

    # NEW: 上传并扩展音乐
    p_up_ext = sub.add_parser("upload-extend", help="上传并扩展音乐")
    p_up_ext.add_argument("--upload-url", help="音频文件的公网URL（与 --file 二选一）")
    p_up_ext.add_argument("--file", help="本地音频文件路径（与 --upload-url 二选一）")
    p_up_ext.add_argument("--upload-path", default="audio/extend", help="远端保存路径（配合 --file 使用）")
    p_up_ext.add_argument("--name", default="extend_input.mp3", help="远端文件名（配合 --file 使用）")
    p_up_ext.add_argument("--model", default="V4_5", help="模型：V3_5/V4/V4_5/V4_5PLUS/V5")
    p_up_ext.add_argument("--default-param", action="store_true", help="defaultParamFlag=true 自定义参数续写")
    p_up_ext.add_argument("--instrumental", action="store_true", help="是否器乐（可选）")
    p_up_ext.add_argument("--prompt", help="defaultParam=true 或非自定义时的提示词/歌词")
    p_up_ext.add_argument("--style", help="defaultParam=true 必填：风格")
    p_up_ext.add_argument("--title", help="defaultParam=true 必填：标题")
    p_up_ext.add_argument("--continue-at", type=int, help="defaultParam=true 必填：续写起点（秒）")
    p_up_ext.add_argument("--callback", help="回调URL，可选")
    p_up_ext.add_argument("--download", action="store_true", help="完成后下载mp3与封面")

    # 人声/伴奏分离
    p_sep = sub.add_parser("separate", help="人声/伴奏分离")
    p_sep.add_argument("--task-id", required=True, help="生成音乐的taskId")
    p_sep.add_argument("--audio-id", required=True, help="audioId")
    p_sep.add_argument("--type", default="separate_vocal", choices=["separate_vocal", "split_stem"], help="分离类型")
    p_sep.add_argument("--download", action="store_true", help="完成后下载分离后的音频")

    # 转 WAV
    p_wav = sub.add_parser("wav", help="转换为WAV")
    p_wav.add_argument("--task-id", required=True)
    p_wav.add_argument("--audio-id", required=True)
    p_wav.add_argument("--download", action="store_true", help="完成后下载wav")

    # 生成 MP4
    p_mp4 = sub.add_parser("mp4", help="生成音乐视频MP4")
    p_mp4.add_argument("--task-id", required=True)
    p_mp4.add_argument("--audio-id", required=True)
    p_mp4.add_argument("--author", help="视频作者名")
    p_mp4.add_argument("--domain", help="域名")
    p_mp4.add_argument("--download", action="store_true", help="完成后下载mp4")

    # 上传
    p_upb = sub.add_parser("upload-b64", help="Base64上传")
    p_upb.add_argument("--file", required=True, help="本地文件路径")
    p_upb.add_argument("--path", default="files/base64", help="远端路径")
    p_upb.add_argument("--name", default="upload.bin", help="远端文件名")

    p_ups = sub.add_parser("upload-stream", help="文件流上传")
    p_ups.add_argument("--file", required=True)
    p_ups.add_argument("--path", default="files/stream")
    p_ups.add_argument("--name", default="upload_stream.bin")

    p_upu = sub.add_parser("upload-url", help="URL直传")
    p_upu.add_argument("--url", required=True)
    p_upu.add_argument("--path", default="files/url")
    p_upu.add_argument("--name", default="upload_from_url.bin")

    # 翻唱（cover）
    p_cover = sub.add_parser("cover", help="上传并翻唱音乐（cover）")
    p_cover.add_argument("--upload-url", help="音频文件的公网URL（与 --file 二选一）")
    p_cover.add_argument("--file", help="本地音频文件路径（与 --upload-url 二选一）")
    p_cover.add_argument("--upload-path", default="audio/cover", help="远端保存路径（配合 --file 使用）")
    p_cover.add_argument("--name", default="cover_input.mp3", help="远端文件名（配合 --file 使用）")
    p_cover.add_argument("--custom", action="store_true", help="自定义模式（customMode=true）")
    p_cover.add_argument("--instrumental", action="store_true", help="只做器乐翻唱（无演唱）")
    p_cover.add_argument("--prompt", help="提示词：custom=false 为创作提示；custom=true 且 instrumental=false 为演唱歌词")
    p_cover.add_argument("--style", help="custom=true 需要：风格")
    p_cover.add_argument("--title", help="custom=true 需要：标题")
    p_cover.add_argument("--model", default="V4_5", help="模型：V3_5/V4/V4_5/V4_5PLUS/V5")
    p_cover.add_argument("--neg", dest="negativeTags", help="负面标签，逗号分隔")
    p_cover.add_argument("--vocal-gender", choices=["m","f","n"], help="人声性别：m/f/n")
    p_cover.add_argument("--style-weight", type=float, help="风格权重 0~1")
    p_cover.add_argument("--weirdness", type=float, help="怪诞度约束 0~1")
    p_cover.add_argument("--audio-weight", type=float, help="对上传音频的依赖权重 0~1")
    p_cover.add_argument("--callback", help="回调URL，可选")
    p_cover.add_argument("--download", action="store_true", help="完成后自动下载成品与封面")

    # NEW: 添加乐器
    p_add_inst = sub.add_parser("add-instrumental", help="为上传音频添加乐器伴奏")
    p_add_inst.add_argument("--upload-url", help="音频文件的公网URL（与 --file 二选一）")
    p_add_inst.add_argument("--file", help="本地音频文件路径（与 --upload-url 二选一）")
    p_add_inst.add_argument("--upload-path", default="audio/add_inst", help="远端保存路径（配合 --file 使用）")
    p_add_inst.add_argument("--name", default="add_inst_input.mp3", help="远端文件名（配合 --file 使用）")
    p_add_inst.add_argument("--title", required=True, help="生成曲目的标题")
    p_add_inst.add_argument("--tags", required=True, help="风格标签，逗号分隔")
    p_add_inst.add_argument("--neg", dest="negativeTags", required=True, help="负面标签，逗号分隔")
    p_add_inst.add_argument("--model", help="模型，例：V4_5PLUS/V5（可选）")
    p_add_inst.add_argument("--vocal-gender", choices=["m","f","n"], help="可选：人声性别（如有）")
    p_add_inst.add_argument("--style-weight", type=float, help="风格权重 0~1")
    p_add_inst.add_argument("--weirdness", type=float, help="怪诞度约束 0~1")
    p_add_inst.add_argument("--audio-weight", type=float, help="对上传音频的依赖权重 0~1")
    p_add_inst.add_argument("--callback", help="回调URL，可选")
    p_add_inst.add_argument("--download", action="store_true", help="完成后自动下载成品与封面")

    # NEW: 添加人声
    p_add_voc = sub.add_parser("add-vocals", help="为上传器乐添加人声")
    p_add_voc.add_argument("--upload-url", help="音频文件的公网URL（与 --file 二选一）")
    p_add_voc.add_argument("--file", help="本地音频文件路径（与 --upload-url 二选一）")
    p_add_voc.add_argument("--upload-path", default="audio/add_vocals", help="远端保存路径（配合 --file 使用）")
    p_add_voc.add_argument("--name", default="add_vocals_input.mp3", help="远端文件名（配合 --file 使用）")
    p_add_voc.add_argument("--prompt", required=True, help="人声内容/风格提示")
    p_add_voc.add_argument("--title", required=True, help="生成曲目的标题")
    p_add_voc.add_argument("--style", required=True, help="音乐/人声风格")
    p_add_voc.add_argument("--neg", dest="negativeTags", required=True, help="负面标签，逗号分隔")
    p_add_voc.add_argument("--model", help="模型，例：V4_5PLUS/V5（可选）")
    p_add_voc.add_argument("--vocal-gender", choices=["m","f","n"], help="人声性别（可选）")
    p_add_voc.add_argument("--style-weight", type=float, help="风格权重 0~1")
    p_add_voc.add_argument("--weirdness", type=float, help="怪诞度约束 0~1")
    p_add_voc.add_argument("--audio-weight", type=float, help="对上传音频的依赖权重 0~1")
    p_add_voc.add_argument("--callback", help="回调URL，可选")
    p_add_voc.add_argument("--download", action="store_true", help="完成后自动下载成品与封面")

    # NEW: 时间戳歌词（同步）
    p_ts = sub.add_parser("ts-lyrics", help="获取带时间戳的歌词（同步返回）")
    p_ts.add_argument("--task-id", required=True, help="生成音乐的taskId")
    p_ts.add_argument("--audio-id", required=True, help="audioId")

    # NEW: 风格增强（同步）
    p_style = sub.add_parser("style-gen", help="风格增强（V4_5+ 特性，立即返回结果）")
    p_style.add_argument("--content", required=True, help="风格内容，如 'Pop, Mysterious'")

    # NEW: 生成封面（异步，轮询封面详情）
    p_cov = sub.add_parser("cover-art", help="为已生成音乐创建封面（异步）")
    p_cov.add_argument("--task-id", required=True, help="音乐任务ID（父任务）")
    p_cov.add_argument("--callback", help="回调URL，可选")
    p_cov.add_argument("--download", action="store_true", help="自动下载生成的封面图片")

    # NEW: 查询封面详情（异步结果查询）
    p_cov_q = sub.add_parser("cover-info", help="查询封面生成详情")
    p_cov_q.add_argument("--task-id", required=True, help="封面生成任务ID")

    # NEW: 替换音乐分区（局部重写）
    p_repl = sub.add_parser("replace-section", help="替换音乐分区（局部重写）")
    p_repl.add_argument("--task-id", required=True, help="父任务ID（原音乐的 taskId）")
    p_repl.add_argument("--audio-id", required=True, help="audioId（原音乐的音频ID）")
    p_repl.add_argument("--prompt", required=True, help="替换片段的提示/歌词")
    p_repl.add_argument("--tags", required=True, help="风格标签，逗号分隔")
    p_repl.add_argument("--title", required=True, help="新标题")
    p_repl.add_argument("--neg", dest="negativeTags", required=True, help="负面标签，逗号分隔")
    p_repl.add_argument("--start", type=float, required=True, help="替换起点（秒）")
    p_repl.add_argument("--end", type=float, required=True, help="替换终点（秒）")
    p_repl.add_argument("--model", help="模型（可选）")
    p_repl.add_argument("--callback", help="回调URL，可选")
    p_repl.add_argument("--download", action="store_true", help="完成后下载成品与封面")

    # NEW: 生成 Persona（同步）
    p_persona = sub.add_parser("persona", help="基于现有音乐生成 Persona（同步返回 personaId）")
    p_persona.add_argument("--task-id", required=True)
    p_persona.add_argument("--audio-id", required=True)
    p_persona.add_argument("--name", required=True, help="Persona 名称")
    p_persona.add_argument("--desc", required=True, help="Persona 描述")

    args = parser.parse_args()
    cli = SunoClient(api_key=args.api_key, poll_interval=args.poll_interval, timeout=args.timeout)

    try:
        if args.cmd == "credits":
            print(cli.get_credits(), "credits")

        elif args.cmd == "lyrics":
            tid = cli.create_lyrics(args.prompt, args.callback)
            info = cli._wait_until(cli.get_lyrics_info, tid)
            print(json.dumps(info, ensure_ascii=False, indent=2))

        elif args.cmd == "gen":
            if args.custom and (not args.style or not args.title):
                raise SystemExit("自定义模式需要 --style 与 --title")
            tid = cli.generate_music(
                prompt=args.prompt, customMode=args.custom, instrumental=args.instrumental,
                model=args.model, style=args.style, title=args.title, callback=args.callback
            )
            info = cli._wait_until(cli.get_music_info, tid)
            print(json.dumps(info, ensure_ascii=False, indent=2))
            if args.download:
                suno_data = _norm(_norm(info, "response"), "sunoData") or _norm(info, "data")
                if suno_data:
                    tr = suno_data[0]
                    title = _norm(tr, "title") or "song"
                    audio_url = _norm(tr, "audioUrl", "audio_url")
                    image_url = _norm(tr, "imageUrl", "image_url")
                    if audio_url:
                        cli._download(audio_url, f"{title}.mp3")
                    if image_url:
                        cli._download(image_url, f"{title}.jpg")

        elif args.cmd == "query-music":
            info = cli.get_music_info(args.task_id)
            print(json.dumps(info, ensure_ascii=False, indent=2))

        elif args.cmd == "extend":
            tid = cli.extend_music(
                audio_id=args.audio_id, model=args.model,
                defaultParamFlag=args.default_param,
                continueAt=args.continue_at, title=args.title, style=args.style, prompt=args.prompt,
                callback=args.callback
            )
            info = cli._wait_until(cli.get_music_info, tid)
            print(json.dumps(info, ensure_ascii=False, indent=2))

        elif args.cmd == "upload-extend":
            upload_url = args.upload_url
            if not upload_url:
                if not args.file:
                    raise SystemExit("需要 --upload-url 或 --file 二选一")
                up = cli.upload_stream(args.file, args.upload_path, args.name)
                upload_url = _norm(_norm(up, "data") or {}, "downloadUrl")
                if not upload_url:
                    raise RuntimeError("文件上传失败：未获得 downloadUrl")

            tid = cli.upload_and_extend(
                uploadUrl=upload_url, model=args.model, defaultParamFlag=args.default_param,
                instrumental=args.instrumental, prompt=args.prompt, style=args.style, title=args.title,
                continueAt=args.continue_at, callback=args.callback
            )
            info = cli._wait_until(cli.get_music_info, tid)
            print(json.dumps(info, ensure_ascii=False, indent=2))
            if args.download:
                suno_data = _norm(_norm(info, "response"), "sunoData") or _norm(info, "data")
                if suno_data:
                    tr = suno_data[0]
                    title = _norm(tr, "title") or "extended_song"
                    audio_url = _norm(tr, "audioUrl", "audio_url")
                    image_url = _norm(tr, "imageUrl", "image_url")
                    if audio_url:
                        cli._download(audio_url, f"{title}.mp3")
                    if image_url:
                        cli._download(image_url, f"{title}.jpg")

        elif args.cmd == "separate":
            tid = cli.separate_vocals(args.task_id, args.audio_id, sep_type=args.type)
            info = cli._wait_until(cli.get_vocal_info, tid)
            print(json.dumps(info, ensure_ascii=False, indent=2))
            if args.download:
                resp = _norm(info, "response") or info
                for k in ("instrumentalUrl", "instrumental_url", "vocalUrl", "vocal_url"):
                    url = _norm(resp, k)
                    if url:
                        cli._download(url)

        elif args.cmd == "wav":
            tid = cli.convert_wav(args.task_id, args.audio_id)
            info = cli._wait_until(cli.get_wav_info, tid)
            print(json.dumps(info, ensure_ascii=False, indent=2))
            wav_resp = _norm(info, "response") or {}
            wav_url = _norm(wav_resp, "wavUrl", "url")
            if args.download and wav_url:
                cli._download(wav_url, "song.wav")

        elif args.cmd == "mp4":
            tid = cli.create_music_video(args.task_id, args.audio_id, author=args.author, domainName=args.domain)
            info = cli._wait_until(cli.get_mp4_info, tid)
            print(json.dumps(info, ensure_ascii=False, indent=2))
            mp4_resp = _norm(info, "response") or {}
            mp4_url = _norm(mp4_resp, "videoUrl", "url")
            if args.download and mp4_url:
                cli._download(mp4_url, "song.mp4")

        elif args.cmd == "upload-b64":
            p = pathlib.Path(args.file)
            b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
            print(json.dumps(cli.upload_base64(b64, args.path, args.name), ensure_ascii=False, indent=2))

        elif args.cmd == "upload-stream":
            print(json.dumps(cli.upload_stream(args.file, args.path, args.name), ensure_ascii=False, indent=2))

        elif args.cmd == "upload-url":
            print(json.dumps(cli.upload_from_url(args.url, args.path, args.name), ensure_ascii=False, indent=2))

        elif args.cmd == "cover":
            upload_url = args.upload_url
            if not upload_url:
                if not args.file:
                    raise SystemExit("需要 --upload-url 或 --file 二选一")
                up = cli.upload_stream(args.file, args.upload_path, args.name)
                upload_url = _norm(_norm(up, "data") or {}, "downloadUrl")
                if not upload_url:
                    raise RuntimeError("文件上传失败：未获得 downloadUrl")

            tid = cli.upload_cover(
                uploadUrl=upload_url,
                customMode=args.custom,
                instrumental=args.instrumental,
                model=args.model,
                prompt=args.prompt,
                style=args.style,
                title=args.title,
                negativeTags=args.negativeTags,
                vocalGender=args.vocal_gender,
                styleWeight=args.style_weight,
                weirdnessConstraint=args.weirdness,
                audioWeight=args.audio_weight,
                callback=args.callback,
            )
            info = cli._wait_until(cli.get_music_info, tid)
            print(json.dumps(info, ensure_ascii=False, indent=2))
            if args.download:
                suno_data = _norm(_norm(info, "response"), "sunoData") or _norm(info, "data")
                if suno_data:
                    tr = suno_data[0]
                    title = _norm(tr, "title") or "cover_song"
                    audio_url = _norm(tr, "audioUrl", "audio_url")
                    image_url = _norm(tr, "imageUrl", "image_url")
                    if audio_url:
                        cli._download(audio_url, f"{title}.mp3")
                    if image_url:
                        cli._download(image_url, f"{title}.jpg")

        elif args.cmd == "add-instrumental":
            upload_url = args.upload_url
            if not upload_url:
                if not args.file:
                    raise SystemExit("需要 --upload-url 或 --file 二选一")
                up = cli.upload_stream(args.file, args.upload_path, args.name)
                upload_url = _norm(_norm(up, "data") or {}, "downloadUrl")
                if not upload_url:
                    raise RuntimeError("文件上传失败：未获得 downloadUrl")
            tid = cli.add_instrumental(
                uploadUrl=upload_url, title=args.title, tags=args.tags, negativeTags=args.negativeTags,
                model=args.model, vocalGender=args.vocal_gender, styleWeight=args.style_weight,
                weirdnessConstraint=args.weirdness, audioWeight=args.audio_weight, callback=args.callback
            )
            info = cli._wait_until(cli.get_music_info, tid)
            print(json.dumps(info, ensure_ascii=False, indent=2))
            if args.download:
                suno_data = _norm(_norm(info, "response"), "sunoData") or _norm(info, "data")
                if suno_data:
                    tr = suno_data[0]
                    title = _norm(tr, "title") or "instrumental_song"
                    audio_url = _norm(tr, "audioUrl", "audio_url")
                    image_url = _norm(tr, "imageUrl", "image_url")
                    if audio_url:
                        cli._download(audio_url, f"{title}.mp3")
                    if image_url:
                        cli._download(image_url, f"{title}.jpg")

        elif args.cmd == "add-vocals":
            upload_url = args.upload_url
            if not upload_url:
                if not args.file:
                    raise SystemExit("需要 --upload-url 或 --file 二选一")
                up = cli.upload_stream(args.file, args.upload_path, args.name)
                upload_url = _norm(_norm(up, "data") or {}, "downloadUrl")
                if not upload_url:
                    raise RuntimeError("文件上传失败：未获得 downloadUrl")
            tid = cli.add_vocals(
                uploadUrl=upload_url, prompt=args.prompt, title=args.title, style=args.style,
                negativeTags=args.negativeTags, model=args.model, vocalGender=args.vocal_gender,
                styleWeight=args.style_weight, weirdnessConstraint=args.weirdness, audioWeight=args.audio_weight,
                callback=args.callback
            )
            info = cli._wait_until(cli.get_music_info, tid)
            print(json.dumps(info, ensure_ascii=False, indent=2))
            if args.download:
                suno_data = _norm(_norm(info, "response"), "sunoData") or _norm(info, "data")
                if suno_data:
                    tr = suno_data[0]
                    title = _norm(tr, "title") or "vocals_song"
                    audio_url = _norm(tr, "audioUrl", "audio_url")
                    image_url = _norm(tr, "imageUrl", "image_url")
                    if audio_url:
                        cli._download(audio_url, f"{title}.mp3")
                    if image_url:
                        cli._download(image_url, f"{title}.jpg")

        elif args.cmd == "ts-lyrics":
            data = cli.get_timestamped_lyrics(args.task_id, args.audio_id)
            print(json.dumps(data, ensure_ascii=False, indent=2))

        elif args.cmd == "style-gen":
            data = cli.style_generate(args.content)
            print(json.dumps(data, ensure_ascii=False, indent=2))

        elif args.cmd == "cover-art":
            child_tid = cli.create_cover(args.task_id, callback=args.callback)
            info = cli._wait_until(cli.get_cover_info, child_tid)
            print(json.dumps(info, ensure_ascii=False, indent=2))
            if args.download:
                resp = _norm(info, "response") or {}
                images: List[str] = resp.get("images") or []
                for i, url in enumerate(images, 1):
                    cli._download(url, f"cover_{i}.png")

        elif args.cmd == "cover-info":
            info = cli.get_cover_info(args.task_id)
            print(json.dumps(info, ensure_ascii=False, indent=2))

        elif args.cmd == "replace-section":
            tid = cli.replace_section(
                taskId=args.task_id, audioId=args.audio_id, prompt=args.prompt, tags=args.tags,
                title=args.title, negativeTags=args.negativeTags, infillStartS=args.start,
                infillEndS=args.end, model=args.model, callback=args.callback
            )
            info = cli._wait_until(cli.get_music_info, tid)
            print(json.dumps(info, ensure_ascii=False, indent=2))
            if args.download:
                suno_data = _norm(_norm(info, "response"), "sunoData") or _norm(info, "data")
                if suno_data:
                    tr = suno_data[0]
                    title = _norm(tr, "title") or "replaced_song"
                    audio_url = _norm(tr, "audioUrl", "audio_url")
                    image_url = _norm(tr, "imageUrl", "image_url")
                    if audio_url:
                        cli._download(audio_url, f"{title}.mp3")
                    if image_url:
                        cli._download(image_url, f"{title}.jpg")

        elif args.cmd == "persona":
            data = cli.generate_persona(args.task_id, args.audio_id, name=args.name, description=args.desc)
            print(json.dumps(data, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"[错误] {e}")


if __name__ == "__main__":
    run_cli()
