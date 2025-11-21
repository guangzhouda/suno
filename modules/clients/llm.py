"""
LLM（大语言模型）客户端模块
支持多个提供商：OpenAI、DeepSeek、通义千问、智谱AI等
"""

from typing import Dict, Any, List, Optional, AsyncIterator
import json
from loguru import logger
from .base import BaseAPIClient


class LLMClient(BaseAPIClient):
    """
    统一的LLM客户端
    支持OpenAI兼容的API接口
    """

    def __init__(self,
                 provider: str,
                 api_key: str,
                 api_base: str,
                 default_model: str = None):
        """
        初始化LLM客户端

        Args:
            provider: 提供商名称 (openai, deepseek, qwen, zhipu等)
            api_key: API密钥
            api_base: API基础URL
            default_model: 默认模型名称
        """
        super().__init__(api_key, api_base, f"LLM-{provider}")
        self.provider = provider
        self.default_model = default_model

        # 根据不同提供商调整请求头
        self._setup_provider_headers()

    def _setup_provider_headers(self):
        """根据提供商设置特定的请求头"""
        if self.provider == "deepseek":
            # DeepSeek使用标准的OpenAI格式
            pass
        elif self.provider == "qwen":
            # 通义千问可能需要特殊的API Key格式
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })
        elif self.provider == "zhipu":
            # 智谱AI使用不同的认证方式
            self.session.headers.update({
                'Authorization': f'{self.api_key}'
            })
        elif self.provider == "openai":
            # OpenAI标准格式
            pass

    def health_check(self) -> bool:
        """健康检查"""
        try:
            # 简单的模型列表查询
            response = self._get('/models')
            return True
        except:
            # 如果模型列表接口不可用，尝试简单对话
            try:
                self.chat(
                    messages=[{"role": "user", "content": "hi"}],
                    max_tokens=5
                )
                return True
            except:
                return False

    def chat(self,
            messages: List[Dict[str, str]],
            model: Optional[str] = None,
            temperature: float = 0.7,
            max_tokens: int = 2000,
            top_p: float = 1.0,
            stream: bool = False,
            **kwargs) -> Dict[str, Any]:
        """
        对话接口

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            model: 模型名称，不指定则使用默认模型
            temperature: 温度参数 (0-2)
            max_tokens: 最大生成token数
            top_p: 核采样参数
            stream: 是否流式输出
            **kwargs: 其他模型特定参数

        Returns:
            API响应
        """
        model = model or self.default_model
        if not model:
            raise ValueError(f"{self.service_name}: 未指定模型")

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": stream,
            **kwargs
        }

        logger.info(f"{self.service_name} 对话请求 - 模型: {model}, 消息数: {len(messages)}")

        try:
            response = self._post('/chat/completions', json=payload)

            # 记录token使用情况
            if 'usage' in response:
                usage = response['usage']
                logger.info(
                    f"Token使用: 输入={usage.get('prompt_tokens', 0)}, "
                    f"输出={usage.get('completion_tokens', 0)}, "
                    f"总计={usage.get('total_tokens', 0)}"
                )

            return response
        except Exception as e:
            logger.error(f"{self.service_name} 对话失败: {e}")
            raise

    def chat_stream(self,
                   messages: List[Dict[str, str]],
                   model: Optional[str] = None,
                   temperature: float = 0.7,
                   max_tokens: int = 2000,
                   **kwargs):
        """
        流式对话接口

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Yields:
            流式响应的每一块数据
        """
        model = model or self.default_model
        if not model:
            raise ValueError(f"{self.service_name}: 未指定模型")

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
            **kwargs
        }

        url = f"{self.api_base}/chat/completions"

        try:
            with self.session.post(url, json=payload, stream=True) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]  # 移除 'data: ' 前缀
                            if data == '[DONE]':
                                break
                            try:
                                chunk = json.loads(data)
                                yield chunk
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"{self.service_name} 流式对话失败: {e}")
            raise

    def complete(self,
                prompt: str,
                model: Optional[str] = None,
                temperature: float = 0.7,
                max_tokens: int = 2000,
                **kwargs) -> Dict[str, Any]:
        """
        文本补全接口（适用于支持该接口的模型）

        Args:
            prompt: 提示文本
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Returns:
            API响应
        """
        model = model or self.default_model
        if not model:
            raise ValueError(f"{self.service_name}: 未指定模型")

        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }

        logger.info(f"{self.service_name} 补全请求 - 模型: {model}")

        try:
            response = self._post('/completions', json=payload)
            return response
        except Exception as e:
            logger.error(f"{self.service_name} 补全失败: {e}")
            raise

    def embeddings(self,
                  input_text: str | List[str],
                  model: Optional[str] = None) -> Dict[str, Any]:
        """
        获取文本向量嵌入

        Args:
            input_text: 输入文本（单个或列表）
            model: 嵌入模型名称

        Returns:
            API响应
        """
        model = model or self.default_model or "text-embedding-ada-002"

        payload = {
            "model": model,
            "input": input_text
        }

        logger.info(f"{self.service_name} 嵌入请求 - 模型: {model}")

        try:
            response = self._post('/embeddings', json=payload)
            return response
        except Exception as e:
            logger.error(f"{self.service_name} 嵌入失败: {e}")
            raise


