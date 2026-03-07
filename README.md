# The Philosophy: Orchestrating the Chaos

Orchestrating AI is fundamentally chaotic. LLMs hallucinate, external APIs drop connections, and multi-step automated reasoning loops can fail unpredictably. Traditional visual builders aren't built to handle this level of non-determinism reliably.

## Meanwhile solves this by enforcing a strict architectural separation

- The Canvas (Visual UI): Where users intuitively design their automation logic.

- The Workflows (Deterministic Logic): Handled by MeanWhile's backend to predictably route tasks, handle conditionals, and manage state.

- The Activities (Non-Deterministic Execution): Where the actual AI calls, data cleaning, and IoT interactions happen. If an activity fails, Temporal automatically catches it, tracks it, and retries it.

## Architecture

Meanwhile leverages Temporal's open-source, MIT-licensed engine to handle the heavy lifting of state management and task queuing.

- MeanWhile UI: A visual canvas where users connect nodes to build processes (e.g., "Incoming Trigger" -> "AI Agent Parsing" -> "Database Update").

- MeanWhile Brain: The high-performance core. It parses visual graphs from the UI into executable workflow commands using the Temporal SDK.

- Temporal Cluster (The Engine): A standalone black-box engine that durably tracks the state of every single workflow step, saving the execution history to PostgreSQL.

## Key Features

- Visual AI Orchestration: Build multi-step AI workflows with complex reasoning, loops, and conditional routing without writing code.

- Absolute Transparency & Execution Logs: Every prompt, system instruction, token count, and raw LLM output is durably saved. Users can see exactly what the AI was thinking and why a node failed.

- Time-Travel Debugging: Download the exact execution history of a failed production workflow and replay it locally to find the exact line of logic that broke, without re-triggering expensive AI API calls.

- "Never-Fail" Durability: Built-in exponential retries and timeouts for flaky external APIs or rate-limited endpoints.

- High-Performance Core: Optimized for lightweight, and lightning-fast execution capable of handling heavy loads.

## Tech Stack

### Backend

- **FastAPI**: High-performance web framework for building APIs
- **Pydantic-AI**: AI-first data validation and serialization
- **SlowAPI**: Rate limiting middleware for FastAPI
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **PostgreSQL**: Relational database
- **Temporalio**: Distributed workflow and activity execution engine

### Frontend

- **React**: UI library for building interactive interfaces
- **React Flow**: Library for building node-based UIs and visual workflows
- **shadcn/ui**: High-quality, customizable React components
- **Zustand**: Lightweight state management
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast frontend build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework

### Cloud Provider

- **Railway**: Cloud deployment platform

## Development

The backend is the Python package `meanwhile`. The package lives in the `meanwhile/` directory at project root. Imports use `meanwhile.*` (e.g. `from meanwhile.api import create_app`).

**From project root:**

- Install and run the API: `uv sync` then `uv run meanwhile-api`
- Run the worker: `uv run meanwhile-worker`
- Run tests: `uv run pytest tests/ -v`
- Verify imports: `uv run python -c "from meanwhile.api import create_app; print('ok')"`
- Run database migrations: `uv run alembic upgrade head` (see `docs/database.md` for schema and downgrade).
- Config and env vars (Temporal, DB, etc.) are documented in `docs/config.md`. Use the same env (or `.env`) for the API and worker.

### Docker

You can run the full backend stack (PostgreSQL, API, worker) with Docker Compose. Temporal is not in Compose; run it on the host (e.g. `temporal server start-dev`) and set `TEMPORAL_TARGET=host.docker.internal:7233` in `.env`.

- **Run the stack:** `docker compose up --build` (see `docs/docker.md`).
- **Required env:** Use `.env` (see `.env.example`); `docs/docker.md` lists variables and how to run migrations when using Docker.
- **Frontend:** The `web/` app is not part of this Compose for MVP; run it from the host if needed.
