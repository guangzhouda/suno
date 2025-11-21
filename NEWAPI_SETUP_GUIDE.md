# New API 配置和测试指南

## 📋 你需要测试的两个模型

根据 `docs/LLM-reference.md` 文档：

1. **文本对话模型** - `deepseek-ai/DeepSeek-V3`
   - 用于歌词生成、歌词改写等文本创作
   - 端点：`POST /v1/chat/completions`

2. **图像生成模型** - `doubao-seedream-4-0-250828`
   - 用于海报制作、封面设计
   - 端点：`POST /v1/images/generations`

**统一API地址：** `https://api.voct.top`

---

## ⚙️ 配置方法

### 方式1：使用config.json（推荐）

1. **复制配置模板**
   ```bash
   copy config.example.json config.json
   ```

2. **编辑config.json**

   找到 `newapi` 配置节，填入你的API密钥：

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

### 方式2：使用环境变量

#### Windows PowerShell
```powershell
# 设置环境变量（当前会话）
$env:NEWAPI_API_KEY="你的API密钥"
$env:NEWAPI_API_BASE="https://api.voct.top"
$env:TEXT_MODEL="deepseek-ai/DeepSeek-V3"
$env:IMAGE_MODEL="doubao-seedream-4-0-250828"

# 验证设置
echo $env:NEWAPI_API_KEY
```

#### Windows CMD
```cmd
set NEWAPI_API_KEY=你的API密钥
set NEWAPI_API_BASE=https://api.voct.top
set TEXT_MODEL=deepseek-ai/DeepSeek-V3
set IMAGE_MODEL=doubao-seedream-4-0-250828
```

#### Git Bash / Linux / Mac
```bash
export NEWAPI_API_KEY="你的API密钥"
export NEWAPI_API_BASE="https://api.voct.top"
export TEXT_MODEL="deepseek-ai/DeepSeek-V3"
export IMAGE_MODEL="doubao-seedream-4-0-250828"
```

---

## 🧪 运行测试

配置完成后，运行测试脚本：

```bash
python test_newapi_models.py
```

### 预期输出

#### 测试成功示例

```
============================================================
🧪 New API 模型测试工具
============================================================

📋 当前配置：
  API地址: https://api.voct.top
  API密钥: 已配置
  文本模型: deepseek-ai/DeepSeek-V3
  图像模型: doubao-seedream-4-0-250828

============================================================
📝 测试文本模型（DeepSeek-V3）
============================================================
API地址: https://api.voct.top
模型: deepseek-ai/DeepSeek-V3

🔄 发送请求...
POST https://api.voct.top/v1/chat/completions
状态码: 200

✅ 请求成功！

💬 模型回复：
你好！我是DeepSeek-V3，一个由DeepSeek开发的大型语言模型...

📊 Token使用：
  输入: 15
  输出: 45
  总计: 60

============================================================
🖼️ 测试图像生成模型（doubao-seedream）
============================================================
API地址: https://api.voct.top
模型: doubao-seedream-4-0-250828

🔄 发送请求...
POST https://api.voct.top/v1/images/generations
提示词: 一只可爱的小猫坐在窗台上，温暖的阳光照进来，温馨治愈的画风
状态码: 200

✅ 请求成功！

🖼️ 生成的图片URL：
https://example.com/generated-image.png

============================================================
📊 测试总结
============================================================
文本模型 (deepseek-ai/DeepSeek-V3): ✅ 通过
图像模型 (doubao-seedream-4-0-250828): ✅ 通过
============================================================

🎉 所有测试通过！可以正常使用这两个模型。
```

---

## ⚠️ 常见问题

### 问题1：未找到API密钥

**错误信息：**
```
❌ 错误：未找到API密钥配置
```

**解决方法：**
1. 确认已经复制并编辑了 `config.json`
2. 或者在PowerShell中设置了环境变量
3. 检查API密钥是否正确（不包含空格、引号等）

### 问题2：401 Unauthorized

**原因：** API密钥无效或格式错误

**解决方法：**
1. 确认API密钥正确
2. 检查是否需要 `Bearer ` 前缀（测试脚本会自动添加）
3. 联系API提供方确认密钥有效性

### 问题3：网络连接超时

**原因：** 无法访问API服务器

**解决方法：**
1. 检查网络连接
2. 确认API地址正确：`https://api.voct.top`
3. 检查防火墙设置

### 问题4：模型不存在

**错误信息：** `model not found` 或 `404`

**解决方法：**
1. 确认模型名称正确：
   - 文本：`deepseek-ai/DeepSeek-V3`
   - 图像：`doubao-seedream-4-0-250828`
2. 联系API提供方确认模型可用性

---

## 📝 手动测试（使用cURL）

如果你想手动测试API，可以使用以下命令：

### 测试文本模型

```bash
curl -X POST https://api.voct.top/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 你的API密钥" \
  -d '{
    "model": "deepseek-ai/DeepSeek-V3",
    "messages": [
      {"role": "user", "content": "你好"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

### 测试图像模型

```bash
curl -X POST https://api.voct.top/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 你的API密钥" \
  -d '{
    "model": "doubao-seedream-4-0-250828",
    "prompt": "一只可爱的小猫",
    "n": 1,
    "size": "1024x1024"
  }'
```

---

## 🔧 集成到项目

测试通过后，可以将New API集成到LLM模块中：

### 更新modules/clients/llm.py

添加New API客户端：

```python
class NewAPIClient(LLMClient):
    """New API 统一接口客户端（支持文本和图像）"""

    def __init__(self, api_key: str, text_model: str = None, image_model: str = None):
        super().__init__(
            provider="newapi",
            api_key=api_key,
            api_base="https://api.voct.top/v1",
            default_model=text_model or "deepseek-ai/DeepSeek-V3"
        )
        self.image_model = image_model or "doubao-seedream-4-0-250828"

    def generate_image(self, prompt: str, size: str = "1024x1024", **kwargs):
        """生成图像"""
        payload = {
            "model": self.image_model,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "response_format": "url",
            **kwargs
        }

        response = self._post('/images/generations', json=payload)
        return response
```

### 更新config.json

确保newapi配置已启用：

```json
{
  "newapi": {
    "api_key": "你的密钥",
    "api_base": "https://api.voct.top",
    "text_model": "deepseek-ai/DeepSeek-V3",
    "image_model": "doubao-seedream-4-0-250828",
    "enabled": true
  }
}
```

---

## 📚 参考文档

- `docs/LLM-reference.md` - New API完整文档
- `LLM_MODULE_GUIDE.md` - LLM模块使用指南
- `test_newapi_models.py` - 测试脚本源码

---

## 🎯 下一步

1. ✅ 配置API密钥
2. ✅ 运行 `python test_newapi_models.py`
3. ✅ 确认两个模型都能正常工作
4. ✅ 查看响应数据，了解返回格式
5. ✅ 开始集成到你的项目中

---

**最后更新：** 2025-11-20
**测试脚本：** `test_newapi_models.py`
