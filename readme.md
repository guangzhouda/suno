
# Suno API 命令行 Demo（Python 3.10+）

一个覆盖核心功能的命令行示例，支持自由选择要执行的功能：  
- 查询积分  
- 生成 **歌词**（并等待完成）  
- 生成 **音乐**（支持自定义/非自定义、可自动下载 MP3 & 封面）  
- **延长**音乐（两种模式）  
- **上传并延长**音乐（`upload-extend`）  
- **添加乐器**（为上传音频生成伴奏）  
- **添加人声**（为上传器乐生成主唱）  
- **时间戳歌词**（同步获取对齐词）  
- **风格增强**（同步生成风格描述/标签）  
- 生成 **MP4** 音乐视频（可下载）  
- **人声/伴奏分离**（可下载分离后的音频）  
- 转 **WAV**（可下载）  
- 生成 **音乐封面**（并查询封面详情，可下载图片）  
- **替换音乐分区**（局部重写）  
- **上传**（Base64 / 文件流 / URL）  
- **翻唱**（上传并翻唱音频）  
- **Persona 生成**（同步返回 personaId）

> 所有下载的文件保存至 `./suno_outputs/`。

---

## 准备

1. **Python 3.10+**  
2. 安装依赖：

   ```bash
   pip install requests
   ```

3. 设置 API Key（推荐使用环境变量）：

   - macOS / Linux:
     ```bash
     export SUNO_API_KEY="你的Key"
     ```
   - Windows PowerShell:
     ```powershell
     $env:SUNO_API_KEY="你的Key"
     ```

---

## 用法总览

```bash
python main.py <子命令> [参数...]
```

### 1) 查询积分
```bash
python main.py credits
```

### 2) 生成歌词（并等待完成）
```bash
python main.py lyrics --prompt "一首关于冒险与发现的中文流行歌，副歌洗脑"
```

### 3) 生成音乐
- **非自定义**（只给 prompt，系统会自动写词）：
  ```bash
  python main.py gen --prompt "积极向上的中文流行，副歌重复关键词出发" --model V4_5 --download
  ```

- **自定义**（你提供风格+标题；若需要演唱歌词，prompt 就是歌词）：
  ```bash
  python main.py gen --custom --style "流行" --title "冒险之歌·自定义" \
    --prompt "（这里放你的完整歌词）" --model V4_5 --download
  ```

### 4) 延长音乐
- 复用原参数：
  ```bash
  python main.py extend --audio-id <原audioId> --model V4_5
  ```

- 自定义参数（`--default-param` 打开；需带 `--continue-at/--title/--style`）：
  ```bash
  python main.py extend --audio-id <原audioId> --model V4_5 --default-param \
    --continue-at 90 --title "冒险之歌·扩展版" --style "流行" \
    --prompt "加入更激昂的尾奏与合唱"
  ```

### 5) **上传并延长音乐**
- 直接使用公网音频 URL：
  ```bash
  python main.py upload-extend --upload-url "https://example.com/your_audio.mp3" \
    --model V4_5 --default-param --continue-at 60 --style "流行" --title "更长的冒险"
  ```
- 本地文件 → 先上传再延长：
  ```bash
  python main.py upload-extend --file ./clip.mp3 --model V4_5 --default-param \
    --continue-at 45 --style "流行" --title "片段延长"
  ```

### 6) **添加乐器**
```bash
python main.py add-instrumental \
  --upload-url "https://example.com/vocals_only.mp3" \
  --title "轻松钢琴" \
  --tags "轻松钢琴, 环境音乐" \
  --neg "重金属, 激进鼓点" \
  --download
```

### 7) **添加人声**
```bash
python main.py add-vocals \
  --upload-url "https://example.com/instrumental.mp3" \
  --prompt "柔和男声，流行风格" \
  --style "流行" \
  --title "轻松钢琴配人声" \
  --neg "嘶吼, 失真" \
  --download
```

### 8) **时间戳歌词**（同步）
```bash
python main.py ts-lyrics --task-id <taskId> --audio-id <audioId>
```

### 9) **风格增强**（同步）
```bash
python main.py style-gen --content "Pop, Mysterious"
```

### 10) 人声/伴奏分离
```bash
python main.py separate --task-id <生成音乐的taskId> --audio-id <audioId> --type separate_vocal --download
```

### 11) 转 WAV
```bash
python main.py wav --task-id <生成音乐的taskId> --audio-id <audioId> --download
```

### 12) 生成 MP4 音乐视频
```bash
python main.py mp4 --task-id <生成音乐的taskId> --audio-id <audioId> \
  --author "YourName" --domain yoursite.com --download
```

### 13) **生成音乐封面**（异步）
```bash
python main.py cover-art --task-id <父任务taskId> --download
```

### 14) **查询封面详情**
```bash
python main.py cover-info --task-id <封面任务taskId>
```

