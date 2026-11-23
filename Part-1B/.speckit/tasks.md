# NL Reminder Agent — Implementation Tasks

> Generated via `/speckit.tasks` during Spec-Driven Development workflow.

Commit messages cite the task ID (for example `1B-0NN [TASK-2][FR-B3..FR-B5]`). Status is updated in the same commit that completes the task.

## Task Breakdown

### TASK-1: Define output schema
- Create JSON Schema for reminder output format.
- **Traces to:** Specification §Output Schema Contract (US-B7, FR-B7)
- **Status:** DONE

### TASK-2: Implement intent classifier
- Regex-based scoring with random noise for non-determinism.
- **Traces to:** INV-2, BP-4, BP-5, BP-6 (US-B3, US-B4, US-B5, FR-B3, FR-B4, FR-B5)
- **Status:** DONE

### TASK-3: Implement datetime extraction
- Use dateparser with future-preference settings.
- Fallback regex for common patterns.
- **Traces to:** INV-4, GR-4 (US-B1, FR-B1)
- **Status:** DONE

### TASK-4: Implement description extraction
- Strip time/intent phrases to isolate the task description.
- **Traces to:** BP-1, BP-2 (US-B1, US-B2, FR-B1, FR-B2)
- **Status:** DONE

### TASK-5: Implement parse_reminder orchestrator
- Wire intent, datetime, and description extraction.
- Implement clarification logic for missing fields.
- **Traces to:** BP-1 through BP-7, GR-1 (US-B1..US-B6, FR-B1..FR-B6)
- **Status:** DONE

### TASK-6: Create evaluation dataset
- Minimum 15 cases covering normal, boundary, ambiguous, missing, malformed, and adversarial inputs.
- **Traces to:** Specification §Evaluation Threshold
- **Status:** DONE

### TASK-7: Build 3-layer evaluation harness
- Layer 1: Schema validation (jsonschema).
- Layer 2: Invariant/property checks.
- Layer 3: Semantic/quality evaluation.
- **Traces to:** Plan §Evaluation Harness Strategy, INV-1..INV-6
- **Status:** DONE

### TASK-8: Run evaluation and document
- Execute harness, capture evidence, write harness-log.md.
- **Traces to:** Constitution §Acceptance Authority
- **Status:** PARTIAL — evidence captured under `evidence/`; `harness-log.md` is written by the student (see `evidence/harness-log.md`).

## Amendment 1 tasks — LLM-backed variant

### TASK-9: Amend constitution, specification, clarifications and plan
- Record the LLM variant, failure classes, configuration and live-probe findings upstream before any implementation.
- **Traces to:** US-B8, FR-B8, Constitution Amendment 1
- **Status:** DONE

### TASK-10: Extend the harness (before implementation)
- Add `--agent`, `--out`, `--pace`; record agent configuration; add `SERVICE_ERROR` class and `INCONCLUSIVE` verdict. Layers, dataset, schema and threshold unchanged.
- **Traces to:** US-B8, FR-B8, FR-B7
- **Status:** DONE

### TASK-11: Write offline tests for the LLM client
- Fake transport tests: empty input makes no call; 429 retried then succeeds; repeated 503 raises `ServiceError`; invalid JSON is not retried and yields `MODEL_OUTPUT_INVALID`; missing key raises `ServiceError`; the key never appears in error text.
- **Traces to:** US-B6, US-B8, FR-B6, FR-B8, GR-1
- **Status:** DONE

### TASK-12: Write the LLM system prompt
- Contract, intent rules, clarification rules, snooze default, data-not-instructions rule, datetime derivation rule.
- **Traces to:** US-B1..US-B6, FR-B1..FR-B6, GR-3, GR-4, Clarification Q3–Q5
- **Status:** DONE

### TASK-13: Implement the LLM-backed agent
- `parse_reminder`, bounded retries, `ServiceError`, contract-field check, key handling.
- **Traces to:** US-B1..US-B8, FR-B1..FR-B8
- **Status:** TODO

### TASK-14: Run the evaluation and keep every run
- Probe first, then run the 20-case evaluation; keep each run under `evidence/llm-variant/runs/`; repair at most twice; save the final generation.
- **Traces to:** Specification Amendment 1 (run verdict), Constitution §Acceptance Authority
- **Status:** TODO
