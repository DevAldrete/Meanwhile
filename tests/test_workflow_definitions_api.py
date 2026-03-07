"""Tests for workflow definitions API (spec 05). TDD: one behavior per test."""

from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from meanwhile.api import create_app
from meanwhile.config import AppSettings
from meanwhile.db import WorkflowDefinition, get_session


# --- In-memory fake for workflow-definitions tests (no PostgreSQL required) ---


class FakeWorkflowDefinitionsStore:
    """In-memory store keyed by definition id. Used by fake session."""

    def __init__(self) -> None:
        self._by_id: dict[str, WorkflowDefinition] = {}
        self._next_id = 0

    def add(self, row: WorkflowDefinition) -> None:
        if not getattr(row, "id", None):
            self._next_id += 1
            row.id = f"fake-id-{self._next_id}"
        now = datetime.now(timezone.utc)
        if not getattr(row, "created_at", None):
            row.created_at = now
        if not getattr(row, "updated_at", None):
            row.updated_at = now
        self._by_id[row.id] = row

    def get(self, id: str) -> WorkflowDefinition | None:
        return self._by_id.get(id)

    def list_ordered_by_updated_at_desc(self) -> list[WorkflowDefinition]:
        return sorted(self._by_id.values(), key=lambda r: r.updated_at or r.created_at, reverse=True)

    def delete(self, id: str) -> bool:
        if id in self._by_id:
            del self._by_id[id]
            return True
        return False


def _make_fake_session(store: FakeWorkflowDefinitionsStore) -> AsyncSession:
    """Build an AsyncMock session that delegates to the in-memory store."""
    session = AsyncMock(spec=AsyncSession)

    def add_sync(instance: object) -> None:
        """Sync like real SQLAlchemy session.add; mutates row so id/created_at/updated_at are set."""
        if isinstance(instance, WorkflowDefinition):
            store.add(instance)

    async def flush() -> None:
        pass

    async def refresh(instance: object) -> None:
        pass

    async def get(entity: type, ident: str):
        if entity is WorkflowDefinition:
            return store.get(ident)
        return None

    async def execute(statement):
        if hasattr(statement, "column_descriptions"):
            rows = store.list_ordered_by_updated_at_desc()
            result = MagicMock()
            result.scalars = MagicMock(return_value=MagicMock(all=lambda: rows))
            return result
        return None

    async def delete(instance: object) -> None:
        if isinstance(instance, WorkflowDefinition):
            store.delete(instance.id)

    session.add = add_sync
    session.flush = flush
    session.refresh = refresh
    session.get = get
    session.execute = execute
    session.delete = delete
    return session


@pytest.fixture
def workflow_definitions_store() -> FakeWorkflowDefinitionsStore:
    """Fresh in-memory store per test."""
    return FakeWorkflowDefinitionsStore()


@pytest.fixture
async def db_session(workflow_definitions_store: FakeWorkflowDefinitionsStore) -> AsyncGenerator[AsyncSession, None]:
    """Fake async session backed by in-memory store."""
    yield _make_fake_session(workflow_definitions_store)


@pytest.fixture
async def app_workflow_definitions(db_session: AsyncSession):
    """App with get_session overridden to use the fake session."""
    app = create_app(
        settings=AppSettings(),
        temporal_client=AsyncMock(),
    )

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    return app


@pytest.fixture
def client_workflow_definitions(app_workflow_definitions):
    """TestClient for workflow-definitions API."""
    return TestClient(app_workflow_definitions)


# --- POST ---


