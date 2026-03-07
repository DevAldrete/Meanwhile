"""Workflow definitions, workflow runs, and execution logs.

Revision ID: 001
Revises:
Create Date: Initial schema

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workflow_definitions",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("graph_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "workflow_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("workflow_definition_id", sa.Text(), nullable=False),
        sa.Column("temporal_workflow_id", sa.Text(), nullable=False),
        sa.Column("temporal_run_id", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("inputs_json", sa.Text(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["workflow_definition_id"], ["workflow_definitions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_workflow_runs_temporal_workflow_id", "workflow_runs", ["temporal_workflow_id"], unique=False)
    op.create_table(
        "execution_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("workflow_run_id", sa.Integer(), nullable=False),
        sa.Column("node_id", sa.Text(), nullable=False),
        sa.Column("step_type", sa.Text(), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["workflow_run_id"], ["workflow_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_execution_logs_workflow_run_id", "execution_logs", ["workflow_run_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_execution_logs_workflow_run_id", table_name="execution_logs")
    op.drop_table("execution_logs")
    op.drop_index("ix_workflow_runs_temporal_workflow_id", table_name="workflow_runs")
    op.drop_table("workflow_runs")
    op.drop_table("workflow_definitions")
