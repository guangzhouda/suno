"""
豆包视频生成模块 - 音乐MV创作

提供基于 Doubao SeeDance 的AI视频生成功能，专注于音乐MV、短视频创作。

功能特点：
- 文生视频：根据文字描述生成视频
- 图生视频：基于首帧图片生成动态视频
- 支持多种比例（16:9、9:16、1:1等）
- 可控制时长（通常5-10秒）
- 适合音乐MV、歌词视频、概念视频

使用示例:
    from modules.clients.doubao_video import generate_mv, text_to_video

    # 快速生成MV
    result = generate_mv(
        lyrics="风吹过海面，带走了思念",
        style="唯美抒情",
        scene="海边日落"
    )

    # 文生视频
    result = text_to_video(
        prompt="一个女孩站在海边，看着夕阳，头发被风吹动",
        ratio="16:9",
        duration=5
    )

    # 图生视频
    result = image_to_video(
        image_url="https://example.com/cover.jpg",
        prompt="镜头缓缓推进，画面逐渐明亮",
        duration=5
    )
"""

import os
import json
import pathlib
from typing import Optional, Dict, Any, Literal
from volcenginesdkarkruntime import Ark


def _get_client(api_key: Optional[str] = None, base_url: Optional[str] = None) -> Ark:
    """
    获取 Ark 客户端实例

    Args:
        api_key: API密钥（可选）
        base_url: API基础URL

    Returns:
        Ark 客户端实例

    Raises:
        RuntimeError: 当无法获取API密钥时
    """
    if not api_key:
        config_file = pathlib.Path("config.json")
        if config_file.exists():
            try:
                with open(config_file, encoding="utf-8") as f:
                    config = json.load(f)
                    doubao_config = config.get("doubao", {})
                    api_key_value = doubao_config.get("api_key", "")
                    if api_key_value.startswith("${") and api_key_value.endswith("}"):
                        env_var = api_key_value[2:-1]
                        api_key = os.getenv(env_var)
                    else:
                        api_key = api_key_value
            except Exception:
                pass

        if not api_key:
            api_key = os.getenv("ARK_API_KEY")

    if not api_key:
        raise RuntimeError(
            "缺少豆包 API Key！请在 config.json 中配置 doubao.api_key "
            "或设置环境变量 ARK_API_KEY"
        )

    base_url = base_url or "https://ark.cn-beijing.volces.com/api/v3"

    return Ark(api_key=api_key, base_url=base_url)


