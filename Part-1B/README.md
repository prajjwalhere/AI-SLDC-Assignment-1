# Part 1B — Natural-Language Reminder Agent (non-deterministic application)

Parses unstructured reminder requests into structured JSON. Supported intents: `create_reminder`, `reschedule`, `snooze`, `cancel`; asks for clarification when the task or the time is missing. Python 3.10+; runtime dependency `dateparser`.

There are two implementations of the same specification and output contract:

| Variant | Module | Non-determinism | Secrets |
|---|---|---|---|
| Regex + `dateparser` (original) | `src/reminder_agent.py` | `dateparser` interpretation and random confidence noise | none |
| LLM-backed (Amendment 1) | `src/reminder_agent_llm.py` | a hosted model (Groq `openai/gpt-oss-120b`, temperature 0) | `GROQ_API_KEY` in the git-ignored `.env` |

The 20-case dataset, the schema, the three evaluation layers and the 80% threshold are the same for both. Each variant has its own evidence.

## Layout

| Path | Purpose |
|---|---|
| `.speckit/` | Spec Kit artifacts: `constitution.md`, `specification.md`, `clarification.md`, `plan.md`, `tasks.md` |
| `src/reminder_agent.py` | Regex + `dateparser` application (`parse_reminder`, `process_batch`) |
| `src/reminder_agent_llm.py` | LLM-backed application (same interface, plus `ServiceError`) |
| `prompts/system_prompt.md` | Description of the reminder-assistant contract (regex variant) |
| `prompts/system_prompt_llm.md` | System prompt used by the LLM-backed variant |
| `tests/test_llm_agent.py` | Offline tests for the LLM client (fake transport, no network, no key) |
| `.env.example` | Names of environment variables only; copy to `.env` for the LLM variant |
| `evals/dataset.json` | Evaluation dataset (20 cases, each with `traces` to INV/BP/GR IDs) |
| `.harness/` | `run_evaluation.py` (single 3-layer evaluation runner), `schema.json` (output contract), `ruff.toml` (lint) |
| `evidence/` | Regex variant: `initial-generation/`, `final-generation/`, `eval-results.json`. LLM variant: `llm-variant/initial-generation/`, `llm-variant/runs/run-N/` (every run kept), `llm-variant/final-generation/`. Plus `harness-log.md` |
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

## LLM-backed variant

```powershell
copy .env.example .env        # then put your key in .env (never commit it)
python -m pytest tests -v     # offline tests, no network or key needed
python src/reminder_agent_llm.py "Remind me to call mom tomorrow at 5pm"
python .harness/run_evaluation.py --agent reminder_agent_llm --out evidence/llm-variant/runs/run-N/eval-results.json --pace 3
```

`--agent` selects the module, `--out` the results file (use a new `run-N` folder each time; never overwrite a run) and `--pace` a pause between cases to stay inside free-tier limits. Failures are kept apart:

| Class | Result |
|---|---|
| Provider/service failure (timeout, HTTP 429/5xx after up to 3 attempts, auth, network, missing key) | case marked `SERVICE_ERROR`, not scored; run verdict `INCONCLUSIVE`, exit code 2 |
| Bad model output (not JSON / missing fields) | `status: "error"`, `MODEL_OUTPUT_INVALID…`; not retried; scored normally |
| Empty input | error response, no API call |
| Anything else | scored by the three layers |

Exit code: `0` PASS, `1` FAIL, `2` INCONCLUSIVE. No secrets are written to results; the key is read only from the environment or `.env`.

## Lint

```powershell
python -m ruff check src --config .harness/ruff.toml --no-cache
```
