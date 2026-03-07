# Provenance: Spec 03 — Config and Temporal connectivity

## Spec executed

`specs/mvp/03-config-and-temporal.md`

## Plan

1. Keep `meanwhile.config` as single source: already using `pydantic_settings.BaseSettings` (from Spec 02) so Temporal and DB settings are read from env with local defaults.
2. Ensure no hardcoded production URLs (defaults are localhost).
3. API and worker already use `get_settings()` from the same module.
4. Health check: catch Temporal connection failure in lifespan and set `temporal_client = None` so `/api/health` returns 503 when Temporal is unavailable; add test.
5. Add `docs/config.md` with env vars and run commands; reference from README.

## Deviations

None.

## Outcome

- **Positive:** All Temporal and database settings come from environment (via BaseSettings); no production URLs or secrets in source.
- **Positive:** API and worker both use `meanwhile.config.get_settings()` for Temporal target, namespace, and task queue.
- **Positive:** With Temporal unavailable (connect_temporal raises), health endpoint returns 503; test `test_health_returns_503_when_temporal_unavailable` added.
- **Positive:** README and `docs/config.md` list required env vars and commands for API and worker.
- **Negative:** No duplicate definition of task queue or Temporal target elsewhere.

All mandatory checks satisfied.
