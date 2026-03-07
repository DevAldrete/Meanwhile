# Spec: Execution logs and history API

## Purpose

Expose HTTP endpoints to read execution logs for a run and to export execution history for time-travel debugging (download and replay locally).

## Prerequisites

- Specs 01–07 executed (workflow_runs, execution_logs, start run API).
- Load README.md (“Absolute transparency”, “Time-travel debugging”).
- **TDD:** Load the tessl__test-driven-development skill. Write failing tests first for: GET /api/runs list and filters, GET /api/runs/{id}, GET /api/runs/{id}/logs, GET /api/runs/{id}/history (404 for missing run). Then implement. One behavior per test; assert response status and body shape.

## Context

Users must see exactly what the AI was thinking and why a node failed; they must be able to download the exact execution history of a failed run and replay it locally. This spec adds read-only APIs for logs and history export.

## Changes

1. **GET /api/runs.** Query params: optional `workflow_definition_id` (filter by definition), optional `status`, optional `limit` (default cap e.g. 50). Return a list of runs (id, workflow_definition_id, temporal_workflow_id, temporal_run_id, status, started_at, finished_at). Order by started_at descending. Return 200. No pagination cursor required for MVP; `limit` is enough.

2. **GET /api/runs/{id}.** Return a single run by id (primary key of workflow_runs): id, workflow_definition_id, temporal_workflow_id, temporal_run_id, status, inputs_json, started_at, finished_at. Return 404 if not found. Return 200 on success.

3. **GET /api/runs/{id}/logs.** Return execution logs for this run. Each item: id, workflow_run_id, node_id, step_type, payload_json, created_at. Order by created_at ascending. Return 200 with a JSON array. If run id does not exist, return 404.

4. **GET /api/runs/{id}/history.** Export the execution history for time-travel. Use the Temporal client to fetch workflow history for the run’s temporal_workflow_id (and temporal_run_id if required). Return the history in a format suitable for replay (e.g. JSON payload that Temporal replay or the SDK can consume). Document in the response or in docs that this file can be used with “replay locally” (e.g. Temporal’s replay tooling). If the run does not exist or has no temporal_run_id yet, return 404. Return 200 with Content-Type application/json and a body that is the serialized history (or a wrapper with a “history” key). Do not require the run to be completed; in-progress runs can have partial history.

5. **OpenAPI.** Tag endpoints (e.g. runs, execution-logs) and add short descriptions. Document the purpose of /history for time-travel debugging.

6. **Performance.** For MVP, no special indexing beyond what spec 02 defined; if the list runs query is slow, note in provenance. Do not add caching in this spec.

## Out of Scope

- Writing or mutating logs from the API (logs are written only by the workflow/activities).
- Canvas or any UI (specs 08–10).
- Authentication or rate limiting (spec 11).
- Replay tooling implementation (only export; replay is local/user responsibility).

## Verification

Every check below is mandatory. Do not skip any.

1. **Positive:** GET /api/runs returns 200 and a JSON array of runs; with query param workflow_definition_id only runs for that definition are returned.
2. **Positive:** GET /api/runs/{id} for an existing run returns 200 with the run payload; for non-existent id returns 404.
3. **Positive:** GET /api/runs/{id}/logs returns 200 and a JSON array of execution_logs for that run, ordered by created_at; for non-existent run id returns 404.
4. **Positive:** GET /api/runs/{id}/history returns 200 with a JSON body suitable for history export (Temporal history format or documented wrapper); for a run without temporal_run_id or non-existent id returns 404.
5. **Negative:** No endpoint in this spec creates or updates runs or logs.
6. **Positive (TDD):** Tests for GET /runs, GET /runs/{id}, GET /runs/{id}/logs, GET /runs/{id}/history were written before or in lockstep with implementation; test suite is green.

## Branch

`spec/08-execution-logs-and-history-api`

## Provenance

`specs/provenance/mvp/08-execution-logs-and-history-api.provenance.md` — overwrite on each execution; do not append.
