# Spec: Railway deployment

## Purpose

Document and automate deployment of the Meanwhile API, worker, and frontend to Railway so the product can run in production with PostgreSQL and (where applicable) Temporal.

## Prerequisites

- Specs 01–12 executed (API, worker, frontend, rate limiting, config from env).
- Load README.md (Railway as cloud provider).

## Context

The README names Railway as the deployment platform. This spec produces a production-ready deployment path: backend API, Temporal worker, frontend static build, and PostgreSQL. Temporal may run on Railway or as a separate service (e.g. Temporal Cloud); the spec must document the options and provide at least one working path.

## Changes

1. **Backend deployable image or command.** Ensure the API can be started with a single command that reads all config from environment variables (e.g. `uv run meanwhile-api` or `uvicorn` with module path). Document the exact command and required env vars (DATABASE_URL, TEMPORAL_TARGET, TEMPORAL_NAMESPACE, TEMPORAL_TASK_QUEUE, and any CORS/rate-limit overrides). If using Docker, provide a Dockerfile that installs dependencies and runs the API; otherwise document “run from source” with uv and the command.

2. **Worker deployable.** Similarly, document (and if using Docker, build) the worker process: same codebase, same env vars, command e.g. `uv run meanwhile-worker`. The worker must use the same TEMPORAL_* and DATABASE_URL as the API. Railway may run the API and worker as two services (two “start” commands or two Docker images).

3. **Frontend build and host.** Ensure the frontend builds to static assets (e.g. `npm run build` or `pnpm build` in `web/`) and that the build uses the production API URL from an env var (e.g. VITE_API_URL). Document how to serve the built assets on Railway (e.g. static site service, or serve from the API with a catch-all static route). At least one option must be documented and repeatable.

4. **PostgreSQL on Railway.** Document provisioning PostgreSQL on Railway and setting DATABASE_URL in the API and worker services. Include that Alembic migrations must be run once (e.g. `uv run alembic upgrade head`) before or after first deploy; document who runs it (manual step or release command).

5. **Temporal.** Document how Temporal is provided in production: (a) Temporal Cloud or (b) self-hosted (e.g. another Railway service or external). List the env vars the API and worker need (TEMPORAL_TARGET, namespace, task queue, and if applicable certs). No requirement to deploy Temporal itself in this spec; only document the integration.

6. **Single deployment doc.** Create one document (e.g. `docs/deployment.md` or a section in README) that lists: (1) services to create on Railway (API, worker, frontend, PostgreSQL), (2) env vars per service, (3) build/start commands per service, (4) migration step, (5) Temporal setup. A reader should be able to deploy from scratch by following this doc.

7. **Secrets.** Document that secrets (DATABASE_URL, Temporal certs, etc.) must be set in Railway’s env or secrets UI and never committed. No secrets in repo or in Dockerfile.

8. **Optional: Dockerfile(s).** If the project does not use Railway’s “run from source” with uv, provide a Dockerfile for the backend (API and worker can share the same image with different CMD). Frontend can be a multi-stage build that produces static files and optionally a minimal server. This is optional if Railway’s native build is used and documented.

## Out of Scope

- CI/CD pipeline (GitHub Actions or other); only document manual or one-click deploy steps.
- Custom domains or TLS (Railway default is acceptable).
- Staging vs production environments (one production path is enough).
- Monitoring or alerting beyond what Railway provides.
- Database backups (document that they are the user’s responsibility or use Railway’s backup feature if applicable).

## Verification

Every check below is mandatory. Do not skip any.

1. **Positive:** A single deployment document exists and lists all services, env vars, and commands needed to run the API, worker, frontend, and DB on Railway.
2. **Positive:** The API and worker start commands use only environment variables for config; no hardcoded production URLs or secrets in code.
3. **Positive:** The frontend build uses a configurable API URL (e.g. VITE_API_URL) and produces static assets that can be served.
4. **Positive:** Migration run (alembic upgrade head) is documented and the document states when/how to run it.
5. **Negative:** No secrets or credentials are committed in the repo or in Dockerfiles; documentation refers to Railway env/secrets only.
6. **Positive:** Temporal production setup (Cloud or self-hosted) is documented with the required env vars for the API and worker.

## Branch

`spec/13-railway-deployment`

## Provenance

`specs/provenance/production/13-railway-deployment.provenance.md` — overwrite on each execution; do not append.
