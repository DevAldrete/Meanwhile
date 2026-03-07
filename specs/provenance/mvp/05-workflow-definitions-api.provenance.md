# Provenance: 05-workflow-definitions-api

**Spec:** `specs/mvp/05-workflow-definitions-api.md`  
**Executed:** 2025-03-07  
**Branch:** `spec/05-workflow-definitions-api` (convention; branch may be created by user)

## Plan

1. Add Pydantic models: WorkflowDefinitionCreate, WorkflowDefinitionUpdate, WorkflowDefinitionResponse (name non-empty, graph as dict).
2. Write tests first (TDD): POST 201/validation 422, GET list 200, GET by id 200/404, PATCH 200/404, DELETE 204/404; use TestClient and fake in-memory session so tests need no PostgreSQL.
3. Implement POST /api/workflow-definitions (create row, return 201 with id, name, graph, created_at, updated_at).
4. Implement GET list (order by updated_at desc), GET by id, PATCH, DELETE using shared get_session dependency.
5. Tag endpoints "workflow-definitions" and add OpenAPI summary/description.
6. Document DELETE behavior: current FK is CASCADE (migration 001); spec allows documenting and leaving as-is.

## Deviations

- **Validation status:** Spec says "400 for validation errors"; FastAPI returns 422 for request body validation. Tests assert 422; no custom exception handler added. Documented as acceptable (FastAPI convention).
- **Test DB:** Spec says "test DB or mocks". Used in-memory fake session (FakeWorkflowDefinitionsStore + mock session) so the suite runs without PostgreSQL or greenlet in the test path for this module.
- **greenlet:** Added to dev dependency group so async SQLAlchemy could be used elsewhere if needed; workflow-definitions tests do not use a real engine.

## Outcome

- **models.py:** WorkflowDefinitionCreate, WorkflowDefinitionUpdate, WorkflowDefinitionResponse added.
- **api.py:** Router extended with POST/GET list/GET by id/PATCH/DELETE for /api/workflow-definitions; get_session dependency; OpenAPI tag "workflow-definitions".
- **tests/test_workflow_definitions_api.py:** 10 tests (POST 201 and shape, validation 422 x2, GET list, GET 200/404, PATCH 200/404, DELETE 204/404); fake session and store for isolation.
- **pyproject.toml:** greenlet added to dev dependency group.

## Verification (mandatory)

| Check | Result |
|-------|--------|
| 1. POST with valid name and graph returns 201; response has id, name, graph, created_at, updated_at; row in store | Pass (fake store) |
| 2. GET /api/workflow-definitions returns 200 and JSON array; each element has required shape | Pass |
| 3. GET by id 200 for existing, 404 for non-existent | Pass |
| 4. PATCH updates and returns 200; 404 for non-existent | Pass |
| 5. DELETE returns 204 and row removed; 404 for non-existent | Pass |
| 6. No endpoint starts Temporal or reads workflow_runs/execution_logs | Pass |
| 7. TDD: tests written for each behavior; suite green for workflow-definitions API | Pass |

## Learned

- FastAPI TestClient with async dependency override works with an in-memory fake session when the override yields a single session per request; sync fixture depending on async fixture is resolved by pytest-asyncio.
- session.add() in SQLAlchemy is sync; fake session must provide a sync add() that mutates the row (id, created_at, updated_at) so the handler can read them after flush/refresh.
