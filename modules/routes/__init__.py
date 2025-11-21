"""
API路由模块
"""

from loguru import logger

__all__ = []


def _import_router(module_name: str, attr: str, label: str):
    try:
        module = __import__(module_name, fromlist=[attr])
        router = getattr(module, attr)
        __all__.append(attr)
        return router
    except Exception as exc:
        logger.warning(f"{label} 路由加载失败：{exc}")
        return None


llm_router = _import_router("modules.routes.llm", "router", "LLM")
newapi_router = _import_router("modules.routes.newapi", "router", "NewAPI")
music_workflow_router = _import_router("modules.routes.music_workflow", "router", "音乐创作工作流")
suno_router = _import_router("modules.routes.suno", "router", "Suno")
doubao_router = _import_router("modules.routes.doubao", "router", "Doubao")
creative_workflow_router = _import_router("modules.routes.creative_workflow", "router", "创意工作流")
