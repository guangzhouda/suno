# Suno AI 音乐创作模块 - 使用总览

> 三个模块，专业音乐创作解决方案

## 📦 模块清单

| 模块文件 | 功能 | 主要函数 |
|---------|------|---------|
| `suno_generate.py` | 音乐生成 | `quick_generate()`, `custom_generate()`, `instrumental_generate()` |
| `suno_extend.py` | 音乐扩展 | `simple_extend()`, `custom_extend()`, `extend_to_length()` |
| `suno_cover.py` | 音乐翻唱 | `cover_from_file()`, `cover_from_url()`, `cover_with_lyrics()` |

## 📚 文档导航

### 🚀 新手入门

| 文档 | 说明 | 阅读时间 |
|------|------|---------|
| [快速入门-5分钟上手](Suno快速入门-5分钟上手.md) | 最快速的入门指南 | 5分钟 |
| [Suno音乐创作完整教程](Suno音乐创作完整教程.md) | 从基础到进阶的完整教程 | 30分钟 |

### 💻 示例程序

| 文件 | 说明 | 运行方式 |
|------|------|---------|
| `suno_music_creator.py` | 完整创作场景示例 | `python examples/suno_music_creator.py` |

## ⚡ 快速开始

### 1. 安装（30秒）

```bash
pip install requests
set SUNO_API_KEY=your_key  # Windows
```

### 2. 第一首歌（2分钟）

```python
from modules.clients import suno_generate

# 一句话生成音乐
task_id = suno_generate.quick_generate(
    prompt="一首关于夏天的轻快流行歌",
    wait=True
)

print("完成！")
```

### 3. 运行示例

```bash
python examples/suno_music_creator.py
```

## 🎯 使用场景

### 场景1: 快速创作
**需求**: 有一个主题，想快速生成一首歌

```python
from modules.clients import suno_generate

# 快速生成（AI 自动创作歌词）
task_id = suno_generate.quick_generate(
    prompt="写一首关于春天花园的民谣",
    model="V5",
    wait=True
)

# 或使用自定义歌词
task_id = suno_generate.custom_generate(
    lyrics="你的歌词...",
    style="民谣",
    title="春天的花园",
    model="V5"
)
```

**推荐文档**: [快速入门](Suno快速入门-5分钟上手.md)

---

### 场景2: 制作完整版
**需求**: 将生成的音乐延长到完整版本

```python
from modules.clients import suno_generate, suno_extend

# 先生成原始版本
task_id = suno_generate.quick_generate(prompt="主题", wait=True)
result = suno_generate.wait_for_completion(task_id)
audio_id = result['data'][0]['id']

# 延长到完整版（保持原风格）
extend_task = suno_extend.simple_extend(
    audio_id=audio_id,
    model="V5",
    wait=True
)

# 或自定义延长
extend_task = suno_extend.custom_extend(
    audio_id=audio_id,
    continue_at=60,  # 从60秒处开始
    style="轻快流行",
    title="完整版",
    prompt="继续轻快的旋律"
)
```

