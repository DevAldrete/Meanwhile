import uuid
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from temporalio.client import Client

from meanwhile.config import AppSettings, get_settings
from meanwhile.models import ChatRequest, ChatResponse, HealthResponse
from meanwhile.temporal import connect_temporal
from meanwhile.workflows import ChatWorkflow

API_TAGS = [
    {"name": "health", "description": "Service and Temporal connectivity checks."},
    {"name": "chat", "description": "Temporal-orchestrated chatbot endpoints."},
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

    app.include_router(router)
    return app
