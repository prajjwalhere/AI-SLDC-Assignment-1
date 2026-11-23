# Part 1A — Traceability Matrix

Chain: `US-n → FR-n → AC-n.m → TASK-n → test → source → commit ID`.
Requirement IDs come from [.speckit/specification.md](.speckit/specification.md); tasks from [.speckit/tasks.md](.speckit/tasks.md).
Commit IDs (`1A-NNN`) are listed in the [Commit index](#commit-index) and appear at the start of every commit message.

## Requirement → implementation → test

| US | FR | AC | Task | Source (`src/todo_cli.py`) | Tests (`tests/test_todo.py`) |
|---|---|---|---|---|---|
| US-1 | FR-1 | AC-1.1 | TASK-2 | `TaskManager.add` | `TestAddTask::test_add_basic_task` |
| US-1 | FR-1 | AC-1.2 | TASK-2 | `TaskManager.add` | `test_add_task_with_priority`, `test_add_task_with_tags` |
| US-1 | FR-1 | AC-1.3 | TASK-2, TASK-6 | `TaskManager.add`, `main` (ValueError → exit 1) | `test_add_task_empty_title_raises`, `test_add_task_whitespace_title_raises` |
| US-1 | FR-1 | AC-1.4 | TASK-2, TASK-6 | `TaskManager.add`, `main` | `test_add_task_invalid_priority_raises` |
| US-1 | FR-1 | (field rules) | TASK-2 | `TaskManager.add`, `_next_id` | `test_add_task_increments_id`, `test_add_task_strips_whitespace_from_title`, `test_add_task_empty_tag_raises`, `test_add_task_has_timestamps` |
| US-2 | FR-2 | AC-2.1 | TASK-2 | `TaskManager.get` | `TestGetTask::test_get_existing_task` |
| US-2 | FR-2 | AC-2.2 | TASK-2, TASK-6 | `TaskManager.get`, `main` (exit 1) | `test_get_nonexistent_task_returns_none` |
| US-3 | FR-3 | AC-3.1 | TASK-2 | `TaskManager.update` | `test_update_title`, `test_update_priority`, `test_update_tags`, `test_update_refreshes_updated_at` |
| US-3 | FR-3 | AC-3.2 | TASK-2 | `TaskManager.update` (allowed fields) | `test_update_invalid_field_raises` |
| US-3 | FR-3 | AC-3.3 | TASK-2, TASK-6 | `TaskManager.update`, `main` | `test_update_nonexistent_raises` |
| US-3 | FR-3 | (title rule) | TASK-2 | `TaskManager.update` | `test_update_empty_title_raises` |
| US-4 | FR-4 | AC-4.1 | TASK-2 | `TaskManager.delete` | `TestDeleteTask::test_delete_existing_task` |
| US-4 | FR-4 | AC-4.2 | TASK-2 | `TaskManager.delete` | `test_delete_does_not_affect_other_tasks` |
| US-4 | FR-4 | AC-4.3 | TASK-2, TASK-6 | `TaskManager.delete`, `main` | `test_delete_nonexistent_raises` |
| US-5 | FR-5 | AC-5.1 | TASK-3 | `TaskManager.transition`, `VALID_TRANSITIONS` | `TestStatusTransitions::test_pending_to_in_progress` |
| US-5 | FR-5 | AC-5.2 | TASK-3 | `TaskManager.transition` | `test_in_progress_to_done` |
| US-5 | FR-5 | AC-5.3 | TASK-3, TASK-6 | `TaskManager.transition`, `main` | `test_pending_to_done_blocked` |
| US-5 | FR-5 | AC-5.4 | TASK-3, TASK-6 | `TaskManager.transition`, `main` | `test_done_to_in_progress_blocked`, `test_done_is_terminal` |
| US-5 | FR-5 | (not found) | TASK-3 | `TaskManager.transition` | `test_transition_nonexistent_raises` |
| US-6 | FR-6 | AC-6.1 | TASK-4 | `TaskManager.list_tasks` | `TestListAndFilter::test_list_all_tasks` |
| US-6 | FR-6 | AC-6.2 | TASK-4 | `TaskManager.list_tasks` | `test_filter_by_tag` |
| US-6 | FR-6 | AC-6.3 | TASK-4 | `TaskManager.list_tasks` | `test_filter_by_status`, `test_filter_invalid_status_raises` |
| US-6 | FR-6 | AC-6.4 | TASK-4 | `TaskManager.list_tasks` | `test_sort_by_priority` |
| US-6 | FR-6 | AC-6.5 | TASK-4 | `TaskManager.list_tasks` | `test_combined_filter_and_sort` |
| US-7 | FR-7 | AC-7.1 | TASK-5 | `TaskManager._load`, `_save` | `TestPersistence::test_data_persists_across_instances` |
| US-7 | FR-7 | AC-7.2 | TASK-5 | `TaskManager._save` | `test_json_file_is_valid_after_operations` |
| US-7 | FR-7 | AC-7.3 | TASK-5 | `TaskManager._load` | `test_empty_file_starts_fresh` |
| US-1..US-7 | Constitution NN#1 (immutable unique IDs) | — | TASK-2 | `TaskManager._next_id` | `TestIdImmutability` (3 tests) |

The suite has 40 tests; every `AC-*` above is covered by at least one test.

## Clarifications → requirements

| Clarification | Decision | Requirements | Verified by |
|---|---|---|---|
| Q1 | `done` is terminal | US-5, FR-5 (AC-5.4) | `test_done_to_in_progress_blocked`, `test_done_is_terminal` |
| Q2 | Corrupt data file raises `ValueError`, never overwritten | US-7, FR-7 | no dedicated test (see gaps) |
| Q3 | Duplicate titles allowed | US-1, FR-1 | not asserted by a test (see gaps) |
| Q4 | UTF-8 in all file operations | US-7, FR-7 (TASK-5) | `test_json_file_is_valid_after_operations` reads the file as UTF-8 |
| Q5 | `update` cannot change `status` | US-3, FR-3 (AC-3.2) | `test_update_invalid_field_raises` |

## Harness traceability

| Gate | Tool | Config | Serves |
|---|---|---|---|
| Lint | ruff | `.harness/ruff.toml` | Constitution: lint violations = 0 |
| Security | bandit | `.harness/bandit.yaml` | Constitution: high-severity security findings = 0 |
| Tests | pytest | `tests/` | All acceptance criteria (FR-1..FR-7) |

## Known gaps (disclosed, not hidden)

- Acceptance criteria that state "exits with code 1" (AC-1.3, AC-1.4, AC-2.2, AC-3.3, AC-4.3, AC-5.3, AC-5.4) are verified at the `TaskManager` level (a `ValueError` is raised). The `main()` mapping of `ValueError` to exit code 1 is not exercised by a subprocess/CLI test.
- AC-6.3 is tested with the `in_progress` filter rather than `pending`.
- Clarification Q2 (corrupted data file) and Q3 (duplicate titles) have no dedicated test.
- Constitution thresholds for coverage (>= 90%), cyclomatic complexity (<= 10) and type hints on all public functions are stated but are not enforced by the three harness gates (ruff rules `E,F,W,I,N,UP,B,S,A`, bandit, pytest).

## Commit index

Every commit of this part, in order (generated from `git log`; hashes are of the commits listed, up to the commit before the index was last refreshed).

| Commit ID | Git hash | Refs | Summary |
|---|---|---|---|
| 1A-001 | f10861d | [CONSTITUTION] | Add Part 1A project constitution (engineering constraints, non-negotiables) |
| 1A-002 | a75b25e | [SPECIFY][US-1..US-7][FR-1..FR-7] | Add Part 1A feature specification with user stories and numbered acceptance criteria |
| 1A-003 | 1e7991d | [CLARIFY][US-1,US-3,US-5,US-7][FR-1,FR-3,FR-5,FR-7] | Add clarifications Q1-Q5 with affected requirements |
| 1A-004 | 945c5ab | [PLAN][FR-1,FR-3,FR-5,FR-7] | Add technical plan, design decisions D1-D4 and harness strategy |
| 1A-005 | da79682 | [TASKS][US-1..US-7][FR-1..FR-7] | Add task breakdown TASK-1..TASK-9 with requirement traces |
| 1A-006 | 727637e | [TASK-1] | Scaffold Part 1A (README with layout and run instructions, requirements.txt) |
| 1A-007 | 5893299 | [TASK-8] | Add harness (ruff, bandit, pytest gates) and runner before implementation |
| 1A-008 | e8f914b | [TASK-7][US-1..US-7][FR-1..FR-7] | Add specification-derived pytest suite (written before implementation) |
| 1A-009 | 581c182 | [TASK-2..TASK-6][US-1..US-7][FR-1..FR-7] | First coding-agent generation of src/todo_cli.py, preserved unchanged in evidence/initial-generation |
| 1A-010 | 350fc4c | [TASK-8][TASK-9] | Record first formal harness run of the initial generation (lint FAIL, security PASS, tests PASS) |
| 1A-011 | 1a9e348 | [REPAIR-1][TASK-2..TASK-6][FR-1..FR-7] | Repair lint findings I001, UP015, UP045 in src/todo_cli.py (no spec, test or harness change) |
| 1A-012 | 580b1cd | [TASK-9] | Preserve final generation and passing harness result (lint, security, tests PASS) |
| 1A-013 | 5100e10 | [TASK-9] | Add harness-log.md placeholder for student-authored log; update TASK-9 status |
| 1A-014 | 188d116 | [TRACEABILITY][US-1..US-7][FR-1..FR-7] | Add US/FR/AC to task, source and test traceability matrix with disclosed gaps |
