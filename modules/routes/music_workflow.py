"""
AI音乐创作工作流 - DeepSeek + Suno 集成
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from loguru import logger
import json
import time
from pathlib import Path

from modules.clients.suno import SunoClient
from modules.routes.suno import normalize_suno_task
from config import get_config

router = APIRouter(prefix="/api/music-workflow", tags=["音乐创作工作流"])

# ==================== Pydantic 模型 ====================

class MusicCreationRequest(BaseModel):
    """音乐创作请求"""
    template: str = Field(..., description="使用的模板ID（如：inspiration_songwriting）")
    user_input: str = Field(..., description="用户输入内容")

    # 可选参数（用于特定模板）
    original_lyrics: Optional[str] = Field(None, description="原歌词（改写/续写时使用）")
    mode: Optional[str] = Field(None, description="改写模式（change_theme/change_language等）")
    target_theme: Optional[str] = Field(None, description="目标主题")
    target_language: Optional[str] = Field(None, description="目标语言")
    original_style: Optional[str] = Field(None, description="原风格（风格迁移时使用）")
    target_style: Optional[str] = Field(None, description="目标风格")

    # 生成参数
    auto_generate_music: bool = Field(True, description="是否自动调用Suno生成音乐")
    wait_for_completion: bool = Field(True, description="是否等待Suno完成")

    class Config:
        json_schema_extra = {
            "example": {
                "template": "inspiration_songwriting",
                "user_input": "想写一首关于跨年夜独自在城市街头的歌，有点孤独但也有期待",
                "auto_generate_music": True,
                "wait_for_completion": False
            }
        }


class WorkflowResponse(BaseModel):
    """工作流响应"""
    success: bool
    template_used: str

    # DeepSeek 生成的歌词信息
    lyrics_data: Optional[Dict[str, Any]] = None
    lyrics_text: Optional[str] = None

    # Suno 生成的音乐信息
    music_task_id: Optional[str] = None
    music_data: Optional[Dict[str, Any]] = None

    # 错误信息
    error: Optional[str] = None
    step_failed: Optional[str] = None


# ==================== 工具函数 ====================

def load_prompt_templates() -> Dict[str, Any]:
    """加载 Prompt 模板"""
    template_file = Path("prompt_templates.json")

    if not template_file.exists():
        raise FileNotFoundError("prompt_templates.json 文件不存在")

    with open(template_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_lyrics_text(lyrics_data: Dict[str, Any]) -> str:
    """从 JSON 数据中提取完整歌词文本"""
    lyrics_dict = lyrics_data.get('lyrics', {})

    parts = []
    order = ['intro', 'verse_1', 'pre_chorus', 'chorus', 'verse_2', 'bridge', 'outro']

    for key in order:
        if key in lyrics_dict and lyrics_dict[key]:
            # 添加段落标签
            label_map = {
                'intro': '[前奏]',
                'verse_1': '[主歌1]',
                'pre_chorus': '[预副歌]',
                'chorus': '[副歌]',
                'verse_2': '[主歌2]',
                'bridge': '[桥段]',
                'outro': '[尾声]'
            }
            parts.append(f"{label_map.get(key, f'[{key}]')}\n{lyrics_dict[key]}")

    return '\n\n'.join(parts)


def call_deepseek_with_template(
    template_id: str,
    user_input: str,
    templates: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """使用模板调用 DeepSeek"""
    from modules.clients.llm import NewAPIClient
    from config import get_config

    config = get_config()

    # 检查模板是否存在
    if template_id not in templates['templates']:
        raise HTTPException(
            status_code=400,
            detail=f"模板不存在: {template_id}"
        )

    template = templates['templates'][template_id]

    # 创建 NewAPI 客户端
    api_key = config.get('newapi.api_key')
    text_model = config.get('newapi.text_model', 'deepseek-ai/DeepSeek-V3')

    client = NewAPIClient(api_key=api_key, text_model=text_model)

    # 构建 user prompt
    user_prompt_template = template['user_prompt_template']
    user_prompt = user_prompt_template.format(
        user_input=user_input,
        **kwargs
    )

    # 构建消息
    messages = [
        {"role": "system", "content": template['system_prompt']},
        {"role": "user", "content": user_prompt}
    ]

    # 获取参数
    params = template.get('parameters', {})
    temperature = params.get('temperature', 0.8)
    max_tokens = params.get('max_tokens', 2000)

    logger.info(f"调用 DeepSeek - 模板: {template['name']}, 输入长度: {len(user_input)}")

    # 调用 DeepSeek
    response = client.chat(
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )

    # 提取内容
    content = response['choices'][0]['message']['content']

    # 尝试解析 JSON
    try:
        # 去掉可能的 markdown 代码块标记
        if content.startswith('```'):
            # 找到第一个换行符
            first_newline = content.find('\n')
            # 找到最后的```
            last_triple = content.rfind('```')
            if first_newline > 0 and last_triple > 0:
                content = content[first_newline+1:last_triple].strip()

        lyrics_data = json.loads(content)
        logger.info(f"成功解析歌词 JSON - 标题: {lyrics_data.get('title', '未命名')}")
        return lyrics_data

    except json.JSONDecodeError as e:
        logger.warning(f"DeepSeek 返回内容不是有效JSON，返回原始文本")
        return {
            "title": "生成的歌词",
            "raw_content": content,
            "parse_error": str(e)
        }


def call_suno_generate_music(
    lyrics: str,
    title: str = "AI Generated Song",
    style: str = "流行",
    model: str = "chirp-v3-5",
    make_instrumental: bool = False,
    wait: bool = True,
    client: Optional[SunoClient] = None
) -> Dict[str, Any]:
    """调用 Suno API 生成音乐"""
    from config import get_config

    config = get_config()

    if not config.is_enabled('suno'):
        raise HTTPException(
            status_code=503,
            detail="Suno 服务未启用，请在 config.json 中配置"
        )

    try:
        suno_client = client or SunoClient()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suno 客户端初始化失败: {e}")

    safe_title = title or "AI Generated Song"
    safe_style = style or "流行"

    logger.info(f"调用 Suno 生成音乐 - 标题: {safe_title}, 风格: {safe_style}")

    try:
        task_id = suno_client.generate_music(
            prompt=lyrics or "",
            customMode=True,
            instrumental=make_instrumental,
            model=model or "chirp-v3-5",
            title=safe_title,
            style=safe_style
        )
    except Exception as e:
        logger.error(f"Suno 生成任务创建失败: {e}")
        raise HTTPException(status_code=500, detail=f"Suno 生成失败: {e}")

    if not wait:
        return {
            "task_id": task_id,
            "status": "pending",
            "tracks": [],
            "message": "任务已提交，稍后可查询状态"
        }

    poll_interval = max(int(config.get('server.poll_interval_seconds', 8)), 1)
    max_wait = max(int(config.get('server.max_poll_timeout_seconds', 120)), poll_interval)
    elapsed = 0

    def fetch_status() -> Dict[str, Any]:
        raw = suno_client.get_music_info(task_id)
        return normalize_suno_task(raw)

    try:
        result = fetch_status()
    except Exception as e:
        logger.warning(f"首次获取 Suno 状态失败: {e}")
        result = {"status": "processing", "tracks": [], "message": str(e)}

    while result.get("status") not in ("complete", "error") and elapsed < max_wait:
        time.sleep(poll_interval)
        elapsed += poll_interval
        try:
            result = fetch_status()
        except Exception as e:
            logger.warning(f"轮询 Suno 状态失败: {e}")
            result = {"status": "processing", "tracks": [], "message": str(e)}
            break

    if result.get("status") == "error":
        logger.error(f"Suno 任务 {task_id} 失败: {result.get('error_message')}")

    return {
        "task_id": task_id,
        "status": result.get("status", "processing"),
        "tracks": result.get("tracks", []),
        "message": result.get("message"),
        "raw": result
    }


# ==================== API 端点 ====================

@router.get("/templates")
async def list_templates():
    """获取所有可用的创作模板"""
    try:
        templates = load_prompt_templates()

        # 简化输出，只返回基本信息
        template_list = []
        for template_id, template_data in templates['templates'].items():
            template_list.append({
                "id": template_id,
                "name": template_data['name'],
                "description": template_data['description'],
                "icon": template_data.get('icon', '🎵')
            })

        return {
            "code": 200,
            "data": {
                "version": templates.get('_version', '1.0.0'),
                "templates": template_list
            }
        }
    except Exception as e:
        logger.error(f"获取模板列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_id}")
async def get_template_detail(template_id: str):
    """获取特定模板的详细信息"""
    try:
        templates = load_prompt_templates()

        if template_id not in templates['templates']:
            raise HTTPException(status_code=404, detail=f"模板不存在: {template_id}")

        return {
            "code": 200,
            "data": templates['templates'][template_id]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取模板详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create")
async def create_music_with_workflow(request: MusicCreationRequest):
    """
    完整的AI音乐创作工作流

    流程：
    1. 使用指定模板调用 DeepSeek 生成歌词
    2. （可选）自动调用 Suno API 生成音乐
    3. 返回完整结果
    """
    try:
        # 加载模板
        templates = load_prompt_templates()

        logger.info(f"开始音乐创作工作流 - 模板: {request.template}")

        # 步骤1: 调用 DeepSeek 生成歌词
        try:
            lyrics_data = call_deepseek_with_template(
                template_id=request.template,
                user_input=request.user_input,
                templates=templates,
                original_lyrics=request.original_lyrics or "",
                mode=request.mode or "",
                target_theme=request.target_theme or "",
                target_language=request.target_language or "",
                original_style=request.original_style or "",
                target_style=request.target_style or "",
                keywords=request.user_input,
                user_emotion=request.user_input,
                scene=request.user_input,
                partial_lyrics=request.original_lyrics or "",
                user_requirements=request.user_input
            )
        except Exception as e:
            logger.error(f"DeepSeek 调用失败: {e}")
            return WorkflowResponse(
                success=False,
                template_used=request.template,
                error=f"歌词生成失败: {str(e)}",
                step_failed="deepseek"
            )

        # 提取歌词文本
        lyrics_text = extract_lyrics_text(lyrics_data)

        logger.info(f"歌词生成成功 - 标题: {lyrics_data.get('title', '未命名')}")

        # 步骤2: （可选）调用 Suno 生成音乐
        music_task_id = None
        music_data = None

        if request.auto_generate_music:
            try:
                title = lyrics_data.get('title', 'AI Generated Song')
                style = lyrics_data.get('style', '流行')
                model = lyrics_data.get('recommended_model', 'chirp-v3-5')
                make_instrumental = lyrics_data.get('make_instrumental', False)

                music_result = call_suno_generate_music(
                    lyrics=lyrics_text,
                    title=title,
                    style=style,
                    model=model,
                    make_instrumental=make_instrumental,
                    wait=request.wait_for_completion
                )

                music_task_id = music_result.get('task_id')
                music_data = music_result

                logger.info(f"Suno 任务已提交 - Task ID: {music_task_id}")

            except Exception as e:
                logger.warning(f"Suno 调用失败（歌词已生成）: {e}")
                # Suno 失败不影响歌词返回

        # 返回完整结果
        return WorkflowResponse(
            success=True,
            template_used=request.template,
            lyrics_data=lyrics_data,
            lyrics_text=lyrics_text,
            music_task_id=music_task_id,
            music_data=music_data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"音乐创作工作流失败: {e}")
        return WorkflowResponse(
            success=False,
            template_used=request.template,
            error=str(e),
            step_failed="unknown"
        )


@router.post("/lyrics-only")
async def generate_lyrics_only(request: MusicCreationRequest):
    """
    仅生成歌词（不调用 Suno）
    适用于用户想先看歌词再决定是否生成音乐的场景
    """
    try:
        templates = load_prompt_templates()

        lyrics_data = call_deepseek_with_template(
            template_id=request.template,
            user_input=request.user_input,
            templates=templates,
            original_lyrics=request.original_lyrics or "",
            mode=request.mode or "",
            target_theme=request.target_theme or "",
            target_language=request.target_language or "",
            original_style=request.original_style or "",
            target_style=request.target_style or ""
        )

        lyrics_text = extract_lyrics_text(lyrics_data)

        return {
            "code": 200,
            "data": {
                "lyrics_data": lyrics_data,
                "lyrics_text": lyrics_text,
                "template_used": request.template
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"歌词生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
