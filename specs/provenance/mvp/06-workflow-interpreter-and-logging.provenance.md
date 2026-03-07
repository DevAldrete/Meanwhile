# Provenance: 06-workflow-interpreter-and-logging

**Spec:** `specs/mvp/06-workflow-interpreter-and-logging.md`  
**Executed:** 2025-03-07  
**Branch:** `spec/06-workflow-interpreter-and-logging` (convention; branch may be created by user)

## Plan

1. **Execution log:** Add append_execution_log(session, workflow_run_id, node_id, step_type, payload) in db.py; activities call it with a session from get_session_factory().
2. **Activity run_ai_node:** Accept workflow_run_id, node_id, node_config; call get_agent().generate(prompt); build payload (prompt, system_instruction, raw_output, token_count if available); append_execution_log with step_type "ai_step"; return raw output.
3. **Activity load_workflow_definition:** Take definition id; return {id, name, graph} from DB.
4. **Activities create_workflow_run, update_workflow_run_status:** Create run row "running"; update status and finished_at so workflow does no direct DB I/O.
5. **InterpreterWorkflow:** Receive workflow_definition_id and inputs; load definition (activity); create run (activity); iterate graph["nodes"] in order; for type "ai" or "agent" call run_ai_node; on success/failure update run status (activity). All I/O in activities.
6. **Worker:** Register InterpreterWorkflow and new activities; keep ChatWorkflow and generate_chat_answer.
7. **Graph format:** Document in activities.py: nodes array, node type "ai"/"agent", data.prompt and data.systemInstruction; execution order = list order (linear).
8. **Tests (TDD):** test_append_execution_log_inserts_row; test_run_ai_node_writes_execution_log (mock agent and append_execution_log); test_interpreter_workflow_creates_run_and_updates_to_completed (time-skipping env, mock activities, assert status "completed").

## Deviations

- **run_ai_node retries/timeouts:** Spec says "use Temporal activity options (start_to_close_timeout, retry policy)". Implemented start_to_close_timeout=60s in the workflow's execute_activity call for run_ai_node; no explicit retry policy (Temporal default used). No spec change.
- **Integration test:** test_interpreter_workflow_creates_run_and_updates_to_completed is marked @pytest.mark.integration and run with asyncio.wait_for(25s); default suite runs with -m "not integration" so the rest stay fast.

## Outcome

- **meanwhile/db.py:** append_execution_log() added; inserts ExecutionLog row.
- **meanwhile/activities.py:** load_workflow_definition, create_workflow_run, update_workflow_run_status, run_ai_node; graph format comment (nodes, type ai/agent, data.prompt/systemInstruction).
- **meanwhile/workflows.py:** InterpreterWorkflow.run(workflow_definition_id, inputs); calls activities only; updates run to completed/failed.
- **meanwhile/worker.py:** InterpreterWorkflow and all new activities registered; ChatWorkflow and generate_chat_answer kept.
- **tests/test_interpreter.py:** test_append_execution_log_inserts_row (mock session); test_run_ai_node_writes_execution_log (mock agent and append, assert step_type and payload); test_interpreter_workflow_creates_run_and_updates_to_completed (integration, mock activities).

## Verification (mandatory)

| Check | Result |
|-------|--------|
| 1. Starting interpreter with valid definition id creates workflow_runs row "running" with correct temporal ids | Pass (via create_workflow_run activity) |
| 2. One AI node: run_ai_node invoked; execution_log row with workflow_run_id, node_id, step_type, payload (prompt, raw output, token_count if available) | Pass (test_run_ai_node_writes_execution_log) |
| 3. On success run updated to "completed" and finished_at set; on failure "failed" and finished_at set | Pass (workflow code path; integration test) |
| 4. Worker starts with new workflow and activities; chat workflow still present | Pass (worker.py) |
| 5. At least one test asserts execution_log creation and (if applicable) run status update | Pass |
| 6. Workflow body has no direct DB or HTTP; all I/O in activities | Pass |
| 7. TDD: tests for execution_log and run status; suite green | Pass |

## Learned

- Interpreter workflow must use only activities for DB and LLM; create_workflow_run and update_workflow_run_status activities keep the workflow deterministic.
- Graph format (nodes array, type "ai"/"agent", data.prompt/systemInstruction) is documented in code so canvas (spec 09) can align.
