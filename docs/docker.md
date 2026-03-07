# Docker and Docker Compose

This document describes how to run the Meanwhile backend (API, worker, and PostgreSQL) with Docker Compose. For MVP, the frontend (`web/`) is not part of the Compose stack; run it separately from the host if needed.

## Running the full stack

From the project root:

```bash
docker compose up --build
```

Or run in the background:

```bash
docker compose up -d --build
```

This starts:

- **db** — PostgreSQL (port 5432)
- **api** — Meanwhile API (port 8000)
- **worker** — Meanwhile Temporal worker

The API and worker use the **same image** (`meanwhile-backend`), with different commands.

## Temporal (run on the host)

Temporal is **not** included in this Compose file. Run a Temporal server on your host so the API and worker can connect to it.

1. Install the [Temporal CLI](https://docs.temporal.io/cli) and start the dev server:

   ```bash
   temporal server start-dev
   ```

2. Ensure the API and worker can reach it. Compose sets `TEMPORAL_TARGET` to `host.docker.internal:7233` by default (Docker Desktop resolves this to the host). On Linux, if `host.docker.internal` is not available, set `TEMPORAL_TARGET` to your host IP (e.g. `172.17.0.1:7233`) in `.env` or in the Compose `environment` section.

3. If Temporal is not running or not reachable, the API will respond to `GET /api/health` with **503** (Temporal client unavailable). When Temporal is up and reachable, `/api/health` returns **200**.

## Required environment variables

Set these in a `.env` file at the project root (see `.env.example`). Compose loads `.env` via `env_file: .env` and overrides `DATABASE_URL` so the API and worker use the `db` service hostname.

| Variable | Description | Default in Compose |
|----------|-------------|--------------------|
| `DATABASE_URL` | Overridden in Compose to `postgresql+asyncpg://meanwhile_user:meanwhile_pass@db:5432/meanwhile_db` | — |
| `TEMPORAL_TARGET` | Temporal server address | `host.docker.internal:7233` |
| `TEMPORAL_NAMESPACE` | Temporal namespace | `default` |
| `TEMPORAL_TASK_QUEUE` | Task queue name | `chatbot-task-queue` |
| `PYDANTIC_AI_MODEL` | Pydantic-AI model | `test` |

Do **not** put production secrets in `.env` committed to the repo; use a local `.env` and keep it out of version control (it is in `.gitignore`).

## Migrations when using Docker

The database schema is managed by Alembic. When using Docker:

1. Start the stack so the `db` service is up:  
   `docker compose up -d db`
2. From your **host** (where the repo and `alembic` are available), run migrations against the containerized DB:

   ```bash
   export DATABASE_URL="postgresql+asyncpg://meanwhile_user:meanwhile_pass@localhost:5432/meanwhile_db"
   uv run alembic upgrade head
   ```

3. Then start the API and worker:  
   `docker compose up api worker`

Alternatively, run migrations once the stack is up, then restart the API/worker if needed. See `docs/database.md` for schema and downgrade commands.

## Building and running the image manually

- **Build:**  
  `docker build -t meanwhile-api .`

- **Run API:**  
  `docker run -p 8000:8000 --env-file .env meanwhile-api`

- **Run worker:**  
  `docker run --env-file .env meanwhile-api uv run meanwhile-worker`

The worker container needs the same env vars as the API (`DATABASE_URL`, `TEMPORAL_TARGET`, `TEMPORAL_NAMESPACE`, `TEMPORAL_TASK_QUEUE`).

## Frontend

The frontend (`web/`) is not part of this Compose setup for MVP. To use the canvas UI, run the frontend dev server from the host (e.g. `cd web && npm run dev`) and point it at the API at `http://localhost:8000`.
