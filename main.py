"""
轻量后端入口：仅挂载 Suno 基础接口，供 maono.html 调用。

运行前准备：
1) 安装依赖：
   pip install fastapi uvicorn requests python-multipart loguru pydantic
   # 或使用已有 requirements：pip install -r .history/requirements.txt
2) 配置 Suno API Key（两选一）：
   - 环境变量：set SUNO_API_KEY=你的key
   - config.json 中写入：
       {
         "suno": { "api_key": "你的key" }
       }
3) 启动：
   uvicorn main:app --reload --port 8000
4) 前端：
   运行静态服务（避免 file:// 产生跨域/无法访问），例如：
   python -m http.server 5500
   打开 http://127.0.0.1:5500/maono.html
   后端默认 http://127.0.0.1:8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.routes import suno as suno_routes
from modules.routes import doubao as doubao_routes
from modules.routes import upload as upload_routes

app = FastAPI(title="Maono Suno API")

# 如需跨域访问，可放开下方配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(suno_routes.router)
app.include_router(doubao_routes.router)
app.include_router(upload_routes.router)


@app.get("/")
async def root():
    return {"status": "ok", "service": "maono-suno-backend"}
