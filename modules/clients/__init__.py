"""
API 客户端模块（精简版）

仅默认导出 SunoClient，避免在无依赖环境下导入 Doubao/LLM。
如需 Doubao/LLM，请在有依赖时显式导入对应模块。
"""

from .suno import SunoClient

__all__ = [
    "SunoClient",
]
