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
