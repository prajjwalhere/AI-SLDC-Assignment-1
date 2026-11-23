# Smart Todo CLI — Project Constitution

> Generated via `/speckit.constitution` during Spec-Driven Development workflow.

## Project Identity

A command-line task management application providing CRUD operations, tagging,
priority sorting, and JSON-based persistence.

## Target Users

Developers and power users who prefer terminal-based task management.

## Engineering Constraints

| Constraint | Threshold |
|---|---|
| Language | Python 3.10+ (stdlib only for core logic) |
| External runtime deps | None for production code |
| Data persistence | Local JSON file |
| Type hints | All public functions |
| Max cyclomatic complexity | 10 per function |
| Security findings (high) | 0 |
| Lint violations (error-level) | 0 |
| Test coverage (core logic) | >= 90% |

## Non-Negotiable Requirements

1. **Unique immutable IDs** — Task IDs must be unique and never change once assigned.
2. **Forward-only status transitions** — `pending → in_progress → done`; no backward moves.
3. **Data integrity** — The JSON data file must be valid after every write operation.
4. **Proper exit codes** — 0 for success, 1 for errors.
5. **Input validation** — All user-facing parameters must be validated before processing.
6. **No secrets** — Source code must not contain API keys, tokens, or credentials.

## Acceptance Authority

- Automated harness gates (lint, security, tests) must all PASS.
- Human reviewer makes the final ACCEPT / REJECT decision.
