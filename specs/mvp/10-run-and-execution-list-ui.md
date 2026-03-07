# Spec: Run and execution list UI

## Purpose

Let users trigger a workflow run from the canvas (or from a definition detail) and see a list of runs for that definition (or globally) with status and link to execution detail.

## Prerequisites

- Specs 01–09 executed (canvas, start run API, GET /api/runs and GET /api/workflow-definitions/{id}/runs if implemented).
- Load README.md for product context.

## Context

After designing a workflow on the canvas, users need to run it and see runs in progress or completed. This spec adds the “Run” action and a runs list; execution detail and logs are spec 11.

## Changes

1. **Run button from canvas.** When the canvas is showing a saved workflow (has definition id), add a “Run” (or “Run workflow”) button. On click: (a) optionally collect inputs (MVP: empty object or a simple key-value form if the interpreter accepts inputs); (b) call POST /api/workflow-definitions/{id}/run with inputs; (c) on 202, show success and either navigate to the run detail (spec 11) or to a “runs” list with the new run highlighted; (d) on 4xx/5xx show error message. The response body must be used to obtain the run id (or temporal_workflow_id) for navigation.

2. **Runs list entry point.** Provide a way to open a list of runs. Options: (a) a “Runs” link in the app that shows GET /api/runs (all runs or filtered), or (b) a “Runs” section on the canvas or definition view that shows GET /api/workflow-definitions/{id}/runs for the current definition. At least one of these must be implemented. The list must show for each run: id or temporal_workflow_id, status, started_at (and optionally finished_at). List must be ordered by started_at descending.

3. **Link to run detail.** Each row (or run card) must link to the execution detail view (spec 11) so the user can open a run and see logs. Use run id (primary key) for the link (e.g. /runs/{id}). If spec 11 is not yet implemented, the link target can be a placeholder route that will be implemented in spec 11.

4. **Status display.** Show run status (running, completed, failed) clearly—e.g. badge or label. No need to poll for updates in this spec; a refresh button or manual reload is acceptable for MVP.

5. **Empty and error states.** If there are no runs, show an empty state message. If the API returns an error when loading the list, show an error message and optionally a retry action.

6. **API base URL.** Use the same configurable API base URL as the canvas (no new env vars unless already present).

## Out of Scope

- Execution detail page content (logs, history download)—spec 11.
- Real-time updates (WebSocket or polling) for status; manual refresh is enough.
- Authentication or filtering by user.
- Pagination (use limit from API if available).

## Verification

Every check below is mandatory. Do not skip any.

1. **Positive:** From the canvas with a saved definition, “Run” calls POST /api/workflow-definitions/{id}/run and on 202 the user sees success and can navigate to the run or runs list.
2. **Positive:** The runs list (global or per-definition) loads via GET /api/runs or GET /api/workflow-definitions/{id}/runs and displays run id, status, and started_at for each run.
3. **Positive:** Each run in the list has a link to the run detail (e.g. /runs/{id}) that navigates to the execution detail route.
4. **Positive:** Status is visibly displayed (running/completed/failed or equivalent).
5. **Negative:** This spec does not implement the full execution detail page content (logs, history); only the entry point and list.

## Branch

`spec/10-run-and-execution-list-ui`

## Provenance

`specs/provenance/mvp/10-run-and-execution-list-ui.provenance.md` — overwrite on each execution; do not append.
