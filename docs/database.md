# Database

Meanwhile uses PostgreSQL with async SQLAlchemy (asyncpg) and Alembic for migrations.

## Running migrations

From project root:

```bash
uv run alembic upgrade head
```

To reverse the last migration:

```bash
uv run alembic downgrade -1
```

Then to re-apply:

```bash
uv run alembic upgrade head
```

## Schema (MVP)

- **workflow_definitions** — Stored workflow definitions (the graph from the canvas). One row per definition; `graph_json` holds the graph payload.
- **workflow_runs** — One row per run of a workflow; links to a definition and stores Temporal workflow/run ids, status, and inputs.
- **execution_logs** — Per-step execution data for a run (node_id, step_type, payload with prompt/tokens/raw output, etc.); indexed by `workflow_run_id`.
