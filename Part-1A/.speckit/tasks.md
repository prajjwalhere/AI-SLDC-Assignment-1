# Smart Todo CLI — Implementation Tasks

> Generated via `/speckit.tasks` during Spec-Driven Development workflow.

Commit messages cite the task ID (for example `1A-0NN [TASK-2][US-1..US-4][FR-1..FR-4]`). Status is updated in the same commit that completes the task.

## Task Breakdown

### TASK-1: Scaffold project structure
- Create `src/todo_cli.py`, `tests/test_todo.py`, `.harness/` directory.
- **Traces to:** Plan §Architecture
- **Status:** DONE

### TASK-2: Implement TaskManager core (CRUD)
- Implement `add()`, `get()`, `update()`, `delete()` methods.
- Include input validation per specification FR-1 through FR-4.
- **Traces to:** US-1, US-2, US-3, US-4, FR-1, FR-2, FR-3, FR-4
- **Status:** TODO

### TASK-3: Implement status transition state machine
- Implement `transition()` with forward-only enforcement.
- **Traces to:** US-5, FR-5, Constitution §Non-Negotiable #2
- **Status:** TODO

### TASK-4: Implement listing, filtering, and sorting
- Implement `list_tasks()` with tag filter, status filter, priority sort.
- **Traces to:** US-6, FR-6
- **Status:** TODO

### TASK-5: Implement JSON persistence layer
- Implement `_load()` and `_save()` with UTF-8 encoding.
- Validate file structure on load.
- **Traces to:** US-7, FR-7, Clarification Q4
- **Status:** TODO

### TASK-6: Implement CLI entry point
- Wire argparse subcommands to TaskManager methods.
- Ensure proper exit codes (0/1).
- **Traces to:** US-1..US-7, Constitution §Non-Negotiable #4
- **Status:** TODO

### TASK-7: Write specification-derived tests
- Create pytest test suite covering all acceptance criteria.
- **Traces to:** All FR acceptance criteria (US-1..US-7, FR-1..FR-7)
- **Status:** TODO

### TASK-8: Configure and run harness
- Set up ruff, bandit, and pytest as harness gates.
- Create harness runner script.
- **Traces to:** Plan §Harness Strategy, Constitution §Acceptance Authority
- **Status:** DONE

### TASK-9: Capture evidence and document
- Record initial harness run, any failures, repairs, and final result.
- Write harness-log.md.
- **Traces to:** Constitution §Acceptance Authority
- **Status:** TODO
