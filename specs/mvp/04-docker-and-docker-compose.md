# Spec: Docker and Docker Compose

## Purpose

Add Docker images for the Meanwhile API and worker and extend Docker Compose so the full stack (PostgreSQL, API, worker, and optionally Temporal) can run locally with one command.

## Prerequisites

- Specs 01–03 executed (package layout, database schema and migrations, config from env).
- Load README.md for tech stack and architecture.

## Context

The project already has a `docker-compose.yml` with PostgreSQL. For consistent local development and for production-style runs, the API and worker should be containerized. This spec adds Dockerfiles and composes them with the existing DB (and optionally a Temporal service) so developers can run `docker compose up` and have a working backend.

## Changes

1. **Backend Dockerfile.** Create a Dockerfile at the project root (or in a `docker/` directory) that builds the Meanwhile backend. It must: (a) use a Python base image compatible with the project (e.g. Python 3.13), (b) install dependencies via `uv` or `pip` from `pyproject.toml`, (c) copy the application code (the `meanwhile` package and `main.py`), (d) expose the API port (e.g. 8000), (e) set the default command to run the API (e.g. `uv run meanwhile-api` or `uvicorn`). Document in comments or a short README section how to build and run the image (e.g. `docker build -t meanwhile-api .` and which env vars are required at runtime).

2. **Worker as same image, different command.** Use the same image for the worker by overriding the command (e.g. `uv run meanwhile-worker`). Do not require a second Dockerfile unless there is a strong reason (e.g. different base). Document that the worker container needs the same env vars as the API (DATABASE_URL, TEMPORAL_*).

3. **Extend docker-compose.yml.** Add services: (a) **api** — build from the backend Dockerfile, command to run the API, depends_on db (and optionally temporal), environment from env_file or explicit variables (DATABASE_URL pointing to the db service, TEMPORAL_TARGET if Temporal is in the compose), ports 8000:8000, healthcheck that hits /api/health if available; (b) **worker** — same image as api, command to run the worker, depends_on db (and optionally temporal), same env. Fix the existing db healthcheck if incorrect (e.g. `pg_isready -U meanwhile_user -d meanwhile_db` not `-d meanwhile_pass`). Ensure the db service is named so DATABASE_URL can use hostname `db` and port 5432.

4. **Temporal in Compose (optional).** Either add a Temporal server service to docker-compose (e.g. temporalio/auto-setup or official Temporal Docker images) so that `docker compose up` brings up DB + Temporal + API + worker, or document that Temporal must be run separately (e.g. `temporal server start-dev`) and TEMPORAL_TARGET set to host.docker.internal or the host IP. Prefer one of: (a) Temporal in compose with api/worker depending on it, or (b) clear docs that Temporal runs on the host and how to point containers at it. Do not leave Temporal unspecified.

5. **Migrations at startup (optional).** Either document that the user must run `uv run alembic upgrade head` before or after starting the stack, or add an init container / entrypoint script that runs migrations when the api (or worker) starts. If migrations run in the same container as the API, ensure the DB is reachable and migrations complete before the API listens (e.g. wait-for-it or a startup script). This step is optional for MVP; documenting a manual migration step is acceptable.

6. **.dockerignore.** Add a .dockerignore at the Docker build context root to exclude .venv, .git, __pycache__, tests (if not needed in image), web (frontend), and other files that should not be copied into the image. This keeps the image smaller and avoids invalidating the cache unnecessarily.

7. **Documentation.** In README or docs/docker.md, add: (a) how to run the full stack (`docker compose up`), (b) required env vars and where to set them (e.g. .env.example), (c) how to run migrations when using Docker, (d) that the frontend (web/) is not part of this compose for MVP (or add a frontend service that builds and serves the SPA; if added, document it).

## Out of Scope

- Frontend in Docker (can be added in a later spec).
- Production orchestration (Kubernetes, etc.); this spec is for local/dev Docker Compose.
- Multi-stage builds for minimal image size (optional; single-stage is acceptable).
- Docker Compose profiles for “api only” vs “full stack”; a single default compose is enough.

## Verification

Every check below is mandatory. Do not skip any.

1. **Positive:** `docker compose build` (or `docker compose up --build`) builds the backend image without error.
2. **Positive:** `docker compose up -d db` brings up PostgreSQL; the db healthcheck passes (e.g. `docker compose ps` shows db healthy).
3. **Positive:** With DB (and Temporal if in compose) up, `docker compose up api worker` (or `docker compose up`) starts the API and worker; the API responds to GET /api/health with 200 when Temporal is available (or 503 if Temporal is not in compose and not provided).
4. **Positive:** The same image is used for both api and worker services (same image name, different command).
5. **Positive:** A .dockerignore exists and excludes .venv, .git, and other non-runtime paths from the build context.
6. **Negative:** No secrets or production credentials are baked into the Dockerfile or compose file; credentials come from env or .env.

## Branch

`spec/04-docker-and-docker-compose`

## Provenance

`specs/provenance/mvp/04-docker-and-docker-compose.provenance.md` — overwrite on each execution; do not append.
