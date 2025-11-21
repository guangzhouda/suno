# LLM模块使用指南

## 📁 模块结构

```
PythonProject/
├── modules/                    # 业务模块目录
│   ├── __init__.py
│   ├── clients/               # API客户端
│   │   ├── __init__.py
│   │   ├── base.py           # 基础客户端类
│   │   └── llm.py            # LLM客户端 ⭐
│   ├── models/               # Pydantic模型
│   │   ├── __init__.py
│   │   └── llm.py            # LLM请求/响应模型 ⭐
│   └── routes/               # API路由
│       ├── __init__.py
│       └── llm.py            # LLM路由 ⭐
├── config/                    # 配置管理
│   ├── __init__.py
│   └── settings.py           # 配置类 ⭐
└── ai_platform.py            # 主程序
```

---

## 🚀 快速开始

### 1. 配置LLM服务

编辑 `config.json`：

```json
{
  "llm": {
    "provider": "deepseek",
    "api_key": "your-deepseek-api-key",
    "api_base": "https://api.deepseek.com/v1",
    "default_model": "deepseek-chat",
    "enabled": true
  }
}
```

### 2. 在主程序中集成

在 `ai_platform.py` 中添加：

```python
# 导入LLM路由
from modules.routes import llm_router

# 注册路由
app.include_router(llm_router)
```

### 3. 启动服务

```bash
python ai_platform.py

# 访问API文档
# http://localhost:8000/docs
```

---

## 📝 支持的提供商

### 1. DeepSeek（推荐）

```json
{
  "llm": {
    "provider": "deepseek",
    "api_key": "sk-xxx",
    "api_base": "https://api.deepseek.com/v1",
    "default_model": "deepseek-chat",
    "enabled": true
  }
}
```

**可用模型：**
- `deepseek-chat` - 通用对话模型
- `deepseek-coder` - 代码专用模型

### 2. OpenAI

```json
{
  "llm": {
    "provider": "openai",
    "api_key": "sk-xxx",
    "api_base": "https://api.openai.com/v1",
    "default_model": "gpt-3.5-turbo",
    "enabled": true
  }
}
```

**可用模型：**
- `gpt-3.5-turbo` - 快速响应
- `gpt-4` - 更强大的模型
- `gpt-4-turbo` - GPT-4优化版本

### 3. 通义千问（Qwen）

```json
{
  "llm": {
    "provider": "qwen",
    "api_key": "sk-xxx",
    "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "default_model": "qwen-turbo",
    "enabled": true
  }
}
```

**可用模型：**
- `qwen-turbo` - 快速模型
- `qwen-plus` - 增强模型
- `qwen-max` - 最强模型

### 4. 智谱AI（ZhipuAI）

```json
{
  "llm": {
    "provider": "zhipu",
    "api_key": "your-key",
    "api_base": "https://open.bigmodel.cn/api/paas/v4",
    "default_model": "glm-4",
    "enabled": true
  }
}
```

**可用模型：**
- `glm-4` - GLM-4模型
- `glm-3-turbo` - GLM-3 Turbo

---

## 🔌 API端点

### 1. 对话接口

**端点:** `POST /api/llm/chat`

**请求示例:**
```json
{
  "messages": [
    {"role": "system", "content": "你是一个有帮助的AI助手"},
    {"role": "user", "content": "你好，请介绍一下自己"}
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**响应示例:**
```json
{
  "code": 200,
  "data": {
    "choices": [
      {
        "message": {
          "role": "assistant",
          "content": "你好！我是一个AI助手..."
        }
      }
    ],
    "usage": {
      "prompt_tokens": 20,
      "completion_tokens": 50,
      "total_tokens": 70
    }
  }
}
```

### 2. 流式对话

**请求示例:**
```json
{
  "messages": [
    {"role": "user", "content": "讲一个故事"}
  ],
  "stream": true
}
```

**响应:** Server-Sent Events (SSE)流
```
data: {"choices":[{"delta":{"content":"从前"}}]}
data: {"choices":[{"delta":{"content":"有一"}}]}
...
data: [DONE]
```

### 3. 文本补全

**端点:** `POST /api/llm/completion`

**请求示例:**
```json
{
  "prompt": "从前有一座山，山里有座庙，庙里有个",
  "temperature": 0.8,
  "max_tokens": 100
}
```

### 4. 向量嵌入

**端点:** `POST /api/llm/embeddings`

**请求示例:**
```json
{
  "input": "这是一段需要向量化的文本",
  "model": "text-embedding-ada-002"
}
```

### 5. 模型列表

**端点:** `GET /api/llm/models`

**响应示例:**
```json
{
  "code": 200,
  "data": {
    "provider": "deepseek",
    "current_model": "deepseek-chat",
    "available_models": [
      {"id": "deepseek-chat", "name": "DeepSeek Chat"},
      {"id": "deepseek-coder", "name": "DeepSeek Coder"}
    ]
  }
}
```

### 6. 健康检查

**端点:** `GET /api/llm/health`

**响应示例:**
```json
{
  "status": "ok",
  "provider": "deepseek",
  "model": "deepseek-chat"
}
```

---

## 💻 代码示例

### Python调用示例

```python
import requests

