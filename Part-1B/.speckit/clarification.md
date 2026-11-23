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

## Amendment 1 clarifications (LLM-backed variant)

## Q6: Which provider and model, and why?

**Answer:** Groq with `openai/gpt-oss-120b`. A small live probe was run before the formal evaluation (2026-11-23, synthetic inputs only):
- The first choice, Google Gemini, was not usable: `gemini-2.5-flash` returned HTTP 404 (retired for new users); the current flash models (`gemini-3.8-flash`, `3.7-flash`, `3.5-flash`, `3.5-flash-lite`, `3.1-flash-lite`, `3-flash-preview`, `flash-latest`) returned HTTP 503 on every attempt over several tries; the pro models returned HTTP 429 (no quota).
- Groq's model list loaded, and `openai/gpt-oss-20b`, `openai/gpt-oss-120b` and `qwen/qwen3.8-27b` all returned valid JSON-object-mode answers in under one second for two probe requests. `openai/gpt-oss-120b` was chosen.

**Affects:** US-B8, FR-B8, Evaluation Threshold (configuration)

## Q7: What counts as a service failure and what counts as a wrong answer?

**Answer:** See the failure-class table in `specification.md` Amendment 1. Timeouts, HTTP 429/5xx after bounded retries, authentication and network errors, and a missing key are service failures. Output that is not valid JSON or lacks contract fields is bad model output and is never retried. Everything else is judged by the three layers.

**Affects:** US-B8, FR-B8

## Q8: Are the dataset, schema, harness evaluators or threshold changed for the LLM variant?

**Answer:** No. The 20-case dataset, `.harness/schema.json`, the layer 1–3 evaluators and the 80% threshold are unchanged. The only harness additions are command-line options to select the agent module and the output path, a `--pace` delay, and recording of service errors as a separate class. A repair may change only the LLM agent module and its prompt.

**Affects:** Evaluation Threshold, FR-B7, FR-B8

## Q9: What happens to the regex implementation and its evidence?

**Answer:** It is kept unchanged. Its 20/20 result remains valid for that implementation and is not overwritten; LLM-variant evidence lives under `evidence/llm-variant/`.

**Affects:** FR-B1..FR-B7
