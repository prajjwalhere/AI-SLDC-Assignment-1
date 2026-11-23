"""Non-Deterministic Evaluation Harness for NL Reminder Agent.

Three-layer pipeline per specification:
  Layer 1 — Structural: JSON schema conformance
  Layer 2 — Property/Invariant: deterministic rules from spec (INV-1..INV-6)
  Layer 3 — Semantic/Quality: ground-truth comparison with fuzzy matching

Aggregate: binary pass/fail per case; overall >= 80% threshold.

Options (Amendment 1): --agent selects the agent module (default: reminder_agent), --out selects the
results file, --pace sets a pause between cases. An agent may raise an exception with the attribute
`is_service_error = True` (provider outage, rate limit, timeout...). Such a case is recorded as
SERVICE_ERROR, is excluded from the pass rate, and makes the run verdict INCONCLUSIVE (exit code 2).
"""

import argparse
import importlib
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import jsonschema

PART_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = PART_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

DEFAULT_AGENT = "reminder_agent"

HARNESS_DIR = PART_DIR / ".harness"
EVALS_DIR = PART_DIR / "evals"
EVIDENCE_DIR = PART_DIR / "evidence"
SCHEMA_PATH = HARNESS_DIR / "schema.json"
DATASET_PATH = EVALS_DIR / "dataset.json"

PASS_THRESHOLD = 0.80


def load_schema() -> dict:
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_dataset() -> list[dict]:
    with open(DATASET_PATH, encoding="utf-8") as f:
        return json.load(f)


# --- Layer 1: Structural Validation ---

def validate_schema(output: dict, schema: dict) -> dict:
    """Layer 1: Validate output against JSON schema."""
    try:
        jsonschema.validate(instance=output, schema=schema)
        return {"passed": True, "errors": []}
    except jsonschema.ValidationError as e:
        return {"passed": False, "errors": [e.message]}
    except jsonschema.SchemaError as e:
        return {"passed": False, "errors": [f"Schema error: {e.message}"]}


# --- Layer 2: Property/Invariant Checks ---

def check_invariants(output: dict) -> dict:
    """Layer 2: Check specification invariants INV-1 through INV-6."""
    errors = []

    # INV-1: status must be valid
    if output.get("status") not in {"success", "clarify", "error"}:
        errors.append(f"INV-1: Invalid status '{output.get('status')}'")

    # INV-2: intent must be valid
    valid_intents = {"create_reminder", "reschedule", "snooze", "cancel", None}
    if output.get("intent") not in valid_intents:
        errors.append(f"INV-2: Invalid intent '{output.get('intent')}'")

    # INV-3: confidence must be in [0.0, 1.0]
    conf = output.get("confidence")
    if conf is not None:
        if not isinstance(conf, (int, float)) or conf < 0.0 or conf > 1.0:
            errors.append(f"INV-3: Confidence {conf} not in [0.0, 1.0]")

    # INV-4: datetime must be valid ISO-8601 if present
    dt = output.get("datetime")
    if dt is not None:
        try:
            datetime.fromisoformat(dt)
        except (ValueError, TypeError):
            errors.append(f"INV-4: Invalid ISO-8601 datetime '{dt}'")

    # INV-5: clarify status requires clarification_needed
    if output.get("status") == "clarify":
        cn = output.get("clarification_needed")
        if not cn or not cn.strip():
            errors.append("INV-5: status='clarify' but no clarification_needed")

    # INV-6: error status requires error message
    if output.get("status") == "error":
        err = output.get("error")
        if not err or not str(err).strip():
            errors.append("INV-6: status='error' but no error message")

    return {"passed": len(errors) == 0, "errors": errors}


# --- Layer 3: Semantic/Quality Evaluation ---

