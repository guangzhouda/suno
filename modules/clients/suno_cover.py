"""
Suno翻唱音乐模块

提供音乐翻唱功能，可以将现有音频转换为新的风格，同时保持原旋律。

功能特点：
- 上传本地音频文件或从URL上传
- 保持原旋律，改变音乐风格
- 支持添加新歌词或保持纯音乐
- 自动处理文件上传流程

使用示例：
    from modules.clients import suno_cover

    # 从本地文件翻唱
    task_id = suno_cover.cover_from_file(
        file_path="original.mp3",
        style="摇滚",
        title="Rock Version"
    )

    # 从URL翻唱
    task_id = suno_cover.cover_from_url(
        file_url="https://example.com/music.mp3",
        style="爵士",
        title="Jazz Cover"
    )

    # 添加歌词翻唱
    task_id = suno_cover.cover_with_lyrics(
        file_path="original.mp3",
        lyrics="新的歌词内容...",
        style="流行",
        title="新版本"
    )
"""

import os
import json
import time
import pathlib
from typing import Optional, Dict, Any, Literal
import requests


def _get_client_config() -> tuple:
    """获取API配置"""
    api_key = None
    api_base = "https://api.sunoapi.org/api/v1"
    upload_base = "https://sunoapiorg.redpandaai.co/api"

    # 尝试从 config.json 读取
    config_file = pathlib.Path("config.json")
    if config_file.exists():
        try:
            with open(config_file, encoding="utf-8") as f:
                config = json.load(f)
                suno_config = config.get("suno", {})
                api_key = suno_config.get("api_key")
        except Exception:
            pass

    # 从环境变量读取
    if not api_key:
        api_key = os.getenv("SUNO_API_KEY")

    if not api_key:
        raise RuntimeError(
            "缺少 Suno API Key！请在 config.json 中配置 suno.api_key "
            "或设置环境变量 SUNO_API_KEY"
        )

    return api_key, api_base, upload_base


def _post_request(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """发送POST请求"""
    api_key, api_base, _ = _get_client_config()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    url = f"{api_base}{endpoint}"

    for _ in range(3):  # 重试3次
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code >= 500:
                time.sleep(1)
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            if _ == 2:
                raise
            time.sleep(1)

    return {}


def _get_request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """发送GET请求"""
    api_key, api_base, _ = _get_client_config()

    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"{api_base}{endpoint}"

    for _ in range(3):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=60)
            if response.status_code >= 500:
                time.sleep(1)
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            if _ == 2:
                raise
            time.sleep(1)

    return {}


