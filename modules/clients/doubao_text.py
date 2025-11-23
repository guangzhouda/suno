"""
豆包文本对话模块 - 歌词生成

提供基于 DeepSeek-V3 的文本生成功能，专注于歌词创作和文本对话。

功能特点：
- 支持多轮对话
- 可自定义系统提示词
- 适合歌词、诗歌、文案生成
- 支持温度参数调节创作风格

使用示例：
    from modules.clients.doubao_text import generate_lyrics, chat

    # 快速生成歌词
    lyrics = generate_lyrics(
        prompt="写一首关于夏天海边的轻快流行歌",
        style="流行",
        language="中文"
    )

    # 自定义对话
    response = chat(
        messages=[
            {"role": "system", "content": "你是一位专业的词曲作者"},
            {"role": "user", "content": "帮我写一首摇滚风格的歌词"}
        ],
        temperature=0.8
    )
"""

import os
import json
import pathlib
from typing import List, Dict, Optional
from volcenginesdkarkruntime import Ark


def _get_client(api_key: Optional[str] = None, base_url: Optional[str] = None) -> Ark:
    """
    获取 Ark 客户端实例

    Args:
        api_key: API密钥（可选，优先级：参数 > config.json > 环境变量）
        base_url: API基础URL（默认为北京地区）

    Returns:
        Ark 客户端实例

    Raises:
        RuntimeError: 当无法获取API密钥时
    """
    # 优先级：参数 > 配置文件 > 环境变量
    if not api_key:
        # 尝试从 config.json 读取
        config_file = pathlib.Path("config.json")
        if config_file.exists():
            try:
                with open(config_file, encoding="utf-8-sig") as f:  # 兼容 BOM
                    config = json.load(f)
                    doubao_config = config.get("doubao", {})

                    # 读取 API key
                    api_key_value = doubao_config.get("api_key", "")
                    if api_key_value.startswith("${") and api_key_value.endswith("}"):
                        env_var = api_key_value[2:-1]
                        api_key = os.getenv(env_var)
                    else:
                        api_key = api_key_value
            except Exception:
                pass

        # 从环境变量读取
        if not api_key:
            api_key = os.getenv("ARK_API_KEY")

    if not api_key:
        raise RuntimeError(
            "缺少豆包 API Key！请在 config.json 中配置 doubao.api_key "
            "或设置环境变量 ARK_API_KEY"
        )

    base_url = base_url or "https://ark.cn-beijing.volces.com/api/v3"

    return Ark(api_key=api_key, base_url=base_url)


def chat(
    messages: List[Dict[str, str]],
    model: str = "deepseek-v3-250324",
    temperature: float = 0.7,
    max_tokens: int = 2000,
    api_key: Optional[str] = None,
    **kwargs
) -> str:
    """
    文本对话功能

    Args:
        messages: 对话消息列表，格式：
            [
                {"role": "system", "content": "系统提示词"},
                {"role": "user", "content": "用户消息"},
                {"role": "assistant", "content": "助手回复"}
            ]
        model: 模型ID（默认 deepseek-v3-250324）
        temperature: 温度参数 (0-1)，越高越有创造性
        max_tokens: 最大生成token数
        api_key: API密钥（可选）
        **kwargs: 其他参数（如 top_p, frequency_penalty 等）

    Returns:
        生成的文本内容

    Raises:
        RuntimeError: API调用失败时

    示例:
        >>> messages = [
        ...     {"role": "system", "content": "你是一位专业作词人"},
        ...     {"role": "user", "content": "写一首关于春天的歌"}
        ... ]
        >>> response = chat(messages, temperature=0.8)
    """
    client = _get_client(api_key)

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        return completion.choices[0].message.content.strip()

    except Exception as e:
        raise RuntimeError(f"文本对话失败: {e}")


