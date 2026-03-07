import json
from datetime import datetime, timezone
from functools import lru_cache

from temporalio import activity

from meanwhile.agent import ChatbotAgent, PydanticAIChatbotAgent
from meanwhile.config import get_settings
from meanwhile.db import (
    WorkflowDefinition,
    WorkflowRun,
    append_execution_log,
    get_session_factory,
)
from meanwhile.models import ChatResult


@lru_cache(maxsize=1)
def get_agent() -> ChatbotAgent:
    settings = get_settings()
    return PydanticAIChatbotAgent(model_name=settings.pydantic_ai_model)


@activity.defn
async def generate_chat_answer(prompt: str) -> ChatResult:
    agent = get_agent()
    return await agent.generate(prompt)


# --- Interpreter workflow activities (spec 06) ---

# Graph format (MVP): graph has "nodes" (list) and optionally "edges".
# nodes: [{ "id": str, "type": str (e.g. "ai", "agent"), "data": { "prompt"?: str, "systemInstruction"?: str } }].
# Execution order: order of nodes in the list (linear).


@activity.defn
async def load_workflow_definition(workflow_definition_id: str) -> dict:
    """Load a workflow definition by id; return dict with name and graph (parsed)."""
    factory = get_session_factory()
    async with factory() as session:
        row = await session.get(WorkflowDefinition, workflow_definition_id)
        if row is None:
            raise ValueError(f"Workflow definition not found: {workflow_definition_id}")
        graph = json.loads(row.graph_json) if isinstance(row.graph_json, str) else row.graph_json
        await session.commit()
        return {"id": row.id, "name": row.name, "graph": graph}


@activity.defn
async def create_workflow_run(
    workflow_definition_id: str,
    temporal_workflow_id: str,
    temporal_run_id: str | None,
    inputs_json: str,
) -> int:
    """Create a workflow_runs row with status 'running'; return run id."""
    factory = get_session_factory()
    async with factory() as session:
        row = WorkflowRun(
            workflow_definition_id=workflow_definition_id,
            temporal_workflow_id=temporal_workflow_id,
            temporal_run_id=temporal_run_id,
            status="running",
            inputs_json=inputs_json,
        )
        session.add(row)
        await session.flush()
        run_id = row.id
        await session.commit()
        return run_id


@activity.defn
async def update_workflow_run_status(
    workflow_run_id: int,
    status: str,
    finished_at: datetime | None = None,
) -> None:
    """Update workflow_runs row status and optionally finished_at."""
    factory = get_session_factory()
    async with factory() as session:
        row = await session.get(WorkflowRun, workflow_run_id)
        if row is None:
            return
        row.status = status
        if finished_at is not None:
            row.finished_at = finished_at
        await session.commit()


@activity.defn
async def run_ai_node(
    workflow_run_id: int,
    node_id: str,
    node_config: dict,
) -> str:
    """
    Run one AI node: call agent with prompt (and optional system instruction),
    write execution_log row with prompt, tokens, raw output, then return result text.
    """
    agent = get_agent()
    prompt = node_config.get("prompt") or node_config.get("message") or ""
    system_instruction = node_config.get("systemInstruction") or node_config.get("system_instruction")
    result = await agent.generate(prompt)
    raw_output = result.answer
    token_count = getattr(result, "token_count", None)
    payload = {
        "prompt": prompt,
        "system_instruction": system_instruction,
        "raw_output": raw_output,
    }
    if token_count is not None:
        payload["token_count"] = token_count
    factory = get_session_factory()
    async with factory() as session:
        await append_execution_log(
            session,
            workflow_run_id=workflow_run_id,
            node_id=node_id,
            step_type="ai_step",
            payload=payload,
        )
        await session.commit()
    return raw_output
