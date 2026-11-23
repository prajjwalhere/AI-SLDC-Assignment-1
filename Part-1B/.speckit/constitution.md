# NL Reminder Agent — Project Constitution

> Generated via `/speckit.constitution` during Spec-Driven Development workflow.

## Project Identity

A natural-language reminder agent that parses unstructured reminder requests
into structured JSON output. Supports create, reschedule, snooze, and cancel
intents with date/time extraction and clarification requests.

## Engineering Constraints

| Constraint | Threshold |
|---|---|
| Language | Python 3.10+ |
| External deps (runtime) | `dateparser` only |
| Output format | JSON conforming to defined schema |
| Type hints | All public functions |
| Lint violations (error) | 0 |
| Security findings (high) | 0 |
| Evaluation pass rate | >= 80% of test cases |

## Non-Negotiable Requirements

1. **Schema conformance** — Every output must match the defined JSON schema regardless of input.
2. **Supported intents only** — Output intent must be one of: `create_reminder`, `reschedule`, `snooze`, `cancel`.
3. **Mandatory clarification** — When description or datetime is missing for `create_reminder`, the agent must request clarification instead of guessing.
4. **Safe datetime** — Extracted datetimes must be valid ISO-8601 strings; no fabricated dates.
5. **Graceful error handling** — Malformed or empty input must return an error response, never crash.
6. **No secrets** — Source code must not contain API keys or credentials.

## Acceptance Authority

- Evaluation harness threshold (>= 80%) must be met.
- Human reviewer makes the final ACCEPT / REJECT decision.

## Amendment 1 — LLM-backed implementation variant

> Added after the first accepted run, through the SDD artifacts (see `specification.md` Amendment 1). Non-Negotiable Requirements 1–6 above are unchanged and apply to both variants.

- **Second implementation.** `src/reminder_agent_llm.py` calls a hosted LLM. The regex implementation `src/reminder_agent.py` and its evidence are preserved unchanged.
- **Dependencies.** The LLM variant uses the Python standard library only (`http.client`); no vendor SDK.
- **Network.** Only the LLM variant may open network connections, and only to the configured provider over HTTPS.
- **Secrets.** The API key comes only from the process environment or the git-ignored `Part-1B/.env`. It must never be logged, committed, or written into evidence; error text must mask it.
- **Data sent to the provider.** Synthetic evaluation inputs only.
- **Protected during repair.** The evaluation dataset, the output schema, the harness evaluators and the 80% threshold may not be changed to obtain a PASS. A repair may change only the LLM agent module and its prompt. At most two repair attempts per cycle, then stop for human review.
- **Failure classes.** Service failures, bad model output, application failures and evaluation failures must be distinguishable in code and in recorded results. A provider outage is never counted as a wrong answer.
