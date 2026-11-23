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

| US-B8 | FR-B8 | Amendment 1 failure classes, run verdict | TASK-9, TASK-10, TASK-11, TASK-13, TASK-14 | `src/reminder_agent_llm.py` (`ServiceError`, `_request_with_retries`, `_extract_output`), `.harness/run_evaluation.py` (`SERVICE_ERROR`, `INCONCLUSIVE`) | `tests/test_llm_agent.py` (16 offline tests); live runs `evidence/llm-variant/runs/run-1`, `run-2` |

The LLM-backed variant (`src/reminder_agent_llm.py`, prompt `prompts/system_prompt_llm.md`, tasks TASK-12/13) realises FR-B1..FR-B7 against the same 20 cases as the regex variant; its results are in `evidence/llm-variant/`.

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
- `tests/test_llm_agent.py` covers only the LLM client's retry policy, failure classes and key handling (offline); behaviour is verified by the evaluation dataset.
- LLM variant: two live runs (run-1, run-2) of the 20 cases, both 20/20; outputs differed between the runs in 9 of 20 cases (wording, confidence, one datetime) even at temperature 0. No repair was needed, so no held-out set was added. The prompt was written before any run and was not changed afterwards, but its author had already seen the dataset (for example the part-of-day time rule), so the 20 cases are not an unseen test set.
- Before the formal runs, Gemini was tried first and was unusable (retired model name, repeated HTTP 503, no pro quota); see Clarification Q6. Groq `openai/gpt-oss-120b` was used instead.

## Commit index

Every commit of this part, in order (generated from `git log`; hashes are of the commits listed, up to the commit before the index was last refreshed).

| Commit ID | Git hash | Refs | Summary |
|---|---|---|---|
| 1B-001 | db5197f | [CONSTITUTION] | Add Part 1B project constitution (schema conformance, supported intents, mandatory clarification, 80% threshold) |
| 1B-002 | 7351469 | [SPECIFY][US-B1..US-B7][FR-B1..FR-B7] | Add Part 1B specification (schema contract, INV, BP, GR, threshold) with user stories and FR IDs |
| 1B-003 | 3e9c2a0 | [CLARIFY][US-B1..US-B5][FR-B1..FR-B5] | Add clarifications Q1-Q5 with affected requirements |
| 1B-004 | d5162b7 | [PLAN][FR-B1..FR-B7] | Add technical plan, non-determinism strategy and 3-layer harness strategy |
| 1B-005 | df9ccef | [TASKS][US-B1..US-B7][FR-B1..FR-B7] | Add task breakdown TASK-1..TASK-8 with requirement traces |
| 1B-006 | 982f55d | [TASK-1][US-B7][FR-B7] | Add output JSON schema contract; scaffold Part 1B README and requirements |
| 1B-007 | ed9921d | [TASK-6][BP-1..BP-7][INV-1..INV-5][GR-1][GR-3] | Add evaluation dataset (20 cases, 6 categories) with per-case traces |
| 1B-008 | 9df4c28 | [TASK-7][INV-1..INV-6] | Add 3-layer evaluation harness (schema, invariants, semantic) with 80% threshold; add ruff config |
| 1B-009 | f075913 | [PROMPT][US-B1..US-B7][FR-B1..FR-B7] | Add reminder-assistant system prompt |
| 1B-010 | 2028b63 | [TASK-2..TASK-5][US-B1..US-B6][FR-B1..FR-B6] | First coding-agent generation of src/reminder_agent.py, preserved unchanged in evidence/initial-generation |
| 1B-011 | 6fde4c1 | [TASK-8] | Record evaluation results of the initial generation (20/20 PASS, threshold 80%) |
| 1B-012 | bedef66 | [REPAIR-1][TASK-2..TASK-5][FR-B1..FR-B6] | Repair lint findings I001 (import block) and S311 (random.uniform noise, per-line noqa) in src/reminder_agent.py |
| 1B-013 | b340837 | [TASK-8] | Preserve final generation and final evaluation results (20/20 PASS) |
| 1B-014 | 5f01800 | [TASK-8] | Add harness-log.md placeholder for student-authored log; update TASK-8 status |
| 1B-015 | 1944713 | [TRACEABILITY][US-B1..US-B7][FR-B1..FR-B7] | Add US/FR/INV/BP/GR to task, source and evaluation-case traceability matrix with disclosed gaps |
| 1B-016 | d728fa6 | [AMEND-1][CONSTITUTION][FR-B8] | Amend constitution for LLM-backed variant (stdlib only, key handling, protected files, failure classes) |
| 1B-017 | 8f26af5 | [AMEND-1][SPECIFY][US-B8][FR-B8] | Amend specification with LLM variant configuration, failure classes and run verdict; threshold unchanged |
| 1B-018 | 96b85f3 | [AMEND-1][CLARIFY][US-B8][FR-B8] | Add clarifications Q6-Q9 incl. live-probe findings (Gemini 404/503/429, Groq selected) |
| 1B-019 | add6141 | [AMEND-1][PLAN][FR-B8] | Add LLM variant architecture, harness changes, evidence layout and repair policy |
| 1B-020 | bf6a66b | [AMEND-1][TASKS][US-B8][FR-B8] | Add TASK-9..TASK-14 for the LLM-backed variant (TASK-9 done) |
| 1B-021 | 6b8cb34 | [TASK-10][US-B8][FR-B8][FR-B7] | Extend harness with --agent/--out/--pace, agent config recording and SERVICE_ERROR/INCONCLUSIVE class (layers, dataset, schema, threshold unchanged) |
| 1B-022 | 8793e72 | [TASK-11][US-B6][US-B8][FR-B6][FR-B8][GR-1] | Add offline tests for LLM client (retry policy, failure classes, key handling) before implementation |
| 1B-023 | 6a10361 | [TASK-12][US-B1..US-B6][FR-B1..FR-B6][GR-3][GR-4] | Add LLM system prompt (contract, intent rules, data-not-instructions, no fabricated datetimes) |
| 1B-024 | d945f82 | [AMEND-1][SPECIFY][FR-B8] | Record reasoning effort and output limit in LLM configuration table (found during pre-run live probe) |
| 1B-025 | ae3bb56 | [TASK-13][US-B1..US-B8][FR-B1..FR-B8] | First generation of src/reminder_agent_llm.py (Groq, stdlib only), preserved unchanged with its prompt in evidence/llm-variant/initial-generation |
| 1B-026 | 85539ae | [TASK-14][FR-B1..FR-B8] | Record LLM variant formal run 1 (20/20 PASS, 0 service errors, threshold 80%) with console output |
| 1B-027 | 408a094 | [TASK-14][FR-B1..FR-B8] | Record LLM variant repeat run 2 (20/20 PASS; 9/20 outputs differ in wording/confidence/datetime) |
| 1B-028 | 88fb105 | [TASK-14] | Preserve LLM variant final generation (identical to first generation: no repair was needed) with last run results |
| 1B-029 | 5e1cbce | [TASK-14][US-B8][FR-B8] | Document LLM variant in Part 1B README, add .env.example (names only), update TASK-14 status |
| 1B-030 | 83d6ead | [TRACEABILITY][US-B8][FR-B8] | Add FR-B8/LLM variant rows and updated disclosed gaps to Part 1B traceability matrix |
