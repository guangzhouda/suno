# 豆包AI模块使用指南

本文档介绍四个独立的豆包AI模块，用于音乐创作全流程。

## 📦 模块概览

| 模块 | 文件 | 功能 | 模型 |
|------|------|------|------|
| **文本对话** | `doubao_text.py` | 歌词生成、文本对话 | deepseek-v3-250324 |
| **图像生成** | `doubao_image.py` | 专辑封面、海报生成 | doubao-seedream-4-0-250828 |
| **图像理解** | `doubao_vision.py` | 图片分析、图片成歌 | doubao-seed-1-6-vision-250815 |
| **视频生成** | `doubao_video.py` | 音乐MV、短视频 | doubao-seedance-1-0-pro-250528 |

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install volcengine-python-sdk[ark]
```

### 2. 配置API Key

**方式一：环境变量（推荐）**

```bash
# Windows
set ARK_API_KEY=your_api_key_here

# Linux/Mac
export ARK_API_KEY=your_api_key_here
```

**方式二：配置文件**

在项目根目录创建 `config.json`：

```json
{
  "doubao": {
    "api_key": "${ARK_API_KEY}",
    "models": {
      "text": "deepseek-v3-250324",
      "image": "doubao-seedream-4-0-250828",
      "vision": "doubao-seed-1-6-vision-250815",
      "video": "doubao-seedance-1-0-pro-250528"
    }
  }
}
```

### 3. 测试模块

```bash
# 测试文本模块
python modules/clients/doubao_text.py

# 测试图像模块
python modules/clients/doubao_image.py

# 测试视觉模块
python modules/clients/doubao_vision.py

# 测试视频模块
python modules/clients/doubao_video.py
```

## 📖 详细使用

### 模块1：文本对话（doubao_text.py）

#### 核心功能

```python
from modules.clients import doubao_text

# 1. 快速生成歌词
lyrics = doubao_text.generate_lyrics(
    prompt="夏日海边的回忆",
    style="清新流行",
    mood="温暖怀旧",
    theme="青春回忆",
    language="中文",
    temperature=0.8  # 创造性温度（0-1）
)

# 2. 自定义对话
response = doubao_text.chat(
    messages=[
        {"role": "system", "content": "你是专业作词人"},
        {"role": "user", "content": "如何写好一首摇滚歌词？"}
    ],
    temperature=0.7
)

# 3. 优化歌词
refined_lyrics = doubao_text.refine_lyrics(
    original_lyrics=old_lyrics,
    refinement_request="让副歌更有力量感"
)
```

#### 参数说明

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `prompt` | str | 歌词主题 | 必填 |
| `style` | str | 音乐风格 | "流行" |
| `language` | str | 语言 | "中文" |
| `mood` | str | 情绪 | None |
| `temperature` | float | 创造性（0-1） | 0.7 |

#### 预设风格

```python
# 可用风格
STYLE_TEMPLATES = {
    "流行": "旋律悦耳，朗朗上口",
    "摇滚": "激情澎湃，节奏强烈",
    "民谣": "质朴真诚，故事性强",
    "说唱": "节奏感强，押韵讲究",
    "古风": "典雅诗意，意境悠远",
    "爵士": "复古优雅，低调奢华",
    # ...
}
```

---

### 模块2：图像生成（doubao_image.py）

#### 核心功能

```python
from modules.clients import doubao_image

# 1. 快速生成专辑封面
result = doubao_image.generate_album_cover(
    title="夏日回忆",
    artist="李明",
    style="清新流行",
    mood="温暖怀旧",
    color_scheme="暖色调",
    elements="海边、夕阳、吉他",
    size="1K",
    watermark=False
)
print(f"封面URL: {result['url']}")

# 2. 自定义图像生成
result = doubao_image.generate_image(
    prompt="赛博朋克风格的未来城市，霓虹灯闪烁",
    size="2K",
    watermark=False,
    response_format="url"  # 或 "b64_json"
)

# 3. 根据歌词生成封面
cover = doubao_image.generate_cover_from_lyrics(
    lyrics=my_lyrics,
    style="民谣"
)

