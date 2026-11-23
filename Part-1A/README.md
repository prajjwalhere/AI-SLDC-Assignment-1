# Part 1A — Smart Todo & Task CLI (deterministic application)

A command-line task manager: task CRUD, tag filtering, priority sorting, forward-only status transitions and JSON persistence. Python 3.10+, standard library only for production code.

## Layout

| Path | Purpose |
|---|---|
| `.speckit/` | Spec Kit artifacts: `constitution.md`, `specification.md`, `clarification.md`, `plan.md`, `tasks.md` |
| `src/todo_cli.py` | The application (`TaskManager` + argparse CLI) |
| `tests/test_todo.py` | Deterministic pytest suite derived from the specification's acceptance criteria |
| `.harness/` | Harness: `run_harness.py` runner, `ruff.toml` (lint), `bandit.yaml` (security) |
| `evidence/` | `initial-generation/`, `final-generation/`, `harness-results.json`, `harness-log.md` |
| `TRACEABILITY.md` | US → FR → AC → TASK → test → source → commit matrix |

## Setup

```powershell
python -m pip install -r requirements.txt
```

## Run the application

```powershell
python src/todo_cli.py add "Fix bug" -p high -t work urgent
python src/todo_cli.py list --tag work --sort-priority
python src/todo_cli.py transition 1 in_progress
python src/todo_cli.py get 1
python src/todo_cli.py update 1 --title "Fix login bug"
python src/todo_cli.py delete 1
```

Data is stored in `todos.json` in the current working directory (git-ignored). Exit code is `0` on success and `1` on error.

## Run the tests

```powershell
python -m pytest tests -v
```

## Run the harness (lint → security → tests)

```powershell
python .harness/run_harness.py
```

The runner executes three gates (ruff, bandit, pytest), prints PASS/FAIL per gate, writes `evidence/harness-results.json` and exits `0` only if all gates pass. No API keys or secrets are used or required.
