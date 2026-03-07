# Spec: Config and Temporal connectivity

## Purpose

Ensure the Meanwhile backend reads all runtime configuration from the environment and that the API and worker share the same Temporal connection settings and task queue.

## Prerequisites

- Specs 01 and 02 executed (package layout and database with config supporting `database_url` or equivalent).
- Load README.md for architecture (Temporal cluster, task queue, MeanWhile Brain).

## Context

The app and worker must connect to the same Temporal namespace and task queue and use the same DB URL. Config must be env-driven for production (e.g. Railway) and support local defaults for development. This spec does not add new workflows or activities; it only makes config explicit and consistent.

## Changes

1. **Centralize settings in one config module.** Use the existing `meanwhile.config` (or the module chosen in spec 01) as the single source of truth for: Temporal target, namespace, task queue; database URL; and any existing settings (e.g. Pydantic-AI model). All values must be read from environment variables with sensible defaults for local development. Document the env vars in README or in a single `docs/config.md` (e.g. `TEMPORAL_TARGET`, `TEMPORAL_NAMESPACE`, `TEMPORAL_TASK_QUEUE`, `DATABASE_URL`, and any existing ones).

2. **No hardcoded secrets or hostnames in code.** Ensure no default in code uses a production URL or secret; local defaults (e.g. `localhost:7233`, `localhost:5432`) are acceptable. Production must set env vars.

3. **API and worker use the same config.** The FastAPI app and the Temporal worker must both obtain Temporal target, namespace, and task queue from the same `get_settings()` (or equivalent) so they always agree. No duplicate definition of task queue or target in different files.

4. **Health check reflects Temporal connectivity.** The existing `/api/health` (or equivalent) must require a successful Temporal client connection to return 200. If Temporal is unavailable, return 503. No new health endpoints are required unless the current one does not already reflect Temporal.

5. **Document how to run worker and API.** In README or docs, add one sentence each for: (a) starting the API (e.g. `uv run meanwhile-api`), (b) starting the worker (e.g. `uv run meanwhile-worker`), (c) that both require the same env (or same `.env` file) for Temporal and DB.

## Out of Scope

- Adding new Temporal workflows or activities.
- Database migrations or new tables.
- Rate limiting, auth, or deployment automation (later specs).

## Verification

Every check below is mandatory. Do not skip any.

1. **Positive:** All Temporal and database-related settings are read from environment variables (or a single env-loaded settings object); no literal production URLs or secrets in source.
2. **Positive:** The API and the worker import and use the same config function for Temporal target, namespace, and task queue.
3. **Positive:** With Temporal unavailable, the health endpoint returns 503 (or equivalent); with Temporal available, it returns 200.
4. **Positive:** README or docs list the required env vars and the commands to run the API and worker.
5. **Negative:** No duplicate definition of task queue or Temporal target in separate modules.

## Branch

`spec/03-config-and-temporal`

## Provenance

`specs/provenance/mvp/03-config-and-temporal.provenance.md` — overwrite on each execution; do not append.