def generate_lyrics(
    prompt: str,
    style: str = "流行",
    language: str = "中文",
    mood: Optional[str] = None,
    theme: Optional[str] = None,
    temperature: float = 0.7,
    model: str = "deepseek-v3-250324",
    api_key: Optional[str] = None
) -> str:
    """
    生成歌词（便捷函数）

    Args:
        prompt: 歌词主题或创作要求
        style: 音乐风格（如：流行、摇滚、民谣、说唱、古风等）
        language: 语言（中文/英文）
        mood: 情绪（如：欢快、伤感、励志、温柔等）
        theme: 主题（如：爱情、友情、梦想、回忆等）
        temperature: 创造性温度 (0-1)
        model: 模型ID
        api_key: API密钥（可选）

    Returns:
        生成的歌词文本

    示例:
        >>> lyrics = generate_lyrics(
        ...     prompt="夏天海边的回忆",
        ...     style="清新流行",
        ...     mood="温暖怀旧",
        ...     theme="青春回忆"
        ... )
    """
    # 构建系统提示词
    system_prompt = f"""你是一位专业的词曲作者，擅长创作{style}风格的歌词。
你的作品：
- 富有画面感和情感张力
- 韵律自然，朗朗上口
- 主题明确，层次清晰
- 语言{language}，文字优美

请根据用户需求创作歌词，只输出歌词内容，不要添加额外说明。"""

    # 构建用户提示词
    user_prompt = f"请为我创作一首{style}风格的{language}歌词。\n\n"
    user_prompt += f"主题：{prompt}\n"

    if mood:
        user_prompt += f"情绪：{mood}\n"
    if theme:
        user_prompt += f"主题元素：{theme}\n"

    user_prompt += """
要求：
1. 包含主歌（Verse）和副歌（Chorus）
2. 结构清晰（如：主歌-副歌-主歌-副歌-桥段-副歌）
3. 每段之间用空行分隔
4. 标注段落名称（如 [Verse 1]、[Chorus] 等）
5. 确保押韵和节奏感
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return chat(messages, model=model, temperature=temperature, api_key=api_key)


def refine_lyrics(
    original_lyrics: str,
    refinement_request: str,
    temperature: float = 0.5,
    api_key: Optional[str] = None
) -> str:
    """
    优化和修改歌词

    Args:
        original_lyrics: 原始歌词
        refinement_request: 修改要求（如："让副歌更有力量感"、"改成英文"等）
        temperature: 温度参数（建议较低以保持原意）
        api_key: API密钥（可选）

    Returns:
        优化后的歌词

    示例:
        >>> refined = refine_lyrics(
        ...     original_lyrics=old_lyrics,
        ...     refinement_request="让整体更有画面感，增加细节描写"
        ... )
    """
    system_prompt = "你是一位专业的歌词编辑，擅长优化和改进歌词内容。"

    user_prompt = f"""请根据以下要求修改歌词：

原始歌词：
{original_lyrics}

修改要求：
{refinement_request}

要求：
1. 保持原有结构和韵律
2. 只输出修改后的歌词，不要添加说明
3. 保持段落标注（如 [Verse]、[Chorus] 等）
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    return chat(messages, temperature=temperature, api_key=api_key)


# 预设风格模板
STYLE_TEMPLATES = {
    "流行": {
        "characteristics": "旋律悦耳，朗朗上口，情感真挚，贴近生活",
        "structure": "主歌-副歌-主歌-副歌-桥段-副歌",
        "language": "简洁明了，易于传唱"
    },
    "摇滚": {
        "characteristics": "激情澎湃，节奏强烈，反叛精神，力量感强",
        "structure": "主歌-副歌-主歌-副歌-吉他solo-副歌",
        "language": "直接有力，情绪爆发"
    },
    "民谣": {
        "characteristics": "质朴真诚，故事性强，情感细腻，贴近自然",
        "structure": "主歌-副歌-主歌-副歌-尾声",
        "language": "叙事性强，画面感丰富"
    },
    "说唱": {
        "characteristics": "节奏感强，押韵讲究，态度鲜明，文字密集",
        "structure": "Verse-Hook-Verse-Hook-Bridge-Hook",
        "language": "口语化，押韵精准，文字游戏"
    },
    "古风": {
        "characteristics": "典雅诗意，意境悠远，文言雅致，韵味十足",
        "structure": "起-承-转-合",
        "language": "引经据典，诗词化表达"
    }
}


if __name__ == "__main__":
    # 测试代码
    print("=== 豆包文本对话模块测试 ===\n")

    try:
        # 测试1：快速生成歌词
        print("测试1：生成歌词")
        lyrics = generate_lyrics(
            prompt="夏日午后的咖啡馆",
            style="轻音乐",
            mood="慵懒放松",
            theme="都市慢生活"
        )
        print(lyrics)
        print("\n" + "="*50 + "\n")

        # 测试2：自定义对话
        print("测试2：自定义对话")
        response = chat(
            messages=[
                {"role": "system", "content": "你是一位专业作词人"},
                {"role": "user", "content": "给我一些写摇滚歌词的技巧"}
            ],
            temperature=0.7
        )
        print(response)

    except Exception as e:
        print(f"测试失败: {e}")
