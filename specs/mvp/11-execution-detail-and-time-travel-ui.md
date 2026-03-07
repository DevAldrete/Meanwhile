# Spec: Execution detail and time-travel UI

## Purpose

Provide a run detail page that shows execution logs (prompts, token counts, raw outputs) and a way to download execution history for time-travel debugging.

## Prerequisites

- Specs 01–10 executed (runs list, GET /api/runs/{id}, GET /api/runs/{id}/logs, GET /api/runs/{id}/history).
- Load README.md (“Absolute transparency”, “Time-travel debugging”).

## Context

Users must see exactly what the AI was thinking and why a node failed; they must be able to download the exact execution history and replay it locally. The APIs for logs and history exist (spec 08); this spec adds the UI to view logs and download history.

## Changes

1. **Run detail route.** Add a route (e.g. /runs/:id) that loads a single run by id. Call GET /api/runs/{id}. Display run metadata: id, workflow_definition_id, status, started_at, finished_at, and optionally inputs_json. If the run is not found (404), show a “Run not found” message and a link back to the runs list.

2. **Logs section.** On the same page, fetch GET /api/runs/{id}/logs and display the list of execution logs. Each log entry must show at least: node_id, step_type, created_at, and a readable representation of payload_json (e.g. prompt, token count, raw output). Format for readability (e.g. code block for raw output, labels for prompt vs output). Order by created_at ascending.

3. **Download history button.** Add a “Download history” (or “Export for time-travel”) button that calls GET /api/runs/{id}/history and triggers a file download (e.g. save as JSON with a filename like `meanwhile-history-{runId}.json`). Document in the UI (tooltip or short text) that the file can be used to replay the workflow locally for debugging.

4. **Link back to runs list and canvas.** Provide navigation: back to runs list and optionally a link to the workflow definition (canvas) that produced this run.

5. **Loading and error states.** Show loading while fetching run and logs; show error message if the run or logs request fails, with option to retry or go back.

6. **API base URL.** Use the same configurable API base URL as the rest of the app.

## Out of Scope

- Implementing the actual replay tooling (user runs replay locally).
- Editing or deleting runs or logs.
- Real-time log streaming (polling or one-time load is enough).
- Authentication.

## Verification

Every check below is mandatory. Do not skip any.

1. **Positive:** Opening /runs/{id} for an existing run loads run metadata and displays status, started_at, finished_at.
2. **Positive:** The same page loads and displays execution logs (node_id, step_type, payload content) in chronological order.
3. **Positive:** “Download history” fetches GET /api/runs/{id}/history and triggers a file download with the response body; the downloaded file is valid JSON.
4. **Positive:** For a non-existent run id, the page shows “Run not found” (or equivalent) and does not crash.
5. **Negative:** This spec does not add new backend endpoints; it only consumes existing run, logs, and history APIs.

## Branch

`spec/11-execution-detail-and-time-travel-ui`

## Provenance

`specs/provenance/mvp/11-execution-detail-and-time-travel-ui.provenance.md` — overwrite on each execution; do not append.