def test_post_workflow_definition_returns_201_and_shape(client_workflow_definitions) -> None:
    """POST with valid name and graph returns 201 and response includes id, name, graph, created_at, updated_at."""
    payload = {"name": "My Flow", "graph": {"nodes": [], "edges": []}}
    with client_workflow_definitions as client:
        response = client.post("/api/workflow-definitions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "My Flow"
    assert data["graph"] == {"nodes": [], "edges": []}
    assert "created_at" in data
    assert "updated_at" in data


def test_post_workflow_definition_validation_empty_name_returns_422(client_workflow_definitions) -> None:
    """POST with empty name returns 422 (FastAPI validation)."""
    payload = {"name": "", "graph": {}}
    with client_workflow_definitions as client:
        response = client.post("/api/workflow-definitions", json=payload)
    assert response.status_code == 422


def test_post_workflow_definition_validation_graph_not_object_returns_422(client_workflow_definitions) -> None:
    """POST with graph that is not a JSON object (e.g. array) returns 422 (FastAPI validation)."""
    payload = {"name": "Flow", "graph": []}
    with client_workflow_definitions as client:
        response = client.post("/api/workflow-definitions", json=payload)
    assert response.status_code == 422


# --- GET list ---


def test_get_workflow_definitions_list_returns_200_and_array(client_workflow_definitions) -> None:
    """GET /api/workflow-definitions returns 200 and a JSON array."""
    with client_workflow_definitions as client:
        response = client.get("/api/workflow-definitions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


# --- GET by id ---


def test_get_workflow_definition_by_id_returns_200(client_workflow_definitions) -> None:
    """GET /api/workflow-definitions/{id} for existing id returns 200 with definition."""
    with client_workflow_definitions as client:
        create_resp = client.post(
            "/api/workflow-definitions",
            json={"name": "One", "graph": {"nodes": [{"id": "a"}]}},
        )
    assert create_resp.status_code == 201
    def_id = create_resp.json()["id"]
    with client_workflow_definitions as client:
        response = client.get(f"/api/workflow-definitions/{def_id}")
    assert response.status_code == 200
    assert response.json()["id"] == def_id
    assert response.json()["name"] == "One"
    assert response.json()["graph"] == {"nodes": [{"id": "a"}]}


def test_get_workflow_definition_by_id_returns_404(client_workflow_definitions) -> None:
    """GET /api/workflow-definitions/{id} for non-existent id returns 404."""
    with client_workflow_definitions as client:
        response = client.get("/api/workflow-definitions/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


# --- PATCH ---


def test_patch_workflow_definition_returns_200(client_workflow_definitions) -> None:
    """PATCH with name and/or graph updates the row and returns 200 with updated resource."""
    with client_workflow_definitions as client:
        create_resp = client.post(
            "/api/workflow-definitions",
            json={"name": "Original", "graph": {"x": 1}},
        )
    assert create_resp.status_code == 201
    def_id = create_resp.json()["id"]
    with client_workflow_definitions as client:
        response = client.patch(
            f"/api/workflow-definitions/{def_id}",
            json={"name": "Updated", "graph": {"x": 2}},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated"
    assert data["graph"] == {"x": 2}


def test_patch_workflow_definition_returns_404(client_workflow_definitions) -> None:
    """PATCH to non-existent id returns 404."""
    with client_workflow_definitions as client:
        response = client.patch(
            "/api/workflow-definitions/00000000-0000-0000-0000-000000000000",
            json={"name": "X"},
        )
    assert response.status_code == 404


# --- DELETE ---


def test_delete_workflow_definition_returns_204(client_workflow_definitions) -> None:
    """DELETE for existing id returns 204 and the row is removed."""
    with client_workflow_definitions as client:
        create_resp = client.post(
            "/api/workflow-definitions",
            json={"name": "To Delete", "graph": {}},
        )
    assert create_resp.status_code == 201
    def_id = create_resp.json()["id"]
    with client_workflow_definitions as client:
        response = client.delete(f"/api/workflow-definitions/{def_id}")
    assert response.status_code == 204
    with client_workflow_definitions as client:
        get_resp = client.get(f"/api/workflow-definitions/{def_id}")
    assert get_resp.status_code == 404


def test_delete_workflow_definition_returns_404(client_workflow_definitions) -> None:
    """DELETE to non-existent id returns 404."""
    with client_workflow_definitions as client:
        response = client.delete("/api/workflow-definitions/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
