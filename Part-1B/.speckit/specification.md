# NL Reminder Agent — Feature Specification

> Generated via `/speckit.specify` during Spec-Driven Development workflow.

## Overview

Parse unstructured natural-language reminder requests into structured JSON.
The agent classifies intent, extracts date/time, identifies the reminder
description, and requests clarification when mandatory fields are missing.

## Traceability Scheme

Every requirement is traceable through the chain
`US-Bn  →  FR-Bn  →  INV-n / BP-n / GR-n  →  TASK-n  →  evaluation cases (TC-nn)  →  commit ID`.

- `US-Bn` — user story; `FR-Bn` — functional requirement (the `B` suffix distinguishes Part 1B IDs from Part 1A's `US-n` / `FR-n`).
- `INV-n` structural invariants, `BP-n` behavioural properties and `GR-n` guardrail rules are defined below and are the checkable form of each `FR-Bn`.
- Each evaluation case in `evals/dataset.json` lists the IDs it covers in its `traces` field.
- Commit messages cite the commit ID plus the `TASK`/`US`/`FR` IDs they serve (see the repository root `README.md`). The full matrix is in `../TRACEABILITY.md`.

## User Stories

| ID | Story | Realised by |
|---|---|---|
| US-B1 | As a user, I want to say what I need to be reminded of and when, so that a structured reminder is created. | FR-B1 |
| US-B2 | As a user, I want to be asked a question when my request lacks the task or the time, so that nothing is guessed. | FR-B2 |
| US-B3 | As a user, I want to cancel a reminder in plain language, so that I do not have to use a form. | FR-B3 |
| US-B4 | As a user, I want to snooze a reminder for a period of time, so that I am reminded again later. | FR-B4 |
| US-B5 | As a user, I want to reschedule a reminder to a new time, so that it still fits my plans. | FR-B5 |
| US-B6 | As a user, I want empty, malformed or hostile input to be handled safely, so that the agent never crashes or misbehaves. | FR-B6 |
| US-B7 | As an integrator, I want every response to follow a fixed schema, so that downstream code can rely on it despite wording variation. | FR-B7 |

## Functional Requirements

| ID | Requirement | Checkable as |
|---|---|---|
| FR-B1 | Create-reminder requests with both a description and a time produce `status: "success"` with `description` and `datetime` populated. | BP-1, INV-4, GR-4 |
| FR-B2 | A create request missing the description or the time produces `status: "clarify"` with a non-empty `clarification_needed` asking *what* or *when*. | BP-2, BP-3, INV-5 |
| FR-B3 | Cancel requests produce `intent: "cancel"`. | BP-4, INV-2 |
| FR-B4 | Snooze requests produce `intent: "snooze"` with a `snooze_duration` (default 15 minutes, Clarification Q5). | BP-5, INV-2 |
| FR-B5 | Reschedule requests produce `intent: "reschedule"`. | BP-6, INV-2, INV-4 |
| FR-B6 | Empty, whitespace-only, malformed, very long or injection-like input is handled without crashing; empty input returns `status: "error"` with an error message. | BP-7, INV-6, GR-1, GR-2, GR-3, GR-4 |
| FR-B7 | Every output conforms to the output schema contract and the structural invariants. | INV-1, INV-2, INV-3, INV-4 |

## Output Schema Contract

Every output must include these fields:

```json
{
  "status": "success | clarify | error",
  "intent": "create_reminder | reschedule | snooze | cancel | null",
  "confidence": 0.0-1.0,
  "description": "string | null",
  "datetime": "ISO-8601 string | null",
  "error": "string | null"
}
```

Optional fields (present when relevant):
- `clarification_needed`: string — present when `status == "clarify"`
- `snooze_duration`: string — present when `intent == "snooze"`
- `is_date_only`: boolean — present when datetime has no time component

## Structural Invariants

- INV-1: `status` must be one of `{"success", "clarify", "error"}`.
- INV-2: `intent` must be one of `{"create_reminder", "reschedule", "snooze", "cancel", null}`.
- INV-3: `confidence` must be a number in `[0.0, 1.0]`.
- INV-4: If `datetime` is non-null, it must be a valid ISO-8601 string.
- INV-5: If `status == "clarify"`, then `clarification_needed` must be present and non-empty.
- INV-6: If `status == "error"`, then `error` must be present and non-empty.

## Behavioural Properties

- BP-1: **Create reminder** inputs that contain both a description and a time should produce `status: "success"` with both `description` and `datetime` populated.
- BP-2: **Missing description** — a create request with time but no clear task should produce `status: "clarify"` asking what to be reminded about.
- BP-3: **Missing time** — a create request with a task but no time should produce `status: "clarify"` asking when.
- BP-4: **Cancel** inputs should produce `intent: "cancel"`.
- BP-5: **Snooze** inputs should produce `intent: "snooze"` with a `snooze_duration`.
- BP-6: **Reschedule** inputs should produce `intent: "reschedule"`.
- BP-7: **Empty/malformed input** should produce `status: "error"`.

## Safety / Guardrail Rules

- GR-1: Empty or whitespace-only input must return an error, not crash.
- GR-2: Extremely long input (>10,000 chars) should be handled gracefully.
- GR-3: Inputs with injection-like patterns (SQL, HTML, script tags) must not cause errors or unexpected behavior — treat them as regular text.
- GR-4: The agent must never fabricate a datetime not derivable from the input.

## Evaluation Threshold

- **Overall pass rate:** >= 80% of evaluation cases must pass all applicable checks.
- **Scoring method:** Each test case is scored binary (pass/fail) across three layers: schema validation, property/invariant checks, and semantic/quality evaluation. A case passes only if all applicable layers pass.

## Traceability

Each evaluation case maps to one or more of the invariants (INV-*), behavioural properties (BP-*), or guardrail rules (GR-*) defined above.
