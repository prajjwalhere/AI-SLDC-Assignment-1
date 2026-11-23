# Smart Todo CLI — Feature Specification

> Generated via `/speckit.specify` during Spec-Driven Development workflow.

## Overview

Build a deterministic CLI application for task management with the following
capabilities: task CRUD, tag-based filtering, JSON persistence, priority sorting,
and enforced status transitions.

## Traceability Scheme

Every requirement is traceable through the chain
`US-n  →  FR-n  →  AC-n.m  →  TASK-n  →  tests  →  commit ID`.

- `US-n` — user story (added to make the story-to-requirement link explicit).
- `FR-n` — functional requirement. Each FR is realised by exactly one user story (same number).
- `AC-n.m` — numbered, binary acceptance criterion of `FR-n`.
- Commit messages cite the commit ID plus the `TASK`/`US`/`FR` IDs they serve
  (see the repository root `README.md`). The full matrix is in `../TRACEABILITY.md`.

## User Stories

| ID | Story | Realised by |
|---|---|---|
| US-1 | As a CLI user, I want to add a task with a title, priority and tags, so that I can capture work to be done. | FR-1 |
| US-2 | As a CLI user, I want to retrieve a single task by its id, so that I can inspect its details. | FR-2 |
| US-3 | As a CLI user, I want to update a task's title, priority or tags, so that I can keep it accurate. | FR-3 |
| US-4 | As a CLI user, I want to delete a task, so that I can remove work that is no longer relevant. | FR-4 |
| US-5 | As a CLI user, I want to move a task forward through `pending → in_progress → done`, so that its progress is tracked reliably. | FR-5 |
| US-6 | As a CLI user, I want to list tasks filtered by tag or status and sorted by priority, so that I can focus on what matters. | FR-6 |
| US-7 | As a CLI user, I want my tasks saved to a JSON file, so that they survive between sessions. | FR-7 |

## Feature Requirements

### FR-1: Task Creation (add)

**User story:** US-1

| Field | Rule |
|---|---|
| `title` | Non-empty string, whitespace-trimmed |
| `priority` | Enum: `high`, `medium` (default), `low` |
| `tags` | List of non-empty strings; default `[]` |
| `status` | Always starts as `pending` |
| `id` | Auto-incremented integer, unique, immutable |
| `created_at` | ISO-8601 timestamp at creation |
| `updated_at` | ISO-8601 timestamp, refreshed on every mutation |

**Acceptance Criteria:**
- AC-1.1: `add "Buy milk"` creates a task with id=1, status=pending, priority=medium.
- AC-1.2: `add "Fix bug" -p high -t work urgent` sets priority=high, tags=["work","urgent"].
- AC-1.3: `add ""` exits with code 1 and prints an error.
- AC-1.4: `add "Task" -p critical` exits with code 1 (invalid priority).

### FR-2: Task Retrieval (get)

**User story:** US-2

**Acceptance Criteria:**
- AC-2.1: `get <id>` prints JSON for an existing task.
- AC-2.2: `get <nonexistent-id>` exits with code 1.

### FR-3: Task Update (update)

**User story:** US-3

| Updatable Fields | Constraint |
|---|---|
| `title` | Must remain non-empty |
| `priority` | Must be a valid priority value |
| `tags` | Replacement list |

**Acceptance Criteria:**
- AC-3.1: `update <id> --title "New"` changes only the title and refreshes `updated_at`.
- AC-3.2: Attempting to update `status` via update (not transition) fails.
- AC-3.3: Updating a nonexistent task exits with code 1.

### FR-4: Task Deletion (delete)

**User story:** US-4

**Acceptance Criteria:**
- AC-4.1: `delete <id>` removes the task; subsequent `get <id>` returns nothing.
- AC-4.2: Deleting one task does not affect others.
- AC-4.3: Deleting a nonexistent task exits with code 1.

### FR-5: Status Transitions (transition)

**User story:** US-5

| From | Allowed To |
|---|---|
| `pending` | `in_progress` |
| `in_progress` | `done` |
| `done` | *(terminal — no transitions)* |

**Acceptance Criteria:**
- AC-5.1: `transition <id> in_progress` moves a pending task to in_progress.
- AC-5.2: `transition <id> done` moves an in_progress task to done.
- AC-5.3: Skipping a state (pending → done) exits with code 1.
- AC-5.4: Reversing (done → in_progress) exits with code 1.

### FR-6: Listing, Filtering & Sorting (list)

**User story:** US-6

**Acceptance Criteria:**
- AC-6.1: `list` returns all tasks as a JSON array.
- AC-6.2: `list --tag work` returns only tasks tagged "work".
- AC-6.3: `list --status pending` returns only pending tasks.
- AC-6.4: `list --sort-priority` returns tasks ordered high → medium → low.
- AC-6.5: Filters and sort can be combined.

### FR-7: JSON Persistence

**User story:** US-7

**Acceptance Criteria:**
- AC-7.1: Data survives process restart (new TaskManager reads saved file).
- AC-7.2: The JSON file is structurally valid after every operation.
- AC-7.3: A fresh start with no file produces an empty task list.
