"""Tests for interpreter workflow and execution logging (spec 06)."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from temporalio.contrib.pydantic import pydantic_data_converter

from meanwhile.activities import run_ai_node
from meanwhile.db import append_execution_log
from meanwhile.models import ChatResult
from meanwhile.workflows import InterpreterWorkflow


@pytest.mark.asyncio
async def test_run_ai_node_writes_execution_log(monkeypatch: pytest.MonkeyPatch) -> None:
    """run_ai_node calls agent and appends an execution_log row with ai_step and payload."""
    fake_agent = AsyncMock()
    fake_agent.generate.return_value = ChatResult(answer="model said hello")
    monkeypatch.setattr("meanwhile.activities.get_agent", lambda: fake_agent)

    logs: list[tuple[int, str, str, dict]] = []

    async def capture_append(session, workflow_run_id, node_id, step_type, payload):
        logs.append((workflow_run_id, node_id, step_type, payload))

    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_factory = MagicMock()
    mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
    mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

    with patch("meanwhile.activities.get_session_factory", return_value=mock_factory), patch(
        "meanwhile.activities.append_execution_log", side_effect=capture_append
    ):
        result = await run_ai_node(
            workflow_run_id=42,
            node_id="node-1",
            node_config={"prompt": "Hello", "systemInstruction": "Be brief"},
        )

    assert result == "model said hello"
    assert len(logs) == 1
    wf_run_id, node_id, step_type, payload = logs[0]
    assert wf_run_id == 42
    assert node_id == "node-1"
    assert step_type == "ai_step"
    assert payload["prompt"] == "Hello"
    assert payload["system_instruction"] == "Be brief"
    assert payload["raw_output"] == "model said hello"


@pytest.mark.asyncio
async def test_append_execution_log_inserts_row() -> None:
    """append_execution_log adds one ExecutionLog to the session."""
    import json
    from meanwhile.db import ExecutionLog

    mock_session = MagicMock()
    mock_session.add = MagicMock()
    mock_session.flush = AsyncMock()

    await append_execution_log(
        mock_session,
        workflow_run_id=1,
        node_id="n1",
        step_type="ai_step",
        payload={"prompt": "x", "raw_output": "y"},
    )

    mock_session.add.assert_called_once()
    call_arg = mock_session.add.call_args[0][0]
    assert isinstance(call_arg, ExecutionLog)
    assert call_arg.workflow_run_id == 1
    assert call_arg.node_id == "n1"
    assert call_arg.step_type == "ai_step"
    payload = json.loads(call_arg.payload_json)
    assert payload["prompt"] == "x"
    assert payload["raw_output"] == "y"
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_interpreter_workflow_creates_run_and_updates_to_completed() -> None:
    """Interpreter workflow creates workflow_runs row and updates to completed on success."""
    from datetime import datetime, timezone
    from temporalio import activity
    from temporalio.testing import WorkflowEnvironment
    from temporalio.worker import Worker

    created_run_id: list[int | None] = [None]
    final_status: list[str | None] = [None]

    @activity.defn(name="load_workflow_definition")
    async def mock_load_workflow_definition(wdef_id: str) -> dict:
        return {
            "id": wdef_id,
            "name": "Test",
            "graph": {
                "nodes": [
                    {"id": "ai-1", "type": "ai", "data": {"prompt": "Hi"}},
                ],
            },
        }

    @activity.defn(name="create_workflow_run")
    async def mock_create_workflow_run(
        wdef_id: str, tw_id: str, tr_id: str, inputs_json: str
    ) -> int:
        created_run_id[0] = 999
        return 999

    @activity.defn(name="run_ai_node")
    async def mock_run_ai_node(run_id: int, node_id: str, config: dict) -> str:
        return "ok"

    @activity.defn(name="update_workflow_run_status")
    async def mock_update_workflow_run_status(
        run_id: int, status: str, finished_at: datetime | None = None
    ) -> None:
        final_status[0] = status

    async def run_test() -> dict:
        env = await WorkflowEnvironment.start_time_skipping(
            data_converter=pydantic_data_converter
        )
        try:
            async with Worker(
                env.client,
                task_queue="interpreter-test-queue",
                workflows=[InterpreterWorkflow],
                activities=[
                    mock_load_workflow_definition,
                    mock_create_workflow_run,
                    mock_update_workflow_run_status,
                    mock_run_ai_node,
                ],
            ):
                return await env.client.execute_workflow(
                    InterpreterWorkflow.run,
                    args=["def-123"],
                    id="interpreter-wf-1",
                    task_queue="interpreter-test-queue",
                )
        finally:
            await env.shutdown()

    result = await asyncio.wait_for(run_test(), timeout=25.0)
    assert result["status"] == "completed"
    assert result["run_id"] == 999
    assert final_status[0] == "completed"