# 对话示例
response = requests.post('http://localhost:8000/api/llm/chat', json={
    "messages": [
        {"role": "user", "content": "你好"}
    ],
    "temperature": 0.7,
    "max_tokens": 2000
})

result = response.json()
print(result['data']['choices'][0]['message']['content'])
```

### JavaScript调用示例

```javascript
// 对话示例
async function chat(message) {
    const response = await fetch('http://localhost:8000/api/llm/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            messages: [{role: 'user', content: message}],
            temperature: 0.7,
            max_tokens: 2000
        })
    });

    const result = await response.json();
    return result.data.choices[0].message.content;
}

// 流式对话示例
async function chatStream(message) {
    const response = await fetch('http://localhost:8000/api/llm/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            messages: [{role: 'user', content: message}],
            stream: true
        })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const {done, value} = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = line.slice(6);
                if (data === '[DONE]') return;

                const json = JSON.parse(data);
                const content = json.choices[0]?.delta?.content;
                if (content) {
                    console.log(content);  // 实时输出
                }
            }
        }
    }
}
```

### cURL调用示例

```bash
# 对话
curl -X POST http://localhost:8000/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好"}],
    "temperature": 0.7,
    "max_tokens": 2000
  }'

# 流式对话
curl -X POST http://localhost:8000/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "讲个故事"}],
    "stream": true
  }'
```

---

## 🔧 高级用法

### 1. 直接使用LLM客户端

```python
from modules.clients.llm import create_llm_client

# 创建客户端
client = create_llm_client(
    provider="deepseek",
    api_key="your-api-key",
    model="deepseek-chat"
)

# 对话
response = client.chat(
    messages=[
        {"role": "user", "content": "你好"}
    ],
    temperature=0.7,
    max_tokens=2000
)

print(response)
```

### 2. 流式输出

```python
# 流式对话
for chunk in client.chat_stream(
    messages=[{"role": "user", "content": "讲个故事"}],
    temperature=0.8
):
    content = chunk['choices'][0]['delta'].get('content', '')
    print(content, end='', flush=True)
```

### 3. 添加自定义提供商

```python
from modules.clients.llm import LLMClient

# 创建自定义客户端
custom_client = LLMClient(
    provider="custom",
    api_key="your-key",
    api_base="https://api.custom.com/v1",
    default_model="custom-model"
)

# 使用
response = custom_client.chat(...)
```

---

## 🎨 前端集成

前端代码已在 `templates/index.html` 的"文字处理"标签页中实现。

关键代码：
```javascript
// 发送消息
async function sendMessage(event) {
    event.preventDefault();
    const message = document.getElementById('text-message').value;

    chatMessages.push({role: 'user', content: message});
    updateChatDisplay();

    const response = await fetch('/api/llm/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({messages: chatMessages})
    });

    const data = await response.json();
    const reply = data.data.choices[0].message.content;

    chatMessages.push({role: 'assistant', content: reply});
    updateChatDisplay();
}
```

---

## 📊 性能优化

### 1. 连接池

客户端使用 `requests.Session()` 实现连接复用：
```python
self.session = requests.Session()
```

### 2. 错误重试

自动重试机制（最多3次）：
```python
for attempt in range(max_retries):
    try:
        response = self.session.request(...)
        return response.json()
    except:
        time.sleep(2 ** attempt)  # 指数退避
```

### 3. 流式输出

减少首字延迟：
```python
response = client.chat(messages=..., stream=True)
```

---

## 🛠️ 故障排查

### 问题1：服务未启用

**错误:** `503: LLM服务未启用`

**解决:**
```json
{
  "llm": {
    "enabled": true  // ← 确保设置为true
  }
}
```

### 问题2：API密钥错误

**错误:** `401: Unauthorized`

**解决:** 检查API密钥是否正确配置

### 问题3：模型不存在

**错误:** `400: Model not found`

**解决:** 检查模型名称是否正确

---

## 📚 参考资料

- [DeepSeek API文档](https://platform.deepseek.com/docs)
- [OpenAI API文档](https://platform.openai.com/docs)
- [通义千问API文档](https://help.aliyun.com/zh/dashscope/)
- [智谱AI API文档](https://open.bigmodel.cn/dev/api)

---

**最后更新:** 2025-11-20
**文档版本:** v1.0.0
