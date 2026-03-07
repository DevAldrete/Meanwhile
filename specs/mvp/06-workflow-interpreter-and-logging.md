# Spec: Workflow interpreter and execution logging

## Purpose

Implement the “Brain”: a Temporal workflow that takes a workflow definition id and inputs, loads the graph from the database, executes it step-by-step (calling activities for each node), and writes execution logs so every prompt, token count, and raw output is durably stored.

## Prerequisites

- Specs 01–05 executed (layout, DB, config, workflow definitions API and table).
- Load README.md (Brain, Activities, “absolute transparency”, execution logs).
- Load the SDD skill; optional: temporal-python-testing skill for workflow tests.
- **TDD:** Load the tessl__test-driven-development skill. Write failing tests first for: execution log creation, "run AI node" activity output, interpreter workflow run status updates. Then implement to pass. One behavior per test; use mocks for DB and Temporal where appropriate.

## Context

The README states that the Brain parses visual graphs into executable workflow commands and that every prompt, system instruction, token count, and raw LLM output is durably saved. This spec implements one interpreter workflow that (1) loads a definition by id, (2) executes the graph (MVP: linear execution order by node id or explicit order field), (3) runs an AI activity for “AI” nodes and records results in `execution_logs`. The existing `ChatWorkflow` can remain for backward compatibility or be deprecated in favor of this interpreter; the spec must not remove the ability to run the existing chat endpoint unless explicitly required.

## Changes

1. **Execution log writing.** Add a shared way to append a row to `execution_logs` (workflow_run_id, node_id, step_type, payload_json, created_at). This may be called from an activity (e.g. “run AI node”) that receives run id and node payload and writes the log. Use the same DB session/engine as the rest of the app; activities must obtain a DB connection (e.g. from config) and insert one row per log entry. step_type must include at least one value for “activity” or “ai_step”; payload_json must store prompt, tokens, raw output (or equivalent) for AI steps.

2. **Activity: run AI node.** Implement a Temporal activity that: (a) accepts workflow run id, node id, and node config (e.g. prompt, system instruction), (b) calls the existing Pydantic-AI agent (or equivalent) to produce a result, (c) writes to `execution_logs` a payload that includes prompt, system instruction, token count if available, and raw model output, (d) returns a result (e.g. the model output) for the workflow to pass to the next node. Use retries and timeouts per README (“never-fail” durability); use Temporal activity options (e.g. start_to_close_timeout, retry policy).

3. **Interpreter workflow.** Implement a single Temporal workflow (e.g. `CanvasWorkflow` or `InterpreterWorkflow`) that: (a) receives workflow_definition_id and inputs (JSON/dict), (b) loads the workflow definition from the database (by id) inside the workflow or via an activity “load definition”; (c) creates a row in `workflow_runs` with status “running”, temporal_workflow_id and temporal_run_id from workflow.info(), inputs_json, started_at; (d) iterates over the graph nodes in a deterministic order (MVP: use node order from graph or a single “nodes” array order); (e) for each “AI” or “agent” node, calls the “run AI node” activity with run id, node id, and node config, then writes an execution_log entry if not already done by the activity; (f) on success, updates the workflow_runs row to status “completed” and sets finished_at; (g) on failure, updates status to “failed” and sets finished_at. The workflow must be deterministic: only use activities for DB and LLM; do not do I/O inside the workflow body except via activities.

4. **Worker registration.** Register the new workflow and the new activity (and “load definition” activity if used) in the Temporal worker so they are available on the same task queue as the API. Keep the existing ChatWorkflow and generate_chat_answer registered if the existing chat API is still in use.

5. **Load definition activity.** If the workflow cannot do DB access directly, implement an activity “load workflow definition” that takes definition id and returns the graph JSON (or name + graph). Use it at the start of the interpreter workflow. Ensure the workflow does not do non-deterministic or blocking I/O in the workflow function body.

6. **Graph format.** Assume the graph has a list of nodes (e.g. nodes array) and optionally edges. For MVP, execution order is defined by either (a) the order of nodes in the graph, or (b) a single “start” node and following edges until no next. Document in code or a short doc the assumed shape (e.g. `nodes: [{ id, type, data: { prompt?, systemInstruction? } }]`) so the canvas can align in a later spec.

7. **Tests (TDD).** Write failing tests first: (a) execution_log row created with expected step_type and payload when activity runs, (b) workflow_runs row updated to completed/failed. Then implement. Add at least one test that runs the interpreter workflow (or the “run AI node” activity) with a mock or test agent and verifies that an execution_log row is created with the expected step_type and payload shape. Prefer unit tests with mocked DB and Temporal where possible; integration test optional.

## Out of Scope

- Conditional branching or loops in the graph (MVP is linear).
- Non-AI node types (e.g. “database update”, “IoT”) beyond what is needed to pass data.
- Canvas UI or API for starting runs (spec 07).
- Reading logs via API (spec 08).
- Changing the existing /api/chat contract; coexistence is enough.

## Verification

Every check below is mandatory. Do not skip any.

1. **Positive:** Starting the interpreter workflow with a valid definition id and inputs creates a row in `workflow_runs` with status “running” and correct temporal_workflow_id/run_id.
2. **Positive:** For a graph with one AI node, the “run AI node” activity is invoked and an row is inserted into `execution_logs` with workflow_run_id, node_id, step_type, and payload_json containing prompt and raw output (and token count if the agent provides it).
3. **Positive:** On successful completion, the workflow_runs row is updated to status “completed” and finished_at is set; on workflow failure, status is “failed” and finished_at is set.
4. **Positive:** The worker starts without error and includes the new workflow and activities; the existing chat workflow still runs if the chat endpoint is still present.
5. **Positive:** At least one test exists that asserts execution_log creation and (if applicable) workflow run status update.
6. **Negative:** The workflow body does not perform direct DB or HTTP calls; all I/O is in activities.
7. **Positive (TDD):** Tests for execution_log and workflow run status were written before or in lockstep with implementation; test suite is green for these behaviors.

## Branch

`spec/06-workflow-interpreter-and-logging`

## Provenance

`specs/provenance/mvp/06-workflow-interpreter-and-logging.provenance.md` — overwrite on each execution; do not append.
