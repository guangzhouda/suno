# 🎵 AI 音乐创作平台 v2.0 - 设计文档

> **创建时间**: 2025-11-21
> **状态**: 🚧 开发中

---

## 📊 技术架构

### API 能力映射

| API | 功能 | 优先级 |
|-----|------|--------|
| **Suno API** | 音乐生成、翻唱、延长、人声处理 | ⭐⭐⭐ 高 |
| **豆包 DeepSeek-V3** | 歌词生成、意图分析 | ⭐⭐⭐ 高 |
| **豆包 图像生成** | 专辑封面设计 | ⭐⭐ 中 |
| **豆包 图像理解** | 图片成歌（分析图片） | ⭐⭐ 中 |
| **豆包 视频生成** | 音乐 MV（优先使用） | ⭐⭐ 中 |

---

## 🏗️ 模块结构

```
modules/
├── clients/
│   ├── suno.py           # ✅ 已完成 - Suno API 客户端
│   ├── doubao.py         # ✅ 已完成 - 豆包 API 客户端
│   ├── base.py           # ✅ 基础客户端
│   └── __init__.py       # ✅ 已更新导出
│
├── routes/
│   ├── music_workflow.py # 🚧 需更新 - 音乐工作流路由
│   ├── suno.py           # ⏳ 待创建 - Suno 专用路由
│   ├── file_upload.py    # ⏳ 待创建 - 文件上传路由
│   └── __init__.py       # 🚧 需更新
│
└── utils/
    ├── audio_processor.py # ⏳ 待创建（可选）
    └── file_handler.py    # ⏳ 待创建 - 文件处理工具
```

---

## 🎨 核心工作流

### 1. 💡 灵感写歌（已有，需增强）

```
用户输入主题/情绪
  ↓
豆包 DeepSeek 生成歌词 ✅
  ↓
Suno 生成音乐 🚧
  ↓
（可选）豆包生成封面 ⏳
  ↓
（可选）豆包生成 MV ⏳
```

### 2. 🎤 AI翻唱（新功能）

```
用户上传音频文件
  ↓
Suno 文件上传 → 获得 URL
  ↓
Suno Cover API 翻唱
  ├─ 改变风格（民谣→摇滚）
  ├─ 改变音色（男声→女声）
  └─ 多语言翻唱
```

### 3. 📷 图片成歌（新功能）

```
用户上传图片
  ↓
文件上传 → 获得图片 URL
  ↓
豆包 Vision API 分析图片
  ├─ 场景识别
  ├─ 情绪提取
  └─ 色彩分析
  ↓
豆包 DeepSeek 生成歌词（基于图片描述）
  ↓
Suno 生成音乐（风格匹配图片氛围）
  ↓
（可选）用原图生成 MV
```

---

## 🔧 API 端点设计

### 统一服务 (ai_platform.py:8000)

```
ai_platform.py (端口 8000)
│
├── /                                    # Web 界面
│
├── /api/music-workflow/*                # 音乐工作流
│   ├── /templates                       # 模板列表
│   ├── /create                          # 完整工作流
│   └── /lyrics-only                     # 仅歌词
│
├── /api/suno/*                          # Suno 音乐服务
│   ├── /generate                        # 生成音乐
│   ├── /cover                           # 翻唱功能 ⭐
│   ├── /extend                          # 延长音乐
│   ├── /separate-vocals                 # 人声分离
│   ├── /add-vocals                      # 添加人声
│   ├── /add-instrumental                # 添加伴奏
│   ├── /to-wav                          # 转WAV
│   ├── /task/{taskId}                   # 任务状态
│   └── /upload                          # 文件上传 ⭐
│
├── /api/doubao/*                        # 豆包 AI 服务
│   ├── /chat                            # 文本对话（歌词）
│   ├── /image/generate                  # 图像生成（封面）
│   ├── /image/understand                # 图像理解 ⭐
│   ├── /video/generate                  # 视频生成（MV）
│   └── /image-to-song                   # 图片成歌 ⭐
│
└── /api/upload/*                        # 文件上传服务
    ├── /audio                           # 音频上传
    └── /image                           # 图片上传
```

---

## 📝 Suno 核心参数

