# AI 创作平台配置指南

## 📝 配置文件位置

配置文件：`config.json`（项目根目录）

## 🔑 API Key 配置方式

### 方式1：直接在 config.json 中配置（推荐）

编辑 `config.json` 文件：

```json
{
  "newapi": {
    "api_key": "sk-8iPAxpcfZrJs836lMuZuTv65D5Pu49r8zTFICWEbz4Ii0MNe",
    "enabled": true
  },
  "suno": {
    "api_key": "你的Suno API Key",  // ← 在这里填写你的 Suno API key
    "enabled": true
  }
}
```

### 方式2：使用环境变量（可选）

**PowerShell:**
```powershell
$env:NEWAPI_API_KEY="sk-你的key"
$env:SUNO_API_KEY="你的suno key"
python ai_platform.py
```

**Linux/Mac:**
```bash
export NEWAPI_API_KEY="sk-你的key"
export SUNO_API_KEY="你的suno key"
python ai_platform.py
```

## 📍 可用的 API 端点

### 音乐生成 (Suno)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/suno/credits` | GET | 查询积分 |
| `/api/suno/generate` | POST | 生成音乐 |
| `/api/suno/lyrics` | POST | 生成歌词 |
| `/api/suno/extend` | POST | 延长音乐 |

### 图片生成 (New API)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/image/generate` | POST | 生成图片 |

**请求示例：**
```json
{
  "prompt": "一只可爱的猫",
  "size": "1024x1024"
}
```

### 文字处理 (New API - DeepSeek V3)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/text/chat` | POST | AI对话 |

**请求示例：**
```json
{
  "messages": [
    {"role": "user", "content": "你好"}
  ]
}
```

### 系统接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/config/services` | GET | 服务配置 |

## 🐛 常见问题排查

### 1. Suno API 返回 400 错误

**原因：** API key 未配置或配置错误

**解决方法：**
```json
// config.json
{
  "suno": {
    "api_key": "替换成真实的key",  // ← 修改这里
    "enabled": true
  }
}
```

或者暂时禁用：
```json
{
  "suno": {
    "enabled": false  // ← 设置为false
  }
}
```

### 2. 图片生成请求失败重试

**可能原因：**
- 网络连接问题
- API 服务器繁忙（图片生成需要30-120秒）
- 超时设置过短

**查看详细错误：**

重启服务后，新的日志会显示详细的HTTP状态码和响应内容：
```
ImageGen-newapi 请求失败 (状态码: 503, 响应: Service Temporarily Unavailable)
```

**解决方法：**
- 等待几分钟后重试
- 检查网络连接
- 查看日志中的具体错误信息

### 3. 文字处理没有返回

**检查端点路径：**

❌ 错误的路径：
```
POST /api/text-processing/chat
```

✅ 正确的路径：
```
POST /api/text/chat
```

**测试命令：**
```bash
curl -X POST http://localhost:8000/api/text/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "你好"}]}'
```

### 4. 服务启动后网页打不开

**检查服务是否正常运行：**
```bash
# 检查端口占用
netstat -ano | findstr :8000

# 测试API
curl http://localhost:8000/api/health
```

**访问地址：**
- http://localhost:8000
- http://127.0.0.1:8000

**如果端口被占用：**
1. 方式1：修改 config.json 中的端口
   ```json
   {
     "server": {
       "port": 8001  // 改用其他端口
     }
   }
   ```

2. 方式2：杀死占用端口的进程
   ```powershell
   # 查找进程ID
   netstat -ano | findstr :8000

   # 结束进程
   taskkill /PID <进程ID> /F
   ```

## 🧪 测试 API 是否正常

### 测试 New API（文本）

```bash
curl -X POST https://api.voct.top/v1/chat/completions \
  -H "Authorization: Bearer sk-你的key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-ai/DeepSeek-V3",
    "messages": [{"role": "user", "content": "hi"}],
    "max_tokens": 10
  }'
```

### 测试 New API（图片）

```bash
curl -X POST https://api.voct.top/v1/images/generations \
  -H "Authorization: Bearer sk-你的key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seedream-4-0-250828",
    "prompt": "a cat",
    "size": "1024x1024"
  }' \
  --max-time 180
```

**注意：** 图片生成通常需要 30-120 秒

## 📊 查看服务状态

访问健康检查端点：
```bash
curl http://localhost:8000/api/health
```

**返回示例：**
```json
{
  "status": "ok",
  "services": {
    "suno": true,
    "image_generation": true,
    "text_processing": true
  },
  "timestamp": "2025-11-21T09:00:00.000000"
}
```

## 🔍 日志说明

### 正常日志
```
INFO: Uvicorn running on http://0.0.0.0:8000 ✅
INFO: 127.0.0.1:56939 - "GET / HTTP/1.1" 200 OK ✅
```

### 错误日志

**API Key 错误：**
```
ImageGen-newapi HTTP错误: 状态码: 401, 响应: Unauthorized
```
→ 检查 config.json 中的 api_key 配置

**服务器错误：**
```
ImageGen-newapi 请求失败 (状态码: 503)，重试 1/3
```
→ 服务器繁忙，会自动重试

**超时：**
```
ImageGen-newapi 请求超时，重试 1/3
```
→ 网络问题或图片生成时间过长，会自动重试（最多3次）

## 📚 完整配置示例

```json
{
  "newapi": {
    "api_key": "sk-8iPAxpcfZrJs836lMuZuTv65D5Pu49r8zTFICWEbz4Ii0MNe",
    "api_base": "https://api.voct.top",
    "text_model": "deepseek-ai/DeepSeek-V3",
    "image_model": "doubao-seedream-4-0-250828",
    "enabled": true
  },

  "suno": {
    "api_key": "你的Suno API Key",
    "api_base": "https://api.sunoapi.org/api/v1",
    "upload_base": "https://sunoapiorg.redpandaai.co/api",
    "enabled": true
  },

  "image_generation": {
    "provider": "newapi",
    "api_key": "sk-8iPAxpcfZrJs836lMuZuTv65D5Pu49r8zTFICWEbz4Ii0MNe",
    "api_base": "https://api.voct.top/v1",
    "default_model": "doubao-seedream-4-0-250828",
    "enabled": true
  },

  "text_processing": {
    "provider": "newapi",
    "api_key": "sk-8iPAxpcfZrJs836lMuZuTv65D5Pu49r8zTFICWEbz4Ii0MNe",
    "api_base": "https://api.voct.top/v1",
    "default_model": "deepseek-ai/DeepSeek-V3",
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

---

**最后更新：** 2025-11-21
**适用版本：** v2.0.1+
