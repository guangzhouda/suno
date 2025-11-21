"""
LLM模块集成示例

这个文件展示了如何在主程序中集成LLM模块
你可以参考这个示例来更新 ai_platform.py
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# ==================== 第1步：导入LLM模块 ====================
from modules.routes import llm_router
from config import get_config

# ==================== 第2步：创建FastAPI应用 ====================
app = FastAPI(
    title="AI创作平台",
    description="集成LLM的多功能AI平台",
    version="2.0.0"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 第3步：注册LLM路由 ====================
# 这是关键的一步！
app.include_router(llm_router)

# ==================== 第4步：添加其他路由 ====================

@app.get("/")
async def index():
    """主页"""
    return {"message": "AI创作平台", "llm_enabled": True}


@app.get("/api/health")
async def health_check():
    """健康检查"""
    config = get_config()

    return {
        "status": "ok",
        "services": {
            "llm": config.is_enabled('llm'),
            "suno": config.is_enabled('suno')
        }
    }


# ==================== 第5步：启动服务 ====================
if __name__ == "__main__":
    import uvicorn

    config = get_config()
    host = config.get('server.host', '0.0.0.0')
    port = config.get('server.port', 8000)

    logger.info(f"启动AI创作平台: http://{host}:{port}")
    logger.info(f"LLM服务: {'已启用' if config.is_enabled('llm') else '未启用'}")
    logger.info(f"API文档: http://{host}:{port}/docs")

    uvicorn.run(
        "integrate_llm_example:app",
        host=host,
        port=port,
        reload=True
    )


# ==================== 集成说明 ====================
"""
要在 ai_platform.py 中集成LLM模块，需要做以下修改：

1. 在文件开头添加导入：
   from modules.routes import llm_router
   from config import get_config

2. 在创建app后，注册路由：
   app.include_router(llm_router)

3. 更新健康检查接口，添加LLM状态：
   services['llm'] = config.is_enabled('llm')

4. 启动时显示LLM状态：
   logger.info(f"LLM服务: {'已启用' if config.is_enabled('llm') else '未启用'}")

完整示例：
"""

# ==================== ai_platform.py 集成代码示例 ====================
"""
# 在 ai_platform.py 的开头添加：
from modules.routes import llm_router

# 在创建app后添加：
app.include_router(llm_router)

# 更新 /api/health 端点：
@app.get("/api/health")
async def health_check():
    services = {}

    # 原有的服务检查...
    if config.is_enabled('suno'):
        try:
            client = get_suno_client()
            services['suno'] = client.health_check()
        except:
            services['suno'] = False

    # 添加LLM服务检查
    if config.is_enabled('llm'):
        try:
            from modules.clients.llm import create_llm_client
            provider = config.get('llm.provider')
            api_key = config.get('llm.api_key')
            api_base = config.get('llm.api_base')
            model = config.get('llm.default_model')

            client = create_llm_client(provider, api_key, api_base, model)
            services['llm'] = client.health_check()
        except:
            services['llm'] = False

    return {
        "status": "ok",
        "services": services,
        "timestamp": datetime.now().isoformat()
    }

# 在主程序启动时添加：
if __name__ == "__main__":
    logger.info(f"LLM服务: {'已启用' if config.is_enabled('llm') else '未启用'}")
    if config.is_enabled('llm'):
        logger.info(f"LLM提供商: {config.get('llm.provider')}")
        logger.info(f"LLM模型: {config.get('llm.default_model')}")
"""