def evaluate_semantics(output: dict, expected: dict) -> dict:
    """Layer 3: Evaluate semantic correctness against expected outcomes."""
    errors = []

    # Check expected status
    if "status" in expected:
        if output.get("status") != expected["status"]:
            errors.append(
                f"Expected status='{expected['status']}', got '{output.get('status')}'"
            )

    # Check expected intent
    if "intent" in expected:
        if output.get("intent") != expected["intent"]:
            errors.append(
                f"Expected intent='{expected['intent']}', got '{output.get('intent')}'"
            )

    # Check intent is one of allowed values
    if "intent_one_of" in expected:
        if output.get("intent") not in expected["intent_one_of"]:
            errors.append(
                f"Expected intent in {expected['intent_one_of']}, got '{output.get('intent')}'"
            )

    # Check description contains expected substring (fuzzy)
    if "description_contains" in expected:
        desc = output.get("description") or ""
        if expected["description_contains"].lower() not in desc.lower():
            errors.append(
                f"Expected description to contain '{expected['description_contains']}', "
                f"got '{desc}'"
            )

    # Check datetime is non-null when expected
    if expected.get("datetime_not_null") and output.get("datetime") is None:
        errors.append("Expected datetime to be non-null, got null")

    # Check clarification is present
    if expected.get("has_clarification"):
        if not output.get("clarification_needed"):
            errors.append("Expected clarification_needed to be present")

    # Check clarification topic
    if "clarification_about" in expected:
        cn = (output.get("clarification_needed") or "").lower()
        topic = expected["clarification_about"]
        if topic == "what" and "what" not in cn and "about" not in cn:
            errors.append(f"Clarification should ask about 'what', got: '{cn}'")
        elif topic == "when" and "when" not in cn and "time" not in cn:
            errors.append(f"Clarification should ask about 'when', got: '{cn}'")

    # Check error message is present
    if expected.get("has_error_message"):
        if not output.get("error"):
            errors.append("Expected error message to be present")

    # Check snooze duration
    if "snooze_duration_contains" in expected:
        sd = output.get("snooze_duration") or ""
        if expected["snooze_duration_contains"] not in sd:
            errors.append(
                f"Expected snooze_duration to contain '{expected['snooze_duration_contains']}', "
                f"got '{sd}'"
            )

    if expected.get("snooze_duration_not_null") and not output.get("snooze_duration"):
        errors.append("Expected snooze_duration to be non-null")

    return {"passed": len(errors) == 0, "errors": errors}


# --- Main Evaluation Runner ---

