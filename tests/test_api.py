from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from meanwhile.api import create_app
from meanwhile.config import AppSettings
from meanwhile.models import ChatResponse


class FakeTemporalClient:
    async def execute_workflow(self, _workflow, request, **kwargs):  # noqa: ANN001
        return ChatResponse(
            workflow_id=kwargs["id"],
            run_id="run-1",
            conversation_id=request.conversation_id,
            answer="hello from fake temporal",
        )


def test_health_endpoint_returns_ok() -> None:
    app = create_app(
        settings=AppSettings(),
        temporal_client=FakeTemporalClient(),
    )

    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_returns_503_when_temporal_unavailable() -> None:
    app = create_app(settings=AppSettings(), temporal_client=None)

    with patch("meanwhile.api.connect_temporal", new_callable=AsyncMock) as mock_connect:
        mock_connect.side_effect = Exception("Temporal unavailable")
        with TestClient(app) as client:
            response = client.get("/api/health")

    assert response.status_code == 503


def test_chat_endpoint_returns_temporal_result() -> None:
    app = create_app(
        settings=AppSettings(temporal_task_queue="test-queue"),
        temporal_client=FakeTemporalClient(),
    )

    payload = {
        "prompt": "Explain Temporal",
        "user_id": "user-1",
        "conversation_id": "conv-123",
    }

    with TestClient(app) as client:
        response = client.post("/api/chat", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["conversation_id"] == "conv-123"
    assert body["answer"] == "hello from fake temporal"
    assert body["workflow_id"].startswith("chat-conv-123-")
