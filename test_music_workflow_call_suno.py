"""
Tests for call_suno_generate_music helper.
"""

from types import SimpleNamespace

from modules.routes import music_workflow


class DummyConfig:
    def is_enabled(self, service: str) -> bool:
        return service == "suno"

    def get(self, key: str, default=None):
        overrides = {
            "server.poll_interval_seconds": 0,
            "server.max_poll_timeout_seconds": 5,
        }
        return overrides.get(key, default)


class FakeSunoClient:
    def __init__(self, statuses):
        self.statuses = statuses
        self.generate_called = False
        self.info_calls = 0

    def generate_music(self, **kwargs):
        self.generate_called = True
        return "test-task-1"

    def get_music_info(self, task_id):
        self.info_calls += 1
        status = self.statuses[min(self.info_calls - 1, len(self.statuses) - 1)]
        return status


def test_call_suno_generate_music_wait(monkeypatch):
    config = DummyConfig()
    monkeypatch.setattr(music_workflow, "get_config", lambda: config)
    monkeypatch.setattr(music_workflow.time, "sleep", lambda _: None)

    statuses = [
        {"status": "STARTED", "response": {"sunoData": []}},
        {
            "status": "SUCCESS",
            "response": {"sunoData": [{"id": "a1", "audioUrl": "https://example.com/audio.mp3"}]},
        },
    ]
    client = FakeSunoClient(statuses)

    result = music_workflow.call_suno_generate_music(
        lyrics="test lyrics",
        title="demo",
        style="流行",
        wait=True,
        client=client,
    )

    assert result["task_id"] == "test-task-1"
    assert result["status"] == "complete"
    assert result["tracks"][0]["audio_url"] == "https://example.com/audio.mp3"
    assert client.info_calls >= 1


def test_call_suno_generate_music_no_wait(monkeypatch):
    config = DummyConfig()
    monkeypatch.setattr(music_workflow, "get_config", lambda: config)

    client = FakeSunoClient([{"status": "SUCCESS", "response": {"sunoData": []}}])

    result = music_workflow.call_suno_generate_music(
        lyrics="test lyrics",
        title="demo",
        style="流行",
        wait=False,
        client=client,
    )

    assert result["status"] == "pending"
    assert client.info_calls == 0
