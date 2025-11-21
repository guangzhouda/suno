# Suno AI 音乐创作 - 快速入门指南

## ⚡ 30秒配置

```bash
# 1. 确认已安装 requests
pip install requests

# 2. 配置 API Key（三选一）

# 方式1：环境变量（推荐）
set SUNO_API_KEY=your_api_key      # Windows
export SUNO_API_KEY=your_api_key   # Linux/Mac

# 方式2：config.json（项目根目录）
{
  "suno": {
    "api_key": "your_api_key"
  }
}

# 方式3：直接在代码中传递（不推荐）
```

## 🎵 第一首歌（2分钟）

### 最简单的方式

创建文件 `my_first_suno_song.py`：

```python
from modules.clients import suno_generate

# 一句话生成音乐（自动创作歌词）
task_id = suno_generate.quick_generate(
    prompt="一首关于夏天海滩的轻快流行歌",
    wait=True  # 等待生成完成
)

print(f"✓ 生成完成！任务ID: {task_id}")
print("可以在 Suno API 后台查看和下载音频")
```

运行：
```bash
python my_first_suno_song.py
```

## 📚 三大核心模块

| 模块 | 导入 | 核心功能 |
|------|------|---------|
| 🎼 生成 | `from modules.clients import suno_generate` | 创作新音乐 |
| ⏱️ 扩展 | `from modules.clients import suno_extend` | 延长音乐 |
| 🎤 翻唱 | `from modules.clients import suno_cover` | 改编风格 |

## 🔥 常用代码片段

### 1. 快速生成（最简单）

```python
from modules.clients import suno_generate

# AI 自动创作歌词
task_id = suno_generate.quick_generate(
    prompt="写一首关于春天的民谣",
    model="V5",  # V3_5/V4/V4_5/V4_5PLUS/V5
    wait=True    # 等待完成
)
```

### 2. 自定义歌词生成

```python
from modules.clients import suno_generate

# 使用自己的歌词
lyrics = """
春风吹过花园
蝴蝶在飞舞
阳光洒在脸上
温暖的感觉
"""

task_id = suno_generate.custom_generate(
    lyrics=lyrics,
    style="民谣",
    title="春天的花园",
    model="V5"
)
```

### 3. 纯音乐（无人声）

```python
from modules.clients import suno_generate

# 生成纯音乐伴奏
task_id = suno_generate.instrumental_generate(
    style="轻快的爵士钢琴曲，下午茶氛围",
    title="午后咖啡时光",
    model="V5"
)
```

### 4. 延长音乐

```python
from modules.clients import suno_extend

# 使用原参数延长（最简单）
task_id = suno_extend.simple_extend(
    audio_id="e231****-****-****-****-****8cadc7dc",  # 从生成结果获取
    model="V5"
)

# 自定义延长
task_id = suno_extend.custom_extend(
    audio_id="e231****-****-****-****-****8cadc7dc",
    continue_at=60,  # 从60秒处开始延长
    style="轻快流行",
    title="夏日回忆 (Extended)",
    prompt="继续轻快的旋律，增加更多欢快的节奏"
)
```

### 5. 翻唱/改编

```python
from modules.clients import suno_cover

# 上传本地音频并改编
task_id = suno_cover.cover_from_file(
    file_path="my_song.mp3",  # 本地文件（≤2分钟）
    style="电子流行风格，合成器主导",
    title="电音版本",
    model="V5"
)

# 或从 URL 改编
task_id = suno_cover.cover_from_url(
    file_url="https://example.com/song.mp3",
    style="爵士风格",
    title="爵士版本"
)
```

### 6. 查询任务状态

```python
from modules.clients import suno_generate

# 查询任务状态
status = suno_generate.get_task_status(task_id)

print(f"状态: {status.get('status')}")  # pending/processing/completed/failed
print(f"进度: {status.get('progress', 0)}%")

# 如果完成，获取音频链接
if status.get('status') == 'completed':
    audios = status.get('data', [])
    for audio in audios:
        print(f"音频链接: {audio.get('audio_url')}")
        print(f"视频链接: {audio.get('video_url')}")
```

## 🎯 完整流程示例

