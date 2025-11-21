# Suno AI 音乐创作 - 完整教程

> 从入门到精通，掌握 Suno AI 音乐创作的所有技巧

## 📖 目录

1. [环境准备](#环境准备)
2. [模块一：音乐生成](#模块一音乐生成-suno_generate)
3. [模块二：音乐扩展](#模块二音乐扩展-suno_extend)
4. [模块三：音乐翻唱](#模块三音乐翻唱-suno_cover)
5. [高级技巧](#高级技巧)
6. [完整工作流](#完整工作流)
7. [常见问题](#常见问题)

---

## 环境准备

### 安装依赖

```bash
pip install requests
```

### 配置 API Key

#### 方法1：环境变量（推荐）

```bash
# Windows
set SUNO_API_KEY=your_api_key_here

# Linux/Mac
export SUNO_API_KEY=your_api_key_here

# 或添加到 ~/.bashrc 或 ~/.zshrc
echo 'export SUNO_API_KEY=your_api_key_here' >> ~/.bashrc
source ~/.bashrc
```

#### 方法2：config.json

在项目根目录创建 `config.json`：

```json
{
  "suno": {
    "api_key": "your_api_key_here"
  }
}
```

支持环境变量语法：

```json
{
  "suno": {
    "api_key": "${SUNO_API_KEY}"
  }
}
```

### 验证配置

```python
from modules.clients import suno_generate

try:
    # 测试 API 连接（此处仅导入，实际使用时会自动验证）
    print("✓ API Key 配置成功")
except Exception as e:
    print(f"✗ 配置失败: {e}")
```

---

## 模块一：音乐生成 (suno_generate)

### 基础使用

#### 1. 快速生成（AI 自动创作歌词）

```python
from modules.clients import suno_generate

# 最简单的方式：输入一句话，AI 自动创作
task_id = suno_generate.quick_generate(
    prompt="一首关于春天的轻快民谣",
    model="V5",
    wait=False  # 不等待，立即返回任务ID
)

print(f"任务ID: {task_id}")
```

#### 2. 自定义歌词生成

```python
# 使用自己的歌词创作音乐
lyrics = """
春风吹过田野
花儿开满山坡
蝴蝶在飞舞
歌声在回荡

温暖的阳光
洒在脸庞
这是春天的味道
这是希望的颜色
"""

task_id = suno_generate.custom_generate(
    lyrics=lyrics,
    style="民谣，吉他伴奏，轻快节奏",
    title="春天的田野",
    model="V5"
)
```

#### 3. 纯音乐生成（无人声）

```python
# 生成纯音乐伴奏
task_id = suno_generate.instrumental_generate(
    style="轻柔的钢琴曲，适合下午茶，带有轻微的弦乐背景",
    title="午后时光",
    model="V5"
)
```

### 进阶参数

#### 完整参数使用

```python
task_id = suno_generate.generate_music(
    # 基础参数
    prompt="一首关于夜晚城市的歌",
    custom_mode=True,  # 使用自定义模式
    instrumental=False,  # 是否纯音乐
    model="V5",  # 模型版本

    # 自定义模式参数（custom_mode=True 时必需）
    title="城市夜曲",
    style="电子流行，合成器主导，节奏缓慢",

    # 可选参数
    persona_id=None,  # 人格ID（特定音色）
    negative_tags="嘈杂，混乱",  # 不想要的风格
    vocal_gender="f",  # 人声性别：m/f

    # 权重参数（0-1之间）
    style_weight=0.8,  # 风格权重
    weirdness_constraint=0.3,  # 创意度（越高越独特）
    audio_weight=0.5,  # 音频影响力

    callback_url=None  # 回调URL（可选）
)
```

### 等待任务完成

#### 方式1：使用 wait 参数

```python
# 自动等待完成
task_id = suno_generate.quick_generate(
    prompt="主题",
    wait=True,  # 等待完成
    max_wait_time=300  # 最多等待5分钟
)
```

#### 方式2：手动等待

```python
# 先提交任务
task_id = suno_generate.quick_generate(
    prompt="主题",
    wait=False
)

# 稍后等待
result = suno_generate.wait_for_completion(
    task_id=task_id,
    max_wait_time=300,
    check_interval=10  # 每10秒检查一次
)

print(f"状态: {result['status']}")
print(f"音频: {result['data'][0]['audio_url']}")
```

#### 方式3：轮询查询

```python
import time

task_id = suno_generate.quick_generate(prompt="主题")

while True:
    status = suno_generate.get_task_status(task_id)

    if status['status'] == 'completed':
        print("✓ 生成完成！")
        for item in status['data']:
            print(f"音频: {item['audio_url']}")
            print(f"视频: {item['video_url']}")
        break

    elif status['status'] == 'failed':
        print("✗ 生成失败")
        break

    else:
        print(f"状态: {status['status']}, 进度: {status.get('progress', 0)}%")
        time.sleep(10)
```

### 模型版本选择

```python
# V5（推荐）：最新版本，质量最高
task_id = suno_generate.quick_generate(prompt="主题", model="V5")

# V4_5PLUS：质量很高，生成时间稍长
task_id = suno_generate.quick_generate(prompt="主题", model="V4_5PLUS")

# V4_5：平衡选择，质量和速度都不错
task_id = suno_generate.quick_generate(prompt="主题", model="V4_5")

# V4：标准版本
task_id = suno_generate.quick_generate(prompt="主题", model="V4")

# V3_5：较早版本，兼容性好
task_id = suno_generate.quick_generate(prompt="主题", model="V3_5")
```

### 歌词长度限制

```python
# V3_5/V4：最多 3000 字符
# V4_5/V4_5PLUS/V5：最多 5000 字符

lyrics = "你的歌词内容..."

if len(lyrics) > 5000:
    print("⚠️ 歌词过长，V5 最多支持 5000 字符")
elif len(lyrics) > 3000:
    print("⚠️ 歌词较长，建议使用 V4_5 或更高版本")
else:
    print("✓ 歌词长度合适")
```

---

## 模块二：音乐扩展 (suno_extend)

### 基础使用

#### 1. 简单扩展（使用原参数）

```python
from modules.clients import suno_extend

# 保持原音乐的风格和参数，直接延长
task_id = suno_extend.simple_extend(
    audio_id="e231****-****-****-****-****8cadc7dc",  # 从生成结果获取
    model="V5"
)
```

#### 2. 自定义扩展

```python
# 完全控制扩展参数
task_id = suno_extend.custom_extend(
    audio_id="e231****-****-****-****-****8cadc7dc",
    continue_at=60,  # 从60秒处开始扩展
    style="轻快流行",
    title="夏日回忆 (Extended)",
    prompt="继续轻快的旋律，增加更多欢快的节奏",
    model="V5"
)
```

#### 3. 扩展到指定长度

```python
# 自动计算扩展位置，扩展到目标时长
task_id = suno_extend.extend_to_length(
    audio_id="e231****-****-****-****-****8cadc7dc",
    current_duration=60,  # 当前时长60秒
    target_duration=120,  # 目标时长120秒
    style="轻快流行",
    title="夏日回忆 (Extended)",
    model="V5"
)
```

### 进阶使用

#### 完整参数控制

```python
task_id = suno_extend.extend_music(
    # 必需参数
    audio_id="e231****-****-****-****-****8cadc7dc",
    use_custom_params=True,  # 使用自定义参数
    model="V5",

    # 自定义参数（use_custom_params=True 时必需）
    continue_at=60,  # 扩展起始位置（秒）
    title="Extended Version",
    style="电子流行",

    # 可选参数
    prompt="继续之前的旋律，逐渐加强节奏",
    persona_id=None,
    negative_tags="突兀，不连贯",
    vocal_gender="f",

    # 权重参数
    style_weight=0.7,
    weirdness_constraint=0.2,
    audio_weight=0.8,  # 音频影响力（扩展时建议较高）

    callback_url=None
)
```

#### 扩展位置选择技巧

```python
# 1. 从结尾扩展（最常见）
continue_at = 60  # 如果音乐60秒，从60秒处扩展

# 2. 从中间扩展（重新演绎后半段）
continue_at = 30  # 从30秒处开始重新生成

# 3. 从开头扩展（前奏延长）
continue_at = 10  # 从10秒处重新开始

# 注意：continue_at 必须 > 0 且 < 原音频总时长
```

### 等待扩展完成

```python
# 方式1：使用 wait 参数
task_id = suno_extend.simple_extend(
    audio_id="audio_id",
    wait=True,
    max_wait_time=300
)

# 方式2：手动等待
task_id = suno_extend.simple_extend(audio_id="audio_id")
result = suno_extend.wait_for_completion(task_id, max_wait_time=300)

# 方式3：查询状态
status = suno_extend.get_task_status(task_id)
```

### 多次扩展

```python
# 可以对同一首音乐多次扩展
original_audio_id = "abc123"

# 第一次扩展：60秒 → 120秒
task_1 = suno_extend.simple_extend(original_audio_id)
result_1 = suno_extend.wait_for_completion(task_1)
extended_1_id = result_1['data'][0]['id']

# 第二次扩展：120秒 → 180秒
task_2 = suno_extend.simple_extend(extended_1_id)
result_2 = suno_extend.wait_for_completion(task_2)
```

---

## 模块三：音乐翻唱 (suno_cover)

### 基础使用

#### 1. 本地文件翻唱

```python
from modules.clients import suno_cover

# 上传本地音频文件并改编风格
task_id = suno_cover.cover_from_file(
    file_path="my_song.mp3",  # 本地文件路径
    style="电子流行，合成器主导，节奏感强",
    title="电音版本",
    model="V5"
)
```

#### 2. URL 文件翻唱

```python
# 直接使用网络音频文件
task_id = suno_cover.cover_from_url(
    file_url="https://example.com/song.mp3",
    style="爵士风格，萨克斯主导，慵懒节奏",
    title="爵士版本",
    model="V5"
)
```

#### 3. 带歌词翻唱

```python
# 使用自定义歌词进行翻唱
task_id = suno_cover.cover_with_lyrics(
    file_path="original.mp3",
    lyrics="""
夜晚的城市
霓虹灯闪烁
孤独的人
走在街头
""",
    style="R&B 风格",
    title="R&B 版本",
    vocal_gender="m",  # 男声
    model="V5"
)
```

### 进阶使用

#### 完整参数控制

```python
# 先上传文件
upload_url = suno_cover.upload_file(
    file_path="song.mp3",
    file_name="my_original_song.mp3"
)

# 然后进行翻唱
task_id = suno_cover.cover_music(
    upload_url=upload_url,
    custom_mode=True,  # 使用自定义模式
    instrumental=False,  # 是否纯音乐
    model="V5",

    # 自定义参数
    style="电子流行",
    title="电音版",
    prompt="保持原旋律，增加电子元素",

    # 可选参数
    persona_id=None,
    negative_tags="嘈杂",
    vocal_gender="f",

    # 权重参数
    style_weight=0.7,
    weirdness_constraint=0.3,
    audio_weight=0.9,  # 翻唱时建议较高，保持原曲特征

    callback_url=None
)
```

#### 文件上传方式

```python
# 方式1：上传本地文件
upload_url = suno_cover.upload_file(
    file_path="local_song.mp3",
    file_name="my_song.mp3"
)

# 方式2：使用网络文件
upload_url = suno_cover.upload_from_url(
    file_url="https://example.com/song.mp3",
    file_name="online_song.mp3"
)

# 然后使用 upload_url 进行翻唱
task_id = suno_cover.cover_music(
    upload_url=upload_url,
    style="风格描述",
    title="标题"
)
```

### 音频文件要求

```python
import os
from pydub import AudioSegment

# 检查文件时长
audio = AudioSegment.from_file("song.mp3")
duration_seconds = len(audio) / 1000

if duration_seconds > 120:
    print(f"⚠️ 音频时长 {duration_seconds}秒，超过2分钟限制")
    print("建议：剪辑到2分钟以内")

    # 自动剪辑到2分钟
    trimmed = audio[:120000]  # 前120秒
    trimmed.export("song_trimmed.mp3", format="mp3")
else:
    print(f"✓ 音频时长 {duration_seconds}秒，符合要求")

# 检查文件大小
file_size_mb = os.path.getsize("song.mp3") / (1024 * 1024)
if file_size_mb > 50:
    print(f"⚠️ 文件大小 {file_size_mb:.2f}MB，可能过大")
```

### 风格转换技巧

```python
# 1. 风格对比翻唱
original_style = "民谣"
new_style = "电子舞曲"

# 2. 细节风格描述
style = """
电子流行风格
- 合成器主导
- 强烈的底鼓节奏
- 副歌部分加入 drop
- 保持原曲旋律线
"""

# 3. 参考艺人风格
style = "类似 The Weeknd 的 R&B 风格，电子元素和人声处理"

# 4. 器乐组合
style = "爵士风格，萨克斯和钢琴为主，低音提琴伴奏"
```

---

## 高级技巧

### 技巧1：批量创作

```python
from modules.clients import suno_generate
import json

# 批量创作多首歌
themes = [
    {"prompt": "春天的花园", "style": "民谣"},
    {"prompt": "夏日海滩", "style": "流行"},
    {"prompt": "秋天的落叶", "style": "古风"},
    {"prompt": "冬日雪景", "style": "电子"}
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

# 稍后批量查询
for task in tasks:
    status = suno_generate.get_task_status(task['task_id'])
    print(f"{task['theme']}: {status['status']}")
```

### 技巧2：版本迭代

```python
# 创作同一首歌的多个版本
base_lyrics = "..."

versions = [
    {"name": "温柔版", "style": "轻柔民谣，吉他伴奏", "weirdness": 0.2},
    {"name": "激情版", "style": "摇滚风格，电吉他主导", "weirdness": 0.5},
    {"name": "实验版", "style": "电子实验，独特音效", "weirdness": 0.9}
]

for ver in versions:
    task_id = suno_generate.generate_music(
        prompt=base_lyrics,
        custom_mode=True,
        style=ver['style'],
        title=f"我的歌曲 - {ver['name']}",
        weirdness_constraint=ver['weirdness'],
        model="V5"
    )
    print(f"已创建 {ver['name']}，任务ID: {task_id}")
```

### 技巧3：完整专辑制作

```python
import os
import json

# 创建专辑项目
album_name = "我的第一张专辑"
album_dir = f"outputs/{album_name}"
os.makedirs(album_dir, exist_ok=True)

# 专辑曲目列表
tracks = [
    {"title": "开场曲", "style": "ambient", "duration": 30},
    {"title": "主打歌", "style": "流行", "duration": 180},
    {"title": "慢歌", "style": "民谣", "duration": 240},
    {"title": "尾声", "style": "钢琴独奏", "duration": 60}
]

album_info = {"album": album_name, "tracks": []}

for idx, track in enumerate(tracks, 1):
    print(f"\n=== 制作第 {idx} 首：{track['title']} ===")

    # 生成音乐
    task_id = suno_generate.instrumental_generate(
        style=track['style'],
        title=f"{idx:02d}. {track['title']}",
        model="V5"
    )

    # 等待完成
    result = suno_generate.wait_for_completion(task_id)
    audio_url = result['data'][0]['audio_url']
    audio_id = result['data'][0]['id']

    # 如果需要扩展到指定时长
    if track['duration'] > 60:
        extend_task = suno_extend.extend_to_length(
            audio_id=audio_id,
            current_duration=60,
            target_duration=track['duration'],
            style=track['style'],
            title=f"{track['title']} Extended"
        )
        extend_result = suno_extend.wait_for_completion(extend_task)
        audio_url = extend_result['data'][0]['audio_url']

    # 保存信息
    track_info = {
        "track_number": idx,
        "title": track['title'],
        "style": track['style'],
        "audio_url": audio_url,
        "task_id": task_id
    }
    album_info['tracks'].append(track_info)

    print(f"✓ 完成：{track['title']}")

# 保存专辑信息
with open(f"{album_dir}/album_info.json", "w", encoding="utf-8") as f:
    json.dump(album_info, f, indent=2, ensure_ascii=False)

print(f"\n🎉 专辑《{album_name}》制作完成！")
print(f"信息保存在: {album_dir}/album_info.json")
```

### 技巧4：智能续写

```python
# 根据前一段音乐的风格，智能续写下一段
def smart_continue(audio_id, continue_style):
    """
    智能续写音乐

    Args:
        audio_id: 原音频ID
        continue_style: 续写方向
            - "similar": 保持相同风格
            - "buildup": 逐渐高潮
            - "breakdown": 逐渐平静
            - "change": 风格转换
    """

    style_prompts = {
        "similar": "继续相同的风格和节奏",
        "buildup": "逐渐增强节奏和能量，走向高潮",
        "breakdown": "逐渐放缓节奏，趋于平静",
        "change": "转换到对比的风格，制造惊喜"
    }

    task_id = suno_extend.custom_extend(
        audio_id=audio_id,
        continue_at=60,  # 假设从60秒处续写
        style="根据前段自动匹配",
        title="Continued",
        prompt=style_prompts[continue_style],
        model="V5"
    )

    return task_id

# 使用示例
original_id = "abc123"
buildup_task = smart_continue(original_id, "buildup")
```

### 技巧5：多风格混搭

```python
# 同一首歌，多风格翻唱
original_file = "original_song.mp3"

cover_styles = [
    "电子舞曲 (EDM)",
    "爵士风格",
    "摇滚风格",
    "古典交响乐改编",
    "lo-fi hip hop"
]

cover_tasks = []
for style in cover_styles:
    task_id = suno_cover.cover_from_file(
        file_path=original_file,
        style=style,
        title=f"Original - {style}",
        model="V5"
    )
    cover_tasks.append({"style": style, "task_id": task_id})
    print(f"已提交 {style} 版本")

# 保存任务信息
with open("cover_tasks.json", "w") as f:
    json.dump(cover_tasks, f, indent=2, ensure_ascii=False)
```

---

## 完整工作流

### 工作流1：从概念到成品

```python
from modules.clients import suno_generate, suno_extend, suno_cover
import json
import os

# ===== 第1步：概念设计 =====
print("=== 第1步：概念设计 ===")
project_name = "夏日回忆"
project_dir = f"outputs/{project_name}"
os.makedirs(project_dir, exist_ok=True)

concept = {
    "theme": "夏日海边的美好回忆",
    "mood": "温暖、怀旧、轻快",
    "style": "清新流行",
    "target_duration": 180  # 3分钟
}

# ===== 第2步：创作歌词 =====
print("\n=== 第2步：创作歌词 ===")
lyrics = """
海风轻轻吹过
浪花拍打海岸
阳光洒在脸上
温暖的夏天

我们在海边奔跑
笑声回荡在耳边
这些美好的时光
永远留在心间

夏日夏日
我们的回忆
像海浪一样
永不停息
"""

with open(f"{project_dir}/lyrics.txt", "w", encoding="utf-8") as f:
    f.write(lyrics)

# ===== 第3步：生成原始版本 =====
print("\n=== 第3步：生成原始版本 ===")
gen_task = suno_generate.custom_generate(
    lyrics=lyrics,
    style=concept['style'],
    title=project_name,
    model="V5"
)

print(f"生成任务ID: {gen_task}")
gen_result = suno_generate.wait_for_completion(gen_task, max_wait_time=300)

original_audio_id = gen_result['data'][0]['id']
original_audio_url = gen_result['data'][0]['audio_url']
print(f"✓ 原始版本生成完成")
print(f"Audio ID: {original_audio_id}")

# ===== 第4步：扩展到目标时长 =====
print("\n=== 第4步：扩展到目标时长 ===")
if concept['target_duration'] > 60:
    extend_task = suno_extend.extend_to_length(
        audio_id=original_audio_id,
        current_duration=60,
        target_duration=concept['target_duration'],
        style=concept['style'],
        title=f"{project_name} (Full Version)",
        model="V5"
    )

    extend_result = suno_extend.wait_for_completion(extend_task)
    full_audio_id = extend_result['data'][0]['id']
    full_audio_url = extend_result['data'][0]['audio_url']
    print(f"✓ 完整版本生成完成")
else:
    full_audio_id = original_audio_id
    full_audio_url = original_audio_url

# ===== 第5步：创作多个版本 =====
print("\n=== 第5步：创作多个版本 ===")
# 先下载完整版本到本地（假设已下载）
# 这里假设文件路径
full_version_file = f"{project_dir}/full_version.mp3"

# 创作不同风格的翻唱版本
cover_versions = [
    {"style": "电子流行，合成器主导", "name": "EDM Remix"},
    {"style": "声学版本，吉他伴奏", "name": "Acoustic Version"},
    {"style": "lo-fi hip hop 风格", "name": "Lo-fi Version"}
]

versions_info = []
for ver in cover_versions:
    print(f"创作 {ver['name']}...")
    # cover_task = suno_cover.cover_from_file(
    #     file_path=full_version_file,
    #     style=ver['style'],
    #     title=f"{project_name} - {ver['name']}",
    #     model="V5"
    # )
    # versions_info.append({"name": ver['name'], "task_id": cover_task})

# ===== 第6步：保存项目信息 =====
print("\n=== 第6步：保存项目信息 ===")
project_info = {
    "project_name": project_name,
    "concept": concept,
    "original": {
        "task_id": gen_task,
        "audio_id": original_audio_id,
        "audio_url": original_audio_url
    },
    "full_version": {
        "task_id": extend_task if concept['target_duration'] > 60 else None,
        "audio_id": full_audio_id,
        "audio_url": full_audio_url
    },
    # "versions": versions_info
}

with open(f"{project_dir}/project_info.json", "w", encoding="utf-8") as f:
    json.dump(project_info, f, indent=2, ensure_ascii=False)

print(f"\n🎉 项目《{project_name}》制作完成！")
print(f"项目文件夹: {project_dir}")
```

### 工作流2：音乐改编工作室

```python
def remix_studio(original_file, project_name):
    """
    音乐改编工作室：创作多个混音版本

    Args:
        original_file: 原始音频文件路径
        project_name: 项目名称
    """
    import os
    import json
    from modules.clients import suno_cover

    # 创建项目目录
    project_dir = f"outputs/remix_{project_name}"
    os.makedirs(project_dir, exist_ok=True)

    # 定义混音版本
    remixes = [
        {
            "name": "Club Mix",
            "style": "电子舞曲，强劲底鼓，适合夜店",
            "weirdness": 0.3
        },
        {
            "name": "Chill Mix",
            "style": "lo-fi hip hop，慵懒节奏，适合学习",
            "weirdness": 0.4
        },
        {
            "name": "Acoustic Mix",
            "style": "声学版本，吉他和钢琴，温暖人声",
            "weirdness": 0.2
        },
        {
            "name": "Experimental Mix",
            "style": "实验电子，独特音效，艺术化表达",
            "weirdness": 0.8
        }
    ]

    # 逐个创作
    remix_info = []
    for remix in remixes:
        print(f"\n创作 {remix['name']}...")

        # 上传文件
        upload_url = suno_cover.upload_file(
            file_path=original_file,
            file_name=f"{project_name}_original.mp3"
        )

        # 创作混音
        task_id = suno_cover.cover_music(
            upload_url=upload_url,
            custom_mode=True,
            style=remix['style'],
            title=f"{project_name} - {remix['name']}",
            weirdness_constraint=remix['weirdness'],
            model="V5"
        )

        remix_info.append({
            "name": remix['name'],
            "style": remix['style'],
            "task_id": task_id
        })

        print(f"✓ {remix['name']} 任务已提交")

    # 保存项目信息
    with open(f"{project_dir}/remix_info.json", "w") as f:
        json.dump(remix_info, f, indent=2, ensure_ascii=False)

    print(f"\n🎉 混音项目《{project_name}》创建完成！")
    print(f"共创作 {len(remixes)} 个版本")
    print(f"项目信息: {project_dir}/remix_info.json")

# 使用示例
# remix_studio("my_song.mp3", "Summer Vibes")
```

---

## 常见问题

### Q1: 任务一直在 processing 状态？

**A**: 这是正常现象，音乐生成通常需要 1-3 分钟。

```python
# 建议使用自动等待
result = suno_generate.wait_for_completion(
    task_id,
    max_wait_time=300,  # 最多等待5分钟
    check_interval=10   # 每10秒检查一次
)
```

### Q2: 生成失败（status: failed）？

**可能原因**：
1. API Key 无效或已过期
2. 账户积分不足
3. 参数不合法（如歌词过长）
4. 网络问题

**解决方法**：
```python
try:
    task_id = suno_generate.quick_generate(prompt="测试")
except RuntimeError as e:
    print(f"错误信息: {e}")
    # 检查具体错误原因
```

### Q3: 如何获取 audio_id？

**A**: 从生成任务的结果中获取

```python
result = suno_generate.wait_for_completion(task_id)

# 获取第一个音频的 ID
audio_id = result['data'][0]['id']

# 或获取所有音频的 ID
audio_ids = [item['id'] for item in result['data']]
```

### Q4: 翻唱时提示文件过大？

**A**: 音频文件限制为 2 分钟

```python
from pydub import AudioSegment

# 剪辑音频到2分钟
audio = AudioSegment.from_file("long_song.mp3")
trimmed = audio[:120000]  # 前120秒
trimmed.export("trimmed_song.mp3", format="mp3")

# 使用剪辑后的文件
task_id = suno_cover.cover_from_file("trimmed_song.mp3", ...)
```

### Q5: 如何下载生成的音频？

**A**: 使用 requests 下载

```python
import requests

# 获取音频 URL
status = suno_generate.get_task_status(task_id)
audio_url = status['data'][0]['audio_url']

# 下载
response = requests.get(audio_url)
with open("my_song.mp3", "wb") as f:
    f.write(response.content)

print("✓ 下载完成")
```

### Q6: 模型版本如何选择？

**A**: 推荐使用 V5

| 模型 | 质量 | 速度 | 歌词限制 | 推荐场景 |
|------|------|------|---------|---------|
| V5 | ⭐⭐⭐⭐⭐ | 中等 | 5000字符 | 所有场景（推荐） |
| V4_5PLUS | ⭐⭐⭐⭐⭐ | 较慢 | 5000字符 | 追求最高质量 |
| V4_5 | ⭐⭐⭐⭐ | 快 | 5000字符 | 平衡选择 |
| V4 | ⭐⭐⭐ | 快 | 3000字符 | 兼容旧项目 |
| V3_5 | ⭐⭐⭐ | 最快 | 3000字符 | 快速测试 |

### Q7: 如何保证音乐风格一致？

**A**: 使用相同的 style 参数和较低的 weirdness_constraint

```python
# 创作系列歌曲，保持风格一致
consistent_style = "轻快流行，吉他和钢琴伴奏，温暖人声"

for theme in themes:
    task_id = suno_generate.custom_generate(
        lyrics=theme['lyrics'],
        style=consistent_style,  # 使用相同风格
        title=theme['title'],
        weirdness_constraint=0.2,  # 较低创意度，保持一致
        model="V5"
    )
```

### Q8: 生成的音乐在哪里查看？

**A**:
1. 从返回结果中获取 URL
2. 访问 Suno API 后台
3. 下载到本地

```python
result = suno_generate.wait_for_completion(task_id)

print(f"音频 URL: {result['data'][0]['audio_url']}")
print(f"视频 URL: {result['data'][0]['video_url']}")
print(f"在线播放: {result['data'][0]['video_url']}")
```

### Q9: API 调用次数有限制吗？

**A**: 取决于你的 API Key 套餐

- 建议合理使用，不要频繁提交大量任务
- 批量任务建议间隔提交
- 使用 `wait=False` 提交后统一查询

### Q10: 如何提高生成质量？

**最佳实践**：

1. **详细的风格描述**
```python
# ❌ 不好
style = "流行"

# ✅ 好
style = "清新流行，吉他和钢琴伴奏，女声温柔，节奏轻快适合夏天"
```

2. **使用最新模型**
```python
model = "V5"  # 总是使用最新版本
```

3. **合理的权重参数**
```python
style_weight = 0.8  # 较高，明确风格
weirdness_constraint = 0.3  # 中等，有创意但不过分
audio_weight = 0.5  # 生成时中等，扩展时较高
```

4. **清晰的歌词结构**
```python
lyrics = """
[Verse 1]
第一段歌词...

[Chorus]
副歌部分...

[Verse 2]
第二段歌词...

[Chorus]
副歌重复...

[Bridge]
过渡段...

[Outro]
结尾...
"""
```

---

## 总结

### 三大模块对比

| 功能 | suno_generate | suno_extend | suno_cover |
|------|---------------|-------------|------------|
| **核心功能** | 创作新音乐 | 延长音乐 | 改编风格 |
| **输入** | 歌词/提示词 | 音频ID | 音频文件/URL |
| **输出** | 新音乐 | 延长版音乐 | 翻唱版音乐 |
| **时长** | 固定（通常60秒） | 原时长+新增 | 保持原时长 |
| **典型场景** | 从零创作 | 制作完整版 | 多风格改编 |

### 推荐工作流

1. **创作新歌** → `suno_generate`
2. **延长到完整** → `suno_extend`
3. **创作多版本** → `suno_cover`

### 快速参考

```python
# 生成
from modules.clients import suno_generate
task = suno_generate.quick_generate("主题", wait=True)

# 扩展
from modules.clients import suno_extend
task = suno_extend.simple_extend(audio_id, wait=True)

# 翻唱
from modules.clients import suno_cover
task = suno_cover.cover_from_file("file.mp3", "风格", "标题")
```

---

**祝你音乐创作愉快！🎵**
