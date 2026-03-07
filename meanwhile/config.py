from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


_DEFAULT_DATABASE_URL = (
    "postgresql+asyncpg://meanwhile_user:meanwhile_pass@localhost:5432/meanwhile_db"
)


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    temporal_target: str = Field(default="localhost:7233")
    temporal_namespace: str = Field(default="default")
    temporal_task_queue: str = Field(default="chatbot-task-queue")
    pydantic_ai_model: str = Field(default="test")
    database_url: str = Field(default=_DEFAULT_DATABASE_URL)


def get_settings() -> AppSettings:
    return AppSettings()
