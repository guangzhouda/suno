"""
Suno音乐扩展模块

提供音乐延长和续写功能，可以将现有音乐扩展到更长时间。

功能特点：
- 支持指定扩展位置（从某个时间点开始扩展）
- 支持使用原参数或自定义参数
- 保持音乐风格的连贯性
- 支持续写提示词指导扩展方向

使用示例：
    from modules.clients import suno_extend

    # 使用原参数扩展（最简单）
    task_id = suno_extend.simple_extend(
        audio_id="e231****-****-****-****-****8cadc7dc"
    )

    # 自定义扩展
    task_id = suno_extend.custom_extend(
        audio_id="e231****-****-****-****-****8cadc7dc",
        continue_at=60,  # 从60秒处开始扩展
        style="轻快流行",
        title="夏日回忆 (Extended)",
        prompt="继续轻快的旋律，增加更多欢快的节奏"
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


def extend_music(
    audio_id: str,
    *,
    use_custom_params: bool = False,
    model: Literal["V3_5", "V4", "V4_5", "V4_5PLUS", "V5"] = "V5",
    continue_at: Optional[int] = None,
    title: Optional[str] = None,
    style: Optional[str] = None,
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
    扩展音乐（底层函数）

    Args:
        audio_id: 原音频ID（从生成任务中获取）
        use_custom_params: 是否使用自定义参数
            - False: 使用原音频的参数（只需提供audio_id）
            - True: 使用自定义参数（需要提供continue_at/title/style）
        model: 模型版本（必须与原音频一致）
        continue_at: 扩展起始位置（秒数，use_custom_params=True时必需）
            - 必须大于0且小于原音频总时长
        title: 扩展后的标题（use_custom_params=True时必需）
        style: 音乐风格（use_custom_params=True时必需）
        prompt: 续写提示（可选，指导扩展方向）
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
        >>> # 使用原参数扩展
        >>> task_id = extend_music(
        ...     audio_id="e231****-****-****-****-****8cadc7dc",
        ...     use_custom_params=False
        ... )
        >>>
        >>> # 自定义扩展
        >>> task_id = extend_music(
        ...     audio_id="e231****-****-****-****-****8cadc7dc",
        ...     use_custom_params=True,
        ...     continue_at=60,
        ...     title="夏日回忆 (Extended)",
        ...     style="轻快流行",
        ...     prompt="继续轻快的旋律"
        ... )
    """
    # 参数验证
    if use_custom_params:
        if continue_at is None or not title or not style:
            raise ValueError(
                "use_custom_params=True 时必须提供 continue_at, title 和 style"
            )

    # 构建请求
    payload: Dict[str, Any] = {
        "audioId": audio_id,
        "defaultParamFlag": use_custom_params,
        "model": model,
        "callBackUrl": callback_url or "https://example.invalid/extend"
    }

    if use_custom_params:
        payload.update({
            "continueAt": continue_at,
            "title": title,
            "style": style
        })
        if prompt:
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
    result = _post_request("/generate/extend", payload)

    if result.get("code") != 200:
        raise RuntimeError(result.get("msg", "扩展音乐失败"))

    return result["data"]["taskId"]


def simple_extend(
    audio_id: str,
    model: Literal["V3_5", "V4", "V4_5", "V4_5PLUS", "V5"] = "V5",
    wait: bool = False,
    max_wait_time: int = 300
) -> str:
    """
    简单扩展（使用原参数）

    最简单的扩展方式，保持原音乐的所有参数和风格。

    Args:
        audio_id: 原音频ID
        model: 模型版本（必须与原音频一致）
        wait: 是否等待完成
        max_wait_time: 最大等待时间（秒）

    Returns:
        任务ID

    示例:
        >>> task_id = simple_extend(
        ...     audio_id="e231****-****-****-****-****8cadc7dc"
        ... )
        >>> print(f"扩展任务ID: {task_id}")
    """
    task_id = extend_music(
        audio_id=audio_id,
        use_custom_params=False,
        model=model
    )

    if wait:
        print(f"正在扩展音乐... (任务ID: {task_id})")
        wait_for_completion(task_id, max_wait_time)

    return task_id


