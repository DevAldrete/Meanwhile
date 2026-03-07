# Spec: Workflow definitions API

## Purpose

Provide a CRUD HTTP API for workflow definitions so the canvas can save and load graph data (name and graph JSON) and the Brain can execute them later.

## Prerequisites

- Specs 01–04 executed (package layout, database with `workflow_definitions` table, config, Docker).
- Load README.md for product context (Canvas → Workflows separation).
- **TDD:** Load the tessl__test-driven-development skill. Use red-green-refactor: write a failing test for each behavior first, then implement the minimum code to pass. One behavior per test; assert observable outcomes (HTTP status, response shape, DB state), not implementation details.

## Context

The Canvas produces a visual graph; the backend must store it as a workflow definition (name + graph payload). This spec adds only the API and persistence for definitions; it does not implement execution or the canvas UI.

## Changes

1. **Tests first (TDD).** For each endpoint below, write the test(s) before implementing: POST (201, validation failures 400, response shape), GET list (200, shape), GET by id (200, 404), PATCH (200, 404), DELETE (204, 404). Use FastAPI TestClient and a test DB or mocks; ensure tests fail for the right reason (missing endpoint or wrong behavior), then implement to pass.
2. **POST /api/workflow-definitions.** Request body: JSON with `name` (string) and `graph` (JSON object — the React Flow graph or equivalent serialization). Validate that `name` is non-empty and that `graph` is a JSON object. Create a row in `workflow_definitions` with `graph_json` set to the stringified or JSONB representation of `graph`. Return 201 with a representation that includes `id`, `name`, `graph` (or `graph_json`), `created_at`, `updated_at`. Use the DB session from the shared db module (spec 02).

3. **GET /api/workflow-definitions.** Return a list of all workflow definitions. Each item includes `id`, `name`, `graph` (parsed from `graph_json`), `created_at`, `updated_at`. Order by `updated_at` descending. Return 200 with a JSON array.

4. **GET /api/workflow-definitions/{id}.** Return a single definition by primary key. Include `id`, `name`, `graph`, `created_at`, `updated_at`. If not found, return 404. Return 200 on success.

5. **PATCH /api/workflow-definitions/{id}.** Request body: optional `name` (string), optional `graph` (JSON object). Update only the provided fields. If the definition does not exist, return 404. Return 200 with the full updated resource (same shape as GET by id).

6. **DELETE /api/workflow-definitions/{id}.** Delete the definition by id. If not found, return 404. Return 204 on success. Do not cascade-delete runs or logs in this spec; either define FK without cascade or leave runs/logs handling to a later spec (document the current behavior).

7. **OpenAPI tags and descriptions.** Tag these endpoints (e.g. `workflow-definitions`) and add short summary/description so the API docs are clear.

8. **Errors.** Use consistent HTTP status codes: 400 for validation errors (e.g. missing or invalid `name`/`graph`), 404 for missing resource, 503 if DB is unavailable (optional; FastAPI default 500 is acceptable if documented).

## Out of Scope

- Validating graph structure (e.g. node types, edges) beyond “must be a JSON object.”
- Execution of workflows or starting runs.
- Canvas UI or any frontend.
- Authentication or authorization.
- Pagination for GET list (MVP returns full list).

## Verification

Every check below is mandatory. Do not skip any.

1. **Positive:** POST with valid `name` and `graph` returns 201 and the response includes `id`, `name`, `graph`, `created_at`, `updated_at`; the row exists in `workflow_definitions`.
2. **Positive:** GET /api/workflow-definitions returns 200 and a JSON array; each element has the shape above.
3. **Positive:** GET /api/workflow-definitions/{id} for an existing id returns 200 with that definition; for a non-existent id returns 404.
4. **Positive:** PATCH with `name` and/or `graph` updates the row and returns 200 with the updated resource; PATCH to non-existent id returns 404.
5. **Positive:** DELETE for an existing id returns 204 and the row is removed; DELETE to non-existent id returns 404.
6. **Negative:** No endpoint in this spec starts a Temporal workflow or reads `workflow_runs` / `execution_logs`.
7. **Positive (TDD):** Each endpoint has tests that were written before or in lockstep with implementation; running the test suite shows green for all workflow-definitions API behaviors.

## Branch

`spec/05-workflow-definitions-api`

## Provenance

`specs/provenance/mvp/05-workflow-definitions-api.provenance.md` — overwrite on each execution; do not append.
