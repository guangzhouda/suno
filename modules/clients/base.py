"""
API客户端基类
"""

import time
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from fastapi import HTTPException
from loguru import logger


class BaseAPIClient(ABC):
    """API客户端基类"""

    def __init__(self, api_key: str, api_base: str, service_name: str):
        self.api_key = api_key
        self.api_base = api_base.rstrip('/')
        self.service_name = service_name
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """通用请求方法，带重试机制"""
        url = f"{self.api_base}{endpoint}"
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                if response.status_code >= 500 and attempt < max_retries - 1:
                    logger.warning(f"{self.service_name} 请求失败，重试 {attempt + 1}/{max_retries}")
                    time.sleep(2 ** attempt)
                    continue
                logger.error(f"{self.service_name} HTTP错误: {e}")
                raise HTTPException(status_code=response.status_code, detail=str(e))
            except Exception as e:
                logger.error(f"{self.service_name} 请求异常: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        raise HTTPException(status_code=500, detail=f"{self.service_name} 请求失败")

    def _get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """GET请求"""
        return self._request('GET', endpoint, **kwargs)

    def _post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """POST请求"""
        return self._request('POST', endpoint, **kwargs)

    @abstractmethod
    def health_check(self) -> bool:
        """健康检查"""
        pass
