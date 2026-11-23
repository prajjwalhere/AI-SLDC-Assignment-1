# Assignment 1 — Spec-Driven Development and Harness Engineering

AI-Augmented Software Development Life Cycle (SEZG534, BITS Pilani) · Assignment 1: *From specification-controlled coding agents to deterministic and non-deterministic validation.*

Two small applications, each specified with Spec Kit-style artifacts (constitution → specify → clarify → plan → tasks), implemented by an AI coding agent, and verified by a harness that is independent of the generated code.

| Folder | Application | Harness |
|---|---|---|
| [Part-1A/](Part-1A/) | Smart Todo & Task CLI (deterministic) | Lint (ruff) → security (bandit) → unit/contract tests (pytest) |
| [Part-1B/](Part-1B/) | Natural-Language Reminder Agent (non-deterministic) | One 3-layer pipeline: schema → invariants → semantic/quality, 20 cases, 80% threshold |

```
Assignment-1/
  README.md
  Part-1A/   .speckit/  src/  tests/  .harness/  evidence/  TRACEABILITY.md  README.md
  Part-1B/   .speckit/  src/  prompts/  evals/  .harness/  evidence/  TRACEABILITY.md  README.md
```

## Setup environment

| Item | Value |
|---|---|
| OS | Windows 11 Home |
| Shell | PowerShell |
| Python | 3.13.7 (projects target Python 3.10+) |
| Git | 2.39.3 (Windows) |
| Part 1A tooling | ruff 0.17.6, bandit 1.9.4, pytest 9.2.0 |
| Part 1B tooling | dateparser 1.5.1, jsonschema 4.26.0, ruff 0.17.6 |
| AI coding agent | Claude (Anthropic) |
| Spec Kit | The artifacts live in each part's `.speckit/` folder and keep the `/speckit.*` command headers they were produced with. The `specify` CLI is not installed on this machine, so no `specify` version or `init-options.json` is recorded. |

No API keys, tokens or `.env` files are used or required by either part.

## How to run

```powershell
# Part 1A
cd Part-1A
python -m pip install -r requirements.txt
python .harness/run_harness.py          # lint -> security -> tests; exit 0 only if all pass

# Part 1B
cd ..\Part-1B
python -m pip install -r requirements.txt
python .harness/run_evaluation.py       # 3-layer evaluation; exit 0 only if pass rate >= 80%
```

Each part's README has the full run instructions. Both harnesses were run successfully from a fresh clone of this repository.

## Traceability

Requirements are traceable end to end:

`user story (US-n / US-Bn) → functional requirement (FR-n / FR-Bn) → acceptance criterion or invariant/property/guardrail (AC-n.m, INV-n, BP-n, GR-n) → task (TASK-n) → test or evaluation case → source → commit ID`

- Part 1A uses `US-1..US-7`, `FR-1..FR-7`, `AC-n.m`; Part 1B uses `US-B1..US-B7`, `FR-B1..FR-B7`, `INV-n`, `BP-n`, `GR-n`.
- **Every commit message starts with its own commit ID** followed by the IDs it serves:

  ```
  <ID> [<task / artifact>][<US ids>][<FR ids>]: <message>
  1A-009 [TASK-2..TASK-6][US-1..US-7][FR-1..FR-7]: First coding-agent generation ...
  ```

  | Prefix | Scope |
  |---|---|
  | `ROOT-nnn` | Repository-level commits (setup, README) |
  | `1A-nnn` | Part 1A commits (numbered in order) |
  | `1B-nnn` | Part 1B commits (numbered in order) |

  Artifact tags used in messages: `CONSTITUTION`, `SPECIFY`, `CLARIFY`, `PLAN`, `TASKS`, `PROMPT`, `REPAIR-n`, `TRACEABILITY`; `TASK-n` refers to `.speckit/tasks.md` of that part.
- Full matrices and the commit index: [Part-1A/TRACEABILITY.md](Part-1A/TRACEABILITY.md), [Part-1B/TRACEABILITY.md](Part-1B/TRACEABILITY.md).
- The first generation of each application is preserved unchanged in `evidence/initial-generation/` and the final one in `evidence/final-generation/`; the repair between them is a separate commit (`1A-011`, `1B-012`).

## Evidence provenance

The two applications, specifications, harnesses, datasets and evidence artifacts were developed in an earlier working copy. This repository re-creates that work with a step-by-step commit history. The source files, tests, dataset, harness code and the recorded harness/evaluation results (`evidence/**/harness-results.json`, `eval-results.json`) are carried over from that working copy unchanged. Additions made while assembling this repository, none of which alter the applications, tests, dataset or thresholds:

- user-story and functional-requirement IDs, `Affects:` / `Serves` trace lines and task trace lines in the `.speckit/` artifacts;
- `TRACEABILITY.md` matrices (including disclosed gaps) and the per-part READMEs;
- `Part-1B/.harness/ruff.toml` (the same rule set as Part 1A) so the lint check described for Part 1B is reproducible;
- `requirements.txt` files.

## Harness logs and human decisions

`Part-1A/evidence/harness-log.md` and `Part-1B/evidence/harness-log.md` (including the final ACCEPT/REJECT decision, known limitations and residual risks) are written by the student, not by the AI agent.

## AI-use statement

An AI coding agent (Claude, via Claude Code) was used, under the student's direction, to re-create and organise this repository: the Spec Kit-style artifacts, the application code, the tests, the harness scripts, the evaluation dataset, the READMEs and traceability documents, and the commit history. The student chose the problems, supplied the original work and the assignment prompt, and is responsible for reviewing the submitted software and evidence. The harness logs and the reflection report are written by the student and were not generated by the AI agent. The AI agent did not add itself as a co-author of any commit.
