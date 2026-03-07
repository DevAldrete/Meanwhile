# Provenance: 04-docker-and-docker-compose

**Spec:** `specs/mvp/04-docker-and-docker-compose.md`  
**Executed:** 2025-03-06  
**Branch:** `spec/04-docker-and-docker-compose` (convention; branch may be created by user)

## Plan

1. Create a single-stage Dockerfile at project root: Python 3.13-slim, install uv, copy pyproject.toml/uv.lock and sync deps, copy `meanwhile/` and `main.py`, install project, set PYTHONPATH=/app, default CMD `uv run meanwhile-api`, expose 8000.
2. Use the same image for the worker by overriding command to `uv run meanwhile-worker` in docker-compose.
3. Extend docker-compose: fix db healthcheck to `pg_isready -U meanwhile_user -d meanwhile_db`; add api and worker services building from the Dockerfile, image name `meanwhile-backend`, env from .env with DATABASE_URL overridden to use host `db`, TEMPORAL_TARGET default `host.docker.internal:7233`, healthcheck for api hitting GET /api/health.
4. Document Temporal on host (not in compose): run `temporal server start-dev` on host, point containers at host via TEMPORAL_TARGET.
5. Document migrations: run from host with DATABASE_URL=localhost:5432 after db is up.
6. Add .dockerignore excluding .venv, .git, **pycache**, tests, web, docs, specs, .env, alembic (pyproject.toml and uv.lock kept for build).
7. Add docs/docker.md and a short Docker section in README (run stack, env, migrations, frontend out of scope).

## Deviations

- **PYTHONPATH:** The installed console script `meanwhile-api` (main:main) could not import `main` inside the container because the project root was not on `sys.path`. Added `ENV PYTHONPATH=/app` in the Dockerfile so the script finds `main.py`. No spec change required; the spec already required the default command to run the API.
- **env_file:** Compose uses `env_file: .env`. If `.env` is missing, Compose still starts; we set explicit `environment` with defaults so DATABASE_URL and TEMPORAL_* work. No deviation from spec.

## Outcome

- **Dockerfile:** Added at project root; builds and runs API/worker with `uv run meanwhile-api` / `uv run meanwhile-worker`.
- **docker-compose.yml:** db healthcheck fixed; api and worker added, same image `meanwhile-backend`, different commands; DATABASE_URL points at `db:5432`; healthcheck for api uses `curl` to GET /api/health.
- **.dockerignore:** Added; excludes .venv, .git, **pycache**, tests, web, docs, specs, .env, alembic (and similar); keeps pyproject.toml and uv.lock.
- **Documentation:** `docs/docker.md` added (full stack, Temporal on host, env vars, migrations, manual build/run, frontend out of scope). README updated with a short Docker subsection pointing to docs/docker.md.

## Verification (mandatory)

| Check | Result |
|-------|--------|
| 1. `docker compose build` builds backend image without error | Pass |
| 2. `docker compose up -d db` brings up PostgreSQL; db healthcheck passes | Pass (`docker compose ps` shows db healthy) |
| 3. With DB up, `docker compose up api worker` starts API and worker; GET /api/health returns 200 when Temporal available or 503 when not | Pass (503 when Temporal not in compose) |
| 4. Same image for api and worker (same image name, different command) | Pass (`meanwhile-backend`) |
| 5. .dockerignore exists and excludes .venv, .git, and other non-runtime paths | Pass |
| 6. No secrets or production credentials in Dockerfile or compose; credentials from env/.env | Pass |

## Learned

- For setuptools console scripts that reference a top-level module (e.g. `main:main`) not part of the installed package, the container needs the project root on PYTHONPATH so the script can import that module after install.
