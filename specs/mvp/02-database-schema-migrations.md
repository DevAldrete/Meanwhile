# Spec: Database schema and migrations

## Purpose

Introduce a PostgreSQL schema and Alembic migrations for workflow definitions, workflow runs, and execution logs so the rest of the MVP can persist and query this data.

## Prerequisites

- Spec 01 (backend package layout) executed so that the `meanwhile` package and runnability are established.
- Load README.md for tech stack (SQLAlchemy, PostgreSQL, Alembic).
- Backend uses async drivers: asyncpg and SQLAlchemy async where applicable (per README and existing dependencies).

## Context

Meanwhile stores (1) workflow definitions (the graph from the canvas), (2) runs of those workflows (each execution), and (3) execution logs (per-step data: prompts, token counts, raw LLM output, etc.) for transparency and time-travel. The README states that execution history is durably saved. This spec defines the tables and migrations only; no API or application logic.

## Changes

1. **Database connection configuration.** Add settings for the database URL (e.g. `database_url` or `DATABASE_URL`) to the existing config module used by the app (e.g. `meanwhile.config`). Use environment variables for production; support a default for local dev (e.g. `postgresql+asyncpg://meanwhile_user:meanwhile_pass@localhost:5432/meanwhile_db` to align with the existing `docker-compose.yml` if present). Do not change the existing Temporal or Pydantic-AI settings beyond adding DB settings.

2. **SQLAlchemy metadata and async engine.** Introduce a single place (e.g. a `meanwhile.db` or `meanwhile.models.db` module) that defines the SQLAlchemy declarative base and provides an async engine and session factory bound to the configured database URL. Use `create_async_engine` and async session; expose a way for the FastAPI app to get a session (e.g. dependency or context manager) that will be used in later specs.

3. **Table: workflow_definitions.** Columns: `id` (UUID or bigint primary key), `name` (text, nullable or not per product choice), `graph_json` (JSONB or text), `created_at` (timestamp with time zone), `updated_at` (timestamp with time zone). No other tables in this spec reference workflow_definitions by name; the name is the single source of truth for this table.

4. **Table: workflow_runs.** Columns: `id` (primary key), `workflow_definition_id` (FK to workflow_definitions), `temporal_workflow_id` (text), `temporal_run_id` (text, nullable), `status` (text, e.g. running, completed, failed), `inputs_json` (JSONB or text), `started_at`, `finished_at` (nullable). Index or unique constraint on `temporal_workflow_id` if appropriate for lookups.

5. **Table: execution_logs.** Columns: `id` (primary key), `workflow_run_id` (FK to workflow_runs), `node_id` (text, from the graph), `step_type` (text, e.g. activity, decision), `payload_json` (JSONB for prompt, tokens, raw output, etc.), `created_at`. Support querying by `workflow_run_id` (index).

6. **Alembic.** Initialize Alembic in the project if not already present. Configure Alembic to use the same database URL as the app (from config) and to discover the declarative base and tables from the same module used in step 2. Create one initial migration that creates the three tables (workflow_definitions, workflow_runs, execution_logs). Migration must be reversible (downgrade drops the tables).

7. **Documentation.** In README or a single `docs/database.md`, document how to run migrations (e.g. `uv run alembic upgrade head`) and the schema purpose in one sentence per table.

## Out of Scope

- API endpoints or business logic that read/write these tables.
- Temporal workflow or activity code.
- Seed data or fixtures (optional; not required by this spec).
- Changing docker-compose or deployment; use existing DB URL pattern only.

## Verification

Every check below is mandatory. Do not skip any.

1. **Positive:** `uv run alembic upgrade head` runs successfully and creates or updates the database to include `workflow_definitions`, `workflow_runs`, and `execution_logs`.
2. **Positive:** `uv run alembic downgrade -1` (or equivalent) reverses the migration and removes those tables (or leaves DB in a prior state); `upgrade head` again succeeds.
3. **Positive:** The application config exposes a database URL and the async engine/session factory use it without hardcoding credentials in code.
4. **Positive:** At least one place in the codebase (e.g. the new db module) defines the three tables with the columns specified above; Alembic migration reflects that definition.
5. **Negative:** No API routes or Temporal code in this spec; only schema, config, engine, and migrations.

## Branch

`spec/02-database-schema-migrations`

## Provenance

`specs/provenance/mvp/02-database-schema-migrations.provenance.md` — overwrite on each execution; do not append.
