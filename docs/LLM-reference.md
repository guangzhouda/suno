## 一、统一约定（给大模型看的总说明）

1. 你可以通过 HTTP 调用 New API，接口前缀统一为：
    `https://https://api.voct.top`
2. 所有接口都使用 **Bearer Token 鉴权**，请求头必须包含：
   - `Content-Type: application/json`（图像编辑/变体使用表单时除外）
   - `Authorization: Bearer $NEWAPI_API_KEY`
3. 你主要会用到两个端点：
   - 文本聊天（用于歌词生成和改写）：
      `POST /v1/chat/completions`
   - 图像生成（用于海报制作）：
      `POST /v1/images/generations`
4. 默认使用与 OpenAI 兼容的格式：
   - `model` 字段指定模型，例如：`"deepseek-ai/DeepSeek-V3"`（文本）、`"doubao-seedream-4-0-250828"`（图片）

下面分模块说明。

------

## 二、文字对话接口（Chat Completions）—— 用于歌词生成 & 歌词改写

### 2.1 基本调用方式

**端点：**
 `POST https://<your-domain>/v1/chat/completions`

**必要字段：**

- `model`：文本模型名称，例如 `"gpt-4.1"`
- `messages`：一个数组，每一项是一个消息对象，包含：
  - `role`: `"developer" | "system" | "user" | "assistant" | "tool"`
  - `content`: 文本或富内容（本场景主要用纯文本）

**典型结构：**

- 用 `developer`（或 `system`）写“角色和任务说明”
- 用 `user` 写“具体需求和素材”（如主题、原歌词等）
- 模型返回的 `assistant` 消息里，就是你要的歌词或 JSON 结果

------

### 2.2 通用约束（建议喂给模型）

当你调用 `/v1/chat/completions` 时，请遵守以下约束：

1. **始终显式指定 `model`，例如 `"gpt-4.1"`。**

2. 如果需要结构化结果（比如标题 + 歌词），建议使用 `response_format`：

   ```
   json
   
   
   复制编辑
   "response_format": { "type": "json_object" }
   ```

   这样可以强制模型输出合法 JSON，便于后续处理。

3. 不要向接口回传任何二进制内容（图片、音频），只传文本。

4. 如果对话较长，需合理设置 `max_tokens`，保证能完整输出歌词。

------

### 2.3 场景一：歌词生成（从零写歌）

**目标：**
 根据用户的主题、情绪、风格等信息，调用 `/v1/chat/completions` 让模型生成一首完整歌词，并返回结构化结果。

**调用建议：**

- 使用一个 `developer` 消息，定义你的角色，例如：

  > 你是一名专业作词人，会根据用户提供的主题和风格创作歌词。
  >  输出统一使用 JSON 格式，包含 `title` 和 `lyrics` 字段。
  >  `lyrics` 中请按 Verse / Chorus / Bridge 分段，并用清晰的分段标记。

- 在 `user` 消息中，放入用户需求（例如来自前端表单的参数）：

  - 主题（跨年前夜的独白）
  - 情绪（治愈 / 悲伤 / 热血…）
  - 风格（Pop / City Pop / 国风…）
  - 语言（中文 / 英文 / 多语言）
  - 是否需要押韵、段落结构要求等

**返回格式建议：**

要求模型输出类似结构（可在 `developer` 消息中写明）：

```
json复制编辑{
  "title": "跨年前夜的独白",
  "language": "zh",
  "emotion": "治愈",
  "style": "City Pop",
  "lyrics": {
    "verse_1": "...",
    "pre_chorus": "...",
    "chorus": "...",
    "verse_2": "...",
    "bridge": "..."
  }
}
```

**使用要点（写给大模型）：**

- 你需要根据用户给出的情绪 / 风格，用合适的用词和画面感。
- 你生成的歌词应该方便后续交给音乐生成接口（如 Suno），保持稳定的行数和节奏结构。
- 尽量少用过长句子，便于谱曲。

------

### 2.4 场景二：歌词改写（好歌改词）

**目标：**
 给定一份已经存在的歌词，让模型按指定方式改写（换主题、换语言等），输出结构化的新歌词。

**调用建议：**

1. `developer` 消息：明确你的任务是“在保留节奏结构的前提下改写歌词”。

   要点可以包括：

   - 保留每段的行数和大致节奏（音节数差不多）。
   - 如果是换主题，比如“失恋 → 友情”，要用新的意象，但不抄原句。
   - 如果是换语言，要忠实传达情绪，同时考虑唱起来顺口。

2. `user` 消息中包含：

   - 原歌词（带段落结构）
   - 改写模式（例如：换主题到“友情”、从中文改写成英文）

**期望输出 JSON 结构示例：**

```
json复制编辑{
  "mode": "change_theme",
  "target_theme": "友情",
  "original_language": "zh",
  "target_language": "zh",
  "rewritten_lyrics": {
    "verse_1": "...",
    "pre_chorus": "...",
    "chorus": "...",
    "verse_2": "...",
    "bridge": "..."
  },
  "notes": "这里可以简要说明改写思路，例如：把恋人替换为多年老友..."
}
```

