# Configuration

All runtime configuration is read from environment variables (or a `.env` file in the project root). The API and worker use the same config module (`meanwhile.config.get_settings()`), so they always share the same Temporal and database settings.

## Environment variables

| Variable | Description | Default (local dev) |
|----------|-------------|----------------------|
| `TEMPORAL_TARGET` | Temporal server address | `localhost:7233` |
| `TEMPORAL_NAMESPACE` | Temporal namespace | `default` |
| `TEMPORAL_TASK_QUEUE` | Task queue name | `chatbot-task-queue` |
| `DATABASE_URL` | PostgreSQL URL (async: use `postgresql+asyncpg://...`) | `postgresql+asyncpg://meanwhile_user:meanwhile_pass@localhost:5432/meanwhile_db` |
| `PYDANTIC_AI_MODEL` | Pydantic-AI model name | `test` |

Production must set these (and must not rely on defaults). No production URLs or secrets are hardcoded in the codebase.

## Running the API and worker

- **API:** `uv run meanwhile-api` (from project root). Serves the FastAPI app (e.g. port 8000).
- **Worker:** `uv run meanwhile-worker` (from project root). Runs the Temporal worker.

Both must use the same environment (or the same `.env` file) so that Temporal target, namespace, task queue, and database URL match.
