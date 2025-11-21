# 🎵 AI 音乐创作工作流使用指南

## 🎯 功能概述

完整的 AI 音乐创作系统：**用户输入 → DeepSeek 分析创作 → Suno 生成音乐**

### 工作流程

```
📝 用户灵感/想法
    ↓
🤖 DeepSeek V3 分析意图
    ↓
✍️  生成结构化歌词
    ↓
🎵 Suno API 生成音乐
    ↓
✅ 完整作品
```

### 核心优势

- ✅ **智能分析**：DeepSeek 理解用户意图，提取主题、情绪、风格
- ✅ **专业创作**：6种创作模板，覆盖不同场景
- ✅ **结构化输出**：标准JSON格式，包含完整metadata
- ✅ **一键生成**：自动调用 Suno 生成音乐

---

## 📚 可用的创作模板

### 1. 💡 灵感写歌 (`inspiration_songwriting`)

**适用场景：** 根据灵感、想法、情绪创作全新歌曲

**示例输入：**
```
想写一首关于跨年夜独自在城市街头的歌，有点孤独但也有对新年的期待，适合一个人安静听的那种
```

**输出内容：**
- 歌曲标题
- 主题提取（如：孤独与期待）
- 情绪定义（如：治愈、忧伤）
- 风格推荐（如：民谣、City Pop）
- 完整歌词（Verse-Chorus-Bridge结构）
- 创作思路说明
- 推荐的 Suno 模型

### 2. ✏️ 歌词改写 (`lyrics_rewrite`)

**适用场景：** 保留原歌词结构，改写主题或语言

**改写模式：**
- `change_theme` - 换主题（爱情→友情、都市→乡村）
- `change_language` - 换语言（中英互译，保持韵律）
- `change_style` - 换情绪风格（伤感→欢快）
- `modernize` - 现代化改编（古风→流行）

**示例输入：**
```json
{
  "original_lyrics": "夜色渐深 街灯昏黄...",
  "mode": "change_theme",
  "target_theme": "温暖治愈"
}
```

**核心要求：**
- 保留行数和节奏
- 音节数相近（±2字符）
- 情感自然过渡

### 3. 🎸 风格迁移 (`style_transfer`)

**适用场景：** 将歌词改编为不同音乐风格

**支持风格：**
- 流行（Pop）
- 摇滚（Rock）
- 民谣（Folk）
- 说唱（Hip-hop）
- 电子（EDM）
- 爵士（Jazz）
- 古风（Chinese Traditional）

**示例：** 将民谣歌词改编为摇滚风格

### 4. 📝 续写歌词 (`continue_writing`)

**适用场景：** 根据片段补全完整歌词

**示例输入：**
```
[主歌1]
窗外雨声淅沥
思绪随风飘去
...
```

**系统会：**
1. 分析现有风格和节奏
2. 识别已有结构
3. 补全缺失部分
4. 保持风格一致

### 5. ⚡ 快速生成 (`quick_generation`)

**适用场景：** 关键词快速创作（即兴、灵感闪现）

**示例输入：**
```
夏天、海边、夕阳、吉他、青春
```

**特点：**
- 简洁高效
- 创意优先
- 篇幅适中

### 6. 🌸 情绪疗愈 (`emotional_healing`)

**适用场景：** 创作治愈系歌曲

**适用情境：**
- 失恋治愈
- 压力释放
- 自我和解
- 心灵放松

**特点：**
- 情绪温和
- 画面温馨
- 节奏舒缓（60-90 BPM）
- 传递希望

---

## 🚀 使用方法

### 方式1：API 调用

#### 启动服务

```bash
python integrate_newapi_guide.py
```

#### 查看可用模板

```bash
curl http://localhost:8000/api/music-workflow/templates
```

**响应示例：**
```json
{
  "code": 200,
  "data": {
    "version": "1.0.0",
    "templates": [
      {
        "id": "inspiration_songwriting",
        "name": "灵感写歌",
        "description": "根据用户的灵感、想法或情绪，创作完整歌词",
        "icon": "💡"
      },
      ...
    ]
  }
}
```

#### 创作音乐（完整工作流）

```bash
curl -X POST http://localhost:8000/api/music-workflow/create \
  -H "Content-Type: application/json" \
  -d '{
    "template": "inspiration_songwriting",
    "user_input": "想写一首关于跨年夜的歌",
    "auto_generate_music": true,
    "wait_for_completion": false
  }'
```

**参数说明：**
- `template`: 模板ID
- `user_input`: 用户输入
- `auto_generate_music`: 是否自动调用 Suno（默认 true）
- `wait_for_completion`: 是否等待 Suno 完成（默认 true）

**响应示例：**
```json
{
  "success": true,
  "template_used": "inspiration_songwriting",
  "lyrics_data": {
    "title": "跨年夜的独白",
    "theme": "孤独与期待",
    "emotion": "治愈",
    "style": "City Pop",
    "lyrics": {
      "verse_1": "...",
      "chorus": "...",
      "verse_2": "...",
      "bridge": "..."
    },
    "recommended_model": "chirp-v3-5",
    "reasoning": "根据用户描述的场景..."
  },
  "lyrics_text": "[主歌1]\n...",
  "music_task_id": "suno_task_12345",
  "music_data": {...}
}
```

#### 仅生成歌词（不调用 Suno）

```bash
curl -X POST http://localhost:8000/api/music-workflow/lyrics-only \
  -H "Content-Type: application/json" \
  -d '{
    "template": "quick_generation",
    "user_input": "夏天、海边、吉他"
  }'
```