**使用要点（写给大模型）：**

- 你必须保留段落结构（有哪些段以及每段的行数），方便复用原曲旋律。
- 如无特别说明，建议保持原语言不变；如果用户要求改语言，要在 JSON 中同时标出原语言和目标语言。
- 不要输出额外解释文本到 JSON 外面；所有解释建议放在 JSON 的 `notes` 字段中。

------

## 三、图像生成接口（Image）—— 用于海报制作

### 3.1 基本调用方式

**端点：**

- 创建图片：`POST /v1/images/generations`

**基础请求字段：**

- `model`：推荐使用 `"dall-e-3"` 做高质量海报。
- `prompt`：文本描述（海报内容）
- `n`：生成图片数量，海报一般 `1` 即可
- `size`：图片分辨率，例如 `"1024x1024"` 或 `"1792x1024"`（横版海报）
- `quality`：可选 `"hd"`，用于更精细的图片（仅 dall-e-3 支持）
- `style`：`"vivid"`（更夸张艺术）或 `"natural"`（更真实）
- `response_format`：`"url"` 或 `"b64_json"`，通常用 `"url"` 即可

------

### 3.2 海报制作的调用策略（写给大模型）

你的任务：根据一首歌（标题 + 情绪 + 风格 + 核心意象）设计海报，并调用 `/v1/images/generations` 生成图片。

**步骤建议：**

1. 从已有信息中提取**视觉要素**：
   - 歌曲标题
   - 主题 / 故事背景（如：跨年前夜、城市夜景、告别、自我成长…）
   - 情绪（治愈 / 热血 / 伤感…）
   - 风格（City Pop、摇滚、民谣…）
2. 在你内部先构思一段详细的图像描述（可不返回给用户，只用来构造 `prompt`），注意包括：
   - 场景（室内 / 街头 / 舞台 / 星空 / 海边…）
   - 主体元素（人物 / 乐器 / 城市 / 自然景观…）
   - 颜色氛围（例如霓虹粉紫 / 暖黄灯光 / 冷蓝色调）
   - 构图（远景 / 特写 / 居中 / 对称）
3. 把这些元素组织成简洁但具体的英文或中文 `prompt`。如果需要更稳定效果，建议使用英文。

**海报场景下的参数推荐：**

- `model`: `"dall-e-3"`
- `size`:
  - `"1024x1024"` 用于方形封面
  - `"1792x1024"` 用于横版 banner 海报
  - `"1024x1792"` 用于竖版海报
- `quality`: `"hd"`（精致的宣传海报更合适）
- `style`:
  - `"vivid"`：适合电子、City Pop、二次元等比较炫的风格
  - `"natural"`：适合民谣、轻音乐、真实乐队现场感

**海报 prompt 构造要点：**

在构造 `prompt` 时，注意：

- 包含歌曲情绪和风格，例如：

  - “dreamy city pop style”
  - “melancholic acoustic folk”

- 指明这是“music poster / album cover / concert poster”，让模型理解是海报风格。

- 可以提到大标题文字的位置，比如：

  > “with space at the top for the song title”
  >  “minimalist layout, focus on central character, clear area for typography”

**示例结构（逻辑模板）：**

> A [emotion] [music style] album cover for a song about [theme],
>  set in [scene], with [main visual elements],
>  color palette of [colors],
>  cinematic lighting, highly detailed, illustration style / realistic style,
>  with empty space at the top for the Chinese title.

你不一定要输出这段文字给用户看，但需要把类似信息放进 `prompt` 字段里。

------

## 四、这三个业务功能的组合调用逻辑（给大模型的高阶指导）

### 4.1 歌词生成（从0开始）

1. 接到用户需求（主题、情绪、风格）后：
2. 先调用 `/v1/chat/completions`，使用“歌词生成”策略：
   - 角色设定为专业作词人
   - 输出 JSON：标题 + 结构化歌词
3. 把生成的歌词返回给用户或交给后续音乐生成模块使用。

### 4.2 歌词改写

1. 接到：原歌词 + 改写要求（换主题/换语言…）
2. 调用 `/v1/chat/completions`，使用“歌词改写”策略：
   - 保留结构
   - 输出 JSON：`rewritten_lyrics`
3. 返回新歌词，同时标明改写模式和目标主题/语言。

### 4.3 海报制作

有两种常见路径：

**路径 A：基于歌词/歌曲信息直接生成海报**

1. 获取歌曲信息（标题、情绪、风格、核心意象）。
2. 在内部总结成视觉描述。
3. 调用 `/v1/images/generations`：
   - `model: "dall-e-3"`
   - 构造包含场景、颜色、风格的 `prompt`
4. 返回图片 URL。

**路径 B：先让 Chat 帮忙写“海报描述”，再调用 Image**

1. 调用 `/v1/chat/completions`，让模型先输出一个专门用于海报的 `prompt` 文案（英文/中文均可）。
2. 再把这个文案作为 `prompt` 传给 `/v1/images/generations`。
3. 这样可以让“文本模型”和“图像模型”分工更清晰。