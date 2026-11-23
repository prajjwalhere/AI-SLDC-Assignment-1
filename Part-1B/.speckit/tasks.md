# NL Reminder Agent — Implementation Tasks

> Generated via `/speckit.tasks` during Spec-Driven Development workflow.

Commit messages cite the task ID (for example `1B-0NN [TASK-2][FR-B3..FR-B5]`). Status is updated in the same commit that completes the task.

## Task Breakdown

### TASK-1: Define output schema
- Create JSON Schema for reminder output format.
- **Traces to:** Specification §Output Schema Contract (US-B7, FR-B7)
- **Status:** TODO

### TASK-2: Implement intent classifier
- Regex-based scoring with random noise for non-determinism.
- **Traces to:** INV-2, BP-4, BP-5, BP-6 (US-B3, US-B4, US-B5, FR-B3, FR-B4, FR-B5)
- **Status:** TODO

### TASK-3: Implement datetime extraction
- Use dateparser with future-preference settings.
- Fallback regex for common patterns.
- **Traces to:** INV-4, GR-4 (US-B1, FR-B1)
- **Status:** TODO

### TASK-4: Implement description extraction
- Strip time/intent phrases to isolate the task description.
- **Traces to:** BP-1, BP-2 (US-B1, US-B2, FR-B1, FR-B2)
- **Status:** TODO

### TASK-5: Implement parse_reminder orchestrator
- Wire intent, datetime, and description extraction.
- Implement clarification logic for missing fields.
- **Traces to:** BP-1 through BP-7, GR-1 (US-B1..US-B6, FR-B1..FR-B6)
- **Status:** TODO

### TASK-6: Create evaluation dataset
- Minimum 15 cases covering normal, boundary, ambiguous, missing, malformed, and adversarial inputs.
- **Traces to:** Specification §Evaluation Threshold
- **Status:** TODO

### TASK-7: Build 3-layer evaluation harness
- Layer 1: Schema validation (jsonschema).
- Layer 2: Invariant/property checks.
- Layer 3: Semantic/quality evaluation.
- **Traces to:** Plan §Evaluation Harness Strategy, INV-1..INV-6
- **Status:** TODO

### TASK-8: Run evaluation and document
- Execute harness, capture evidence, write harness-log.md.
- **Traces to:** Constitution §Acceptance Authority
- **Status:** TODO
