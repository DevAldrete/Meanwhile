# The Philosophy: Orchestrating the Chaos

Orchestrating AI is fundamentally chaotic. LLMs hallucinate, external APIs drop connections, and multi-step automated reasoning loops can fail unpredictably. Traditional visual builders aren't built to handle this level of non-determinism reliably.

## DotBrain solves this by enforcing a strict architectural separation

- The Canvas (Visual UI): Where users intuitively design their automation logic.

- The Workflows (Deterministic Logic): Handled by DotBrain's backend to predictably route tasks, handle conditionals, and manage state.

- The Activities (Non-Deterministic Execution): Where the actual AI calls, data cleaning, and IoT interactions happen. If an activity fails, Temporal automatically catches it, tracks it, and retries it.

## Architecture

DotBrain leverages Temporal's open-source, MIT-licensed engine to handle the heavy lifting of state management and task queuing.

- DotBrain UI: A visual canvas where users connect nodes to build processes (e.g., "Incoming Trigger" -> "AI Agent Parsing" -> "Database Update").

- DotBrain Brain: The high-performance core. It parses visual graphs from the UI into executable workflow commands using the Temporal SDK.

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
