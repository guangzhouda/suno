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