def run_evaluation(agent_name: str = DEFAULT_AGENT, out_path: Path | None = None, pace: float = 0.0) -> dict:
    """Run the full 3-layer evaluation pipeline."""
    agent_module = importlib.import_module(agent_name)
    parse_reminder = agent_module.parse_reminder
    agent_info = getattr(agent_module, "AGENT_INFO", {"module": agent_name})

    schema = load_schema()
    dataset = load_dataset()

    print(f"Evaluation started: {datetime.now().isoformat()}")
    print(f"Agent: {agent_name} {agent_info}")
    print(f"Dataset: {len(dataset)} cases")
    print(f"Threshold: {PASS_THRESHOLD * 100:.0f}%")
    print()

    results = []

    for index, case in enumerate(dataset):
        case_id = case["id"]
        category = case["category"]
        input_text = case["input"]
        expected = case.get("expected", {})

        if index > 0 and pace > 0:
            time.sleep(pace)

        print(f"--- {case_id} [{category}] ---")
        print(f"  Input: {repr(input_text[:80])}")

        # Run the agent
        try:
            output = parse_reminder(input_text)
            crashed = False
        except Exception as e:
            if getattr(e, "is_service_error", False):
                # Provider / service failure: not a verdict on the application (Amendment 1, FR-B8)
                print(f"  SERVICE_ERROR: {getattr(e, 'code', 'SERVICE_ERROR')}: {e}")
                results.append({
                    "case_id": case_id,
                    "category": category,
                    "input": input_text,
                    "output": None,
                    "service_error": {"code": getattr(e, "code", "SERVICE_ERROR"), "message": str(e)},
                    "overall": "SERVICE_ERROR",
                })
                continue
            output = {"_crash": str(e)}
            crashed = True
            print(f"  CRASH: {e}")

        if crashed:
            results.append({
                "case_id": case_id,
                "category": category,
                "input": input_text,
                "output": output,
                "layer1": {"passed": False, "errors": ["Agent crashed"]},
                "layer2": {"passed": False, "errors": ["Agent crashed"]},
                "layer3": {"passed": False, "errors": ["Agent crashed"]},
                "overall": "FAIL",
            })
            print(f"  Result: FAIL (crash)")
            continue

        # Layer 1: Schema
        l1 = validate_schema(output, schema)
        print(f"  L1 Schema:   {'PASS' if l1['passed'] else 'FAIL'}")
        if not l1["passed"]:
            for e in l1["errors"]:
                print(f"    - {e}")

        # Layer 2: Invariants
        l2 = check_invariants(output)
        print(f"  L2 Invariant: {'PASS' if l2['passed'] else 'FAIL'}")
        if not l2["passed"]:
            for e in l2["errors"]:
                print(f"    - {e}")

        # Layer 3: Semantics
        l3 = evaluate_semantics(output, expected)
        print(f"  L3 Semantic: {'PASS' if l3['passed'] else 'FAIL'}")
        if not l3["passed"]:
            for e in l3["errors"]:
                print(f"    - {e}")

        case_passed = l1["passed"] and l2["passed"] and l3["passed"]
        overall = "PASS" if case_passed else "FAIL"
        print(f"  Overall: {overall}")

        results.append({
            "case_id": case_id,
            "category": category,
            "input": input_text,
            "output": output,
            "layer1": l1,
            "layer2": l2,
            "layer3": l3,
            "overall": overall,
        })

    # Aggregate (service errors are reported separately and are not scored)
    service_errors = sum(1 for r in results if r["overall"] == "SERVICE_ERROR")
    evaluated = [r for r in results if r["overall"] != "SERVICE_ERROR"]
    total = len(evaluated)
    passed = sum(1 for r in evaluated if r["overall"] == "PASS")
    pass_rate = passed / total if total > 0 else 0.0
    threshold_met = pass_rate >= PASS_THRESHOLD
    if service_errors:
        verdict = "INCONCLUSIVE"
    else:
        verdict = "PASS" if threshold_met else "FAIL"

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"  Cases:     {total}")
    print(f"  Passed:    {passed}")
    print(f"  Failed:    {total - passed}")
    if service_errors:
        print(f"  Service errors (not scored): {service_errors}")
    print(f"  Pass rate: {pass_rate * 100:.1f}%")
    print(f"  Threshold: {PASS_THRESHOLD * 100:.0f}%")
    print(f"  VERDICT:   {verdict}")

    if not threshold_met:
        print("\n  Failed cases:")
        for r in evaluated:
            if r["overall"] == "FAIL":
                print(f"    {r['case_id']}: {r['input'][:50]}...")
                for layer in ["layer1", "layer2", "layer3"]:
                    for e in r[layer]["errors"]:
                        print(f"      [{layer}] {e}")

    # Save results
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    eval_output = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent_info,
        "total_cases": total,
        "passed": passed,
        "failed": total - passed,
        "service_errors": service_errors,
        "pass_rate": round(pass_rate, 4),
        "threshold": PASS_THRESHOLD,
        "verdict": verdict,
        "cases": results,
    }

    results_path = Path(out_path) if out_path else EVIDENCE_DIR / "eval-results.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(eval_output, f, indent=2, default=str)

    print(f"\nResults saved to: {results_path}")
    print(f"Evaluation completed: {datetime.now().isoformat()}")

    if verdict == "INCONCLUSIVE":
        sys.exit(2)
    sys.exit(0 if threshold_met else 1)


def main() -> None:
    parser = argparse.ArgumentParser(description="3-layer evaluation harness for the NL Reminder Agent")
    parser.add_argument("--agent", default=DEFAULT_AGENT, help="agent module in src/ (default: reminder_agent)")
    parser.add_argument("--out", default=None, help="results file (default: evidence/eval-results.json)")
    parser.add_argument("--pace", type=float, default=0.0, help="seconds to pause between cases")
    args = parser.parse_args()
    run_evaluation(args.agent, Path(args.out) if args.out else None, args.pace)


if __name__ == "__main__":
    main()
