"""
豆包 API 客户端

提供豆包 AI 功能：
- 文本对话（DeepSeek-V3 歌词生成）
- 图像生成（专辑封面）
- 图像理解（图片成歌）
- 视频生成（音乐 MV）
"""

import os
import json
import pathlib
from typing import Optional, Dict, Any, List
from volcenginesdkarkruntime import Ark


class DoubaoClient:
    """豆包 API 客户端"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        # 优先级：参数 > 配置文件 > 环境变量
        if api_key:
            self.api_key = api_key
        else:
            # 尝试从 config.json 读取
            config_file = pathlib.Path("config.json")
            if config_file.exists():
                try:
                    with open(config_file, encoding="utf-8-sig") as f:  # 兼容 BOM
                        config = json.load(f)
                        doubao_config = config.get("doubao", {})

                        # 读取 API key，如果是环境变量占位符则解析
                        api_key_value = doubao_config.get("api_key", "")
                        if api_key_value.startswith("${") and api_key_value.endswith("}"):
                            env_var = api_key_value[2:-1]  # 提取环境变量名
                            self.api_key = os.getenv(env_var)
                        else:
                            self.api_key = api_key_value

                        self.models = doubao_config.get("models", {})
                except Exception as e:
                    print(f"警告：读取 config.json 失败: {e}")

            # 从环境变量读取
            if not self.api_key:
                self.api_key = os.getenv("ARK_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "缺少豆包 API Key！请在 config.json 中配置 doubao.api_key "
                "或设置环境变量 ARK_API_KEY"
            )

        self.base_url = base_url or "https://ark.cn-beijing.volces.com/api/v3"

        # 初始化 Ark 客户端
        self.client = Ark(
            api_key=self.api_key,
            base_url=self.base_url
        )

        # 默认模型配置
        if not hasattr(self, 'models'):
            self.models = {
                "text": "deepseek-v3-250324",
                "image": "doubao-seedream-4-0-250828",
                "vision": "doubao-seed-1-6-vision-250815",
                "video": "doubao-seedance-1-0-pro-fast-251015"
            }

    # ==================== 文本对话 ====================

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        文本对话（用于生成歌词）

        Args:
            messages: 对话消息列表 [{"role": "user", "content": "..."}]
            model: 模型ID（默认使用 deepseek-v3-250324）
            temperature: 温度参数 (0-1)
            max_tokens: 最大token数
            **kwargs: 其他参数

        Returns:
            生成的文本内容
        """
        model = model or self.models.get("text", "deepseek-v3-250324")

        try:
            completion = self.client.chat.completions.create(
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
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        生成歌词（便捷方法）

        Args:
            prompt: 用户提示
            system_prompt: 系统提示（可选）
            temperature: 温度参数

        Returns:
            生成的歌词
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        return self.chat(messages=messages, temperature=temperature)

    # ==================== 图像生成 ====================

    def generate_image(
        self,
        prompt: str,
        size: str = "2K",
        model: Optional[str] = None,
        watermark: bool = False,
        response_format: str = "url"
    ) -> Dict[str, Any]:
        """
        生成图像（专辑封面）

        Args:
            prompt: 图像描述
            size: 图像尺寸 ("2K", "1024x1024" 等)
            model: 模型ID（默认使用 doubao-seedream-4-0-250828）
            watermark: 是否添加水印
            response_format: 返回格式 ("url" 或 "b64_json")

        Returns:
            包含图像URL的字典
        """
        model = model or self.models.get("image", "doubao-seedream-4-0-250828")

        try:
            response = self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                response_format=response_format,
                watermark=watermark
            )

            # 返回第一张图片的URL
            return {
                "url": response.data[0].url if response_format == "url" else None,
                "b64_json": response.data[0].b64_json if response_format == "b64_json" else None,
                "prompt": prompt,
                "size": size
            }

        except Exception as e:
            raise RuntimeError(f"图像生成失败: {e}")

    # ==================== 图像理解 ====================

    def understand_image(
        self,
        image_url: str,
        question: str = "这是哪里？描述一下这张图片的内容、氛围和情绪。",
        model: Optional[str] = None
    ) -> str:
        """
        图像理解（图片成歌的第一步）

        Args:
            image_url: 图片URL
            question: 询问内容
            model: 模型ID（默认使用 doubao-seed-1-6-vision-250815）

        Returns:
            图像描述文本
        """
        model = model or self.models.get("vision", "doubao-seed-1-6-vision-250815")

        try:
            response = self.client.chat.completions.create(
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

    def image_to_song_description(self, image_url: str) -> Dict[str, str]:
        """
        图片成歌：分析图片并提取音乐创作元素

        Args:
            image_url: 图片URL

        Returns:
            包含场景、情绪、风格等信息的字典
        """
        question = """
        请详细分析这张图片，并提取以下信息用于音乐创作：
        1. 主要场景和元素
        2. 整体氛围和情绪
        3. 色彩基调（冷色调/暖色调）
        4. 适合的音乐风格
        5. 推荐的乐器和节奏

        请用JSON格式返回：
        {
            "scene": "场景描述",
            "emotion": "情绪",
            "color_tone": "色调",
            "style": "音乐风格",
            "instruments": "推荐乐器",
            "tempo": "节奏"
        }
        """

        description = self.understand_image(image_url, question)

        # 尝试解析JSON
        try:
            import json
            # 提取JSON内容（可能包含在```json```代码块中）
            if "```json" in description:
                json_str = description.split("```json")[1].split("```")[0].strip()
            elif "```" in description:
                json_str = description.split("```")[1].split("```")[0].strip()
            else:
                json_str = description

            result = json.loads(json_str)
            return result

        except Exception:
            # 解析失败，返回原始描述
            return {
                "scene": description,
                "emotion": "未知",
                "color_tone": "未知",
                "style": "流行",
                "instruments": "未知",
                "tempo": "中速"
            }

    def image_to_lyrics(
        self,
        image_url: str,
        prompt: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, str]:
        """
        图片生成歌词

        Args:
            image_url: 图片 URL
            prompt: 额外要求/风格补充
            model: 视觉模型 ID

        Returns:
            包含标题与歌词的字典
        """
        model = model or self.models.get("vision", "doubao-seed-1-6-vision-250815")

        # 约束模型输出格式，优先要求 JSON，便于前端解析
        user_text = """
        请观看图片，直接写一首适合该画面的中文歌词，并给出简洁标题。
        输出 JSON，不要包含多余解释：
        {
          "title": "歌曲标题",
          "lyrics": "完整歌词，多段落可换行保留标签",
          "description": "一句话概括画面与情绪"
        }
        """
        if prompt:
            user_text += f"\n补充要求：{prompt}"

        try:
            response = self.client.chat.completions.create(
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
                                "text": user_text
                            }
                        ]
                    }
                ]
            )

            content = response.choices[0].message.content.strip()

            # 尝试解析 JSON，兼容代码块
            json_str = content
            if "```json" in content:
                json_str = content.split("```json", 1)[1].split("```", 1)[0].strip()
            elif "```" in content:
                json_str = content.split("```", 1)[1].split("```", 1)[0].strip()

            payload: Dict[str, str] = {}
            try:
                payload = json.loads(json_str)
            except Exception:
                # 如果不是 JSON，作为歌词文本返回
                payload = {
                    "lyrics": content,
                    "title": "AI Song",
                    "description": ""
                }

            # 兜底补全字段
            lyrics = payload.get("lyrics") or payload.get("text") or payload.get("content") or content
            title = payload.get("title") or "AI Song"
            desc = payload.get("description") or payload.get("desc") or ""

            return {
                "title": title,
                "lyrics": lyrics,
                "description": desc,
                "raw": content
            }

        except Exception as e:
            raise RuntimeError(f"图片生成歌词失败: {e}")

    # ==================== 视频生成 ====================

    def generate_video(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成视频（音乐 MV）

        Args:
            prompt: 视频描述（含镜头描述）
            image_url: 首帧图片URL（可选，用于图生视频）
            model: 模型ID（默认使用 doubao-seedance-1-0-pro-250528）
            **kwargs: 其他参数（ratio, dur 等）

        Returns:
            包含任务信息的字典
        """
        model = model or self.models.get("video", "doubao-seedance-1-0-pro-250528")

        # 构建内容
        content = []

        # 文本提示
        content.append({"text": prompt, "type": "text"})

        # 如果提供了图片，添加图片（图生视频）
        if image_url:
            content.append({
                "image_url": {"url": image_url},
                "type": "image_url"
            })

        try:
            response = self.client.content_generation.tasks.create(
                model=model,
                content=content
            )

            # 返回任务信息
            return {
                "task_id": response.req_id if hasattr(response, 'req_id') else None,
                "status": "submitted",
                "prompt": prompt,
                "image_url": image_url
            }

        except Exception as e:
            raise RuntimeError(f"视频生成失败: {e}")

    def create_music_video(
        self,
        lyrics: str,
        style: str = "流行",
        image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建音乐 MV（便捷方法）

        Args:
            lyrics: 歌词
            style: 音乐风格
            image_url: 封面图片URL（可选）

        Returns:
            视频任务信息
        """
        # 将歌词转换为视频描述
        prompt = f"""
        为{style}风格的音乐创作MV视频。

        歌词内容：
        {lyrics}

        要求：
        - 多个镜头切换
        - 画面与歌词意境相符
        - 色调与音乐风格匹配
        - 比例 16:9
        - 时长 5秒

        --ratio 16:9 --dur 5
        """

        return self.generate_video(prompt, image_url=image_url)

    def get_video_task(self, task_id: str) -> Dict[str, Any]:
        """
        查询视频任务状态
        """
        try:
            result = self.client.content_generation.tasks.get(task_id=task_id)
            data = {}
            # 对象转简易 dict
            if hasattr(result, "__dict__"):
                data = dict(result.__dict__)
            data["status"] = getattr(result, "status", None)
            data["task_id"] = task_id
            data["data"] = getattr(result, "data", None)
            return data
        except Exception as e:
            raise RuntimeError(f"查询视频任务失败: {e}")
