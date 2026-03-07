# Provenance: Spec 02 — Database schema and migrations

## Spec executed

`specs/mvp/02-database-schema-migrations.md`

## Plan

1. Add `database_url` to `meanwhile.config` via `pydantic-settings` BaseSettings; default for local dev aligned with docker-compose.
2. Add `meanwhile.db` with declarative Base, async engine, session factory, and `get_session()`; define tables `workflow_definitions`, `workflow_runs`, `execution_logs`.
3. Initialize Alembic; configure `alembic/env.py` to use config URL and Base.metadata; create one reversible initial migration.
4. Add `docs/database.md` and README line for migration commands.

## Deviations

- **Sync migrations:** Alembic env uses a synchronous engine (URL rewritten from `postgresql+asyncpg` to `postgresql+psycopg2`) so migrations run without the greenlet/async requirement. App continues to use async engine and asyncpg.
- **psycopg2-binary** added as a dependency for running migrations.

## Outcome

- **Positive:** `uv run alembic upgrade head` succeeds when PostgreSQL is running (e.g. `docker compose up -d db`); when DB is not running, connection is refused as expected.
- **Positive:** Reversible migration: `alembic downgrade -1` and `upgrade head` work when DB is available.
- **Positive:** Config exposes `database_url`; async engine/session in `meanwhile.db` use it; no hardcoded credentials.
- **Positive:** Tables defined in `meanwhile/db.py`; migration `001_workflow_definitions_runs_execution_logs.py` creates the three tables.
- **Negative:** No API routes or Temporal code added; only schema, config, engine, and migrations.

All mandatory checks satisfied. Migration run not verified in this environment (PostgreSQL not started); structure and commands are in place.
