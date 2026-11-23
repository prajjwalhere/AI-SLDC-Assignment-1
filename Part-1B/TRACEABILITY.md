# Part 1B — Traceability Matrix

Chain: `US-Bn → FR-Bn → INV / BP / GR → TASK-n → evaluation case (TC-nn) → source → commit ID`.
Requirement IDs come from [.speckit/specification.md](.speckit/specification.md); tasks from [.speckit/tasks.md](.speckit/tasks.md); case-to-requirement links are the `traces` field of each case in [evals/dataset.json](evals/dataset.json).
Commit IDs (`1B-NNN`) are listed in the [Commit index](#commit-index) and appear at the start of every commit message.

## Requirement → implementation → evaluation

| US | FR | Checks (spec) | Task | Source (`src/reminder_agent.py`) | Evaluation cases (`traces`) |
|---|---|---|---|---|---|
| US-B1 | FR-B1 | BP-1, INV-4, GR-4 | TASK-3, TASK-4, TASK-5 | `extract_datetime`, `extract_description`, `parse_reminder` | BP-1: TC-01, TC-02, TC-03, TC-18, TC-20 · INV-4: TC-01, TC-03, TC-06, TC-18, TC-20 |
| US-B2 | FR-B2 | BP-2, BP-3, INV-5 | TASK-4, TASK-5 | `extract_description`, `parse_reminder` | BP-2: TC-07 · BP-3: TC-08 · INV-5: TC-07, TC-08, TC-11 |
| US-B3 | FR-B3 | BP-4, INV-2 | TASK-2, TASK-5 | `classify_intent` (`CANCEL_PATTERNS`), `parse_reminder` | BP-4: TC-04, TC-19 |
| US-B4 | FR-B4 | BP-5, INV-2 | TASK-2, TASK-5 | `classify_intent` (`SNOOZE_PATTERNS`), `extract_snooze_duration` | BP-5: TC-05, TC-09, TC-10 |
| US-B5 | FR-B5 | BP-6, INV-2, INV-4 | TASK-2, TASK-3, TASK-5 | `classify_intent` (`RESCHEDULE_PATTERNS`), `extract_datetime`, `parse_reminder` | BP-6: TC-06, TC-11 |
| US-B6 | FR-B6 | BP-7, INV-6, GR-1, GR-2, GR-3, GR-4 | TASK-5 | `parse_reminder` (empty-input branch) | BP-7: TC-12, TC-13 · GR-1: TC-12, TC-13, TC-14 · GR-3: TC-16, TC-17 |
| US-B7 | FR-B7 | INV-1, INV-2, INV-3, INV-4 | TASK-1, TASK-7 | `.harness/schema.json`, `.harness/run_evaluation.py` (`validate_schema`, `check_invariants`) | INV-1: TC-01, TC-02, TC-14, TC-15, TC-16, TC-17 · INV-2: TC-04, TC-05, TC-06, TC-10, TC-15, TC-19 |

Layers 1 and 2 of the harness run on **every** case regardless of its `traces`, so INV-1..INV-6 are checked for all 20 cases.

## Evaluation pipeline → requirements

| Layer | Implementation (`.harness/run_evaluation.py`) | Enforces |
|---|---|---|
| 1 — Structural | `validate_schema` + `.harness/schema.json` | Output schema contract (FR-B7) |
| 2 — Property / invariant | `check_invariants` | INV-1..INV-6 |
| 3 — Semantic / quality | `evaluate_semantics` | Expected status, intent, description, datetime, clarification topic, error message, snooze duration per case (BP-1..BP-7) |
| Aggregate | `run_evaluation` | Threshold: pass rate >= 80% (specification §Evaluation Threshold, constitution §Acceptance Authority) |

## Clarifications → requirements

| Clarification | Decision | Requirements |
|---|---|---|
| Q1 | Three sources of non-determinism (dateparser, confidence noise, threshold boundaries) | INV-3, INV-4, GR-4, FR-B1, FR-B7 |
| Q2 | Single reminder per call; `process_batch` for independent inputs | US-B1, FR-B1 |
| Q3 | Unparseable datetime → `datetime: null`; create → clarify (BP-3) | US-B2, FR-B2, INV-4 |
| Q4 | Snooze = relative duration; reschedule = target datetime | US-B4, US-B5 |
| Q5 | Default snooze duration 15 minutes | US-B4, FR-B4 (`extract_snooze_duration`) |

## Known gaps (disclosed, not hidden)

- **GR-2** (input longer than 10,000 characters) and **GR-4** (never fabricate a datetime) are in the specification but no evaluation case lists them in `traces`.
- **INV-3** and **INV-6** are enforced by layer 2 on every case but no case lists them in `traces`.
- Each case is evaluated once per run (no repetitions), although the application is non-deterministic by design.
- Layer 3 uses substring / ground-truth comparison, not an LLM judge.
- The lint pre-check is not part of `run_evaluation.py`; it is run separately with ruff (see README). `random.uniform` in `classify_intent` carries a per-line `# noqa: S311` suppression.
- `tests/` is not used in Part 1B; the evaluation dataset and harness are the verification mechanism.

## Commit index

Filled in from `git log` in the final repository-finish commit.
