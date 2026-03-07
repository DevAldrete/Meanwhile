# Spec: Backend package layout and runnability

## Purpose

Establish a single, canonical Python package layout for the Meanwhile backend so that imports, tests, and CLI entrypoints work from project root with no ambiguity.

## Prerequisites

- Load README.md for product context.
- Verify project root contains `pyproject.toml`, `main.py`, and a directory that holds the backend code (currently `src/` with modules like `api.py`, `workflows.py`).

## Context

The README describes a backend (MeanWhile Brain) using FastAPI, Temporal, and PostgreSQL. The codebase currently uses the package name `meanwhile` in imports (e.g. `from meanwhile.api import create_app`). The physical layout must match this import structure so that `uv run`, `pytest`, and `meanwhile-api` / `meanwhile-worker` work from the project root without ad-hoc `PYTHONPATH` or path hacks in production. This spec makes the package layout explicit and runnable.

## Changes

1. **Define the package root.** Ensure the Python package named `meanwhile` is discoverable from the project root. If the project uses a flat `src/` with no `meanwhile` subpackage, add a `meanwhile` package (e.g. `src/meanwhile/`) and move or re-export existing modules so that `import meanwhile` and `from meanwhile.api import ...` resolve correctly. Alternatively, configure the build system (e.g. in `pyproject.toml`) so that the package name `meanwhile` maps to the existing `src` directory if the tooling supports it. Document the chosen layout in this spec or in a single `docs/backend-layout.md` (or a short section in README) so future agents and humans know the single source of truth.

2. **Align `pyproject.toml` with the layout.** Ensure `[project.scripts]` entry points `meanwhile-api` and `meanwhile-worker` reference the correct module paths (e.g. `main:main` and `main:worker_main`) and that the package containing `meanwhile` is installed in editable/development mode when using `uv run` from the project root.

3. **Remove or replace path manipulation in tests.** If `tests/conftest.py` or similar modifies `sys.path` to force imports to work, remove that once the package layout is correct. Tests must import via `meanwhile.*` after running from project root (e.g. `uv run pytest`).

4. **Verify runnability.** Add or update a minimal verification that (a) `uv run python -c "from meanwhile.api import create_app; print('ok')"` succeeds, (b) `uv run meanwhile-api` starts the API (or document the exact command), and (c) `uv run pytest tests/` runs the test suite. Document the exact commands in README or in a single "Development" or "Running" section.

## Out of Scope

- Changing the frontend (`web/`) or any non-Python layout.
- Adding new API endpoints or workflows.
- Database or Temporal configuration (covered in later specs).
- Renaming the project or the package to something other than `meanwhile`.

## Verification

Every check below is mandatory. Do not skip any.

1. **Positive:** From project root, `uv run python -c "from meanwhile.api import create_app; print('ok')"` exits with code 0 and prints `ok`.
2. **Positive:** From project root, `uv run pytest tests/ -v` runs and all tests pass (or the only failures are documented environment assumptions, e.g. no Temporal server).
3. **Positive:** A single document or README section describes where the `meanwhile` package lives and how to run the API and worker from project root.
4. **Negative:** No test file or conftest adds the project root or `src` to `sys.path` in a way that would be required for `import meanwhile` to work if the package were not properly installed.
5. **Positive:** `pyproject.toml` lists the correct script entry points and the package is installable (e.g. `uv sync` succeeds).

## Branch

`spec/01-backend-package-layout`

## Provenance

`specs/provenance/mvp/01-backend-package-layout.provenance.md` — overwrite on each execution; do not append.
