"""SQLAlchemy async engine, session factory, and declarative base for Meanwhile."""

from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Text, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from meanwhile.config import get_settings


class Base(DeclarativeBase):
    """Declarative base for all Meanwhile ORM models."""

    pass


_engine = None
_session_factory = None


def get_engine():
    """Return the async engine; create from config on first use."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            get_settings().database_url,
            echo=False,
        )
    return _engine


def get_session_factory():
    """Return the async session factory; create on first use."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async session for use as a FastAPI dependency or context manager."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# --- Tables ---


class WorkflowDefinition(Base):
    """Stored workflow definition (graph from the canvas)."""

    __tablename__ = "workflow_definitions"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    graph_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), onupdate=lambda: datetime.now(timezone.utc)
    )

    runs: Mapped[list["WorkflowRun"]] = relationship("WorkflowRun", back_populates="workflow_definition")


class WorkflowRun(Base):
    """A single run of a workflow definition."""

    __tablename__ = "workflow_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workflow_definition_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("workflow_definitions.id", ondelete="CASCADE"),
        nullable=False,
    )
    temporal_workflow_id: Mapped[str] = mapped_column(Text, nullable=False)
    temporal_run_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)  # e.g. running, completed, failed
    inputs_json: Mapped[str] = mapped_column(Text, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workflow_definition: Mapped["WorkflowDefinition"] = relationship("WorkflowDefinition", back_populates="runs")
    execution_logs: Mapped[list["ExecutionLog"]] = relationship("ExecutionLog", back_populates="workflow_run")

    __table_args__ = (Index("ix_workflow_runs_temporal_workflow_id", "temporal_workflow_id"),)


class ExecutionLog(Base):
    """Per-step execution log (prompts, tokens, raw LLM output) for a workflow run."""

    __tablename__ = "execution_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workflow_run_id: Mapped[int] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    node_id: Mapped[str] = mapped_column(Text, nullable=False)
    step_type: Mapped[str] = mapped_column(Text, nullable=False)  # e.g. activity, decision
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

    workflow_run: Mapped["WorkflowRun"] = relationship("WorkflowRun", back_populates="execution_logs")

    __table_args__ = (Index("ix_execution_logs_workflow_run_id", "workflow_run_id"),)
