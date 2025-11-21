"""
LLM相关的API路由
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger
import json

from ..models.llm import ChatRequest, CompletionRequest, EmbeddingRequest
from ..clients.llm import create_llm_client

# 创建路由器
router = APIRouter(prefix="/api/llm", tags=["LLM"])

# 全局客户端实例（懒加载）
_llm_client = None


def get_llm_client():
    """获取LLM客户端（单例模式）"""
    global _llm_client

    if _llm_client is None:
        # 从配置中读取
        from config import get_config
        config = get_config()

        if not config.is_enabled('llm'):
            raise HTTPException(
                status_code=503,
                detail="LLM服务未启用，请在配置文件中启用并配置API密钥"
            )

        provider = config.get('llm.provider', 'deepseek')
        api_key = config.get('llm.api_key')
        api_base = config.get('llm.api_base')
        default_model = config.get('llm.default_model')

        if not api_key:
            raise HTTPException(
                status_code=500,
                detail=f"LLM服务配置错误：未找到 {provider} 的API密钥"
            )

        try:
            _llm_client = create_llm_client(
                provider=provider,
                api_key=api_key,
                api_base=api_base,
                model=default_model
            )
            logger.info(f"LLM客户端初始化成功: {provider} - {default_model}")
        except Exception as e:
            logger.error(f"LLM客户端初始化失败: {e}")
            raise HTTPException(status_code=500, detail=f"LLM客户端初始化失败: {str(e)}")

    return _llm_client


@router.get("/health")
async def health_check():
    """LLM服务健康检查"""
    try:
        client = get_llm_client()
        is_healthy = client.health_check()
        return {
            "status": "ok" if is_healthy else "error",
            "provider": client.provider,
            "model": client.default_model
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    对话接口

    支持标准的对话格式，兼容OpenAI API
    """
    try:
        client = get_llm_client()

        # 转换Pydantic模型为字典
        messages = [msg.dict() for msg in request.messages]

        # 如果不是流式输出，直接返回完整响应
        if not request.stream:
            response = client.chat(
                messages=messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                presence_penalty=request.presence_penalty,
                frequency_penalty=request.frequency_penalty
            )

            return {
                "code": 200,
                "data": response
            }
        else:
            # 流式输出
            async def generate():
                try:
                    for chunk in client.chat_stream(
                        messages=messages,
                        model=request.model,
                        temperature=request.temperature,
                        max_tokens=request.max_tokens,
                        top_p=request.top_p
                    ):
                        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    logger.error(f"流式输出错误: {e}")
                    yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

            return StreamingResponse(
                generate(),
                media_type="text/event-stream"
            )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"对话请求失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/completion")
async def completion(request: CompletionRequest):
    """
    文本补全接口

    适用于支持补全接口的模型
    """
    try:
        client = get_llm_client()

        response = client.complete(
            prompt=request.prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p
        )

        return {
            "code": 200,
            "data": response
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"补全请求失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/embeddings")
async def embeddings(request: EmbeddingRequest):
    """
    向量嵌入接口

    将文本转换为向量表示
    """
    try:
        client = get_llm_client()

        response = client.embeddings(
            input_text=request.input,
            model=request.model
        )

        return {
            "code": 200,
            "data": response
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"嵌入请求失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models():
    """获取可用模型列表"""
    try:
        client = get_llm_client()

        # 预定义的模型列表（根据提供商）
        models_map = {
            "deepseek": [
                {"id": "deepseek-chat", "name": "DeepSeek Chat"},
                {"id": "deepseek-coder", "name": "DeepSeek Coder"}
            ],
            "openai": [
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
                {"id": "gpt-4", "name": "GPT-4"},
                {"id": "gpt-4-turbo", "name": "GPT-4 Turbo"}
            ],
            "qwen": [
                {"id": "qwen-turbo", "name": "通义千问 Turbo"},
                {"id": "qwen-plus", "name": "通义千问 Plus"},
                {"id": "qwen-max", "name": "通义千问 Max"}
            ],
            "zhipu": [
                {"id": "glm-4", "name": "GLM-4"},
                {"id": "glm-3-turbo", "name": "GLM-3 Turbo"}
            ]
        }

        models = models_map.get(client.provider, [])

        return {
            "code": 200,
            "data": {
                "provider": client.provider,
                "current_model": client.default_model,
                "available_models": models
            }
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"获取模型列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
