# NL Reminder Agent — Project Constitution

> Generated via `/speckit.constitution` during Spec-Driven Development workflow.

## Project Identity

A natural-language reminder agent that parses unstructured reminder requests
into structured JSON output. Supports create, reschedule, snooze, and cancel
intents with date/time extraction and clarification requests.

## Engineering Constraints

| Constraint | Threshold |
|---|---|
| Language | Python 3.10+ |
| External deps (runtime) | `dateparser` only |
| Output format | JSON conforming to defined schema |
| Type hints | All public functions |
| Lint violations (error) | 0 |
| Security findings (high) | 0 |
| Evaluation pass rate | >= 80% of test cases |

## Non-Negotiable Requirements

1. **Schema conformance** — Every output must match the defined JSON schema regardless of input.
2. **Supported intents only** — Output intent must be one of: `create_reminder`, `reschedule`, `snooze`, `cancel`.
3. **Mandatory clarification** — When description or datetime is missing for `create_reminder`, the agent must request clarification instead of guessing.
4. **Safe datetime** — Extracted datetimes must be valid ISO-8601 strings; no fabricated dates.
5. **Graceful error handling** — Malformed or empty input must return an error response, never crash.
6. **No secrets** — Source code must not contain API keys or credentials.

## Acceptance Authority

- Evaluation harness threshold (>= 80%) must be met.
- Human reviewer makes the final ACCEPT / REJECT decision.
