# Meanwhile MVP — Spec Suite

This directory contains the full suite of specifications for building the Meanwhile MVP and taking it to production, following [Spec-Driven Development](../../.tessl/tiles/kevin-ryan-io/spec-driven-development/README.md).

## Execution order

Specs are designed to be executed in order. Later specs assume the outcomes of earlier ones.

| Order | Spec | Purpose |
|-------|------|--------|
| 1 | [01-backend-package-layout](mvp/01-backend-package-layout.md) | Canonical Python package layout and runnability |
| 2 | [02-database-schema-migrations](mvp/02-database-schema-migrations.md) | PostgreSQL schema and Alembic migrations for definitions, runs, logs |
| 3 | [03-config-and-temporal](mvp/03-config-and-temporal.md) | Env-based config and Temporal connectivity |
| 4 | [04-docker-and-docker-compose](mvp/04-docker-and-docker-compose.md) | Docker images and Docker Compose for local stack |
| 5 | [05-workflow-definitions-api](mvp/05-workflow-definitions-api.md) | CRUD API for workflow definitions (canvas graphs) — **TDD** |
| 6 | [06-workflow-interpreter-and-logging](mvp/06-workflow-interpreter-and-logging.md) | Brain: interpreter workflow and execution logging — **TDD** |
| 7 | [07-start-run-api](mvp/07-start-run-api.md) | API to start a workflow run from a definition — **TDD** |
| 8 | [08-execution-logs-and-history-api](mvp/08-execution-logs-and-history-api.md) | Read execution logs and export history for time-travel — **TDD** |
| 9 | [09-canvas-ui](mvp/09-canvas-ui.md) | Visual canvas (React Flow) and save/load definitions |
| 10 | [10-run-and-execution-list-ui](mvp/10-run-and-execution-list-ui.md) | Trigger run and list executions in the UI |
| 11 | [11-execution-detail-and-time-travel-ui](mvp/11-execution-detail-and-time-travel-ui.md) | Execution detail view and time-travel download |
| 12 | [12-rate-limiting-and-api-safety](production/12-rate-limiting-and-api-safety.md) | SlowAPI rate limiting and API safety |
| 13 | [13-railway-deployment](production/13-railway-deployment.md) | Deploy API, worker, and frontend to Railway |

## Provenance

After each execution, write the provenance record to the path specified in the spec (overwrite, do not append). Convention:

- `specs/provenance/mvp/<spec-name>.provenance.md`
- `specs/provenance/production/<spec-name>.provenance.md`

Use `git log --follow` on a provenance file to see full history.

## Context sources

- **Intent**: These specs; README.md product vision.
- **Method**: SDD skill; tessl__frontend-design for UI specs; temporal-python-testing for workflow tests; tessl__test-driven-development for specs marked **TDD** (05–08).
- **State**: Provenance files; codebase after each execution.
