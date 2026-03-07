# Spec: Canvas UI

## Purpose

Deliver a visual canvas (React Flow) where users can add nodes, connect them, and save/load workflow definitions via the backend API so that the graph becomes the single source of truth for the Brain.

## Prerequisites

- Specs 01–05 executed (workflow definitions API available).
- Load README.md (Canvas, “visual canvas where users connect nodes”).
- Load the frontend-design skill for UI quality; load the shadcn skill if the project uses shadcn (see web/package.json).

## Context

The README describes the Canvas as the place where users design automation logic (e.g. “Incoming Trigger” → “AI Agent Parsing” → “Database Update”). This spec implements the canvas and its integration with the workflow definitions API; it does not implement running workflows or viewing execution (specs 10–11).

## Changes

1. **Canvas route and layout.** Add a route (e.g. `/canvas` or `/workflows`) that renders a full-screen or main-content React Flow canvas. The canvas must have a defined viewport and support adding nodes and edges. Use the existing React Flow dependency (@xyflow/react) and ensure the graph state (nodes, edges) is held in React state or Zustand so it can be serialized and sent to the API.

2. **Node types for MVP.** Implement at least two node types: (a) a “trigger” or “start” node (no config required for MVP), (b) an “AI” or “agent” node with config: prompt (text) and optionally system instruction (text). Use custom node components (e.g. BaseNode, PlaceholderNode patterns if present) and register them with React Flow. Nodes must have stable ids (e.g. generated on add) and the graph serialization must include node id, type, position, and data (prompt, systemInstruction for AI nodes).

3. **Add node and connect.** Provide a way to add a node (e.g. panel or context menu with “Add trigger”, “Add AI node”) and to connect nodes by edges. Edges define execution order for the interpreter (spec 06). Ensure the serialized graph matches the format assumed by the backend (nodes array, edges array, or equivalent). Document the exact shape in a short comment or types (e.g. GraphPayload type) in the frontend.

4. **Save definition.** A “Save” (or “Save workflow”) action must: (a) serialize the current nodes and edges into the graph format expected by POST /api/workflow-definitions (name + graph), (b) prompt for or use a workflow name (e.g. input field or modal), (c) call POST /api/workflow-definitions with name and graph, (d) on success, store the returned id (e.g. in state or URL) and show success feedback; on error show an error message. Do not overwrite without user confirmation if the canvas was loaded from an existing definition (see Load).

5. **Load definition.** Support loading a definition by id: (a) call GET /api/workflow-definitions/{id}, (b) parse the returned graph into React Flow nodes and edges, (c) set the canvas state to that graph and set the workflow name. Entry point can be a URL (e.g. /canvas/:id) or a list of definitions that links to /canvas/:id. At least one way to open a definition and see it on the canvas is required.

6. **Update definition.** When the canvas is loaded from an existing definition (id in URL or state), “Save” should call PATCH /api/workflow-definitions/{id} with the current graph (and name if editable). Do not create a new definition unless the user explicitly chooses “Save as new” or the canvas is new (no id).

7. **API base URL.** The frontend must call the backend API using a configurable base URL (e.g. env VITE_API_URL or default http://localhost:8000). Do not hardcode production URLs.

8. **Navigation.** Provide a way to navigate from the landing/marketing page to the canvas (e.g. “Start Free Canvas” or “Canvas” link) and, if applicable, back. The canvas page must be reachable without authentication for MVP.

9. **Accessibility and responsiveness.** Canvas must be keyboard-accessible where reasonable (e.g. focus management, escape to cancel). Layout must work on desktop viewport; mobile support is out of scope for this spec.

10. **No execution yet.** Do not add “Run” button or execution list on the canvas in this spec; that is spec 10. Optional: a disabled “Run” or a link to “Run this workflow” that will be wired in spec 09.

## Out of Scope

- Running workflows or showing run status (spec 10).
- Execution detail or time-travel UI (spec 10).
- Authentication or multi-tenancy.
- Additional node types (e.g. database, IoT) beyond trigger and AI for MVP.
- Real-time collaboration or undo/redo beyond browser back/forward if needed.

## Verification

Every check below is mandatory. Do not skip any.

1. **Positive:** Opening the canvas route shows a React Flow canvas with at least one add-node control and the ability to draw edges between nodes.
2. **Positive:** Adding an “AI” node and setting prompt (and optionally system instruction) persists in the graph state and is included in the serialized payload sent to the API on Save.
3. **Positive:** Save with a name calls POST /api/workflow-definitions and returns 201; the user sees success and the returned id is stored or displayed.
4. **Positive:** Loading a definition by id (e.g. GET /api/workflow-definitions/{id}) populates the canvas with the correct nodes and edges; PATCH is used when saving over an existing definition.
5. **Positive:** The frontend uses a configurable API base URL (env or default) and does not rely on hardcoded production hostnames.
6. **Negative:** No “Run workflow” or execution list is implemented in this spec (placeholder or link is acceptable).

## Branch

`spec/09-canvas-ui`

## Provenance

`specs/provenance/mvp/09-canvas-ui.provenance.md` — overwrite on each execution; do not append.
