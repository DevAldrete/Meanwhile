# Spec: Start run API

## Purpose

Expose an HTTP endpoint that starts a workflow run for a given workflow definition and returns the run id and status so the UI can trigger executions and poll or link to run details.

## Prerequisites

- Specs 01–06 executed (definitions API, interpreter workflow, workflow_runs and execution_logs).
- Load README.md for product context.
- **TDD:** Load the tessl__test-driven-development skill. Write failing tests first for: POST returns 202 and run id, POST with invalid definition id returns 404, Temporal unavailable returns 503. Then implement. One behavior per test; use TestClient and mock Temporal client where appropriate.

## Context

The canvas (or a “Run” button) needs to start an execution of a saved workflow definition. The Brain (interpreter workflow) already creates a row in workflow_runs and runs the graph. This spec adds the API that (1) accepts a definition id and optional inputs, (2) starts the interpreter workflow via the Temporal client, (3) returns immediately with run identification (e.g. workflow_run id, temporal_workflow_id, temporal_run_id, status) so the client can show “running” and later navigate to logs.

## Changes

1. **POST /api/workflow-definitions/{id}/run.** Path parameter: workflow definition id (UUID or integer per schema). Request body: JSON with optional `inputs` (object). Validate that the definition exists (return 404 if not). Start the interpreter workflow (from spec 06) with this definition id and the given inputs (or {}). Do not wait for the workflow to complete; start it and return. Response 202 Accepted with a body that includes at least: run id (primary key of the created workflow_runs row, or the temporal_workflow_id if the run row is created inside the workflow), temporal_workflow_id, temporal_run_id if available, status (e.g. "running"). If the run row is created by the workflow asynchronously, the API may need to return temporal_workflow_id and optionally poll or return a placeholder run id; document the exact response shape. Prefer creating the workflow_runs row in the API before starting the workflow so the API can return the run id immediately (then the workflow updates the same row with temporal_run_id when it starts). If that requires passing run id into the workflow, do so.

2. **Idempotency and concurrency.** For MVP, each POST creates a new run. No idempotency key required. Document that multiple POSTs create multiple runs.

3. **Errors.** Return 404 if the workflow definition id does not exist. Return 503 if Temporal client is unavailable (same pattern as existing chat endpoint). Return 400 if request body is invalid (e.g. inputs not an object when provided).

4. **OpenAPI.** Tag the endpoint (e.g. runs or workflow-definitions) and describe that it starts an execution and returns run identification.

5. **Optional: GET /api/workflow-definitions/{id}/runs.** Return a list of runs for this definition (workflow_runs where workflow_definition_id = id), ordered by started_at descending. Each item: run id, temporal_workflow_id, temporal_run_id, status, started_at, finished_at. Return 200. If the definition does not exist, return 404. This is optional for MVP; include it only if it fits within the “single coherent purpose” of this spec (start run + list runs for a definition). If the spec would exceed ~10 changes without it, drop GET list from this spec and add a short “Out of Scope” note that listing runs can be a separate spec or part of the execution list UI spec.

## Out of Scope

- Execution logs or history (spec 08).
- Canvas UI (spec 09).
- Polling or webhooks for completion; client polls run status or logs separately.
- Authentication.

## Verification

Every check below is mandatory. Do not skip any.

1. **Positive:** POST to /api/workflow-definitions/{valid_id}/run with valid body returns 202 and a response containing run identification (run id and/or temporal_workflow_id, status).
2. **Positive:** A new row exists in workflow_runs for that definition with status “running” (or equivalent) and the returned ids match.
3. **Positive:** POST with non-existent definition id returns 404.
4. **Positive:** When Temporal is unavailable, the endpoint returns 503 (or the app’s standard Temporal-unavailable behavior).
5. **Negative:** This spec does not add endpoints for reading execution logs or workflow history export.
6. **Positive (TDD):** Tests for POST /run (202, 404, 503) were written before or in lockstep with implementation; test suite is green.

## Branch

`spec/07-start-run-api`

## Provenance

`specs/provenance/mvp/07-start-run-api.provenance.md` — overwrite on each execution; do not append.