def upload_file(file_path: str, file_name: Optional[str] = None) -> str:
    """
    上传本地音频文件

    Args:
        file_path: 本地文件路径
        file_name: 文件名（可选，默认使用原文件名）

    Returns:
        上传后的文件URL

    Raises:
        FileNotFoundError: 文件不存在
        RuntimeError: 上传失败

    注意：
        - 音频文件不得超过2分钟
        - 支持常见音频格式：mp3, wav, flac, m4a等

    示例:
        >>> upload_url = upload_file("my_music.mp3")
        >>> print(f"上传URL: {upload_url}")
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    api_key, _, upload_base = _get_client_config()

    if not file_name:
        file_name = pathlib.Path(file_path).name

    with open(file_path, "rb") as f:
        files = {"file": (file_name, f)}
        data = {"uploadPath": "music", "fileName": file_name}
        headers = {"Authorization": f"Bearer {api_key}"}

        response = requests.post(
            f"{upload_base}/file-stream-upload",
            headers=headers,
            files=files,
            data=data,
            timeout=300
        )

    response.raise_for_status()
    result = response.json()

    if result.get("code") != 200:
        raise RuntimeError(result.get("msg", "上传文件失败"))

    return result["data"]["url"]


def upload_from_url(file_url: str, file_name: Optional[str] = None) -> str:
    """
    从URL上传音频文件

    Args:
        file_url: 音频文件URL
        file_name: 文件名（可选）

    Returns:
        上传后的文件URL

    Raises:
        RuntimeError: 上传失败

    示例:
        >>> upload_url = upload_from_url(
        ...     "https://example.com/music.mp3"
        ... )
    """
    api_key, _, upload_base = _get_client_config()

    if not file_name:
        file_name = pathlib.Path(file_url).name

    payload = {
        "fileUrl": file_url,
        "uploadPath": "music",
        "fileName": file_name
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{upload_base}/file-url-upload",
        headers=headers,
        json=payload,
        timeout=120
    )

    response.raise_for_status()
    result = response.json()

    if result.get("code") != 200:
        raise RuntimeError(result.get("msg", "从URL上传失败"))

    return result["data"]["url"]


def cover_music(
    upload_url: str,
    *,
    custom_mode: bool = True,
    instrumental: bool = True,
    model: Literal["V3_5", "V4", "V4_5", "V4_5PLUS", "V5"] = "V5",
    style: Optional[str] = None,
    title: Optional[str] = None,
    prompt: Optional[str] = None,
    persona_id: Optional[str] = None,
    negative_tags: Optional[str] = None,
    vocal_gender: Optional[Literal["m", "f"]] = None,
    style_weight: Optional[float] = None,
    weirdness_constraint: Optional[float] = None,
    audio_weight: Optional[float] = None,
    callback_url: Optional[str] = None
) -> str:
    """
    翻唱音乐（底层函数）

    将上传的音频转换为新的风格，保持原旋律。

    Args:
        upload_url: 上传后的音频URL（必需）
        custom_mode: 是否使用自定义模式
        instrumental: 是否生成纯音乐
        model: 模型版本
        style: 目标风格（custom_mode=True时必需）
        title: 新标题（custom_mode=True时必需）
        prompt: 歌词或创作提示
            - custom_mode=True 且 instrumental=False: 作为歌词（必需）
            - custom_mode=False: 作为创作提示（必需）
        persona_id: 人格ID（可选）
        negative_tags: 排除的风格（可选）
        vocal_gender: 人声性别（可选）
        style_weight: 风格权重（0-1，可选）
        weirdness_constraint: 创意约束（0-1，可选）
        audio_weight: 音频影响力（0-1，可选）
        callback_url: 回调URL（可选）

    Returns:
        任务ID

    Raises:
        ValueError: 参数错误
        RuntimeError: API调用失败

    示例:
        >>> # 纯音乐翻唱
        >>> task_id = cover_music(
        ...     upload_url="https://...",
        ...     custom_mode=True,
        ...     instrumental=True,
        ...     style="爵士",
        ...     title="Jazz Version"
        ... )
        >>>
        >>> # 添加歌词翻唱
        >>> task_id = cover_music(
        ...     upload_url="https://...",
        ...     custom_mode=True,
        ...     instrumental=False,
        ...     style="流行",
        ...     title="Pop Cover",
        ...     prompt="新的歌词内容..."
        ... )
    """
    # 参数验证
    if custom_mode:
        if not style or not title:
            raise ValueError("custom_mode=True 时必须提供 style 和 title")
        if not instrumental and not prompt:
            raise ValueError("custom_mode=True 且 instrumental=False 时必须提供 prompt（歌词）")
    else:
        if not prompt:
            raise ValueError("custom_mode=False 时必须提供 prompt（创作提示）")

    # 构建请求
    payload: Dict[str, Any] = {
        "uploadUrl": upload_url,
        "customMode": custom_mode,
        "instrumental": instrumental,
        "model": model,
        "callBackUrl": callback_url or "https://example.invalid/cover"
    }

    if custom_mode:
        payload.update({"style": style, "title": title})
        if not instrumental:
            payload["prompt"] = prompt
    else:
        payload["prompt"] = prompt

    # 添加可选参数
    if persona_id:
        payload["personaId"] = persona_id
    if negative_tags:
        payload["negativeTags"] = negative_tags
    if vocal_gender:
        payload["vocalGender"] = vocal_gender
    if style_weight is not None:
        payload["styleWeight"] = float(style_weight)
    if weirdness_constraint is not None:
        payload["weirdnessConstraint"] = float(weirdness_constraint)
    if audio_weight is not None:
        payload["audioWeight"] = float(audio_weight)

    # 发送请求
    result = _post_request("/generate/upload-cover", payload)

    if result.get("code") != 200:
        raise RuntimeError(result.get("msg", "翻唱音乐失败"))

    return result["data"]["taskId"]


def cover_from_file(
    file_path: str,
    style: str,
    title: str,
    model: Literal["V3_5", "V4", "V4_5", "V4_5PLUS", "V5"] = "V5",
    wait: bool = False,
    max_wait_time: int = 300
) -> str:
    """
    从本地文件翻唱（纯音乐）

    适合快速翻唱本地音频文件为不同风格。

    Args:
        file_path: 本地音频文件路径
        style: 目标风格（如："爵士"、"摇滚"、"古典"）
        title: 新标题
        model: 模型版本
        wait: 是否等待完成
        max_wait_time: 最大等待时间（秒）

    Returns:
        任务ID

    注意：
        - 文件不得超过2分钟
        - 会保持原旋律，只改变风格

    示例:
        >>> task_id = cover_from_file(
        ...     file_path="original.mp3",
        ...     style="摇滚",
        ...     title="Rock Version"
        ... )
    """
    # 1. 上传文件
    print(f"正在上传文件: {file_path}...")
    upload_url = upload_file(file_path)
    print(f"✓ 文件上传成功")

    # 2. 提交翻唱任务
    print(f"正在提交翻唱任务...")
    task_id = cover_music(
        upload_url=upload_url,
        custom_mode=True,
        instrumental=True,
        model=model,
        style=style,
        title=title
    )
    print(f"✓ 任务提交成功: {task_id}")

    if wait:
        print(f"正在翻唱...")
        wait_for_completion(task_id, max_wait_time)

    return task_id


def cover_from_url(
    file_url: str,
    style: str,
    title: str,
    model: Literal["V3_5", "V4", "V4_5", "V4_5PLUS", "V5"] = "V5",
    wait: bool = False,
    max_wait_time: int = 300
) -> str:
    """
    从URL翻唱（纯音乐）

    适合翻唱网络上的音频文件。

    Args:
        file_url: 音频文件URL
        style: 目标风格
        title: 新标题
        model: 模型版本
        wait: 是否等待完成
        max_wait_time: 最大等待时间（秒）

    Returns:
        任务ID

    示例:
        >>> task_id = cover_from_url(
        ...     file_url="https://example.com/music.mp3",
        ...     style="爵士",
        ...     title="Jazz Cover"
        ... )
    """
    # 1. 从URL上传
    print(f"正在从URL上传: {file_url}...")
    upload_url = upload_from_url(file_url)
    print(f"✓ 文件上传成功")

    # 2. 提交翻唱任务
    print(f"正在提交翻唱任务...")
    task_id = cover_music(
        upload_url=upload_url,
        custom_mode=True,
        instrumental=True,
        model=model,
        style=style,
        title=title
    )
    print(f"✓ 任务提交成功: {task_id}")

    if wait:
        print(f"正在翻唱...")
        wait_for_completion(task_id, max_wait_time)

    return task_id


def cover_with_lyrics(
    file_path: str,
    lyrics: str,
    style: str,
    title: str,
    model: Literal["V3_5", "V4", "V4_5", "V4_5PLUS", "V5"] = "V5",
    vocal_gender: Optional[Literal["m", "f"]] = None,
    wait: bool = False,
    max_wait_time: int = 300
) -> str:
    """
    添加歌词翻唱

    将纯音乐或原歌曲翻唱为带有新歌词的版本。

    Args:
        file_path: 本地音频文件路径
        lyrics: 新歌词内容
            - V3_5/V4: 最多3000字符
            - V4_5/V4_5PLUS/V5: 最多5000字符
        style: 目标风格
        title: 新标题
        model: 模型版本
        vocal_gender: 人声性别（"m"/"f"，可选）
        wait: 是否等待完成
        max_wait_time: 最大等待时间（秒）

    Returns:
        任务ID

    示例:
        >>> lyrics = '''
        ... [Verse 1]
        ... 这是新的歌词
        ... 改编自原曲
        ... [Chorus]
        ... 全新的演绎
        ... '''
        >>> task_id = cover_with_lyrics(
        ...     file_path="original.mp3",
        ...     lyrics=lyrics,
        ...     style="流行",
        ...     title="新版本"
        ... )
    """
    # 1. 上传文件
    print(f"正在上传文件: {file_path}...")
    upload_url = upload_file(file_path)
    print(f"✓ 文件上传成功")

    # 2. 提交翻唱任务（带歌词）
    print(f"正在提交翻唱任务...")
    task_id = cover_music(
        upload_url=upload_url,
        custom_mode=True,
        instrumental=False,
        model=model,
        style=style,
        title=title,
        prompt=lyrics,
        vocal_gender=vocal_gender
    )
    print(f"✓ 任务提交成功: {task_id}")

    if wait:
        print(f"正在翻唱...")
        wait_for_completion(task_id, max_wait_time)

    return task_id


def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    查询翻唱任务状态

    Args:
        task_id: 任务ID

    Returns:
        任务信息字典

    示例:
        >>> status = get_task_status(task_id)
        >>> if status.get('status') == 'completed':
        ...     print("翻唱完成！")
    """
    result = _get_request("/generate/record-info", params={"taskId": task_id})

    if result.get("code") != 200:
        raise RuntimeError(result.get("msg", "查询任务状态失败"))

    return result["data"]