### 音乐生成
```python
{
  "prompt": "文本描述或歌词",
  "customMode": true/false,
  "instrumental": true/false,
  "model": "V5",  # V3_5, V4, V4_5, V4_5PLUS, V5
  "style": "Pop",  # customMode=true 时必需
  "title": "歌曲标题"  # customMode=true 时必需
}
```

### 翻唱功能
```python
{
  "uploadUrl": "音频文件URL",  # ⭐ 需要先上传获得
  "customMode": true,
  "style": "Rock",  # 目标风格
  "title": "新标题",
  "prompt": "新歌词"  # 可选
}
```

---

## ⚙️ 配置文件

```json
{
  "suno": {
    "api_key": "${SUNO_API_KEY}",
    "api_base": "https://api.sunoapi.org/api/v1",
    "default_model": "V5",
    "enabled": true
  },

  "doubao": {
    "api_key": "${ARK_API_KEY}",
    "base_url": "https://ark.cn-beijing.volces.com/api/v3",
    "models": {
      "text": "deepseek-v3-250324",
      "image": "doubao-seedream-4-0-250828",
      "vision": "doubao-seed-1-6-vision-250815",
      "video": "doubao-seedance-1-0-pro-250528"
    },
    "enabled": true
  }
}
```

---

## ✅ 已完成

- [x] 创建 SunoClient (modules/clients/suno.py)
  - [x] 音乐生成
  - [x] 翻唱功能 (upload_cover)
  - [x] 文件上传 (upload_stream, upload_from_url)
  - [x] 延长音乐
  - [x] 人声分离
  - [x] 添加人声/伴奏
  - [x] 歌词生成
  - [x] WAV 转换

- [x] 创建 DoubaoClient (modules/clients/doubao.py)
  - [x] 文本对话 (chat, generate_lyrics)
  - [x] 图像生成 (generate_image)
  - [x] 图像理解 (understand_image)
  - [x] 图片成歌分析 (image_to_song_description)
  - [x] 视频生成 (generate_video, create_music_video)

- [x] 更新客户端导出 (modules/clients/__init__.py)

---

## 🚧 进行中

- [ ] 安装依赖 (volcengine-python-sdk[ark])

---

## ⏳ 待完成

### 高优先级
1. **文件上传路由**
   - `/api/upload/audio` - 音频上传（用于翻唱）
   - `/api/upload/image` - 图片上传（用于图片成歌）
   - 需要处理临时文件和URL返回

2. **Suno 路由**
   - `/api/suno/generate` - 音乐生成
   - `/api/suno/cover` - 翻唱
   - `/api/suno/extend` - 延长
   - `/api/suno/task/{taskId}` - 状态查询

3. **更新音乐工作流**
   - 整合 Suno + Doubao
   - 支持新功能（翻唱、图片成歌）
   - 更新模板配置

4. **整合到 ai_platform.py**
   - 移除 music_workflow_app.py
   - 统一所有路由到一个服务
   - 更新 Web 界面

### 中优先级
5. **Doubao 路由**
   - `/api/doubao/chat` - 文本对话
   - `/api/doubao/image/generate` - 图像生成
   - `/api/doubao/image/understand` - 图像理解
   - `/api/doubao/video/generate` - 视频生成

6. **Web 界面更新**
   - 添加"翻唱"功能入口
   - 添加"图片成歌"功能入口
   - 文件上传组件
   - 任务状态显示

---

## 🎯 接下来的步骤

1. ✅ 等待 volcenginesdkarkruntime 安装完成
2. 创建文件上传路由 (`modules/routes/file_upload.py`)
3. 创建 Suno 路由 (`modules/routes/suno.py`)
4. 更新音乐工作流路由
5. 整合到 ai_platform.py

---

## 📋 关键决策记录

1. **MV 生成优先使用豆包**
   - 豆包视频生成效果更好
   - Suno 的 MV API 效果差

2. **翻唱使用 Suno 上传功能**
   - 不要和 Doubao 的图片上传混淆
   - Suno 有专门的文件上传接口

3. **图片成歌需要独立上传服务**
   - 需要将图片上传到可访问的URL
   - 豆包 Vision API 需要图片 URL

4. **统一服务架构**
   - 移除 music_workflow_app.py
   - 所有功能整合到 ai_platform.py (端口 8000)
   - 简化部署和维护

---

**最后更新**: 2025-11-21
**下次审查**: 开发完成后
