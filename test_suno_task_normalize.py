"""
测试 Suno 任务响应标准化逻辑
"""

from modules.routes.suno import normalize_suno_task


def test_normalize_suno_task_success():
    raw = {
        "taskId": "task-123",
        "status": "SUCCESS",
        "response": {
            "taskId": "task-123",
            "sunoData": [
                {
                    "id": "audio-1",
                    "audioUrl": "https://example.com/audio.mp3",
                    "streamAudioUrl": "https://example.com/stream.m3u8",
                    "imageUrl": "https://example.com/cover.jpg",
                    "title": "测试歌曲",
                    "modelName": "chirp-v3-5",
                    "tags": "pop, warm",
                    "duration": 120.5,
                    "createTime": "2025-01-01 00:00:00",
                }
            ],
        },
        "errorCode": None,
        "errorMessage": None,
        "type": "GENERATE",
    }

    normalized = normalize_suno_task(raw)

    assert normalized["status"] == "complete"
    assert normalized["task_id"] == "task-123"
    assert normalized["tracks"][0]["audio_url"] == "https://example.com/audio.mp3"
    assert normalized["tracks"][0]["image_url"] == "https://example.com/cover.jpg"


def test_normalize_suno_task_failure():
    raw = {
        "taskId": "task-456",
        "status": "FAILED",
        "errorMessage": "insufficient credits",
        "errorCode": 429,
        "type": "GENERATE",
    }

    normalized = normalize_suno_task(raw)

    assert normalized["status"] == "error"
    assert normalized["error_code"] == 429
    assert normalized["error_message"] == "insufficient credits"
    assert normalized["tracks"] == []