```python
from modules.clients import suno_generate, suno_extend, suno_cover
import time

# === 第1步：生成原始音乐 ===
print("🎵 生成原始音乐...")
task_id = suno_generate.custom_generate(
    lyrics="""
海风轻轻吹过
浪花拍打海岸
夏天的记忆
永远留在心间
""",
    style="清新流行",
    title="夏日海边",
    model="V5"
)

# 等待完成
result = suno_generate.wait_for_completion(task_id, max_wait_time=300)
audio_id = result['data'][0]['id']
print(f"✓ 生成完成！Audio ID: {audio_id}")

# === 第2步：延长音乐 ===
print("\n⏱️ 延长音乐到更长版本...")
extend_task = suno_extend.simple_extend(
    audio_id=audio_id,
    model="V5",
    wait=True
)
print(f"✓ 延长完成！")

# === 第3步：创作翻唱版本 ===
print("\n🎤 创作电音翻唱版...")
# 假设我们有原音频文件
cover_task = suno_cover.cover_from_file(
    file_path="summer_beach.mp3",  # 从第1步下载的文件
    style="电子舞曲，节奏感强烈",
    title="夏日海边 (EDM Remix)",
    model="V5"
)
print(f"✓ 翻唱完成！")

print("\n🎉 所有任务完成！")
```

## 💡 5个实用技巧

### 1. 记录任务 ID

```python
import json

# 保存任务信息
task_info = {
    "original": task_id_1,
    "extended": task_id_2,
    "cover": task_id_3
}

with open("my_project_tasks.json", "w") as f:
    json.dump(task_info, f, indent=2)
```

### 2. 等待完成并自动查询

```python
# 使用 wait=True 参数
task_id = suno_generate.quick_generate(
    prompt="主题",
    wait=True,  # 自动等待完成
    max_wait_time=300  # 最多等待5分钟
)
```

### 3. 模型版本选择

```python
# V5：最新最好（推荐）
# V4_5PLUS：质量高，速度稍慢
# V4_5：平衡选择
# V4/V3_5：兼容旧项目

task_id = suno_generate.quick_generate(
    prompt="主题",
    model="V5"  # 选择最新版本
)
```

### 4. 歌词长度限制

```python
# V3_5/V4：最多 3000 字符
# V4_5/V4_5PLUS/V5：最多 5000 字符

# 检查歌词长度
lyrics = "你的歌词..."
if len(lyrics) > 5000:
    print("⚠️ 歌词过长，请缩短")
```

### 5. 音频文件限制

```python
# 翻唱功能的音频限制：
# - 最长 2 分钟
# - 支持格式：mp3, wav, flac, ogg

import os

file_path = "my_song.mp3"
file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

if file_size_mb > 50:  # 假设限制为 50MB
    print("⚠️ 文件过大，请压缩或剪辑")
```

## ❓ 常见问题

### 1. API Key 错误

```bash
# 检查环境变量
echo %SUNO_API_KEY%  # Windows
echo $SUNO_API_KEY   # Linux/Mac

# 或在 Python 中检查
import os
print(os.getenv("SUNO_API_KEY"))
```

### 2. 任务失败怎么办？

```python
try:
    task_id = suno_generate.quick_generate(prompt="主题")
except RuntimeError as e:
    print(f"生成失败: {e}")
    # 检查：
    # - API Key 是否正确
    # - 账户积分是否充足
    # - 参数是否合法
```

### 3. 如何下载生成的音频？

```python
# 获取音频 URL
status = suno_generate.get_task_status(task_id)
if status.get('status') == 'completed':
    audio_url = status['data'][0]['audio_url']

    # 使用 requests 下载
    import requests
    response = requests.get(audio_url)
    with open("my_song.mp3", "wb") as f:
        f.write(response.content)
```

### 4. 音频生成时间太长？

- 正常生成时间：1-3 分钟
- 高峰期可能更长
- 使用 `wait=True` 参数自动等待
- 或稍后使用 `get_task_status()` 查询

### 5. 翻唱时音频质量下降？

- 确保原音频质量好（建议 320kbps MP3 或 FLAC）
- 音频时长不超过 2 分钟
- 使用 V5 模型获得最佳质量

## 🚀 运行示例程序

```bash
# 运行综合示例（即将创建）
python examples/suno_music_creator.py

# 查看所有使用场景
```

## 📖 深入学习

- [Suno 完整教程](Suno音乐创作完整教程.md) - 详细讲解所有功能
- [Suno 使用总览](Suno模块使用总览.md) - API 参考文档
- [Suno API 官方文档](https://docs.sunoapi.org) - 官方文档

## 🎯 下一步

1. **运行示例**: 创建自己的第一首歌
2. **尝试延长**: 将生成的音乐延长到更长版本
3. **创作翻唱**: 改编现有音乐的风格
4. **组合使用**: 将三个模块结合使用

## 📞 需要帮助？

查看完整教程或运行示例程序中的交互式创作助手：

```bash
python examples/suno_music_creator.py
# 选择对应的场景进行创作
```

---

**开始你的音乐创作之旅吧！🎵**
