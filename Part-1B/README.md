# Part 1B — Natural-Language Reminder Agent (non-deterministic application)

Parses unstructured reminder requests into structured JSON. Supported intents: `create_reminder`, `reschedule`, `snooze`, `cancel`; asks for clarification when the task or the time is missing. Python 3.10+; runtime dependency `dateparser`.

The application is non-deterministic by design: `dateparser` can interpret ambiguous expressions differently depending on the reference time and locale, and the intent confidence score includes small random noise. No external AI/LLM API is called, so **no API keys or secrets are needed**.

## Layout

| Path | Purpose |
|---|---|
| `.speckit/` | Spec Kit artifacts: `constitution.md`, `specification.md`, `clarification.md`, `plan.md`, `tasks.md` |
| `src/reminder_agent.py` | The application (`parse_reminder`, `process_batch`) |
| `prompts/system_prompt.md` | System prompt describing the reminder-assistant contract |
| `evals/dataset.json` | Evaluation dataset (20 cases, each with `traces` to INV/BP/GR IDs) |
| `.harness/` | `run_evaluation.py` (single 3-layer evaluation runner), `schema.json` (output contract), `ruff.toml` (lint) |
| `evidence/` | `initial-generation/`, `final-generation/`, `eval-results.json`, `harness-log.md` |
| `TRACEABILITY.md` | US → FR → INV/BP/GR → TASK → eval case → source → commit matrix |

## Setup

```powershell
python -m pip install -r requirements.txt
```

## Run the application

```powershell
python src/reminder_agent.py "Remind me to call mom tomorrow at 5pm"
```

## Run the evaluation harness

```powershell
python .harness/run_evaluation.py
```

The runner loads `evals/dataset.json`, calls `parse_reminder` for every case and applies three layers: (1) JSON-schema validation against `.harness/schema.json`, (2) invariant checks INV-1..INV-6, (3) semantic/quality checks against each case's expected properties. A case passes only if all three layers pass; the run passes if the pass rate is at least **80%** (threshold declared in the specification). Results are written to `evidence/eval-results.json` and the runner exits `0` only on PASS.

## Lint

```powershell
python -m ruff check src --config .harness/ruff.toml --no-cache
```
