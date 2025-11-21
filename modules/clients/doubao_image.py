"""
豆包图像生成模块 - 专辑封面生成

提供基于 Doubao SeedReam 的AI图像生成功能，专注于音乐专辑封面、海报等视觉创作。

功能特点：
- 支持多种尺寸输出（2K, 1K 等）
- 可选水印设置
- 支持URL和Base64两种返回格式
- 提供专辑封面预设模板
- 支持根据歌词/音乐风格生成封面

使用示例：
    from modules.clients.doubao_image import generate_album_cover, generate_image

    # 快速生成专辑封面
    result = generate_album_cover(
        title="夏日回忆",
        style="清新流行",
        mood="温暖怀旧"
    )
    print(f"封面URL: {result['url']}")

    # 自定义生成
    result = generate_image(
        prompt="赛博朋克风格的城市夜景，霓虹灯闪烁",
        size="2K",
        watermark=False
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
        base_url: API基础URL（默认为北京地区）

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


def generate_image(
    prompt: str,
    size: str = "2K",
    model: str = "doubao-seedream-4-0-250828",
    watermark: bool = False,
    response_format: Literal["url", "b64_json"] = "url",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    生成图像

    Args:
        prompt: 图像描述（中文或英文）
        size: 图像尺寸，支持：
            - "2K": 2048x2048
            - "1K": 1024x1024
            - "1024x1024": 正方形
            - "1024x768": 横向
            - "768x1024": 竖向
        model: 模型ID（默认 doubao-seedream-4-0-250828）
        watermark: 是否添加水印（默认False）
        response_format: 返回格式
            - "url": 返回图片URL（推荐，图片会过期）
            - "b64_json": 返回Base64编码（适合需要持久化存储）
        api_key: API密钥（可选）

    Returns:
        包含图像信息的字典：
        {
            "url": "图片URL（如果format=url）",
            "b64_json": "Base64编码（如果format=b64_json）",
            "prompt": "生成提示词",
            "size": "图片尺寸",
            "model": "使用的模型"
        }

    Raises:
        RuntimeError: API调用失败时

    示例:
        >>> result = generate_image(
        ...     prompt="夕阳下的海边，温暖色调，电影感",
        ...     size="2K",
        ...     watermark=False
        ... )
        >>> print(result['url'])
    """
    client = _get_client(api_key)

    try:
        response = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            response_format=response_format,
            watermark=watermark
        )

        return {
            "url": response.data[0].url if response_format == "url" else None,
            "b64_json": response.data[0].b64_json if response_format == "b64_json" else None,
            "prompt": prompt,
            "size": size,
            "model": model
        }

    except Exception as e:
        raise RuntimeError(f"图像生成失败: {e}")