def wait_for_completion(
    task_id: str,
    max_wait_time: int = 300,
    check_interval: int = 10
) -> Dict[str, Any]:
    """
    等待翻唱完成

    Args:
        task_id: 任务ID
        max_wait_time: 最大等待时间（秒）
        check_interval: 检查间隔（秒）

    Returns:
        完成的任务信息

    Raises:
        TimeoutError: 等待超时
        RuntimeError: 翻唱失败
    """
    start_time = time.time()
    attempts = 0

    while True:
        attempts += 1
        elapsed = int(time.time() - start_time)

        if elapsed > max_wait_time:
            raise TimeoutError(f"等待超时（{max_wait_time}秒）")

        status_info = get_task_status(task_id)
        status = status_info.get("status", "unknown")

        print(f"\r[{attempts}] 状态: {status} | 已等待: {elapsed}秒", end='')

        if status == "completed":
            print("\n✓ 翻唱完成！")
            return status_info

        elif status == "failed":
            print(f"\n✗ 翻唱失败")
            raise RuntimeError("音乐翻唱失败")

        time.sleep(check_interval)


if __name__ == "__main__":
    # 测试代码
    print("=== Suno 翻唱音乐模块测试 ===\n")

    try:
        print("提示：需要提供实际的音频文件路径进行测试")
        print("\n使用示例:")
        print("""
        # 翻唱本地文件
        task_id = cover_from_file(
            file_path="my_music.mp3",
            style="爵士",
            title="Jazz Version"
        )

        # 从URL翻唱
        task_id = cover_from_url(
            file_url="https://example.com/music.mp3",
            style="摇滚",
            title="Rock Cover"
        )

        # 添加歌词翻唱
        task_id = cover_with_lyrics(
            file_path="my_music.mp3",
            lyrics="新的歌词内容...",
            style="流行",
            title="新版本"
        )
        """)

    except Exception as e:
        print(f"✗ 错误: {e}")
