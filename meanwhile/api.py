import json
import uuid
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from temporalio.client import Client

from meanwhile.config import AppSettings, get_settings
from meanwhile.db import WorkflowDefinition, get_session
from meanwhile.models import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    WorkflowDefinitionCreate,
    WorkflowDefinitionResponse,
    WorkflowDefinitionUpdate,
)
from meanwhile.temporal import connect_temporal
from meanwhile.workflows import ChatWorkflow

API_TAGS = [
    {"name": "health", "description": "Service and Temporal connectivity checks."},
    {"name": "chat", "description": "Temporal-orchestrated chatbot endpoints."},
    {"name": "workflow-definitions", "description": "CRUD for workflow definitions (canvas graph storage)."},
]


def create_app(
    *,
    settings: AppSettings | None = None,
    temporal_client: Client | None = None,
) -> FastAPI:
    app_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app_instance: FastAPI):
        if app_instance.state.temporal_client is None:
            try:
                app_instance.state.temporal_client = await connect_temporal(app_settings)
            except Exception:
                app_instance.state.temporal_client = None
        yield

    app = FastAPI(
        title="Temporal Chatbot API",
        version="0.1.0",
        description="Small chatbot app for exercising Temporal essentials with PydanticAI.",
        openapi_tags=API_TAGS,
        lifespan=lifespan,
    )

    router = APIRouter(prefix="/api")
    app.state.settings = app_settings
    app.state.temporal_client = temporal_client

    def get_temporal_client() -> Client:
        client = app.state.temporal_client
        if client is None:
            raise HTTPException(status_code=503, detail="Temporal client unavailable")
        return client

    @router.get(
        "/health",
        response_model=HealthResponse,
        tags=["health"],
        summary="Health check",
        description="Returns service health. Fails if Temporal client is not initialized.",
    )
    async def health(client: Client = Depends(get_temporal_client)) -> HealthResponse:
        if client is None:
            raise HTTPException(status_code=503, detail="Temporal unavailable")
        return HealthResponse(status="ok")

    @router.post(
        "/chat",
        response_model=ChatResponse,
        status_code=201,
        tags=["chat"],
        summary="Run chatbot workflow",
        description="Starts a Temporal workflow that calls a PydanticAI-powered activity and returns the final answer.",
        responses={
            503: {"description": "Temporal unavailable"},
        },
    )
    async def chat(
        request: ChatRequest,
        client: Client = Depends(get_temporal_client),
    ) -> ChatResponse:
        workflow_id = f"chat-{request.conversation_id}-{uuid.uuid4().hex[:8]}"
        try:
            return await client.execute_workflow(
                ChatWorkflow.run,
                request,
                id=workflow_id,
                task_queue=app_settings.temporal_task_queue,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=503, detail=f"Temporal execution failed: {exc}"
            ) from exc

    # --- Workflow definitions (spec 05) ---

    @router.post(
        "/workflow-definitions",
        response_model=WorkflowDefinitionResponse,
        status_code=201,
        tags=["workflow-definitions"],
        summary="Create workflow definition",
        description="Create a workflow definition with name and graph payload (e.g. React Flow JSON).",
        responses={400: {"description": "Validation error (e.g. empty name, graph not a JSON object)"}},
    )
    async def post_workflow_definition(
        body: WorkflowDefinitionCreate,
        session: AsyncSession = Depends(get_session),
    ) -> WorkflowDefinitionResponse:
        row = WorkflowDefinition(
            name=body.name,
            graph_json=json.dumps(body.graph),
        )
        session.add(row)
        await session.flush()
        await session.refresh(row)
        return WorkflowDefinitionResponse(
            id=row.id,
            name=row.name,
            graph=body.graph,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @router.get(
        "/workflow-definitions",
        response_model=list[WorkflowDefinitionResponse],
        tags=["workflow-definitions"],
        summary="List workflow definitions",
        description="Return all workflow definitions, ordered by updated_at descending.",
    )
    async def get_workflow_definitions(
        session: AsyncSession = Depends(get_session),
    ) -> list[WorkflowDefinitionResponse]:
        result = await session.execute(
            select(WorkflowDefinition).order_by(desc(WorkflowDefinition.updated_at))
        )
        rows = result.scalars().all()
        out = []
        for row in rows:
            graph = json.loads(row.graph_json) if isinstance(row.graph_json, str) else row.graph_json
            out.append(
                WorkflowDefinitionResponse(
                    id=row.id,
                    name=row.name,
                    graph=graph,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                )
            )
        return out

    @router.get(
        "/workflow-definitions/{definition_id}",
        response_model=WorkflowDefinitionResponse,
        tags=["workflow-definitions"],
        summary="Get workflow definition by id",
        description="Return a single workflow definition. 404 if not found.",
        responses={404: {"description": "Definition not found"}},
    )
    async def get_workflow_definition(
        definition_id: str,
        session: AsyncSession = Depends(get_session),
    ) -> WorkflowDefinitionResponse:
        result = await session.get(WorkflowDefinition, definition_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Workflow definition not found")
        graph = json.loads(result.graph_json) if isinstance(result.graph_json, str) else result.graph_json
        return WorkflowDefinitionResponse(
            id=result.id,
            name=result.name,
            graph=graph,
            created_at=result.created_at,
            updated_at=result.updated_at,
        )

    @router.patch(
        "/workflow-definitions/{definition_id}",
        response_model=WorkflowDefinitionResponse,
        tags=["workflow-definitions"],
        summary="Update workflow definition",
        description="Update name and/or graph. Only provided fields are updated. 404 if not found.",
        responses={404: {"description": "Definition not found"}},
    )
    async def patch_workflow_definition(
        definition_id: str,
        body: WorkflowDefinitionUpdate,
        session: AsyncSession = Depends(get_session),
    ) -> WorkflowDefinitionResponse:
        result = await session.get(WorkflowDefinition, definition_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Workflow definition not found")
        if body.name is not None:
            result.name = body.name
        if body.graph is not None:
            result.graph_json = json.dumps(body.graph)
        await session.flush()
        await session.refresh(result)
        graph = json.loads(result.graph_json) if isinstance(result.graph_json, str) else result.graph_json
        return WorkflowDefinitionResponse(
            id=result.id,
            name=result.name,
            graph=graph,
            created_at=result.created_at,
            updated_at=result.updated_at,
        )

    @router.delete(
        "/workflow-definitions/{definition_id}",
        status_code=204,
        tags=["workflow-definitions"],
        summary="Delete workflow definition",
        description="Delete a workflow definition by id. 204 on success. 404 if not found. Note: workflow_runs and execution_logs reference definitions/runs; current FK uses CASCADE (see docs).",
        responses={404: {"description": "Definition not found"}},
    )
    async def delete_workflow_definition(
        definition_id: str,
        session: AsyncSession = Depends(get_session),
    ) -> None:
        result = await session.get(WorkflowDefinition, definition_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Workflow definition not found")
        await session.delete(result)
        await session.flush()

    app.include_router(router)
    return app