### 15) **替换音乐分区**（局部重写）
```bash
python main.py replace-section \
  --task-id <父任务taskId> \
  --audio-id <audioId> \
  --prompt "把第10-20秒改成更激昂的过门" \
  --tags "流行, 史诗" \
  --title "冒险之歌·重写片段" \
  --neg "吵闹, 失真" \
  --start 10.0 --end 20.0 \
  --download
```

### 16) 上传
- Base64
  ```bash
  python main.py upload-b64 --file ./suno_outputs/song.mp3 --path files/base64 --name demo_from_b64.mp3
  ```
- 文件流
  ```bash
  python main.py upload-stream --file ./suno_outputs/song.mp3 --path files/stream --name demo_stream.mp3
  ```
- URL 直传
  ```bash
  python main.py upload-url --url https://httpbin.org/image/jpeg --path images/url --name downloaded.jpg
  ```

### 17) 翻唱
将一段已有音频（如清唱、吉他和声、参考曲段）上传后，让 AI 在保留旋律/风格线索的基础上制作新版本（可选择是否演唱）。
- 直接使用公网音频URL
  ```bash
  python main.py cover \
    --upload-url "https://example.com/your_audio.mp3" \
    --custom --style "流行" --title "我的翻唱" \
    --prompt "（如需演唱，填写完整歌词；器乐翻唱可不写）" \
    --model V4_5 \
    --download
  ```
- 本地文件 → 先上传再翻唱
  ```bash
  python main.py cover \
    --file ./my_audio.mp3 \
    --custom --style "流行" --title "我的翻唱" \
    --prompt "（如需演唱，填写完整歌词）" \
    --model V4_5 \
    --download
  ```

### 18) **Persona 生成**（同步）
```bash
python main.py persona --task-id <taskId> --audio-id <audioId> \
  --name "电子流行歌手" --desc "现代电子风格，动感节奏与合成器音色"
```

---

## 参数与注意事项

1. `--model`：可选 `V3_5 / V4 / V4_5 / V4_5PLUS / V5`，不同模型对 prompt/style 长度限制不同。  
2. `--custom` 自定义模式：
   - 器乐（`--instrumental`）时只需要 `--style --title`；
   - 演唱时需要 `--style --title --prompt(歌词)`。
3. 生成/分离/转换/视频/封面/添加人声乐器/替换分区等任务多数为**异步**，本工具会自动**轮询状态**直到 `SUCCESS` 或失败超时。
4. 生成的音频/视频/图片通常仅保留 14~15 天（以官方为准），建议使用 `--download` 立即保存到本地。  
5. 上传接口使用 `https://sunoapiorg.redpandaai.co/api` 域；临时文件一般保留 3 天。  
6. 生产环境请做好**错误重试/速率限制/积分不足**等异常处理；本工具内置了基础的 3 次服务端错误重试。  
7. 使用第三方/官方 API 时，请遵守相应的服务条款与版权要求。

---

## 典型工作流示例

### A) 从零到成品
```bash
python main.py credits
python main.py lyrics --prompt "一首热血冒险主题的中文流行歌，副歌洗脑"
python main.py gen --custom --style "流行" --title "冒险之歌" \
  --prompt "（粘贴上一步返回的歌词文本）" --model V4_5 --download
python main.py extend --audio-id <audioId> --model V4_5 --default-param \
  --continue-at 90 --title "冒险之歌·扩展版" --style "流行"
python main.py add-vocals --upload-url "<上一步器乐音频URL>" \
  --prompt "更饱满的合唱段落" --style "流行" --title "冒险之歌·合唱版" --neg "嘶吼"
python main.py mp4 --task-id <taskId> --audio-id <audioId> --author "Me" --domain example.com --download
```

### B) 对已有音频做重写
```bash
python main.py upload-extend --file ./riff.mp3 --model V4_5 --default-param \
  --continue-at 30 --style "摇滚" --title "Riff 扩展"
python main.py replace-section --task-id <父taskId> --audio-id <audioId> \
  --prompt "把第20秒到30秒改成更抒情的弦乐" --tags "流行, 弦乐" --title "Riff 局部重写" \
  --neg "失真" --start 20 --end 30 --download
python main.py cover-art --task-id <父taskId> --download
```

---

## 参考
- Suno 文档：
  - 生成音乐：`POST /api/v1/generate`
  - 延长音乐：`POST /api/v1/generate/extend`
  - 上传并延长：`POST /api/v1/generate/upload-extend`
  - 添加乐器：`POST /api/v1/generate/add-instrumental`
  - 添加人声：`POST /api/v1/generate/add-vocals`
  - 时间戳歌词：`POST /api/v1/generate/get-timestamped-lyrics`
  - 风格增强：`POST /api/v1/style/generate`
  - 生成封面：`POST /api/v1/suno/cover/generate`；查询封面详情：`GET /api/v1/suno/cover/record-info`
  - 替换音乐分区：`POST /api/v1/generate/replace-section`
  - 生成 Persona：`POST /api/v1/generate/generate-persona`
```

)