# 4. 生成活动海报
poster = doubao_image.generate_poster(
    event_name="夏日音乐节",
    date="2025年7月15日",
    venue="海滨公园",
    artists="多位人气歌手",
    style="青春活力"
)
```

#### 参数说明

| 参数 | 类型 | 可选值 | 说明 |
|------|------|--------|------|
| `size` | str | "2K", "1K", "1024x1024" 等 | 图片尺寸 |
| `watermark` | bool | True/False | 是否添加水印 |
| `response_format` | str | "url", "b64_json" | 返回格式 |

#### 预设色彩方案

```python
COLOR_SCHEMES = {
    "暖色调": "温暖的橙色、黄色、红色渐变",
    "冷色调": "清冷的蓝色、紫色、青色渐变",
    "黑白": "经典黑白灰色调，高对比度",
    "莫兰迪": "莫兰迪色系，低饱和度",
    "赛博朋克": "霓虹粉、电蓝、荧光绿",
    # ...
}
```

---

### 模块3：图像理解（doubao_vision.py）

#### 核心功能

```python
from modules.clients import doubao_vision

# 1. 基础图像理解
description = doubao_vision.understand_image(
    image_url="https://example.com/photo.jpg",
    question="描述这张图片的内容和氛围"
)

# 2. 图片成歌（提取音乐元素）
music_elements = doubao_vision.image_to_music_prompt(
    image_url="https://example.com/photo.jpg"
)
print(f"推荐风格: {music_elements['style']}")
print(f"推荐情绪: {music_elements['emotion']}")
print(f"推荐乐器: {music_elements['instruments']}")

# 3. 生成歌词创作提示
lyrics_prompt = doubao_vision.image_to_lyrics_prompt(
    image_url="https://example.com/photo.jpg"
)

# 4. 识别图片中的物体
objects = doubao_vision.extract_objects(
    image_url="https://example.com/scene.jpg"
)

# 5. 分析色彩方案
palette = doubao_vision.get_color_palette(
    image_url="https://example.com/colorful.jpg"
)
```

#### 返回格式（音乐元素）

```python
{
    "scene": "场景描述",
    "emotion": "情绪",
    "color_tone": "色调",
    "style": "音乐风格",
    "instruments": "推荐乐器",
    "tempo": "节奏",
    "atmosphere": "整体氛围",
    "keywords": "关键意象词"
}
```

---

### 模块4：视频生成（doubao_video.py）

#### 核心功能

```python
from modules.clients import doubao_video

# 1. 快速生成MV
result = doubao_video.generate_mv(
    lyrics="风吹过海面，带走了思念",
    style="抒情流行",
    scene="海边日落",
    mood="温暖怀旧",
    cover_image_url=None,  # 可选：封面图片
    ratio="16:9",
    duration=5
)
print(f"任务ID: {result['task_id']}")

# 2. 文生视频
result = doubao_video.text_to_video(
    prompt="一个女孩站在海边看夕阳，镜头缓缓拉远",
    ratio="16:9",
    duration=5
)

# 3. 图生视频（基于首帧）
result = doubao_video.image_to_video(
    image_url="https://example.com/cover.jpg",
    prompt="女孩睁开眼睛，微笑看向镜头，头发被风吹动",
    ratio="adaptive",
    duration=5
)

# 4. 生成歌词视频
result = doubao_video.generate_lyric_video(
    lyrics_line="风吹过海面，带走了思念",
    style="简约现代",
    background="海洋蓝色渐变",
    animation="文字从下方浮现"
)

# 5. 生成概念视频
result = doubao_video.generate_concept_video(
    concept="时间流逝与记忆消散",
    style="超现实主义",
    color_tone="冷色调",
    camera_movement="镜头缓缓旋转上升"
)
```

#### 参数说明

| 参数 | 类型 | 可选值 | 说明 |
|------|------|--------|------|
| `ratio` | str | "16:9", "9:16", "1:1", "adaptive" | 视频比例 |
| `duration` | int | 5-10 | 时长（秒） |
| `model` | str | pro / pro-fast | 模型版本 |

#### 预设场景模板

```python
SCENE_TEMPLATES = {
    "海边日落": "海边日落场景，温暖的金色阳光...",
    "城市夜景": "现代城市夜景，霓虹灯闪烁...",
    "森林清晨": "森林清晨场景，阳光透过树叶...",
    "星空夜晚": "星空璀璨的夜晚，银河横跨天际...",
    # ...
}
```

---

## 🔗 完整工作流示例

### 场景：从一张图片创作完整音乐作品

```python
from modules.clients import doubao_text, doubao_image, doubao_vision, doubao_video

# 步骤1：分析图片
image_url = "https://example.com/inspiration.jpg"
music_elements = doubao_vision.image_to_music_prompt(image_url)