**推荐文档**: [完整教程 - 音乐扩展](Suno音乐创作完整教程.md#模块二音乐扩展-suno_extend)

---

### 场景3: 多风格改编
**需求**: 将一首歌改编成多种风格

```python
from modules.clients import suno_cover

original_file = "my_song.mp3"

# 风格1：电子舞曲版本
edm_task = suno_cover.cover_from_file(
    file_path=original_file,
    style="电子舞曲，强劲节奏",
    title="EDM Remix",
    model="V5"
)

# 风格2：声学版本
acoustic_task = suno_cover.cover_from_file(
    file_path=original_file,
    style="声学版本，吉他伴奏",
    title="Acoustic Version",
    model="V5"
)

# 风格3：爵士版本
jazz_task = suno_cover.cover_from_file(
    file_path=original_file,
    style="爵士风格，萨克斯主导",
    title="Jazz Version",
    model="V5"
)
```

**推荐文档**: [完整教程 - 音乐翻唱](Suno音乐创作完整教程.md#模块三音乐翻唱-suno_cover)

---

### 场景4: 专业制作流程
**需求**: 从概念到成品的完整流程

```python
from modules.clients import suno_generate, suno_extend, suno_cover
import json
import os

# 1. 创建项目
project_name = "我的音乐"
project_dir = f"outputs/{project_name}"
os.makedirs(project_dir, exist_ok=True)

# 2. 生成原始版本
print("生成原始版本...")
gen_task = suno_generate.custom_generate(
    lyrics="你的歌词...",
    style="流行",
    title=project_name,
    model="V5"
)
gen_result = suno_generate.wait_for_completion(gen_task)
audio_id = gen_result['data'][0]['id']

# 3. 延长到完整版
print("延长到完整版...")
extend_task = suno_extend.simple_extend(audio_id, wait=True)
extend_result = suno_extend.wait_for_completion(extend_task)

# 4. 创作多个版本
print("创作多个版本...")
# （假设已下载完整版到本地）
# cover_task = suno_cover.cover_from_file(...)

# 5. 保存项目信息
project_info = {
    "name": project_name,
    "original_task": gen_task,
    "extended_task": extend_task,
    "audio_id": audio_id
}

with open(f"{project_dir}/info.json", "w") as f:
    json.dump(project_info, f, indent=2, ensure_ascii=False)

print("完成！")
```

**推荐文档**: [完整教程 - 完整工作流](Suno音乐创作完整教程.md#完整工作流)

---

### 场景5: 批量创作
**需求**: 一次创作多首歌

```python
from modules.clients import suno_generate
import json

themes = [
    {"prompt": "春天", "style": "民谣"},
    {"prompt": "夏天", "style": "流行"},
    {"prompt": "秋天", "style": "古风"},
    {"prompt": "冬天", "style": "电子"}
]

tasks = []
for theme in themes:
    task_id = suno_generate.custom_generate(
        lyrics=f"关于{theme['prompt']}的歌词...",
        style=theme['style'],
        title=theme['prompt'],
        model="V5"
    )
    tasks.append({"theme": theme['prompt'], "task_id": task_id})

# 保存任务列表
with open("batch_tasks.json", "w") as f:
    json.dump(tasks, f, indent=2, ensure_ascii=False)
```

**推荐文档**: [完整教程 - 批量创作](Suno音乐创作完整教程.md#技巧1批量创作)

---

## 🛠️ 工具函数速查

### 生成模块 (suno_generate.py)

```python
from modules.clients import suno_generate

# 快速生成（AI 自动创作歌词）
task_id = suno_generate.quick_generate(
    prompt="一首关于夏天的歌",
    model="V5",         # V3_5/V4/V4_5/V4_5PLUS/V5
    wait=False,         # 是否等待完成
    max_wait_time=300   # 最大等待时间（秒）
)

# 自定义歌词生成
task_id = suno_generate.custom_generate(
    lyrics="你的歌词内容...",
    style="流行",       # 风格描述
    title="歌曲标题",
    model="V5",
    persona_id=None,    # 人格ID（可选）
    vocal_gender=None,  # 人声性别：m/f（可选）
    wait=False
)

# 纯音乐生成（无人声）
task_id = suno_generate.instrumental_generate(
    style="轻柔的钢琴曲",
    title="纯音乐",
    model="V5",
    wait=False
)

# 完整参数生成
task_id = suno_generate.generate_music(
    prompt="主题或歌词",
    custom_mode=True,           # 是否自定义模式
    instrumental=False,         # 是否纯音乐
    model="V5",
    title="标题",
    style="风格描述",
    persona_id=None,
    negative_tags="不想要的风格",
    vocal_gender="f",           # m/f
    style_weight=0.8,           # 风格权重（0-1）
    weirdness_constraint=0.3,   # 创意度（0-1）
    audio_weight=0.5,           # 音频影响力（0-1）
    callback_url=None
)

# 查询任务状态
status = suno_generate.get_task_status(task_id)

# 等待任务完成
result = suno_generate.wait_for_completion(
    task_id=task_id,
    max_wait_time=300,
    check_interval=10
)
```

### 扩展模块 (suno_extend.py)

```python
from modules.clients import suno_extend

# 简单扩展（使用原参数）
task_id = suno_extend.simple_extend(
    audio_id="音频ID",
    model="V5",
    wait=False,
    max_wait_time=300
)

# 自定义扩展
task_id = suno_extend.custom_extend(
    audio_id="音频ID",
    continue_at=60,     # 扩展起始位置（秒）
    style="轻快流行",
    title="Extended Version",
    prompt="继续轻快的旋律",
    model="V5",
    persona_id=None,
    vocal_gender=None,
    wait=False
)

# 扩展到指定长度
task_id = suno_extend.extend_to_length(
    audio_id="音频ID",
    current_duration=60,    # 当前时长（秒）
    target_duration=120,    # 目标时长（秒）
    style="流行",
    title="Extended",
    model="V5"
)

# 完整参数扩展
task_id = suno_extend.extend_music(
    audio_id="音频ID",
    use_custom_params=True,     # 是否使用自定义参数
    model="V5",
    continue_at=60,
    title="Extended",
    style="风格描述",
    prompt="扩展提示",
    persona_id=None,
    negative_tags=None,
    vocal_gender=None,
    style_weight=0.7,
    weirdness_constraint=0.2,
    audio_weight=0.8,           # 扩展时建议较高
    callback_url=None
)

# 查询任务状态
status = suno_extend.get_task_status(task_id)

# 等待任务完成
result = suno_extend.wait_for_completion(
    task_id=task_id,
    max_wait_time=300,
    check_interval=10
)
```

### 翻唱模块 (suno_cover.py)

```python
from modules.clients import suno_cover

# 本地文件翻唱
task_id = suno_cover.cover_from_file(
    file_path="song.mp3",   # 本地文件路径（≤2分钟）
    style="电子流行",
    title="EDM Remix",
    model="V5",
    wait=False
)

# URL 文件翻唱
task_id = suno_cover.cover_from_url(
    file_url="https://example.com/song.mp3",
    style="爵士风格",
    title="Jazz Version",
    model="V5",
    wait=False
)

# 带歌词翻唱
task_id = suno_cover.cover_with_lyrics(
    file_path="song.mp3",
    lyrics="你的歌词...",
    style="R&B 风格",
    title="R&B Version",
    vocal_gender="m",       # m/f
    model="V5",
    wait=False
)

# 完整参数翻唱
# 1. 先上传文件
upload_url = suno_cover.upload_file(
    file_path="song.mp3",
    file_name="original.mp3"
)
# 或从 URL 上传
upload_url = suno_cover.upload_from_url(
    file_url="https://example.com/song.mp3",
    file_name="original.mp3"
)

# 2. 然后翻唱
task_id = suno_cover.cover_music(
    upload_url=upload_url,
    custom_mode=True,
    instrumental=False,
    model="V5",
    style="风格描述",
    title="标题",
    prompt="翻唱提示",
    persona_id=None,
    negative_tags=None,
    vocal_gender=None,
    style_weight=0.7,
    weirdness_constraint=0.3,
    audio_weight=0.9,       # 翻唱时建议较高
    callback_url=None
)

# 查询任务状态
status = suno_cover.get_task_status(task_id)

# 等待任务完成
result = suno_cover.wait_for_completion(
    task_id=task_id,
    max_wait_time=300,
    check_interval=10
)
```

## 📂 项目结构

```
E:\Projects\PythonProject\
├── modules/clients/              # 模块目录
│   ├── suno_generate.py         # 音乐生成模块
│   ├── suno_extend.py           # 音乐扩展模块
│   └── suno_cover.py            # 音乐翻唱模块
├── examples/                     # 示例程序
│   └── suno_music_creator.py   # 综合示例
├── docs/                         # 文档目录
│   ├── Suno快速入门-5分钟上手.md
│   ├── Suno音乐创作完整教程.md
│   └── Suno模块使用总览.md (本文档)
└── outputs/                      # 输出目录（自动创建）
```

## ❓ 常见问题

### Q: 从哪里开始？
**A**: 阅读 [快速入门](Suno快速入门-5分钟上手.md)，5分钟即可上手

### Q: 想要详细学习所有功能？
**A**: 阅读 [完整教程](Suno音乐创作完整教程.md)

### Q: 有完整的代码示例吗？
**A**: 运行 `python examples/suno_music_creator.py`

### Q: 如何获取 audio_id？
**A**: 从生成任务的结果中获取
```python
result = suno_generate.wait_for_completion(task_id)
audio_id = result['data'][0]['id']
```

### Q: 翻唱时音频有什么限制？
**A**: 最长 2 分钟，支持 mp3/wav/flac/ogg 格式

### Q: 模型版本如何选择？
**A**: 推荐使用 V5（最新最好），或 V4_5PLUS（追求最高质量）

## 🎯 学习路径

### 初学者路径

1. **第1天**: 阅读[快速入门](Suno快速入门-5分钟上手.md)，生成第一首歌
2. **第2天**: 尝试延长音乐到完整版
3. **第3天**: 尝试翻唱功能，创作多个版本
4. **第4天**: 阅读[完整教程](Suno音乐创作完整教程.md)，学习高级技巧
5. **第5天**: 运行示例程序，创作完整项目

### 进阶开发者路径

1. 直接阅读[完整教程](Suno音乐创作完整教程.md)
2. 查阅本文档的 API 速查表
3. 研究示例程序源码
4. 根据需求组合使用各模块

## 🔗 外部资源

- **Suno API 官方文档**: https://docs.sunoapi.org
- **API Key 申请**: https://sunoapi.org

## 💡 使用技巧

1. **任务ID管理**: 记录所有任务ID，便于后续查询
2. **模型选择**: 优先使用 V5，追求质量用 V4_5PLUS
3. **等待策略**: 短任务用 `wait=True`，长任务用轮询
4. **文件准备**: 翻唱前确保音频≤2分钟
5. **风格描述**: 越详细越好，包含乐器、节奏、情绪等

## 🚀 开始创作

选择一个入口：

**最快上手** → [快速入门](Suno快速入门-5分钟上手.md)
**系统学习** → [完整教程](Suno音乐创作完整教程.md)
**直接体验** → `python examples/suno_music_creator.py`

---

## 📊 三大模块对比

| 特性 | suno_generate | suno_extend | suno_cover |
|------|---------------|-------------|------------|
| **用途** | 创作新音乐 | 延长音乐 | 改编风格 |
| **输入** | 歌词/提示词 | 音频ID | 音频文件 |
| **时长控制** | 固定（约60秒） | 可延长 | 保持原长 |
| **创作自由度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **保留原曲** | N/A | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **风格变化** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **典型场景** | 从零创作 | 制作完整版 | 多风格改编 |

## 🎵 推荐工作流

### 标准流程
```
概念设计 → 生成 (generate) → 延长 (extend) → 改编 (cover) → 完成
```

### 快速流程
```
快速生成 (quick_generate) → 下载 → 完成
```

### 改编流程
```
准备音频 → 翻唱 (cover) × N种风格 → 完成
```

---

**祝你创作愉快！🎵**
