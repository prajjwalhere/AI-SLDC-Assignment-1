# Smart Todo CLI — Technical Plan

> Generated via `/speckit.plan` during Spec-Driven Development workflow.

## Architecture

```
CLI (argparse)
     │
     ▼
 TaskManager   ←── business logic, validation, state machine
     │
     ▼
 JSON file     ←── persistence layer (stdlib json)
```

**Single-module design:** The application is small enough to live in one Python
file (`todo_cli.py`) with a `TaskManager` class and a `main()` CLI entry point.

## Technology Choices

| Concern | Choice | Rationale |
|---|---|---|
| Language | Python 3.10+ | Constitution constraint |
| CLI framework | `argparse` (stdlib) | No external deps required |
| Persistence | `json` (stdlib) | Simple, human-readable, meets spec |
| Testing | `pytest` | Industry standard, clean fixtures |
| Linting | `ruff` | Fast, comprehensive Python linter |
| Security | `bandit` | Python-specific SAST scanner |

## Data Model

```json
{
  "id": 1,
  "title": "Buy groceries",
  "priority": "medium",
  "status": "pending",
  "tags": ["shopping"],
  "created_at": "2026-11-23T10:00:00",
  "updated_at": "2026-11-23T10:00:00"
}
```

## Key Design Decisions

| # | Decision | Serves |
|---|---|---|
| D1 | **IDs are max(existing) + 1** — simple, monotonically increasing, never reused. | FR-1 (`id`), Constitution NN#1 |
| D2 | **Status transitions enforced in `transition()` method** — single point of control for the state machine. | FR-5, Clarification Q1, Constitution NN#2 |
| D3 | **`_save()` called after every mutation** — ensures data integrity per the constitution. | FR-7 (AC-7.2), Constitution NN#3 |
| D4 | **Validation at the boundary** — `add()`, `update()`, and `transition()` all validate inputs before mutating state. | FR-1, FR-3, FR-5, Constitution NN#5 |

(NN = Non-Negotiable Requirement in the constitution.)

## Harness Strategy

| Gate | Tool | Pass Criteria |
|---|---|---|
| Lint | `ruff check` | Zero error-level violations |
| Security | `bandit` | Zero high-severity findings |
| Tests | `pytest` | All tests pass |
