# Part 1B — Harness Log: Natural-Language Reminder Agent

## 1. Model and configuration (no secrets)

The repository contains two implementations of one application, and the logs should say which one belongs to each result. Two implementations have been used. There are two variants:

- Regex variant, where it uses no LLM and no external API. Intent comes from regex pattern scoring. A single `random.uniform(-0.05, 0.05)` noise value is added to every intent score.
- Dates come from `dateparser`.
- Environment is Python 3.13.7, whereas jsonschema is 4.26.0 and ruff is 0.17.6.

And now the LLM variant. The LLM variant calls the Groq chat completions API with a model, which is `openai/gpt-oss-120b`, where:

- temperature: 0
- reasoning effort: low
- JSON object output mode
- a 1,024 completion token limit
- a 45-second timeout

The current local date and time is given to the model, so relative dates are resolved. The harness spaces calls 3 seconds apart, and the key is read only from the environment, and none appears in any commit or result. The harness records this configuration in each result file under `agent`.

Now we come to the model selection finding. The first choice was Google Gemini, but due to unavailability of the model, I preferred to use Groq API.

## 2. Evaluation threshold and scoring method (as specified before the final evaluation)

- Declared upfront. The threshold was declared in the original specification before the dataset and the harness. It is a pass rate of at least 80%, where each case is scored binary across the three layers, which are schema, invariants and semantic, and passes only if all three layers pass.
- Amendment 1 kept the threshold, dataset, and schema layers unchanged and added the run verdict rules. PASS means no service errors and a pass rate of at least 80%, whereas FAIL means no service errors and a pass rate below 80%. INCONCLUSIVE means any case ended in a service error, and the run is repeated.
- Where to point? Commit `1B-017`, which holds the verdict rules.

## 3. Harness results

Dataset: there are 20 cases:

- Normal: 8
- Boundary: 4
- Ambiguous: 2
- Missing mandatory: 2
- Malformed: 2
- Adversarial: 2

There are three layers. The application runs in process. A crash fails all three layers, and a service error is excluded from scoring.

### 3.1 Layer 1 — structural (schema)

Layer 1 validates against `.harness/schema.json`.

### 3.2 Layer 2 — property / invariant

Layer 2 checks INV-1 to INV-6 in the code.

### 3.3 Layer 3 — semantic / quality

Layer 3 compares status, intent, intent in set, description substring, datetime presence, clarification presence and topic, error message and snooze duration to each case's expected value.

### 3.4 Aggregate result against the threshold

The LLM variant. Run 1, timestamp 21:56:52:

- Layer 1: 20/20
- Layer 2: 20/20
- Layer 3: 20/20

The overall is 20/20, and 0 service errors. Run 1 was pass.

Run 2 produces similar results at 21:59:17, and it passed again with zero service errors.

Now, when we discuss the output differences, 9 of the 20 outputs differ between the runs.

## 4. Failures encountered and evidence supplied to the coding agent

LLM variant: pre-checks were clean (ruff passes, 16 offline tests pass). Neither formal run had any failing case, so there is no failure evidence, and no failure was fed back to the agent. The only failures in this variant were the provider problems during model selection, which happened due to the unavailability of the Gemini API key functioning.

## 5. Repair made and re-evaluation outcome

When it comes to the LLM variant, no repair was needed. `final-generation/reminder_agent_llm.py` is byte-identical to the first generation. The only change between the preserved spec and the run was that reasoning_effort and the token limit were recorded in the configuration table, which was done before the formal run.

Whereas in the regex variant, the repair was fixed by reformatting the imports.

S311 was handled with a per-line `# noqa: S311` suppression, not a code change, because the randomness is deliberate non-determinism. The final file passes ruff. The 20/20 result before and after is in the same file, so no separate post-repair evaluation was recorded.

## 6. Final human review

### Decision (ACCEPT / REJECT)

_Write here._

### Justification

1. Passing: Everything in the dataset passes for both variants, and both harnesses pass from a fresh clone.

### Known limitations and residual risks

1. Not an unseen set: The dataset was authored before the LLM prompt, but the prompt author had seen it. The prompt was not changed after any run, and no held-out set existed.
2. Single evaluation: Each case is evaluated once per run with one repeat run for the LLM variant. Temperature 0 did not make any output identical, whereas layer 3 is substring matching, which is not an LLM judge, and GR-2 and GR-4 have no cases.
3. Suppression: The regex variant carries a `# noqa: S311` suppression.
4. The locale and other limits: The `dateparser` results depend on the locale and reference time. Recurrence is not supported, and only English is handled.