def generate_album_cover(
    title: str,
    artist: Optional[str] = None,
    style: str = "流行",
    mood: str = "温暖",
    color_scheme: Optional[str] = None,
    elements: Optional[str] = None,
    size: str = "1K",
    watermark: bool = False,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    生成专辑封面（便捷函数）

    Args:
        title: 专辑/歌曲标题
        artist: 艺术家名称（可选）
        style: 音乐风格（流行、摇滚、民谣、电子、古风等）
        mood: 情绪氛围（温暖、忧郁、激情、宁静、梦幻等）
        color_scheme: 色彩方案（暖色调、冷色调、黑白、彩虹、渐变等）
        elements: 视觉元素（日落、海洋、城市、星空、花朵等）
        size: 图片尺寸
        watermark: 是否添加水印
        api_key: API密钥（可选）

    Returns:
        包含封面图片信息的字典

    示例:
        >>> cover = generate_album_cover(
        ...     title="夏日回忆",
        ...     artist="李明",
        ...     style="清新流行",
        ...     mood="温暖怀旧",
        ...     color_scheme="暖色调",
        ...     elements="海边、夕阳、吉他"
        ... )
    """
    # 根据风格预设视觉风格
    style_presets = {
        "流行": "现代时尚，色彩明亮，视觉冲击力强",
        "摇滚": "粗粝质感，高对比度，强烈视觉张力，朋克风格",
        "民谣": "自然质朴，温暖柔和，手绘风格，复古质感",
        "电子": "未来科技感，霓虹色彩，几何图形，赛博朋克",
        "古风": "中国风元素，水墨画风，典雅意境，传统美学",
        "爵士": "复古优雅，低调奢华，怀旧色调，艺术气息",
        "说唱": "街头文化，涂鸦艺术，大胆配色，潮流元素",
        "轻音乐": "清新淡雅，柔和色调，简约设计，治愈系"
    }

    # 构建详细的提示词
    prompt_parts = []

    # 基础描述
    if artist:
        prompt_parts.append(f"音乐专辑封面设计，专辑名称《{title}》，艺术家：{artist}")
    else:
        prompt_parts.append(f"音乐专辑封面设计，专辑名称《{title}》")

    # 风格描述
    style_desc = style_presets.get(style, style)
    prompt_parts.append(f"音乐风格：{style}，视觉风格：{style_desc}")

    # 情绪氛围
    prompt_parts.append(f"整体氛围：{mood}")

    # 色彩方案
    if color_scheme:
        prompt_parts.append(f"色彩方案：{color_scheme}")

    # 视觉元素
    if elements:
        prompt_parts.append(f"视觉元素：{elements}")

    # 通用要求
    prompt_parts.append("要求：专业的专辑封面设计，构图精美，艺术感强，适合音乐封面使用，高清画质")

    prompt = "，".join(prompt_parts)

    return generate_image(
        prompt=prompt,
        size=size,
        watermark=watermark,
        api_key=api_key
    )


def generate_cover_from_lyrics(
    lyrics: str,
    style: str = "流行",
    size: str = "1K",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    根据歌词内容生成封面

    该函数会分析歌词，提取关键意象和情感，然后生成相应的封面图片。

    Args:
        lyrics: 歌词内容
        style: 音乐风格
        size: 图片尺寸
        api_key: API密钥（可选）

    Returns:
        包含封面图片信息的字典

    示例:
        >>> lyrics = '''
        ... [Verse]
        ... 夕阳染红了海面
        ... 我们坐在沙滩上
        ... 吉他声随风飘散
        ... ...
        ... '''
        >>> cover = generate_cover_from_lyrics(lyrics, style="民谣")
    """
    # 简单的关键词提取（实际应用中可以使用更复杂的NLP分析）
    # 这里只做简单的示例
    keywords = []

    # 常见意象词库
    imagery_keywords = {
        "自然": ["海", "山", "星", "月", "云", "风", "雨", "雪", "树", "花"],
        "城市": ["城市", "街道", "楼", "灯", "霓虹", "车"],
        "情感": ["心", "梦", "爱", "泪", "笑", "忆"],
        "时间": ["春", "夏", "秋", "冬", "晨", "暮", "夜", "昨天", "明天"]
    }

    # 提取关键意象
    for category, words in imagery_keywords.items():
        for word in words:
            if word in lyrics:
                keywords.append(word)

    # 构建提示词
    if keywords:
        elements = "、".join(keywords[:5])  # 最多取5个关键词
        prompt = f"音乐专辑封面，{style}风格，画面包含：{elements}，意境优美，艺术感强，高清画质"
    else:
        prompt = f"音乐专辑封面，{style}风格，意境优美，艺术感强，高清画质"

    return generate_image(
        prompt=prompt,
        size=size,
        api_key=api_key
    )


def generate_poster(
    event_name: str,
    date: str,
    venue: Optional[str] = None,
    artists: Optional[str] = None,
    style: str = "现代",
    size: str = "768x1024",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    生成音乐活动海报

    Args:
        event_name: 活动名称
        date: 活动日期
        venue: 活动地点（可选）
        artists: 演出艺术家（可选）
        style: 海报风格
        size: 图片尺寸（推荐竖向）
        api_key: API密钥（可选）

    Returns:
        包含海报图片信息的字典

    示例:
        >>> poster = generate_poster(
        ...     event_name="夏日音乐节",
        ...     date="2025年7月15日",
        ...     venue="海滨公园",
        ...     artists="多位人气歌手",
        ...     style="青春活力"
        ... )
    """
    prompt_parts = [
        f"音乐活动海报设计",
        f"活动名称：{event_name}",
        f"日期：{date}"
    ]

    if venue:
        prompt_parts.append(f"地点：{venue}")

    if artists:
        prompt_parts.append(f"演出：{artists}")

    prompt_parts.append(f"风格：{style}，视觉冲击力强，专业海报设计，高清")

    prompt = "，".join(prompt_parts)

    return generate_image(
        prompt=prompt,
        size=size,
        api_key=api_key
    )


# 预设色彩方案
COLOR_SCHEMES = {
    "暖色调": "温暖的橙色、黄色、红色渐变",
    "冷色调": "清冷的蓝色、紫色、青色渐变",
    "黑白": "经典黑白灰色调，高对比度",
    "莫兰迪": "莫兰迪色系，低饱和度，高级灰",
    "赛博朋克": "霓虹粉、电蓝、荧光绿，高饱和度",
    "复古": "复古怀旧色调，做旧质感",
    "梦幻": "梦幻渐变色，柔和过渡",
    "大地色": "棕色、土黄、橄榄绿等自然色"
}

# 预设风格模板
STYLE_TEMPLATES = {
    "极简": "极简主义设计，留白充足，几何图形，现代感",
    "复古": "复古怀旧风格，做旧质感，胶片感，70-80年代风格",
    "手绘": "手绘插画风格，艺术感，温暖质朴",
    "3D": "3D渲染效果，立体感强，现代科技感",
    "拼贴": "拼贴艺术，多元素组合，创意设计",
    "涂鸦": "街头涂鸦艺术，自由奔放，色彩大胆",
    "水彩": "水彩画风格，柔和晕染，清新淡雅",
    "油画": "油画质感，笔触明显，艺术气息浓厚"
}


if __name__ == "__main__":
    # 测试代码
    print("=== 豆包图像生成模块测试 ===\n")

    try:
        # 测试1：生成专辑封面
        print("测试1：生成专辑封面")
        result = generate_album_cover(
            title="夏日回忆",
            artist="测试艺术家",
            style="清新流行",
            mood="温暖怀旧",
            color_scheme="暖色调",
            elements="海边、夕阳、吉他",
            size="1K"
        )
        print(f"封面URL: {result['url']}")
        print(f"提示词: {result['prompt']}")
        print("\n" + "="*50 + "\n")

        # 测试2：自定义生成
        print("测试2：自定义图像生成")
        result2 = generate_image(
            prompt="赛博朋克风格的未来城市，霓虹灯闪烁，夜景",
            size="2K"
        )
        print(f"图片URL: {result2['url']}")

    except Exception as e:
        print(f"测试失败: {e}")
        print("请确保已设置 ARK_API_KEY 环境变量")
