# Spec: Rate limiting and API safety

## Purpose

Apply rate limiting and basic API safety (CORS, error handling) to the Meanwhile API so it is safe to expose in production.

## Prerequisites

- Specs 01–08 executed (API and backend in place).
- Load README.md (SlowAPI for rate limiting).

## Context

The README lists SlowAPI as part of the stack. Production APIs should limit request rate per client and expose minimal error details to avoid leaking internals. This spec adds SlowAPI-based rate limiting and configurable CORS and standardizes error responses where needed.

## Changes

1. **Install and wire SlowAPI.** Ensure SlowAPI is in project dependencies and that the FastAPI app uses SlowAPI’s middleware or limiter. Apply a default rate limit (e.g. 100 requests per minute per IP, or per API key if auth is added later) to the whole API or to specific routers. Document the chosen limit and how to override it (e.g. env var) for different environments.

2. **Limit expensive endpoints.** Apply stricter limits to expensive operations: (a) POST /api/workflow-definitions/{id}/run (e.g. 10/minute per IP or per client), (b) POST /api/workflow-definitions (e.g. 20/minute). Use SlowAPI decorators or route-specific limits. Return 429 Too Many Requests with a Retry-After header or a JSON body that indicates when to retry.

3. **CORS.** Configure CORS on the FastAPI app so the frontend (from a configurable origin, e.g. VITE_ORIGIN or ALLOWED_ORIGINS) can call the API. In production, do not use `allow_origins=["*"]` unless explicitly required; use a list of allowed origins from config. For local dev, allow http://localhost:* and the preview port if used.

4. **Error responses.** Ensure unhandled exceptions do not return stack traces or internal details to the client. Use FastAPI exception handlers to return a generic 500 message and log the full error server-side. Validation errors (422) can expose field-level errors; 500 should not expose internal paths or stack traces.

5. **Health and readiness.** Keep /api/health as a lightweight readiness check. Optionally exclude the health endpoint from rate limiting so load balancers and orchestrators can probe without consuming limit. Document this in comments or config.

6. **Documentation.** In README or docs, document: rate limits per endpoint (or default), how to configure CORS origins, and that 429 responses include retry guidance.

## Out of Scope

- Authentication or API keys (no auth in this spec).
- DDoS or WAF-level protection (handled by platform or infra).
- Request body size limits (use default or platform limits unless product requires otherwise).
- Changing business logic or adding new endpoints.

## Verification

Every check below is mandatory. Do not skip any.

1. **Positive:** SlowAPI is applied to the FastAPI app; exceeding the configured limit for an endpoint returns 429 with a JSON or standard response.
2. **Positive:** POST /api/workflow-definitions/{id}/run (and optionally POST /api/workflow-definitions) has a stricter limit than the default and returns 429 when exceeded.
3. **Positive:** CORS is configured; a request from the allowed frontend origin includes appropriate Access-Control-Allow-Origin and does not block the browser. Allowed origins come from config (env), not hardcoded production URLs.
4. **Positive:** An unhandled exception in the API does not return a stack trace or file paths in the response body; the client receives a generic error message and status 500.
5. **Negative:** Rate limiting and CORS do not break existing tests that call the API from the test client (adjust tests or exempt test user-agent if necessary; document the approach).

## Branch

`spec/12-rate-limiting-and-api-safety`

## Provenance

`specs/provenance/production/12-rate-limiting-and-api-safety.provenance.md` — overwrite on each execution; do not append.
