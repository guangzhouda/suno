"""
New API 集成指南和示例

展示如何在 ai_platform.py 中集成 New API 路由
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# ==================== 第1步：导入路由 ====================
from modules.routes import llm_router, newapi_router, music_workflow_router
from config import get_config

# ==================== 第2步：创建应用 ====================
app = FastAPI(
    title="AI创作平台 - 集成New API",
    description="支持文本对话、图像生成、歌词创作",
    version="2.0.1"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 第3步：注册路由 ====================

# 通用LLM路由（支持多种提供商）
app.include_router(llm_router)

# New API专用路由（文本+图像+歌词）
app.include_router(newapi_router)

# 音乐创作工作流路由（DeepSeek + Suno）
app.include_router(music_workflow_router)

# ==================== 第4步：主页和健康检查 ====================

@app.get("/")
async def index():
    """主页"""
    return {
        "title": "AI创作平台",
        "version": "2.1.0",
        "services": {
            "llm": "通用LLM服务 - /api/llm/*",
            "newapi": "New API服务 - /api/newapi/*",
            "music_workflow": "AI音乐创作工作流 - /api/music-workflow/*"
        },
        "features": [
            "💡 灵感写歌 - DeepSeek分析 + 自动生成歌词",
            "✏️ 歌词改写 - 保留节奏改写主题/语言",
            "🎸 风格迁移 - 将歌词改编为不同风格",
            "📝 续写歌词 - 补全未完成的歌词",
            "⚡ 快速生成 - 关键词快速创作",
            "🌸 情绪疗愈 - 创作治愈系歌曲"
        ],
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    config = get_config()

    services = {
        "newapi": config.is_enabled('newapi'),
        "llm": config.is_enabled('llm'),
        "suno": config.is_enabled('suno')
    }

    return {
        "status": "ok",
        "services": services
    }


# ==================== 第5步：启动服务 ====================

if __name__ == "__main__":
    import uvicorn

    config = get_config()
    host = config.get('server.host', '0.0.0.0')
    port = config.get('server.port', 8000)

    logger.info("="*60)
    logger.info("🚀 启动AI创作平台")
    logger.info("="*60)
    logger.info(f"服务地址: http://{host}:{port}")
    logger.info(f"API文档: http://{host}:{port}/docs")
    logger.info("")
    logger.info("已启用服务：")

    if config.is_enabled('newapi'):
        logger.info(f"  ✅ New API")
        logger.info(f"     - 文本模型: {config.get('newapi.text_model')}")
        logger.info(f"     - 图像模型: {config.get('newapi.image_model')}")

    if config.is_enabled('llm'):
        logger.info(f"  ✅ LLM ({config.get('llm.provider')})")

    if config.is_enabled('suno'):
        logger.info(f"  ✅ Suno 音乐生成")

    logger.info("="*60)

    uvicorn.run(
        "integrate_newapi_guide:app",
        host=host,
        port=port,
        reload=True
    )


# ==================== 使用说明 ====================
"""
## 如何在 ai_platform.py 中集成 New API

### 方法1：最小改动（推荐）

在 ai_platform.py 中只需添加2行代码：

```python
# 1. 导入路由（文件开头）
from modules.routes import llm_router, newapi_router  # ← 添加 newapi_router

# 2. 注册路由（创建app后）
app.include_router(llm_router)
app.include_router(newapi_router)  # ← 添加这一行
```

### 方法2：完整集成（推荐用于生产环境）

参考本文件的完整实现。

### 配置 config.json

确保配置了 newapi 节：

```json
{
  "newapi": {
    "api_key": "你的API密钥",
    "api_base": "https://api.voct.top",
    "text_model": "deepseek-ai/DeepSeek-V3",
    "image_model": "doubao-seedream-4-0-250828",
    "enabled": true
  }
}
```

### API端点说明

集成后可以访问以下端点：

#### 1. 健康检查
GET /api/newapi/health

#### 2. 文本对话
POST /api/newapi/chat
```json
{
  "messages": [
    {"role": "user", "content": "你好"}
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

#### 3. 图像生成
POST /api/newapi/image/generate
```json
{
  "prompt": "一只可爱的小猫",
  "size": "1024x1024",
  "quality": "standard",
  "style": "vivid"
}
```

#### 4. 歌词生成
POST /api/newapi/lyrics/generate
```json
{
  "theme": "跨年前夜的独白",
  "emotion": "治愈",
  "style": "City Pop",
  "language": "zh"
}
```

#### 5. 歌词改写
POST /api/newapi/lyrics/rewrite
```json
{
  "original_lyrics": "原歌词内容...",
  "mode": "change_theme",
  "target_theme": "友情"
}
```

#### 6. 模型列表
GET /api/newapi/models

### 测试命令

```bash
# 启动服务
python integrate_newapi_guide.py

# 或修改 ai_platform.py 后启动
python ai_platform.py

# 访问 API 文档
# http://localhost:8000/docs
```

### cURL测试示例

```bash
# 1. 健康检查
curl http://localhost:8000/api/newapi/health

# 2. 对话测试
curl -X POST http://localhost:8000/api/newapi/chat \\
  -H "Content-Type: application/json" \\
  -d '{
    "messages": [{"role": "user", "content": "你好"}],
    "temperature": 0.7
  }'

# 3. 图像生成
curl -X POST http://localhost:8000/api/newapi/image/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "prompt": "一只可爱的小猫坐在窗台上",
    "size": "1024x1024"
  }'

# 4. 歌词生成
curl -X POST http://localhost:8000/api/newapi/lyrics/generate \\
  -H "Content-Type: application/json" \\
  -d '{
    "theme": "夏日海边",
    "emotion": "治愈",
    "style": "流行",
    "language": "zh"
  }'
```
"""
