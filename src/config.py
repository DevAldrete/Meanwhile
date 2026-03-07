from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    temporal_target: str = Field(default="localhost:7233")
    temporal_namespace: str = Field(default="default")
    temporal_task_queue: str = Field(default="chatbot-task-queue")
    pydantic_ai_model: str = Field(default="test")


def get_settings() -> AppSettings:
    return AppSettings()
