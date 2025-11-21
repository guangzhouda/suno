"""
豆包图像理解模块 - 图片成歌

提供基于 Doubao Vision 的图像理解功能，可以分析图片内容、提取情感元素，用于音乐创作。

功能特点：
- 图片内容识别和描述
- 情感和氛围分析
- 提取音乐创作元素
- 支持图片成歌工作流
- 多模态理解（图片+文本）

使用示例:
    from modules.clients.doubao_vision import understand_image, image_to_music_prompt

    # 分析图片
    description = understand_image(
        image_url="https://example.com/photo.jpg",
        question="描述这张图片的内容和氛围"
    )

    # 图片成歌：提取音乐元素
    music_elements = image_to_music_prompt(
        image_url="https://example.com/photo.jpg"
    )
    print(f"推荐风格: {music_elements['style']}")
    print(f"推荐情绪: {music_elements['emotion']}")
"""

import os
import json
import pathlib
from typing import Optional, Dict, Any, List
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


def understand_image(
    image_url: str,
    question: str = "请详细描述这张图片的内容、氛围和情绪。",
    model: str = "doubao-seed-1-6-vision-250815",
    api_key: Optional[str] = None
) -> str:
    """
    图像理解和分析

    Args:
        image_url: 图片URL（必须是公网可访问的URL）
        question: 询问的问题（默认为全面描述）
        model: 模型ID（默认 doubao-seed-1-6-vision-250815）
        api_key: API密钥（可选）

    Returns:
        图像分析结果文本

    Raises:
        RuntimeError: API调用失败时

    示例:
        >>> description = understand_image(
        ...     image_url="https://example.com/sunset.jpg",
        ...     question="这张图片展现了什么场景？适合什么风格的音乐？"
        ... )
    """
    client = _get_client(api_key)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        },
                        {
                            "type": "text",
                            "text": question
                        }
                    ]
                }
            ]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise RuntimeError(f"图像理解失败: {e}")


def image_to_music_prompt(
    image_url: str,
    api_key: Optional[str] = None
) -> Dict[str, str]:
    """
    图片成歌：分析图片并提取音乐创作元素

    该函数会分析图片的场景、情感、色调等，并转换为适合音乐创作的元素描述。

    Args:
        image_url: 图片URL
        api_key: API密钥（可选）

    Returns:
        包含音乐元素的字典：
        {
            "scene": "场景描述",
            "emotion": "情绪（如：欢快、忧郁、宁静等）",
            "color_tone": "色调（如：暖色调、冷色调）",
            "style": "推荐音乐风格（如：流行、民谣、电子等）",
            "instruments": "推荐乐器",
            "tempo": "推荐节奏（如：快速、中速、慢速）",
            "atmosphere": "整体氛围",
            "keywords": "关键意象词"
        }

    示例:
        >>> elements = image_to_music_prompt(
        ...     image_url="https://example.com/beach.jpg"
        ... )
        >>> print(f"推荐风格: {elements['style']}")
        >>> print(f"推荐情绪: {elements['emotion']}")
    """
    question = """
    请详细分析这张图片，并提取以下信息用于音乐创作：

    1. 场景描述：图片展现的主要场景和元素
    2. 情绪分析：图片传达的情感（欢快、忧郁、宁静、激情、温暖、冷酷等）
    3. 色调分析：整体色彩基调（暖色调、冷色调、高饱和度、低饱和度等）
    4. 推荐音乐风格：最适合这张图片的音乐风格（流行、摇滚、民谣、电子、古风、爵士等）
    5. 推荐乐器：适合的主要乐器
    6. 推荐节奏：合适的节奏速度（快速/中速/慢速/渐变）
    7. 整体氛围：用3-5个词描述整体氛围
    8. 关键意象：提取5个关键视觉元素或意象词

    请用JSON格式返回：
    {
        "scene": "场景描述",
        "emotion": "情绪",
        "color_tone": "色调",
        "style": "音乐风格",
        "instruments": "推荐乐器",
        "tempo": "节奏",
        "atmosphere": "整体氛围",
        "keywords": "关键意象词"
    }
    """

    description = understand_image(image_url, question, api_key=api_key)

    # 尝试解析JSON
    try:
        # 提取JSON内容（可能包含在代码块中）
        if "```json" in description:
            json_str = description.split("```json")[1].split("```")[0].strip()
        elif "```" in description:
            json_str = description.split("```")[1].split("```")[0].strip()
        else:
            json_str = description

        result = json.loads(json_str)

        # 确保所有必需字段都存在
        default_result = {
            "scene": result.get("scene", "未知"),
            "emotion": result.get("emotion", "中性"),
            "color_tone": result.get("color_tone", "均衡"),
            "style": result.get("style", "流行"),
            "instruments": result.get("instruments", "吉他、钢琴"),
            "tempo": result.get("tempo", "中速"),
            "atmosphere": result.get("atmosphere", "舒适"),
            "keywords": result.get("keywords", "")
        }

        return default_result

    except Exception:
        # 解析失败，返回原始描述和默认值
        return {
            "scene": description[:200] if len(description) > 200 else description,
            "emotion": "中性",
            "color_tone": "均衡",
            "style": "流行",
            "instruments": "吉他、钢琴",
            "tempo": "中速",
            "atmosphere": "舒适",
            "keywords": ""
        }


