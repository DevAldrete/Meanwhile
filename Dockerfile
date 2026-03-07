# Meanwhile backend: API and worker (same image, different command).
# Build:  docker build -t meanwhile-api .
# Run API: docker run -p 8000:8000 --env-file .env meanwhile-api
# Run worker: docker run --env-file .env meanwhile-api uv run meanwhile-worker
# Required at runtime: DATABASE_URL, TEMPORAL_TARGET, TEMPORAL_NAMESPACE, TEMPORAL_TASK_QUEUE (see .env.example).

FROM python:3.13-slim

WORKDIR /app

# Install uv for fast, reproducible dependency install
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.local/bin:$PATH"

# Dependencies from lockfile (install deps only first for better layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Application code and install project so `uv run meanwhile-api` works
COPY meanwhile ./meanwhile
COPY main.py ./
RUN uv sync --frozen --no-dev

# Scripts reference main:main; ensure project root is on path
ENV PYTHONPATH=/app

# Default: run the API
EXPOSE 8000
CMD ["uv", "run", "meanwhile-api"]
