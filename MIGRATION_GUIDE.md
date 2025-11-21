# 迁移指南：从旧版到新版AI平台

## 📊 新旧版本对比

### 文件对比

| 文件 | 旧版 | 新版 | 说明 |
|------|------|------|------|
| 主程序 | `suno_web_app_modern.py` | `ai_platform.py` | 全新架构，支持多AI服务 |
| 配置 | `config.json`（简单） | `config.json`（增强） | 支持多服务配置 |
| 前端 | 内嵌HTML | `templates/index.html` | 独立模板，更易维护 |
| 依赖 | 基础依赖 | 增强依赖 | 添加异步支持等 |

### 功能对比

| 功能 | 旧版 | 新版 |
|------|------|------|
| Suno音乐生成 | ✅ 完整支持 | ✅ 完整支持 |
| 图片生成 | ❌ 不支持 | ✅ 框架支持 |
| 视频生成 | ❌ 不支持 | ✅ 框架支持 |
| 文字处理 | ❌ 不支持 | ✅ 框架支持 |
| 音频处理 | ❌ 不支持 | ✅ 框架支持 |
| 主题切换 | ❌ 仅暗色 | ✅ 深色/浅色 |
| 服务管理 | ❌ 无 | ✅ 配置驱动 |
| API文档 | ✅ FastAPI自动生成 | ✅ FastAPI自动生成 |

---

## 🚀 快速开始

### 1. 保留旧版（推荐）

旧版文件已保留，你可以继续使用：

```bash
# 运行旧版
python suno_web_app_modern.py
```

### 2. 使用新版

#### 方式A：使用启动脚本（推荐）

```bash
# Windows
start_ai_platform.bat

# 自动完成：
# - 检查Python环境
# - 创建/激活虚拟环境
# - 安装依赖
# - 检查配置
# - 启动服务
```

#### 方式B：手动启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置API密钥
cp config.example.json config.json
# 编辑 config.json 填入API密钥

# 3. 启动服务
python ai_platform.py

