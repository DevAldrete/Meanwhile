from pydantic import BaseModel, Field


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
