# NL Reminder Agent — Technical Plan

> Generated via `/speckit.plan` during Spec-Driven Development workflow.

## Architecture

```
User input (natural language)
        │
        ▼
  classify_intent()     ← regex pattern matching + random noise
        │
        ▼
  extract_datetime()    ← dateparser (non-deterministic)
        │
        ▼
  extract_description() ← regex stripping of time/intent phrases
        │
        ▼
  parse_reminder()      ← orchestration, clarification logic
        │
        ▼
  Structured JSON output (schema-conformant)
```

| Component | Serves |
|---|---|
| `classify_intent()` | FR-B3, FR-B4, FR-B5 (INV-2, BP-4, BP-5, BP-6) |
| `extract_datetime()` | FR-B1, FR-B5 (INV-4, GR-4) |
| `extract_description()` | FR-B1, FR-B2 (BP-1, BP-2) |
| `parse_reminder()` | FR-B1..FR-B7 (BP-1..BP-7, GR-1) |

## Technology Choices

| Concern | Choice | Rationale |
|---|---|---|
| Language | Python 3.10+ | Constitution constraint |
| Date parsing | `dateparser` | Handles natural language dates; non-deterministic by nature |
| Intent classification | Regex + scoring | Lightweight, no model needed; noise provides non-determinism |
| Schema validation | `jsonschema` | Standard, declarative validation |
| Testing | `pytest` | Consistent with Part 1A |
| Linting | `ruff` | Consistent with Part 1A |

## Non-Determinism Strategy

The application introduces genuine non-determinism through:
1. **dateparser** — its interpretation of ambiguous dates depends on locale settings and reference time.
2. **Random confidence noise** — `random.uniform(-0.05, 0.05)` added to intent scores means repeated calls can produce different confidence values.
3. **Threshold boundary effects** — inputs near score boundaries may classify differently across runs.

## Evaluation Harness Strategy

Three-layer pipeline per the specification:

| Layer | What | How |
|---|---|---|
| Structural | JSON schema conformance | `jsonschema.validate()` against schema |
| Property/Invariant | Deterministic rules from spec | Programmatic checks for INV-1 through INV-6 |
| Semantic/Quality | Meaning correctness | Ground-truth comparison with fuzzy matching |

Aggregate: binary pass/fail per case; overall >= 80% required.

## Amendment 1 — LLM-backed implementation variant

```
 .env / environment  ──►  key (never logged)
        │
 user text ─► guard: empty? ──yes──► error response (no API call)
        │ no
        ▼
 build request: system prompt (prompts/system_prompt_llm.md) + current time + user text as data
        │
        ▼
 Groq chat completions (openai/gpt-oss-120b, temperature 0, JSON object mode, 45 s timeout)
        │   429 / 5xx / timeout → up to 3 attempts with growing waits → ServiceError
        ▼
 parse + contract-field check ──invalid──► status "error", "MODEL_OUTPUT_INVALID: ..." (never retried)
        │ valid
        ▼
 structured output (same contract as the regex variant)
```

| Component | Serves |
|---|---|
| `src/reminder_agent_llm.py` (`parse_reminder`, `ServiceError`, `AGENT_INFO`) | FR-B1..FR-B8 |
| `prompts/system_prompt_llm.md` | FR-B1..FR-B6, GR-3, GR-4 |
| `.harness/run_evaluation.py` options `--agent`, `--out`, `--pace` and service-error class | FR-B8 (evaluation side), Evaluation Threshold |
| `tests/test_llm_agent.py` (offline, fake transport) | FR-B8, GR-1 |

**Harness changes (no weakening).** Default behaviour (agent `reminder_agent`, output `evidence/eval-results.json`) is unchanged. Layers 1–3, dataset, schema and threshold are untouched. The runner additionally records the agent configuration and, per case, a `SERVICE_ERROR` result that is excluded from the pass rate and makes the verdict `INCONCLUSIVE` (exit code 2).

**Evidence layout.** `evidence/llm-variant/initial-generation/` (first generation, saved before the first formal run), `evidence/llm-variant/runs/run-N/` (every run kept, never overwritten) and `evidence/llm-variant/final-generation/`.

**Repair policy.** At most two repair attempts per cycle; repairs change only the LLM agent module and its prompt; all gates and all 20 cases are re-run after every repair.
