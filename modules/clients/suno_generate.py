"""
Suno音乐生成模块

提供AI音乐生成功能，支持两种模式：
- 自定义模式：完全控制歌词、风格、标题
- 简单模式：只需提示词，AI自动生成歌词

功能特点：
- 支持多种模型版本（V3_5, V4, V4_5, V4_5PLUS, V5）
- 支持纯音乐和带歌词两种模式
- 丰富的参数控制（风格、性别、权重等）
- 自动任务状态查询

使用示例：
    from modules.clients import suno_generate

    # 简单模式 - 快速生成
    task_id = suno_generate.quick_generate(
        prompt="一首轻快的夏日流行歌",
        wait=True  # 等待完成
    )

    # 自定义模式 - 完全控制
    task_id = suno_generate.custom_generate(
        lyrics="春天来了，花儿开了...",
        style="清新流行",
        title="春之歌"
    )

    # 纯音乐
    task_id = suno_generate.instrumental_generate(
        style="古典钢琴",
        title="夜的钢琴曲"
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

    return api_key, api_base


def _post_request(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """发送POST请求"""
    api_key, api_base = _get_client_config()

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
    api_key, api_base = _get_client_config()

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


def generate_music(
    prompt: str,
    *,
    custom_mode: bool = False,
    instrumental: bool = False,
    model: Literal["V3_5", "V4", "V4_5", "V4_5PLUS", "V5"] = "V5",
    title: Optional[str] = None,
    style: Optional[str] = None,
    persona_id: Optional[str] = None,
    negative_tags: Optional[str] = None,
    vocal_gender: Optional[Literal["m", "f"]] = None,
    style_weight: Optional[float] = None,
    weirdness_constraint: Optional[float] = None,
    audio_weight: Optional[float] = None,
    callback_url: Optional[str] = None
) -> str:
    """
    生成音乐（底层函数）

    Args:
        prompt: 提示词或歌词
            - custom_mode=False: 作为创作提示（最多500字符）
            - custom_mode=True 且 instrumental=False: 作为歌词（V3_5/V4最多3000字符，V4_5/V4_5PLUS/V5最多5000字符）
        custom_mode: 是否使用自定义模式
        instrumental: 是否生成纯音乐
        model: 模型版本
            - V5: 最新版本，音乐表现力更强，生成更快
            - V4_5PLUS: 音色丰富，最长8分钟
            - V4_5: 智能提示词，生成快，最长8分钟
            - V4: 改进人声质量，最长4分钟
            - V3_5: 更好歌曲结构，最长4分钟
        title: 歌曲标题（custom_mode=True时必需，最多80字符）
        style: 音乐风格（custom_mode=True时必需，V3_5/V4最多200字符，V4_5/V4_5PLUS/V5最多1000字符）
        persona_id: 人格ID（可选，需先通过Generate Persona接口生成）
        negative_tags: 排除的风格特征（可选）
        vocal_gender: 人声性别（"m"男/"f"女，可选）
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
        >>> # 简单模式
        >>> task_id = generate_music(
        ...     prompt="一首轻快的流行歌",
        ...     custom_mode=False
        ... )
        >>>
        >>> # 自定义模式（带歌词）
        >>> task_id = generate_music(
        ...     prompt="春天来了，花儿开了...",
        ...     custom_mode=True,
        ...     instrumental=False,
        ...     title="春之歌",
        ...     style="清新流行"
        ... )
        >>>
        >>> # 纯音乐
        >>> task_id = generate_music(
        ...     prompt="",
        ...     custom_mode=True,
        ...     instrumental=True,
        ...     title="夜的钢琴曲",
        ...     style="古典钢琴"
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
        "customMode": custom_mode,
        "instrumental": instrumental,
        "model": model,
        "callBackUrl": callback_url or "https://example.invalid/music"
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
    result = _post_request("/generate", payload)

    if result.get("code") != 200:
        raise RuntimeError(result.get("msg", "生成音乐失败"))

    return result["data"]["taskId"]


def quick_generate(
    prompt: str,
    model: Literal["V3_5", "V4", "V4_5", "V4_5PLUS", "V5"] = "V5",
    wait: bool = False,
    max_wait_time: int = 300
) -> str:
    """
    快速生成音乐（简单模式）

    适合快速创作，只需提供创作提示，AI自动生成歌词和音乐。

    Args:
        prompt: 创作提示（描述想要的音乐，最多500字符）
            示例："一首轻快的夏日流行歌"、"带有萨克斯的爵士乐"
        model: 模型版本（默认V5）
        wait: 是否等待生成完成（默认False）
        max_wait_time: 最大等待时间（秒，默认300）

    Returns:
        任务ID

    示例:
        >>> task_id = quick_generate("一首轻快的夏日流行歌")
        >>> print(f"任务ID: {task_id}")
        >>>
        >>> # 等待完成
        >>> task_id = quick_generate(
        ...     "一首安静的钢琴曲",
        ...     wait=True
        ... )
    """
    task_id = generate_music(
        prompt=prompt,
        custom_mode=False,
        instrumental=False,
        model=model
    )

    if wait:
        print(f"正在生成音乐... (任务ID: {task_id})")
        wait_for_completion(task_id, max_wait_time)

    return task_id


def custom_generate(
    lyrics: str,
    style: str,
    title: str,
    model: Literal["V3_5", "V4", "V4_5", "V4_5PLUS", "V5"] = "V5",
    persona_id: Optional[str] = None,
    vocal_gender: Optional[Literal["m", "f"]] = None,
    wait: bool = False,
    max_wait_time: int = 300
) -> str:
    """
    自定义生成音乐（带歌词）

    完全控制歌词、风格和标题，适合精确创作。

    Args:
        lyrics: 歌词内容
            - V3_5/V4: 最多3000字符
            - V4_5/V4_5PLUS/V5: 最多5000字符
        style: 音乐风格
            - V3_5/V4: 最多200字符
            - V4_5/V4_5PLUS/V5: 最多1000字符
            示例："清新流行"、"摇滚"、"古典钢琴"
        title: 歌曲标题（最多80字符）
        model: 模型版本
        persona_id: 人格ID（可选）
        vocal_gender: 人声性别（"m"/"f"，可选）
        wait: 是否等待完成
        max_wait_time: 最大等待时间（秒）

    Returns:
        任务ID

    示例:
        >>> lyrics = '''
        ... [Verse 1]
        ... 春天来了，花儿开了
        ... 阳光洒满大地
        ... [Chorus]
        ... 春之歌，春之歌
        ... 唱响希望的旋律
        ... '''
        >>> task_id = custom_generate(
        ...     lyrics=lyrics,
        ...     style="清新流行",
        ...     title="春之歌"
        ... )
    """
    task_id = generate_music(
        prompt=lyrics,
        custom_mode=True,
        instrumental=False,
        model=model,
        title=title,
        style=style,
        persona_id=persona_id,
        vocal_gender=vocal_gender
    )

    if wait:
        print(f"正在生成音乐... (任务ID: {task_id})")
        wait_for_completion(task_id, max_wait_time)

    return task_id


def instrumental_generate(
    style: str,
    title: str,
    model: Literal["V3_5", "V4", "V4_5", "V4_5PLUS", "V5"] = "V5",
    persona_id: Optional[str] = None,
    wait: bool = False,
    max_wait_time: int = 300
) -> str:
    """
    生成纯音乐（无歌词）

    Args:
        style: 音乐风格（如："古典钢琴"、"爵士"、"电子音乐"）
        title: 曲目标题
        model: 模型版本
        persona_id: 人格ID（可选）
        wait: 是否等待完成
        max_wait_time: 最大等待时间（秒）

    Returns:
        任务ID

    示例:
        >>> task_id = instrumental_generate(
        ...     style="古典钢琴",
        ...     title="夜的钢琴曲第五号"
        ... )
    """
    task_id = generate_music(
        prompt="",
        custom_mode=True,
        instrumental=True,
        model=model,
        title=title,
        style=style,
        persona_id=persona_id
    )

    if wait:
        print(f"正在生成纯音乐... (任务ID: {task_id})")
        wait_for_completion(task_id, max_wait_time)

    return task_id


def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    查询音乐生成任务状态

    Args:
        task_id: 任务ID

    Returns:
        任务信息字典，包含：
        - taskId: 任务ID
        - status: 状态（processing/completed/failed）
        - data: 音乐数据（完成时包含音频URL等信息）

    示例:
        >>> status = get_task_status(task_id)
        >>> if status.get('status') == 'completed':
        ...     print(f"音频URL: {status['data'][0]['audioUrl']}")
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
    等待音乐生成完成

    Args:
        task_id: 任务ID
        max_wait_time: 最大等待时间（秒，默认300）
        check_interval: 检查间隔（秒，默认10）

    Returns:
        完成的任务信息

    Raises:
        TimeoutError: 等待超时
        RuntimeError: 生成失败

    示例:
        >>> task_id = quick_generate("一首流行歌")
        >>> result = wait_for_completion(task_id)
        >>> print(f"音频URL: {result['data'][0]['audioUrl']}")
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
            print("\n✓ 生成完成！")
            return status_info

        elif status == "failed":
            print(f"\n✗ 生成失败")
            raise RuntimeError("音乐生成失败")

        time.sleep(check_interval)


# 预设风格模板
STYLE_PRESETS = {
    "流行": "Pop",
    "摇滚": "Rock",
    "民谣": "Folk",
    "爵士": "Jazz",
    "古典": "Classical",
    "电子": "Electronic",
    "嘻哈": "Hip Hop",
    "蓝调": "Blues",
    "乡村": "Country",
    "雷鬼": "Reggae",
    "金属": "Metal",
    "朋克": "Punk",
    "灵魂": "Soul",
    "放克": "Funk"
}


if __name__ == "__main__":
    # 测试代码
    print("=== Suno 音乐生成模块测试 ===\n")

    try:
        # 测试1：快速生成
        print("测试1：快速生成")
        task_id = quick_generate(
            prompt="一首轻快的夏日流行歌",
            model="V5"
        )
        print(f"✓ 任务提交成功")
        print(f"  任务ID: {task_id}")

        # 测试2：查询状态
        print("\n测试2：查询状态")
        status = get_task_status(task_id)
        print(f"✓ 状态: {status.get('status')}")

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        print("请确保已设置 SUNO_API_KEY 环境变量")
