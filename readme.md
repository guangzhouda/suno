# Maono 音乐创作 - 使用指南

## 环境准备
1. 安装依赖（项目根目录）：
   ```bash
   pip install -r requirements.txt
   ```
   关键依赖：fastapi、uvicorn、requests、python-multipart、loguru、pydantic、volcenginesdkarkruntime。

2. 配置 API Key（两选一）：
   - 环境变量：
     ```bash
     set ARK_API_KEY=你的豆包Key
     set SUNO_API_KEY=你的SunoKey
     ```
   - 或编辑 `config.json`：
     ```json
     {
       "doubao": { "api_key": "你的豆包Key" },
       "suno":   { "api_key": "你的SunoKey" }
     }
     ```

## 启动服务
1. 启动后端：
   ```bash
   uvicorn main:app --reload --port 8000
   ```
2. 启动前端静态服务（项目根目录）：
   ```bash
   python -m http.server 5500
   ```
   浏览器打开 `http://127.0.0.1:5500/maono.html`。

## 使用方法
左侧按模式显示表单，右侧展示任务状态/音频/歌词/图片。
- 灵感成歌：输入灵感/歌词，选风格，点“生成”。豆包生成或直接用输入作歌词；标题自动从歌词首行推导并传给 Suno。
- 图片成歌：上传/填写图片 URL，额外要求/风格，点生成。豆包图片→歌词→Suno 生成音乐；标题用豆包或首行推导。
- 音乐续写：选择已保存歌曲自动填 audioId；可填续写提示/风格后生成。
- 翻唱：不填音频 URL 但选已保存歌曲时，自动用本地 mp3 重新上传再翻唱（避免外链失效）；填可下载音频 URL 则直接翻唱。标题/风格必填（有默认）。
- 生成封面/视频：勾选后基于歌词生成封面图或视频（豆包）。
- 已有歌曲生成封面/视频：填“媒体参数/目录名”为 downloads 下的目录名后点击对应按钮。

## 数据与保存
- 生成完成会自动调用 `/api/suno/save` 保存到 `downloads/<歌曲名>`，写入 `meta.json`（含 task_id、audio_id/audio_url、lyrics）。
- `/api/suno/saved` 返回已保存歌曲列表，供续写/翻唱下拉使用。

## 常见问题
- 翻唱报 “Can't fetch the uploaded audio”：选已保存歌曲且不填 URL，走本地上传再翻唱；如用 URL，确保可公网下载且未过期。
- 标题为空：前端会从歌词/提示首行推导；可手动填写。
- 模式表单不显示：强刷（Ctrl+F5）；如仍有问题，查看浏览器控制台报错。
