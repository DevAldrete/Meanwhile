# Provenance: Spec 01 — Backend package layout and runnability

## Spec executed

`specs/mvp/01-backend-package-layout.md`

## Plan

1. Point `main.py` imports from `src.*` to `meanwhile.*`.
2. Remove `sys.path` manipulation from `tests/conftest.py`.
3. Add `[build-system]` and restrict package discovery to `meanwhile*` in `pyproject.toml` so `uv sync` installs the package and `web`/`specs` are not included.
4. Add a "Development" section to README describing package location and run commands.

## Deviations

None.

## Outcome

- **Positive:** `uv run python -c "from meanwhile.api import create_app; print('ok')"` exits 0 and prints `ok`.
- **Positive:** `uv run pytest tests/ -v` runs and all tests pass.
- **Positive:** README documents where the `meanwhile` package lives and how to run the API and worker from project root.
- **Negative:** No test file or conftest adds project root or `src` to `sys.path` for `import meanwhile`.
- **Positive:** `pyproject.toml` lists script entry points `meanwhile-api` and `meanwhile-worker`; `uv sync` succeeds.

All mandatory checks satisfied.
