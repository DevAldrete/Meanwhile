import json
from datetime import datetime, timedelta, timezone

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from meanwhile.activities import (
        create_workflow_run,
        generate_chat_answer,
        load_workflow_definition,
        run_ai_node,
        update_workflow_run_status,
    )
    from meanwhile.models import ChatRequest, ChatResponse


# --- Interpreter workflow (spec 06): runs a workflow definition graph (Brain) ---


@workflow.defn
class InterpreterWorkflow:
    """
    Load a workflow definition by id, create a run record, execute graph nodes
    (MVP: linear order; AI nodes call run_ai_node activity), update run status.
    All I/O (DB, LLM) is in activities; workflow body is deterministic.
    """

    @workflow.run
    async def run(
        self,
        workflow_definition_id: str,
        inputs: dict | None = None,
    ) -> dict:
        info = workflow.info()
        inputs_json = json.dumps(inputs or {})
        definition = await workflow.execute_activity(
            load_workflow_definition,
            workflow_definition_id,
            start_to_close_timeout=timedelta(seconds=30),
        )
        run_id = await workflow.execute_activity(
            create_workflow_run,
            args=[
                workflow_definition_id,
                info.workflow_id,
                info.run_id or "",
                inputs_json,
            ],
            start_to_close_timeout=timedelta(seconds=15),
        )
        now = datetime.now(timezone.utc)
        try:
            graph = definition.get("graph") or {}
            nodes = graph.get("nodes") or []
            for node in nodes:
                node_id = node.get("id") or ""
                node_type = (node.get("type") or "").lower()
                data = node.get("data") or {}
                if node_type in ("ai", "agent"):
                    await workflow.execute_activity(
                        run_ai_node,
                        args=[run_id, node_id, data],
                        start_to_close_timeout=timedelta(seconds=60),
                    )
            await workflow.execute_activity(
                update_workflow_run_status,
                args=[run_id, "completed", now],
                start_to_close_timeout=timedelta(seconds=15),
            )
            return {"run_id": run_id, "status": "completed"}
        except Exception:
            await workflow.execute_activity(
                update_workflow_run_status,
                args=[run_id, "failed", now],
                start_to_close_timeout=timedelta(seconds=15),
            )
            raise


# --- Chat workflow (existing) ---


@workflow.defn
class ChatWorkflow:
    def __init__(self) -> None:
        self._status = "created"

    @workflow.run
    async def run(self, request: ChatRequest) -> ChatResponse:
        self._status = "running"
        result = await workflow.execute_activity(
            generate_chat_answer,
            request.prompt,
            start_to_close_timeout=timedelta(seconds=30),
        )
        self._status = "completed"
        return ChatResponse(
            workflow_id=workflow.info().workflow_id,
            run_id=workflow.info().run_id,
            conversation_id=request.conversation_id,
            answer=result.answer,
        )

    @workflow.signal
    async def set_status(self, value: str) -> None:
        self._status = value

    @workflow.query
    def get_status(self) -> str:
        return self._status