def image_to_lyrics_prompt(
    image_url: str,
    api_key: Optional[str] = None
) -> str:
    """
    图片转歌词提示词

    分析图片并生成适合用于歌词创作的提示词。

    Args:
        image_url: 图片URL
        api_key: API密钥（可选）

    Returns:
        歌词创作提示词

    示例:
        >>> prompt = image_to_lyrics_prompt(
        ...     image_url="https://example.com/mountain.jpg"
        ... )
        >>> print(prompt)
        # 输出类似：写一首关于雄伟山峰的歌，表达征服自然的豪迈情怀...
    """
    question = """
    请分析这张图片，并生成一段适合用于歌词创作的提示词。

    提示词应该包含：
    1. 主要场景和视觉元素
    2. 情感和意境
    3. 可以展开的故事线索
    4. 适合的音乐风格

    请用一段话（100-200字）描述，作为歌词创作的灵感来源。
    不要使用JSON格式，直接输出描述文本即可。
    """

    return understand_image(image_url, question, api_key=api_key)


def analyze_multiple_images(
    image_urls: List[str],
    question: str = "请描述这些图片的共同主题和整体氛围。",
    api_key: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    批量分析多张图片

    Args:
        image_urls: 图片URL列表
        question: 询问的问题
        api_key: API密钥（可选）

    Returns:
        每张图片的分析结果列表

    示例:
        >>> results = analyze_multiple_images(
        ...     image_urls=[
        ...         "https://example.com/img1.jpg",
        ...         "https://example.com/img2.jpg"
        ...     ]
        ... )
    """
    results = []

    for idx, url in enumerate(image_urls, 1):
        try:
            description = understand_image(url, question, api_key=api_key)
            results.append({
                "index": idx,
                "url": url,
                "description": description,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "index": idx,
                "url": url,
                "description": "",
                "status": "failed",
                "error": str(e)
            })

    return results


def compare_images(
    image_url1: str,
    image_url2: str,
    api_key: Optional[str] = None
) -> str:
    """
    比较两张图片的异同

    Args:
        image_url1: 第一张图片URL
        image_url2: 第二张图片URL
        api_key: API密钥（可选）

    Returns:
        比较分析结果

    注意：
        该函数会分别分析两张图片，然后综合描述。
        豆包Vision API 单次调用只支持一张图片。

    示例:
        >>> comparison = compare_images(
        ...     image_url1="https://example.com/day.jpg",
        ...     image_url2="https://example.com/night.jpg"
        ... )
    """
    # 分别分析两张图片
    desc1 = understand_image(
        image_url1,
        "请详细描述这张图片的场景、色调、情绪和氛围。",
        api_key=api_key
    )

    desc2 = understand_image(
        image_url2,
        "请详细描述这张图片的场景、色调、情绪和氛围。",
        api_key=api_key
    )

    # 返回两个描述
    result = f"""图片1分析：
{desc1}

图片2分析：
{desc2}

对比建议：
- 如果两张图片展现不同时间/场景，可以创作对比式歌词
- 如果色调和情绪有明显差异，可以用于表达情感变化
- 如果主题相似，可以创作系列作品
"""

    return result


def extract_objects(
    image_url: str,
    api_key: Optional[str] = None
) -> List[str]:
    """
    识别图片中的主要物体/元素

    Args:
        image_url: 图片URL
        api_key: API密钥（可选）

    Returns:
        物体/元素列表

    示例:
        >>> objects = extract_objects(
        ...     image_url="https://example.com/scene.jpg"
        ... )
        >>> print(objects)
        # ['吉他', '窗户', '夕阳', '沙发', '书架']
    """
    question = """
    请识别这张图片中的主要物体和元素，列出10个最显著的物体。

    直接返回物体列表，每行一个，格式如下：
    1. 物体1
    2. 物体2
    3. 物体3
    ...

    不要添加其他说明文字。
    """

    description = understand_image(image_url, question, api_key=api_key)

    # 解析物体列表
    objects = []
    for line in description.split('\n'):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
            # 移除序号和标点
            obj = line.split('.', 1)[-1].split('、', 1)[-1].split('-', 1)[-1].strip()
            if obj:
                objects.append(obj)

    return objects


def get_color_palette(
    image_url: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    分析图片的色彩方案

    Args:
        image_url: 图片URL
        api_key: API密钥（可选）

    Returns:
        色彩分析结果

    示例:
        >>> palette = get_color_palette(
        ...     image_url="https://example.com/colorful.jpg"
        ... )
        >>> print(palette['dominant_colors'])
    """
    question = """
    请分析这张图片的色彩方案，包括：
    1. 主要颜色（3-5种）
    2. 整体色调（暖色调/冷色调/中性）
    3. 饱和度（高/中/低）
    4. 明度（明亮/适中/暗沉）
    5. 色彩情绪（热情/平静/忧郁/活力等）

    请用JSON格式返回：
    {
        "dominant_colors": ["颜色1", "颜色2", "颜色3"],
        "overall_tone": "整体色调",
        "saturation": "饱和度",
        "brightness": "明度",
        "color_emotion": "色彩情绪"
    }
    """

    description = understand_image(image_url, question, api_key=api_key)

    # 尝试解析JSON
    try:
        if "```json" in description:
            json_str = description.split("```json")[1].split("```")[0].strip()
        elif "```" in description:
            json_str = description.split("```")[1].split("```")[0].strip()
        else:
            json_str = description

        result = json.loads(json_str)
        return result

    except Exception:
        return {
            "dominant_colors": ["未知"],
            "overall_tone": "中性",
            "saturation": "中",
            "brightness": "适中",
            "color_emotion": "平静",
            "raw_description": description
        }


if __name__ == "__main__":
    # 测试代码
    print("=== 豆包图像理解模块测试 ===\n")

    try:
        # 测试图片URL（示例）
        test_image_url = "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"

        # 测试1：基础图像理解
        print("测试1：图像理解")
        description = understand_image(
            image_url=test_image_url,
            question="这是什么地方？描述一下场景和氛围。"
        )
        print(description)
        print("\n" + "="*50 + "\n")

        # 测试2：图片成歌
        print("测试2：提取音乐元素")
        music_elements = image_to_music_prompt(test_image_url)
        print(f"场景: {music_elements['scene']}")
        print(f"情绪: {music_elements['emotion']}")
        print(f"推荐风格: {music_elements['style']}")
        print(f"推荐乐器: {music_elements['instruments']}")
        print(f"节奏: {music_elements['tempo']}")

    except Exception as e:
        print(f"测试失败: {e}")
        print("请确保已设置 ARK_API_KEY 环境变量")