def text_to_video(
    prompt: str,
    ratio: Literal["16:9", "9:16", "1:1", "adaptive"] = "16:9",
    duration: int = 5,
    model: str = "doubao-seedance-1-0-pro-250528",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    文生视频：根据文字描述生成视频

    Args:
        prompt: 视频描述（包含镜头、场景、动作等）
            格式示例："一个女孩站在海边看夕阳，镜头缓缓拉远"
            提示：可以在prompt末尾添加参数，如 "--ratio 16:9 --dur 5"
        ratio: 视频比例
            - "16:9": 横屏（适合电脑、电视）
            - "9:16": 竖屏（适合手机短视频）
            - "1:1": 正方形（适合社交媒体）
            - "adaptive": 自适应
        duration: 视频时长（秒），通常5-10秒
        model: 模型ID
            - "doubao-seedance-1-0-pro-250528": 标准版（质量高）
            - "doubao-seedance-1-0-pro-fast-251015": 快速版
        api_key: API密钥（可选）

    Returns:
        包含任务信息的字典：
        {
            "task_id": "任务ID（用于查询状态）",
            "status": "submitted",
            "prompt": "生成提示词",
            "ratio": "视频比例",
            "duration": 时长
        }

    Raises:
        RuntimeError: API调用失败时

    示例:
        >>> result = text_to_video(
        ...     prompt="一个侦探进入昏暗的房间，检查桌上的线索",
        ...     ratio="16:9",
        ...     duration=5
        ... )
        >>> print(f"任务ID: {result['task_id']}")
    """
    client = _get_client(api_key)

    # 在prompt末尾添加参数（如果用户没有手动添加）
    if "--ratio" not in prompt:
        prompt = f"{prompt} --ratio {ratio}"
    if "--dur" not in prompt and duration:
        prompt = f"{prompt} --dur {duration}"

    # 构建内容
    content = [{"text": prompt, "type": "text"}]

    try:
        response = client.content_generation.tasks.create(
            model=model,
            content=content
        )

        # 返回任务信息
        return {
            "task_id": response.req_id if hasattr(response, 'req_id') else None,
            "status": "submitted",
            "prompt": prompt,
            "ratio": ratio,
            "duration": duration,
            "model": model
        }

    except Exception as e:
        raise RuntimeError(f"视频生成失败: {e}")


def image_to_video(
    image_url: str,
    prompt: str,
    ratio: Literal["16:9", "9:16", "1:1", "adaptive"] = "adaptive",
    duration: int = 5,
    model: str = "doubao-seedance-1-0-pro-fast-251015",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    图生视频：基于首帧图片生成动态视频

    Args:
        image_url: 首帧图片URL（公网可访问）
        prompt: 视频动作描述（描述如何让图片动起来）
            示例："女孩睁开眼，温柔地看向镜头，头发被风吹动，镜头缓缓拉出"
        ratio: 视频比例（adaptive=自适应图片比例）
        duration: 视频时长（秒）
        model: 模型ID（推荐使用fast版本用于图生视频）
        api_key: API密钥（可选）

    Returns:
        包含任务信息的字典

    示例:
        >>> result = image_to_video(
        ...     image_url="https://example.com/girl.jpg",
        ...     prompt="女孩睁开眼睛，微笑看向镜头，头发被风吹动"
        ... )
    """
    client = _get_client(api_key)

    # 添加参数到prompt
    if "--ratio" not in prompt:
        prompt = f"{prompt} --ratio {ratio}"
    if "--dur" not in prompt and duration:
        prompt = f"{prompt} --dur {duration}"

    # 构建内容（先文本后图片）
    content = [
        {"text": prompt, "type": "text"},
        {"image_url": {"url": image_url}, "type": "image_url"}
    ]

    try:
        response = client.content_generation.tasks.create(
            model=model,
            content=content
        )

        return {
            "task_id": response.req_id if hasattr(response, 'req_id') else None,
            "status": "submitted",
            "prompt": prompt,
            "image_url": image_url,
            "ratio": ratio,
            "duration": duration,
            "model": model
        }

    except Exception as e:
        raise RuntimeError(f"图生视频失败: {e}")


def generate_mv(
    lyrics: str,
    style: str = "流行",
    scene: Optional[str] = None,
    mood: Optional[str] = None,
    cover_image_url: Optional[str] = None,
    ratio: Literal["16:9", "9:16", "1:1"] = "16:9",
    duration: int = 5,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    生成音乐MV（便捷函数）

    根据歌词内容自动生成MV视频脚本并创建视频。

    Args:
        lyrics: 歌词内容（完整歌词或片段）
        style: 音乐风格（流行、摇滚、民谣、电子等）
        scene: 场景设定（可选，如：海边、城市、森林等）
        mood: 情绪氛围（可选，如：欢快、忧郁、激情等）
        cover_image_url: 封面图片URL（可选，如果提供则使用图生视频）
        ratio: 视频比例
        duration: 时长
        api_key: API密钥（可选）

    Returns:
        包含任务信息的字典

    示例:
        >>> result = generate_mv(
        ...     lyrics="风吹过海面，带走了思念\\n我站在岸边，回忆从前",
        ...     style="抒情流行",
        ...     scene="海边日落",
        ...     mood="温暖怀旧"
        ... )
    """
    # 构建视频脚本
    script_parts = []

    # 基础描述
    script_parts.append(f"{style}风格的音乐MV")

    # 场景
    if scene:
        script_parts.append(f"场景：{scene}")
    else:
        # 从歌词中推测场景
        if any(word in lyrics for word in ["海", "浪", "沙滩", "岸"]):
            script_parts.append("场景：海边")
        elif any(word in lyrics for word in ["山", "林", "树", "叶"]):
            script_parts.append("场景：山林")
        elif any(word in lyrics for word in ["城市", "街", "楼", "灯"]):
            script_parts.append("场景：都市")
        else:
            script_parts.append("场景：室内空间")

    # 情绪
    if mood:
        script_parts.append(f"氛围：{mood}")

    # 歌词元素（提取关键意象）
    lyrics_preview = lyrics[:100] if len(lyrics) > 100 else lyrics
    script_parts.append(f"画面与歌词意境相符：{lyrics_preview}")

    # 镜头要求
    script_parts.append("多个镜头切换，画面流畅自然，色调与音乐风格匹配")

    # 组合成完整脚本
    prompt = "。".join(script_parts)

    # 根据是否有封面选择生成方式
    if cover_image_url:
        # 图生视频
        return image_to_video(
            image_url=cover_image_url,
            prompt=prompt,
            ratio=ratio,
            duration=duration,
            api_key=api_key
        )
    else:
        # 文生视频
        return text_to_video(
            prompt=prompt,
            ratio=ratio,
            duration=duration,
            api_key=api_key
        )


def generate_lyric_video(
    lyrics_line: str,
    style: str = "简约现代",
    background: str = "渐变色背景",
    animation: str = "文字逐渐出现",
    ratio: Literal["16:9", "9:16", "1:1"] = "16:9",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    生成歌词视频（Lyric Video）

    适合制作纯歌词展示视频，常用于社交媒体分享。

    Args:
        lyrics_line: 歌词内容（一句或几句）
        style: 视觉风格（简约现代、复古、手绘、3D等）
        background: 背景描述
        animation: 动画效果描述
        ratio: 视频比例
        api_key: API密钥（可选）

    Returns:
        包含任务信息的字典

    示例:
        >>> result = generate_lyric_video(
        ...     lyrics_line="风吹过海面，带走了思念",
        ...     style="清新简约",
        ...     background="海洋蓝色渐变",
        ...     animation="文字从下方浮现，轻轻摇曳"
        ... )
    """
    prompt = f"""
    歌词展示视频设计。
    歌词内容："{lyrics_line}"
    视觉风格：{style}
    背景：{background}
    动画效果：{animation}
    要求：文字清晰可读，画面美观，动画流畅自然
    """

    return text_to_video(
        prompt=prompt.strip(),
        ratio=ratio,
        duration=5,
        api_key=api_key
    )


def generate_concept_video(
    concept: str,
    style: str = "艺术感",
    color_tone: str = "电影色调",
    camera_movement: str = "缓慢推进",
    ratio: Literal["16:9", "9:16", "1:1"] = "16:9",
    duration: int = 5,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    生成概念视频

    适合制作抽象的、艺术化的音乐概念视频。

    Args:
        concept: 核心概念/主题（如：时间流逝、梦境、回忆等）
        style: 视觉风格
        color_tone: 色调
        camera_movement: 镜头运动
        ratio: 视频比例
        duration: 时长
        api_key: API密钥（可选）

    Returns:
        包含任务信息的字典

    示例:
        >>> result = generate_concept_video(
        ...     concept="时间流逝与记忆消散",
        ...     style="超现实主义",
        ...     color_tone="冷色调，蓝紫渐变",
        ...     camera_movement="镜头缓缓旋转上升"
        ... )
    """
    prompt = f"""
    概念视频创作。
    主题：{concept}
    视觉风格：{style}
    色调：{color_tone}
    镜头运动：{camera_movement}
    要求：富有艺术感和意境，画面流畅唯美，适合音乐视频使用
    """

    return text_to_video(
        prompt=prompt.strip(),
        ratio=ratio,
        duration=duration,
        api_key=api_key
    )


# 预设镜头语言模板
CAMERA_MOVEMENTS = {
    "推进": "镜头缓缓向前推进",
    "拉远": "镜头缓缓向后拉远",
    "横移": "镜头水平平移",
    "旋转": "镜头绕主体旋转",
    "升降": "镜头上升或下降",
    "跟随": "镜头跟随主体移动",
    "固定": "镜头固定不动",
    "摇晃": "手持摇晃镜头"
}

# 预设场景模板
SCENE_TEMPLATES = {
    "海边日落": "海边日落场景，温暖的金色阳光洒在海面上，波浪轻轻拍打沙滩",
    "城市夜景": "现代城市夜景，霓虹灯闪烁，车流如河，高楼林立",
    "森林清晨": "森林清晨场景，阳光透过树叶洒下斑驳光影，薄雾缭绕",
    "星空夜晚": "星空璀璨的夜晚，银河横跨天际，流星划过",
    "咖啡馆": "温馨的咖啡馆内景，柔和的灯光，窗外街景",
    "雨中街道": "下雨的街道，雨滴打在地面，路灯倒影在水洼中",
    "音乐厅": "音乐厅舞台，聚光灯照射，乐器和麦克风",
    "卧室窗边": "卧室窗边，阳光洒进来，纱帘随风飘动"
}

# 预设风格模板
VISUAL_STYLES = {
    "电影感": "电影级画质，宽银幕比例，专业调色，景深效果",
    "复古胶片": "复古胶片风格，颗粒感，褪色效果，怀旧色调",
    "赛博朋克": "赛博朋克风格，霓虹色彩，高科技元素，未来感",
    "梦幻唯美": "梦幻唯美风格，柔焦效果，光晕，仙气飘飘",
    "黑白艺术": "黑白艺术片风格，高对比度，光影明显",
    "动漫风格": "动漫风格画面，二次元美学，鲜艳色彩",
    "纪实风格": "纪实风格，真实自然，不过度修饰",
    "超现实": "超现实主义，奇幻元素，艺术化表达"
}


if __name__ == "__main__":
    # 测试代码
    print("=== 豆包视频生成模块测试 ===\n")

    try:
        # 测试1：文生视频
        print("测试1：文生视频")
        result = text_to_video(
            prompt="一个侦探进入昏暗的房间，检查桌上的线索，手里拿起某个物品，镜头转向他正在思索",
            ratio="16:9",
            duration=5
        )
        print(f"任务ID: {result['task_id']}")
        print(f"状态: {result['status']}")
        print(f"提示词: {result['prompt']}")
        print("\n" + "="*50 + "\n")

        # 测试2：生成MV
        print("测试2：生成音乐MV")
        result2 = generate_mv(
            lyrics="风吹过海面，带走了思念\n我站在岸边，回忆从前",
            style="抒情流行",
            scene="海边日落",
            mood="温暖怀旧"
        )
        print(f"任务ID: {result2['task_id']}")
        print(f"提示词: {result2['prompt']}")

    except Exception as e:
        print(f"测试失败: {e}")
        print("请确保已设置 ARK_API_KEY 环境变量")