# 步骤2：生成歌词
lyrics = doubao_text.generate_lyrics(
    prompt=f"根据{music_elements['scene']}场景创作",
    style=music_elements['style'],
    mood=music_elements['emotion']
)

# 步骤3：生成封面
cover = doubao_image.generate_album_cover(
    title="AI音乐作品",
    style=music_elements['style'],
    mood=music_elements['emotion'],
    color_scheme=music_elements['color_tone']
)

# 步骤4：生成MV
mv = doubao_video.generate_mv(
    lyrics=lyrics,
    style=music_elements['style'],
    mood=music_elements['emotion'],
    cover_image_url=cover['url']
)

print(f"✓ 歌词: {len(lyrics)}字")
print(f"✓ 封面: {cover['url']}")
print(f"✓ MV任务: {mv['task_id']}")
```

## 📝 运行示例代码

我们提供了完整的示例文件：

```bash
python examples/doubao_modules_example.py
```

该示例包含7个场景：
1. 生成歌词
2. 生成专辑封面
3. 图片成歌
4. 生成音乐MV
5. 完整工作流
6. 纯文生视频
7. AI对话

## ⚙️ 高级配置

### 自定义模型

```python
# 在函数调用时指定模型
lyrics = doubao_text.chat(
    messages=[...],
    model="deepseek-v3-250324"  # 或其他兼容模型
)

image = doubao_image.generate_image(
    prompt="...",
    model="doubao-seedream-4-0-250828"
)
```

### 传递API Key

```python
# 方式1：使用环境变量（推荐）
lyrics = doubao_text.generate_lyrics(...)

# 方式2：直接传递
lyrics = doubao_text.generate_lyrics(
    prompt="...",
    api_key="your_api_key_here"
)
```

### 温度参数调节

```python
# 低温度（0.3-0.5）：更保守、稳定
lyrics = doubao_text.generate_lyrics(
    prompt="...",
    temperature=0.3  # 适合正式、严肃的歌词
)

# 中温度（0.6-0.8）：平衡
lyrics = doubao_text.generate_lyrics(
    prompt="...",
    temperature=0.7  # 默认值，适合大多数场景
)

# 高温度（0.8-1.0）：更有创造性
lyrics = doubao_text.generate_lyrics(
    prompt="...",
    temperature=0.9  # 适合实验性、艺术化的创作
)
```

## 🐛 常见问题

### Q1: API调用失败

**错误信息**: `RuntimeError: 缺少豆包 API Key！`

**解决方法**:
```bash
# 检查环境变量
echo %ARK_API_KEY%  # Windows
echo $ARK_API_KEY   # Linux/Mac

# 重新设置
set ARK_API_KEY=your_key  # Windows
export ARK_API_KEY=your_key  # Linux/Mac
```

### Q2: 视频生成返回任务ID但看不到结果

**说明**: 视频生成是异步任务，需要等待处理完成。

**解决方法**:
- 任务通常需要几分钟到十几分钟
- 需要通过任务ID查询结果（后续版本会添加查询功能）

### Q3: 图片URL无法访问

**错误信息**: 图像理解或图生视频失败

**解决方法**:
- 确保图片URL是公网可访问的
- 图片格式支持：JPG、PNG等常见格式
- 避免使用本地文件路径

### Q4: 生成结果不理想

**解决方法**:
1. 调整温度参数（temperature）
2. 优化提示词（prompt）
3. 尝试不同的风格参数
4. 使用 `refine_lyrics()` 优化结果

## 📊 性能与成本

### API调用时间（参考）

| 功能 | 平均耗时 | 说明 |
|------|----------|------|
| 文本对话 | 2-5秒 | 取决于生成长度 |
| 图像生成 | 5-15秒 | 取决于图片尺寸 |
| 图像理解 | 3-8秒 | 取决于问题复杂度 |
| 视频生成 | 异步 | 提交后需等待处理 |

### 成本优化建议

1. **复用结果**: 保存生成的内容，避免重复调用
2. **批量处理**: 一次性处理多个任务
3. **选择合适尺寸**: 图片不一定要用2K
4. **使用缓存**: 相同输入可缓存结果

## 🔗 相关资源

- **豆包API文档**: https://www.volcengine.com/docs/ark
- **项目仓库**: E:\Projects\PythonProject
- **示例代码**: examples/doubao_modules_example.py

## 📮 反馈与支持

如有问题或建议，请：
1. 查看项目文档
2. 检查环境配置
3. 查看示例代码
4. 提交Issue

---

**更新日期**: 2025-11-21
**文档版本**: v1.0.0