# 或使用uvicorn（支持热重载）
uvicorn ai_platform:app --reload --host 0.0.0.0 --port 8000
```

---

## ⚙️ 配置迁移

### 旧版配置（简单）

```json
{
  "SUNO_API_KEY": "your-api-key-here"
}
```

### 新版配置（增强）

```json
{
  "suno": {
    "api_key": "your-api-key-here",
    "api_base": "https://api.sunoapi.org/api/v1",
    "upload_base": "https://sunoapiorg.redpandaai.co/api",
    "enabled": true
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

### 自动迁移

如果没有 `config.json`，新版会：
1. 尝试从环境变量 `SUNO_API_KEY` 读取
2. 使用默认配置启动

---

## 🔄 API端点变化

### Suno音乐生成

| 功能 | 旧版端点 | 新版端点 | 变化 |
|------|---------|---------|------|
| 查询积分 | `/api/credits` | `/api/suno/credits` | 添加前缀 |
| 生成音乐 | `/api/generate` | `/api/suno/generate` | 添加前缀 |
| 生成歌词 | `/api/lyrics` | `/api/suno/lyrics` | 添加前缀 |
| 延长音乐 | `/api/extend` | `/api/suno/extend` | 添加前缀 |
| 查询任务 | `/api/task/{task_id}` | `/api/suno/task/{task_id}` | 添加前缀 |

**重要：** 所有Suno相关端点都添加了 `/suno` 前缀，以区分不同服务。

### 新增端点

```
GET  /api/health                  # 健康检查（所有服务）
GET  /api/config/services         # 查看已启用服务

POST /api/image/generate          # 图片生成
POST /api/video/generate          # 视频生成
POST /api/text/chat               # 文字对话
POST /api/audio/process           # 音频处理

POST /api/upload                  # 通用文件上传
```

---

## 💡 使用建议

### 场景1：仅使用Suno音乐生成

**推荐：** 使用新版，配置更灵活

```json
{
  "suno": {
    "api_key": "your-key",
    "enabled": true
  },
  "image_generation": { "enabled": false },
  "video_generation": { "enabled": false },
  "text_processing": { "enabled": false },
  "audio_processing": { "enabled": false }
}
```

### 场景2：需要多种AI服务

**推荐：** 使用新版，逐步启用服务

```json
{
  "suno": { "enabled": true, "api_key": "..." },
  "image_generation": { "enabled": true, "api_key": "..." },
  "text_processing": { "enabled": true, "api_key": "..." }
}
```

### 场景3：开发和测试

**推荐：** 使用 `uvicorn --reload` 模式

```bash
uvicorn ai_platform:app --reload --port 8000
```

- 代码修改后自动重载
- 快速迭代开发

---

## 🎨 前端界面变化

### 旧版

- 单一功能页面
- 仅暗色主题
- 所有功能在一个页面

### 新版

- 多标签页布局
- 深色/浅色主题切换
- 功能分类清晰
- 响应式设计
- 更现代的UI组件

---

## 🔧 扩展开发

### 添加新的AI服务（5步）

1. **在配置中添加服务**

```json
{
  "my_service": {
    "api_key": "xxx",
    "api_base": "https://api.example.com",
    "enabled": true
  }
}
```

2. **创建客户端类**

```python
class MyServiceClient(BaseAPIClient):
    def __init__(self):
        api_key = config.get('my_service.api_key')
        api_base = config.get('my_service.api_base')
        super().__init__(api_key, api_base, "MyService")

    def health_check(self) -> bool:
        return True

    def do_task(self, param: str) -> Dict:
        return self._post('/task', json={'param': param})
```

3. **创建Pydantic模型**

```python
class MyServiceRequest(BaseModel):
    param: str = Field(..., description="参数")
```

4. **添加API路由**

```python
@app.post("/api/myservice/task")
async def my_service_task(request: MyServiceRequest):
    client = get_my_service_client()
    result = client.do_task(request.param)
    return {"code": 200, "data": result}
```

5. **更新前端界面**

在 `templates/index.html` 中添加相应的UI组件。

---

## 📂 项目结构

```
PythonProject/
├── 🆕 ai_platform.py              # 新版主程序
├── 🆕 templates/
│   └── index.html                 # 前端模板
├── 🆕 start_ai_platform.bat       # 启动脚本
├── 🆕 AI_PLATFORM_README.md       # 使用文档
├── 🆕 MIGRATION_GUIDE.md          # 本文档
│
├── 📦 suno_web_app_modern.py      # 旧版程序（保留）
├── 📦 config.example.json         # 配置模板（增强）
├── 📦 requirements.txt            # 依赖清单（更新）
│
├── 📁 docs/                       # API文档
├── 📁 hooks/                      # PyInstaller hooks
├── 📁 outputs/                    # 输出目录
└── 📁 .venv/                      # 虚拟环境
```

---

## ⚠️ 注意事项

### 1. 端口冲突

如果同时运行新旧版本，会出现端口冲突（默认都是8000）。

**解决方法：**

```bash
# 方式1：修改配置文件中的端口
"server": { "port": 8001 }

# 方式2：启动时指定端口
uvicorn ai_platform:app --port 8001
```

### 2. API密钥安全

- ✅ 使用 `config.json`（已在 `.gitignore` 中）
- ✅ 使用环境变量
- ❌ 不要硬编码在代码中
- ❌ 不要提交到Git仓库

### 3. 依赖版本

新版增加了一些依赖：

```
aiohttp>=3.9.1        # 异步HTTP客户端
aiofiles>=23.2.1      # 异步文件操作
Pillow>=10.2.0        # 图片处理
orjson>=3.9.10        # 高性能JSON
loguru>=0.7.2         # 日志库
```

如果出现版本冲突，请查看 `requirements.txt`。

### 4. Python版本

- **最低要求：** Python 3.10+
- **推荐版本：** Python 3.11 或 3.12

---

## 🐛 常见问题

### Q1: 启动时提示找不到模块？

```bash
# 确保已安装所有依赖
pip install -r requirements.txt

# 或重新创建虚拟环境
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Q2: 配置文件不生效？

检查：
1. 文件名是否为 `config.json`（不是 `.example`）
2. JSON格式是否正确（使用JSON验证工具）
3. API密钥是否正确填写
4. `enabled` 字段是否设置为 `true`

### Q3: 某些服务标签页显示为禁用？

这是正常的。只有在配置文件中 `enabled: true` 的服务才会启用。

### Q4: 旧版和新版能同时使用吗？

可以，但需要注意：
- 使用不同端口
- 共享同一个 `outputs/` 目录
- 共享同一份配置（如果使用环境变量）

---

## 📞 获取帮助

- 📖 查看 `AI_PLATFORM_README.md` 了解详细用法
- 📚 查看 `/docs` 目录了解API文档
- 🌐 访问 http://localhost:8000/docs 查看交互式API文档
- 💡 查看代码注释了解实现细节

---

## 🎉 总结

### ✅ 新版优势

1. **模块化架构** - 易于扩展新服务
2. **配置驱动** - 灵活启用/禁用服务
3. **现代化UI** - 更好的用户体验
4. **统一接口** - 所有服务遵循相同的模式
5. **完整文档** - 详细的使用和开发文档

### 🔄 迁移步骤

1. ✅ 保留旧版文件（作为备份）
2. ✅ 复制配置文件并更新格式
3. ✅ 安装新的依赖
4. ✅ 使用启动脚本启动新版
5. ✅ 测试所有功能
6. ✅ 根据需要启用其他AI服务

---

**祝你使用愉快！如有问题，请查看文档或提交Issue。**

最后更新：2025-11-20
