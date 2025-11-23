"""
简易配置读取，避免缺失 config 模块导致路由导入失败。

优先读取项目根的 config.json，支持点号路径访问：
  get("suno.api_key") -> 从 {"suno": {"api_key": ...}} 读取

同时提供 is_enabled 便于检查某模块是否配置。
"""

import json
import os
from pathlib import Path
from typing import Any, Optional

_cached_config = None


class Config:
    """轻量配置容器，支持点号路径访问。"""

    def __init__(self):
        self.data = {}
        config_file = Path("config.json")
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                # 读取失败时保持空配置，避免中断服务
                self.data = {}

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """按点号路径取值，如 suno.api_key。"""
        parts = key.split(".")
        value: Any = self.data
        for p in parts:
            if isinstance(value, dict) and p in value:
                value = value[p]
            else:
                return default
        return value

    def is_enabled(self, section: str) -> bool:
        """粗略判断某配置段是否存在。"""
        if self.get(section) is not None:
            return True
        if self.get(f"{section}.api_key"):
            return True
        return False


def get_config() -> Config:
    """获取全局配置实例（懒加载）。"""
    global _cached_config
    if _cached_config is None:
        _cached_config = Config()
    return _cached_config