### 方式2：Python 脚本测试

运行提供的测试脚本：

```bash
python test_music_workflow.py
```

测试脚本会演示所有模板的使用方法。

---

## 🎨 高级用法

### 歌词改写示例

```python
import requests

url = "http://localhost:8000/api/music-workflow/create"

payload = {
    "template": "lyrics_rewrite",
    "user_input": "将这首歌从伤感改为欢快",
    "original_lyrics": """
[主歌1]
窗外雨声不停
心中思念成疾
...
""",
    "mode": "change_style",
    "target_theme": "欢快明亮",
    "auto_generate_music": False
}

response = requests.post(url, json=payload)
result = response.json()

print(result['lyrics_data']['rewritten_lyrics'])
```

### 风格迁移示例

```python
payload = {
    "template": "style_transfer",
    "user_input": "将这首民谣改编为摇滚风格",
    "original_lyrics": "...",
    "original_style": "folk",
    "target_style": "rock",
    "auto_generate_music": True
}
```

---

## 📊 输出格式说明

### DeepSeek 生成的歌词JSON

```json
{
  "title": "歌曲标题",
  "theme": "核心主题",
  "emotion": "主要情绪",
  "style": "音乐风格",
  "tempo": "节奏速度",
  "lyrics": {
    "intro": "前奏描述（可选）",
    "verse_1": "第一段主歌",
    "pre_chorus": "预副歌（可选）",
    "chorus": "副歌",
    "verse_2": "第二段主歌",
    "bridge": "桥段",
    "outro": "尾声（可选）"
  },
  "tags": ["标签1", "标签2"],
  "recommended_model": "chirp-v3-5",
  "make_instrumental": false,
  "reasoning": "创作思路说明"
}
```

### 工作流完整响应

```json
{
  "success": true,
  "template_used": "模板ID",
  "lyrics_data": { /* 上述JSON */ },
  "lyrics_text": "格式化的完整歌词文本",
  "music_task_id": "Suno任务ID",
  "music_data": {
    "task_id": "...",
    "status": "pending",
    ...
  },
  "error": null,
  "step_failed": null
}
```

---

## 🐛 故障排查

### 1. 模板加载失败

**错误：** `prompt_templates.json 文件不存在`

**解决：** 确保项目根目录有 `prompt_templates.json` 文件

### 2. DeepSeek 调用失败

**错误：** `歌词生成失败: API Key错误`

**解决：** 检查 `config.json` 中的 `newapi.api_key` 配置

### 3. JSON 解析失败

DeepSeek 返回的内容可能不是纯JSON（可能包含markdown代码块）

**系统会自动处理：**
- 去掉 ````json` 标记
- 提取纯JSON内容
- 如果仍然失败，返回原始文本

### 4. Suno 调用失败

**当前状态：** Suno 集成待完善（返回模拟数据）

**后续更新：** 需要将 `ai_platform.py` 中的 `SunoClient` 提取到模块中

---

## 🔧 配置说明

### config.json 配置项

```json
{
  "newapi": {
    "api_key": "sk-你的key",
    "api_base": "https://api.voct.top",
    "text_model": "deepseek-ai/DeepSeek-V3",
    "enabled": true
  },
  "suno": {
    "api_key": "你的Suno Key",
    "api_base": "https://api.sunoapi.org/api/v1",
    "enabled": true
  }
}
```

---

## 📈 最佳实践

### 1. 提供详细的用户输入

❌ 不好的输入：
```
写首歌
```

✅ 好的输入：
```
想写一首关于毕业季的歌，回忆大学四年的点滴，有不舍也有对未来的憧憬，
风格偏民谣，适合用吉他弹唱
```

### 2. 选择合适的模板

- 有清晰想法 → `inspiration_songwriting`
- 已有歌词需要改编 → `lyrics_rewrite` 或 `style_transfer`
- 只有片段需要补全 → `continue_writing`
- 快速创作 → `quick_generation`
- 需要疗愈效果 → `emotional_healing`

### 3. 先生成歌词再生成音乐

```python
# 第1步：生成歌词
response = requests.post(url, json={
    "template": "inspiration_songwriting",
    "user_input": "...",
    "auto_generate_music": False  # 先不生成音乐
})

lyrics_data = response.json()['lyrics_data']

# 第2步：查看歌词，决定是否生成音乐
if 满意:
    # 调用 Suno API 生成音乐
    pass
```

---

## 🎯 接下来的任务

### TODO: Suno 集成完善

当前 Suno 调用返回模拟数据，需要：

1. 将 `ai_platform.py` 的 `SunoClient` 提取到 `modules/clients/suno.py`
2. 在 `music_workflow.py` 中导入真实的 `SunoClient`
3. 实现完整的音乐生成流程

### 建议的实现方式

```python
# modules/clients/suno.py
class SunoClient(BaseAPIClient):
    def generate_music(self, lyrics, title, style, model, wait=True):
        # 实现音乐生成逻辑
        pass

# modules/routes/music_workflow.py
from modules.clients.suno import SunoClient

def call_suno_generate_music(...):
    client = SunoClient(...)
    return client.generate_music(...)
```

---

## 📚 相关文档

- [New API 集成总结](NEWAPI_INTEGRATION_SUMMARY.md)
- [配置指南](CONFIGURATION_GUIDE.md)
- [LLM 模块指南](LLM_MODULE_GUIDE.md)

---

**创建日期：** 2025-11-21
**版本：** v1.0.0
**状态：** ✅ 歌词生成完整可用，Suno集成待完善