def custom_extend(
    audio_id: str,
    continue_at: int,
    style: str,
    title: str,
    prompt: Optional[str] = None,
    model: Literal["V3_5", "V4", "V4_5", "V4_5PLUS", "V5"] = "V5",
    persona_id: Optional[str] = None,
    vocal_gender: Optional[Literal["m", "f"]] = None,
    wait: bool = False,
    max_wait_time: int = 300
) -> str:
    """
    自定义扩展

    完全控制扩展参数，可以指定扩展位置和方向。

    Args:
        audio_id: 原音频ID
        continue_at: 扩展起始位置（秒数）
            - 必须大于0且小于原音频总时长
            - 示例：如果原音频120秒，可以设为60表示从中间开始扩展
        style: 音乐风格（可以与原音频相同或不同）
        title: 扩展后的标题
        prompt: 续写提示（可选）
            - 描述如何扩展音乐
            - 示例："继续轻快的旋律，增加更多欢快的节奏"
        model: 模型版本（必须与原音频一致）
        persona_id: 人格ID（可选）
        vocal_gender: 人声性别（可选）
        wait: 是否等待完成
        max_wait_time: 最大等待时间（秒）

    Returns:
        任务ID

    示例:
        >>> task_id = custom_extend(
        ...     audio_id="e231****-****-****-****-****8cadc7dc",
        ...     continue_at=60,
        ...     style="轻快流行",
        ...     title="夏日回忆 (Extended)",
        ...     prompt="继续轻快的旋律，增加更多欢快的节奏"
        ... )
    """
    task_id = extend_music(
        audio_id=audio_id,
        use_custom_params=True,
        model=model,
        continue_at=continue_at,
        title=title,
        style=style,
        prompt=prompt,
        persona_id=persona_id,
        vocal_gender=vocal_gender
    )

    if wait:
        print(f"正在扩展音乐... (任务ID: {task_id})")
        wait_for_completion(task_id, max_wait_time)

    return task_id


def extend_to_length(
    audio_id: str,
    current_duration: int,
    target_duration: int,
    style: str,
    title: str,
    model: Literal["V3_5", "V4", "V4_5", "V4_5PLUS", "V5"] = "V5"
) -> str:
    """
    扩展到指定长度

    根据目标时长自动计算扩展位置。

    Args:
        audio_id: 原音频ID
        current_duration: 当前时长（秒）
        target_duration: 目标时长（秒）
        style: 音乐风格
        title: 扩展后的标题
        model: 模型版本

    Returns:
        任务ID

    示例:
        >>> # 将60秒的音乐扩展到120秒
        >>> task_id = extend_to_length(
        ...     audio_id="e231****-****-****-****-****8cadc7dc",
        ...     current_duration=60,
        ...     target_duration=120,
        ...     style="轻快流行",
        ...     title="夏日回忆 (Extended)"
        ... )
    """
    if target_duration <= current_duration:
        raise ValueError(f"目标时长（{target_duration}秒）必须大于当前时长（{current_duration}秒）")

    # 从当前时长处开始扩展
    continue_at = current_duration

    return custom_extend(
        audio_id=audio_id,
        continue_at=continue_at,
        style=style,
        title=title,
        model=model,
        prompt=f"Extend to {target_duration} seconds"
    )


def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    查询扩展任务状态

    Args:
        task_id: 任务ID

    Returns:
        任务信息字典

    示例:
        >>> status = get_task_status(task_id)
        >>> if status.get('status') == 'completed':
        ...     print("扩展完成！")
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
    等待扩展完成

    Args:
        task_id: 任务ID
        max_wait_time: 最大等待时间（秒）
        check_interval: 检查间隔（秒）

    Returns:
        完成的任务信息

    Raises:
        TimeoutError: 等待超时
        RuntimeError: 扩展失败
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
            print("\n✓ 扩展完成！")
            return status_info

        elif status == "failed":
            print(f"\n✗ 扩展失败")
            raise RuntimeError("音乐扩展失败")

        time.sleep(check_interval)


if __name__ == "__main__":
    # 测试代码
    print("=== Suno 音乐扩展模块测试 ===\n")

    try:
        # 注意：需要先有一个已生成的audio_id
        audio_id = "your_audio_id_here"  # 替换为实际的audio_id

        # 测试1：简单扩展
        print("测试1：简单扩展（使用原参数）")
        print("提示：需要先使用 suno_generate 模块生成音乐，获取 audio_id")

        # task_id = simple_extend(
        #     audio_id=audio_id,
        #     model="V5"
        # )
        # print(f"✓ 扩展任务提交成功")
        # print(f"  任务ID: {task_id}")

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        print("请确保已设置 SUNO_API_KEY 环境变量")
