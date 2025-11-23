# 测试记录（2025-11-21）

- `python -m pytest test_suno_task_normalize.py`
  - 结果：2 通过，0 失败。
  - 附加信息：Pydantic v2 关于类 Config 的弃用警告（来自既有模型），暂不影响此次改动。

- `python -m pytest test_suno_task_normalize.py test_music_workflow_call_suno.py`
  - 结果：4 通过，0 失败。
  - 附加信息：同样出现 Pydantic Config 弃用警告，已记录待后续处理。

- `python -m pytest test_suno_task_normalize.py test_music_workflow_call_suno.py`
  - 结果：4 通过，0 失败（图片成歌上传改动后回归测试）。
  - 附加信息：依旧存在 Pydantic Config 弃用警告。

- `python -m pytest test_suno_task_normalize.py`
  - 结果：2 通过，0 失败。
  - 附加信息：控制台持续出现 Pydantic Config 弃用警告（modules/models/llm.py、modules/routes/newapi.py、modules/routes/music_workflow.py），暂不影响此次图片上传/任务刷新改动。

- 本次 UI 布局与 Suno meta 保存改动未执行联网测试
  - 原因：环境网络/权限受限，无法调用豆包/Suno。
  - 风险：/api/suno/saved 列表与 meta 写入需在有权限环境下验证；前端歌词/图片布局需浏览器确认（已通过截图对齐调试）。
- 本次图片直出歌词改动未执行联网测试
  - 原因：环境网络受限且缺少豆包/Suno 密钥，无法调用外部接口。
  - 风险：接口返回格式未实测，需在有密钥与外网的环境下验证 /api/doubao/image/lyrics 及前端 image_to_song 流程。
