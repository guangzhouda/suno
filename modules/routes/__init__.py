"""
API 路由模块

当前暴露 Suno 与 Doubao 路由，满足音乐生成与豆包多模态能力。
"""

from modules.routes import suno  # noqa: F401
from modules.routes import doubao  # noqa: F401
from modules.routes import upload  # noqa: F401

__all__ = ["suno", "doubao", "upload"]