# ==================== 特定提供商的客户端 ====================

class DeepSeekClient(LLMClient):
    """DeepSeek 客户端"""

    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        super().__init__(
            provider="deepseek",
            api_key=api_key,
            api_base="https://api.deepseek.com/v1",
            default_model=model
        )


class OpenAIClient(LLMClient):
    """OpenAI 客户端"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        super().__init__(
            provider="openai",
            api_key=api_key,
            api_base="https://api.openai.com/v1",
            default_model=model
        )


class QwenClient(LLMClient):
    """通义千问 客户端"""

    def __init__(self, api_key: str, model: str = "qwen-turbo"):
        super().__init__(
            provider="qwen",
            api_key=api_key,
            api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
            default_model=model
        )


class ZhipuClient(LLMClient):
    """智谱AI 客户端"""

    def __init__(self, api_key: str, model: str = "glm-4"):
        super().__init__(
            provider="zhipu",
            api_key=api_key,
            api_base="https://open.bigmodel.cn/api/paas/v4",
            default_model=model
        )

class NewAPIClient(LLMClient):
    """New API 统一接口客户端（支持文本和图像）"""

    def __init__(self, api_key: str, text_model: str = None, image_model: str = None):
        super().__init__(
            provider="newapi",
            api_key=api_key,
            api_base="https://api.voct.top/v1",
            default_model=text_model or "deepseek-ai/DeepSeek-V3"
        )
        self.image_model = image_model or "doubao-seedream-4-0-250828"

    def generate_image(self, prompt: str, size: str = "1024x1024", **kwargs):
        """生成图像"""
        payload = {
            "model": self.image_model,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "response_format": "url",
            **kwargs
        }

        response = self._post('/images/generations', json=payload)
        return response


# ==================== 客户端工厂 ====================

def create_llm_client(provider: str,
                     api_key: str,
                     api_base: str = None,
                     model: str = None) -> LLMClient:
    """
    LLM客户端工厂函数

    Args:
        provider: 提供商名称
        api_key: API密钥
        api_base: 自定义API基础URL
        model: 默认模型

    Returns:
        对应的LLM客户端实例
    """
    provider = provider.lower()

    # 使用预定义的客户端类
    if provider == "deepseek":
        return DeepSeekClient(api_key, model or "deepseek-chat")
    elif provider == "openai":
        return OpenAIClient(api_key, model or "gpt-3.5-turbo")
    elif provider == "qwen":
        return QwenClient(api_key, model or "qwen-turbo")
    elif provider == "zhipu":
        return ZhipuClient(api_key, model or "glm-4")
    elif provider == "newapi":
        # New API统一接口（支持文本和图像）
        return NewAPIClient(api_key, text_model=model)
    else:
        # 通用客户端，需要提供api_base
        if not api_base:
            raise ValueError(f"未知提供商 {provider}，需要提供 api_base")
        return LLMClient(provider, api_key, api_base, model)
