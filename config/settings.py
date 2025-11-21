"""
配置管理模块
"""

import os
import json
from typing import Any, Dict
from pathlib import Path
from loguru import logger


class Config:
    """配置管理类"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            logger.warning(f"配置文件 {self.config_path} 不存在，使用环境变量和默认配置")
            return self._load_from_env()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"成功加载配置文件: {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return self._load_from_env()

    def _load_from_env(self) -> Dict[str, Any]:
        """从环境变量加载配置"""
        return {
            "suno": {
                "api_key": os.getenv("SUNO_API_KEY", ""),
                "api_base": "https://api.sunoapi.org/api/v1",
                "upload_base": "https://sunoapiorg.redpandaai.co/api",
                "enabled": bool(os.getenv("SUNO_API_KEY"))
            },
            "llm": {
                "provider": os.getenv("LLM_PROVIDER", "deepseek"),
                "api_key": os.getenv("LLM_API_KEY", ""),
                "api_base": os.getenv("LLM_API_BASE", "https://api.deepseek.com/v1"),
                "default_model": os.getenv("LLM_MODEL", "deepseek-chat"),
                "enabled": bool(os.getenv("LLM_API_KEY"))
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "output_dir": "outputs",
                "max_upload_size_mb": 50,
                "poll_interval_seconds": 8,
                "max_poll_timeout_seconds": 900
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项

        支持点号路径访问，例如: config.get('suno.api_key')
        """
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    def is_enabled(self, service: str) -> bool:
        """检查服务是否启用"""
        return self.get(f"{service}.enabled", False)

    def reload(self):
        """重新加载配置"""
        self.config = self._load_config()
        logger.info("配置已重新加载")


# 全局配置实例
_config_instance = None


def get_config(config_path: str = "config.json") -> Config:
    """获取配置实例（单例模式）"""
    global _config_instance

    if _config_instance is None:
        _config_instance = Config(config_path)

    return _config_instance
