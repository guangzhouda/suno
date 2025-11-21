# AI创作平台 v2.0

> 多功能AI服务集成平台 - 支持音乐、图片、视频、文字处理和音频处理

## 📋 目录

- [项目简介](#项目简介)
- [核心特性](#核心特性)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [API接口](#api接口)
- [扩展开发](#扩展开发)

---

## 项目简介

这是一个全新设计的AI创作平台，基于原有的Suno音乐生成功能，扩展支持多种AI服务：

- **🎵 音乐创作** - Suno API（完整功能）
- **🖼️ 图片生成** - Stable Diffusion, DALL-E等
- **🎬 视频生成** - 即梦（JiMeng）等视频生成服务
- **💬 文字处理** - DeepSeek等大语言模型
- **🎙️ 音频处理** - 语音识别、音频增强等

### 架构特点

1. **模块化设计** - 每个AI服务独立封装，易于扩展
2. **统一接口** - 所有服务继承统一的基类
3. **配置驱动** - 通过配置文件灵活启用/禁用服务
4. **现代化UI** - 响应式设计，支持深色/浅色主题
5. **异步任务** - 支持长时间任务的轮询和监控

---

## 核心特性

### 🎵 音乐创作（Suno）

- ✅ 生成音乐（自定义/非自定义模式）
- ✅ 生成歌词
- ✅ 延长音乐
- ✅ 上传并延长
- ✅ 添加乐器/人声
- ✅ 人声分离
- ✅ 生成音乐视频
- ✅ 任务状态查询
- ✅ 自动下载（待实现）

### 🖼️ 图片生成

- 🔄 支持多种图片生成模型
- 🔄 自定义尺寸和参数
- 🔄 负面提示词
- 🔄 批量生成

### 🎬 视频生成

- 🔄 即梦视频生成
- 🔄 自定义时长
- 🔄 多种风格

### 💬 文字处理

- 🔄 对话聊天
- 🔄 文本生成
- 🔄 代码辅助

### 🎙️ 音频处理

- 🔄 语音识别
- 🔄 音频增强
- 🔄 人声分离

> 注: ✅ 表示已实现，🔄 表示框架已就绪，需配置API

---

## 快速开始

### 1. 安装依赖

```bash
# 使用Python 3.10+
python --version

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

复制配置模板并填写API密钥：

```bash
# 复制配置文件
cp config.example.json config.json

# 编辑config.json，填入你的API密钥
```

**最小配置示例（仅Suno）：**

```json
{
  "suno": {
    "api_key": "your-suno-api-key-here",
    "api_base": "https://api.sunoapi.org/api/v1",
    "upload_base": "https://sunoapiorg.redpandaai.co/api",
    "enabled": true
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "output_dir": "outputs",
    "max_upload_size_mb": 50
  }
}
```

### 3. 启动服务

```bash
# 方式1：直接运行
python ai_platform.py

# 方式2：使用uvicorn（推荐，支持热重载）
uvicorn ai_platform:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问Web界面

打开浏览器访问：
- **Web界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health

---

## 配置说明

### 完整配置示例

```json
{
  "_comment": "AI创作平台配置文件",

  "suno": {
    "api_key": "your-suno-api-key",
    "api_base": "https://api.sunoapi.org/api/v1",
    "upload_base": "https://sunoapiorg.redpandaai.co/api",
    "enabled": true
  },

  "image_generation": {
    "provider": "stable-diffusion",
    "api_key": "your-image-api-key",
    "api_base": "https://api.stability.ai/v1",
    "models": ["sd-xl-1.0", "sd-2.1"],
    "default_model": "sd-xl-1.0",
    "enabled": false
  },

  "video_generation": {
    "provider": "jimeng",
    "api_key": "your-jimeng-api-key",
    "api_base": "https://api.jimeng.com/v1",
    "models": ["jimeng-v1", "jimeng-v2"],
    "default_model": "jimeng-v2",
    "enabled": false
  },

  "text_processing": {
    "provider": "deepseek",
    "api_key": "your-deepseek-api-key",
    "api_base": "https://api.deepseek.com/v1",
    "models": ["deepseek-chat", "deepseek-coder"],
    "default_model": "deepseek-chat",
    "enabled": false
  },

  "audio_processing": {
    "provider": "custom",
    "api_key": "your-audio-api-key",
    "api_base": "https://api.audio-process.com/v1",
    "models": ["whisper-large", "audio-enhance-v1"],
    "default_model": "audio-enhance-v1",
    "enabled": false
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
```

### 配置项说明

| 配置项 | 说明 | 必填 |
|--------|------|------|
| `{service}.enabled` | 是否启用该服务 | 是 |
| `{service}.api_key` | API密钥 | 是（如果enabled=true） |
| `{service}.api_base` | API基础URL | 是 |
| `{service}.models` | 支持的模型列表 | 否 |
| `{service}.default_model` | 默认模型 | 否 |
| `server.host` | 服务器监听地址 | 否，默认0.0.0.0 |
| `server.port` | 服务器端口 | 否，默认8000 |
| `server.output_dir` | 输出文件目录 | 否，默认outputs |

---

## API接口

### 健康检查

```bash
GET /api/health
```

**响应示例：**

```json
{
  "status": "ok",
  "services": {
    "suno": true,
    "image_generation": false,
    "video_generation": false,
    "text_processing": false,
    "audio_processing": false
  },
  "timestamp": "2025-11-20T14:30:00"
}
```

### 音乐生成相关

#### 查询积分

```bash
GET /api/suno/credits
```

#### 生成音乐

```bash
POST /api/suno/generate
Content-Type: application/json

{
  "prompt": "一首轻快的流行歌曲",
  "model": "V4_5",
  "custom": false,
  "wait": true
}
```

#### 生成歌词

```bash
POST /api/suno/lyrics
Content-Type: application/json

{
  "prompt": "关于夏天和友谊的歌词",
  "wait": true
}
```

#### 延长音乐

```bash
POST /api/suno/extend
Content-Type: application/json

{
  "audio_id": "xxx",
  "model": "V4_5",
  "default_param": false,
  "wait": true
}
```

#### 查询任务状态

```bash
GET /api/suno/task/{task_id}
```

### 图片生成

```bash
POST /api/image/generate
Content-Type: application/json

{
  "prompt": "一只可爱的猫",
  "size": "1024x1024",
  "negative_prompt": "模糊, 低质量"
}
```

### 视频生成

```bash
POST /api/video/generate
Content-Type: application/json

{
  "prompt": "海边日落",
  "duration": 5
}
```

### 文字处理

```bash
POST /api/text/chat
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "你好"}
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

### 音频处理

```bash
POST /api/audio/process
Content-Type: application/json

{
  "audio_url": "https://example.com/audio.mp3",
  "task_type": "transcribe"
}
```

---

## 扩展开发

### 添加新的AI服务

1. **创建客户端类**

在 `ai_platform.py` 中继承 `BaseAPIClient`：

```python
class NewServiceClient(BaseAPIClient):
    """新服务客户端"""

    def __init__(self):
        if not config.is_enabled('new_service'):
            raise ValueError("新服务未启用")

        api_key = config.get('new_service.api_key')
        api_base = config.get('new_service.api_base')

        super().__init__(api_key, api_base, "NewService")

    def health_check(self) -> bool:
        """健康检查"""
        return True

    def do_something(self, **kwargs) -> Dict[str, Any]:
        """执行某项功能"""
        res = self._post('/endpoint', json=kwargs)
        return res
```

2. **添加Pydantic模型**

```python
class NewServiceRequest(BaseModel):
    param1: str = Field(..., description="参数1")
    param2: int = Field(default=10, description="参数2")
```

3. **添加API路由**

```python
@app.post("/api/newservice/action")
async def new_service_action(request: NewServiceRequest):
    try:
        client = get_new_service_client()
        result = client.do_something(**request.dict())
        return {"code": 200, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

4. **更新配置文件**

在 `config.example.json` 中添加：

```json
{
  "new_service": {
    "api_key": "your-api-key",
    "api_base": "https://api.example.com/v1",
    "enabled": false
  }
}
```

5. **更新前端界面**

在 `templates/index.html` 中添加新的标签页和表单。

---

## 项目结构

```
PythonProject/
├── ai_platform.py          # 主应用程序（新）
├── suno_web_app_modern.py  # 原有Suno应用（保留）
├── config.json             # 配置文件（需手动创建）
├── config.example.json     # 配置模板
├── requirements.txt        # Python依赖
├── templates/              # 前端模板
│   └── index.html         # Web界面
├── outputs/               # 输出文件目录
├── docs/                  # API文档
└── hooks/                 # PyInstaller hooks
```

---

## 常见问题

### Q: 如何只启用Suno服务？

A: 在 `config.json` 中，只将 `suno.enabled` 设置为 `true`，其他服务设置为 `false`。

### Q: 如何添加新的图片生成服务？

A: 修改 `ImageGenerationClient` 类，根据不同的 `provider` 实现不同的API调用逻辑。

### Q: 如何部署到生产环境？

A: 推荐使用Docker容器化部署，或使用 `gunicorn` 作为WSGI服务器：

```bash
gunicorn ai_platform:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Q: 如何启用HTTPS？

A: 建议在前端使用Nginx反向代理，配置SSL证书。

---

## 更新日志

### v2.0.0 (2025-11-20)

- 🎉 全新架构设计
- ✨ 支持多种AI服务集成
- 🎨 现代化Web界面
- 🔧 配置驱动的服务管理
- 📦 模块化API客户端
- 🌓 深色/浅色主题切换

### v1.0.0

- 原有Suno音乐生成功能

---

## 许可证

本项目仅供学习和研究使用。

---

## 联系方式

- 项目仓库: （待添加）
- 问题反馈: GitHub Issues
- 文档更新: 2025-11-20

---

**祝你使用愉快！ 🎉**
