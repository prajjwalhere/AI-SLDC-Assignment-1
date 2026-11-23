# NL Reminder Agent — Clarifications

> Generated via `/speckit.clarify` during Spec-Driven Development workflow.

Each clarification lists the requirements it affects (`Affects:`), so the decision stays traceable to the specification.

## Q1: What constitutes "non-deterministic behavior" in this application?

**Answer:** Three sources of non-determinism:
1. `dateparser` can produce different results for ambiguous time expressions (e.g., "next Friday" depends on the current day and locale).
2. Intent confidence scores include small random noise, so the same input may produce slightly different confidence values.
3. Ambiguous inputs may cross decision boundaries differently across runs (e.g., an input near the clarification threshold).

**Affects:** INV-3 (confidence range), INV-4, GR-4, FR-B1, FR-B7, Evaluation Threshold

## Q2: Should the agent handle multi-reminder inputs?

**Answer:** No. Each call to `parse_reminder()` processes a single reminder request. Batch processing is available via `process_batch()` but each input is independent.

**Affects:** US-B1, FR-B1

## Q3: What happens if dateparser cannot parse any date/time?

**Answer:** The agent returns `datetime: null`. For `create_reminder` intents, this triggers a clarification request (BP-3). For other intents, the null datetime is acceptable.

**Affects:** US-B2, FR-B2 (BP-3), INV-4

## Q4: How is "snooze" different from "reschedule"?

**Answer:** Snooze uses a relative duration ("snooze for 15 minutes") without a target datetime. Reschedule moves to a specific new time ("reschedule to 3pm"). The output schema reflects this: snooze has `snooze_duration`, reschedule has `datetime`.

**Affects:** US-B4, US-B5, FR-B4 (BP-5), FR-B5 (BP-6)

## Q5: What is the default snooze duration?

**Answer:** 15 minutes, if no duration is specified in the input.

**Affects:** US-B4, FR-B4 (BP-5)
