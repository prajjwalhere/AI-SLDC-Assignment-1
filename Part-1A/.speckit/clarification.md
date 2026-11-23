# Smart Todo CLI — Clarifications

> Generated via `/speckit.clarify` during Spec-Driven Development workflow.

Each clarification lists the requirements it affects (`Affects:`), so the decision stays traceable to the specification.

## Q1: Can a task be re-opened after being marked done?

**Answer:** No. The constitution mandates forward-only transitions. Once a task
reaches `done`, it is terminal. Users should create a new task if the work
resurfaces.

**Affects:** US-5, FR-5 (AC-5.4)

## Q2: What happens if the JSON file is corrupted or not a valid array?

**Answer:** The application raises a `ValueError` with a clear message. It does
not silently overwrite or discard the file. The user must fix or remove the
corrupted file manually.

**Affects:** US-7, FR-7

## Q3: Are duplicate task titles allowed?

**Answer:** Yes. Tasks are identified by their unique integer `id`, not by title.
Two tasks may share the same title.

**Affects:** US-1, FR-1

## Q4: What encoding should the JSON file use?

**Answer:** UTF-8, explicitly specified in all file operations, to prevent
platform-dependent encoding issues.

**Affects:** US-7, FR-7

## Q5: Should the `update` command allow changing `status`?

**Answer:** No. Status changes go through the dedicated `transition` command,
which enforces the state machine. The `update` command is limited to `title`,
`priority`, and `tags`.

**Affects:** US-3, US-5, FR-3 (AC-3.2), FR-5
