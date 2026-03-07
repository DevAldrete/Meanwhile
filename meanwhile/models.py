from datetime import datetime

from pydantic import BaseModel, Field


# --- Workflow definitions API (spec 05) ---


class WorkflowDefinitionCreate(BaseModel):
    """Request body for POST /api/workflow-definitions."""

    name: str = Field(min_length=1, description="Workflow name")
    graph: dict = Field(description="Graph payload (e.g. React Flow JSON)")


class WorkflowDefinitionUpdate(BaseModel):
    """Request body for PATCH /api/workflow-definitions/{id}."""

    name: str | None = Field(None, min_length=1)
    graph: dict | None = None


class WorkflowDefinitionResponse(BaseModel):
    """Response shape for a single workflow definition."""

    id: str
    name: str | None
    graph: dict
    created_at: datetime
    updated_at: datetime


# --- Chat API ---


class ChatRequest(BaseModel):
    prompt: str = Field(
        min_length=1, examples=["Explain Temporal retries in one paragraph"]
    )
    user_id: str = Field(min_length=1, examples=["demo-user"])
    conversation_id: str = Field(min_length=1, examples=["conv-1"])


class ChatResult(BaseModel):
    answer: str


class ChatResponse(BaseModel):
    workflow_id: str
    run_id: str | None = None
    conversation_id: str
    answer: str


class HealthResponse(BaseModel):
    status: str
