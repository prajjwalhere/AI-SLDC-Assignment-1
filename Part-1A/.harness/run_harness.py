"""Deterministic Harness Runner for Smart Todo CLI.

Runs three sequential gates:
  1. Lint (ruff) — static code quality
  2. Security (bandit) — SAST scan
  3. Tests (pytest) — specification-derived unit/contract tests

Each gate produces a PASS/FAIL result with captured output.
All gates must PASS for the harness to report overall PASS.
"""

import json
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path


PART_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = PART_DIR / "src"
TESTS_DIR = PART_DIR / "tests"
HARNESS_DIR = PART_DIR / ".harness"
EVIDENCE_DIR = PART_DIR / "evidence"


def run_command(cmd: list[str], cwd: str | None = None) -> dict:
    """Run a command and capture its output."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd or str(PART_DIR),
    )
    return {
        "command": " ".join(cmd),
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "passed": result.returncode == 0,
    }


def gate_lint() -> dict:
    """Gate 1: Ruff lint check."""
    print("=" * 60)
    print("GATE 1: Lint (ruff)")
    print("=" * 60)

    result = run_command([
        sys.executable, "-m", "ruff", "check",
        str(SRC_DIR),
        "--config", str(HARNESS_DIR / "ruff.toml"),
    ])

    status = "PASS" if result["passed"] else "FAIL"
    print(f"Result: {status}")
    if result["stdout"]:
        print(result["stdout"])
    if result["stderr"]:
        print(result["stderr"])

    return {"gate": "lint", "tool": "ruff", "status": status, **result}


def gate_security() -> dict:
    """Gate 2: Bandit SAST scan."""
    print("\n" + "=" * 60)
    print("GATE 2: Security (bandit)")
    print("=" * 60)

    result = run_command([
        sys.executable, "-m", "bandit",
        "-r", str(SRC_DIR),
        "-f", "json",
        "--configfile", str(HARNESS_DIR / "bandit.yaml"),
    ])

    try:
        bandit_output = json.loads(result["stdout"])
        high_issues = [
            r for r in bandit_output.get("results", [])
            if r.get("issue_severity") == "HIGH"
        ]
        passed = len(high_issues) == 0
    except (json.JSONDecodeError, KeyError):
        high_issues = []
        passed = result["passed"]

    status = "PASS" if passed else "FAIL"
    print(f"Result: {status}")
    if high_issues:
        for issue in high_issues:
            print(f"  HIGH: {issue.get('issue_text')} at {issue.get('filename')}:{issue.get('line_number')}")
    else:
        print("  No high-severity findings.")

    return {
        "gate": "security",
        "tool": "bandit",
        "status": status,
        "high_issues": len(high_issues),
        **result,
        "passed": passed,
    }


def gate_tests() -> dict:
    """Gate 3: Pytest unit & contract tests."""
    print("\n" + "=" * 60)
    print("GATE 3: Tests (pytest)")
    print("=" * 60)

    result = run_command([
        sys.executable, "-m", "pytest",
        str(TESTS_DIR),
        "-v",
        "--tb=short",
    ])

    status = "PASS" if result["passed"] else "FAIL"
    print(f"Result: {status}")
    print(result["stdout"])
    if result["stderr"]:
        print(result["stderr"])

    return {"gate": "tests", "tool": "pytest", "status": status, **result}


def main() -> None:
    print(f"Harness run started: {datetime.now().isoformat()}")
    print(f"Part directory: {PART_DIR}")
    print()

    results = []
    results.append(gate_lint())
    results.append(gate_security())
    results.append(gate_tests())

    # Summary
    print("\n" + "=" * 60)
    print("HARNESS SUMMARY")
    print("=" * 60)

    all_passed = all(r["passed"] for r in results)
    for r in results:
        print(f"  {r['gate']:12s}  {r['status']}")

    overall = "PASS" if all_passed else "FAIL"
    print(f"\n  OVERALL: {overall}")
    print(f"\nHarness run completed: {datetime.now().isoformat()}")

    # Save results
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "timestamp": datetime.now().isoformat(),
        "overall": overall,
        "gates": [
            {"gate": r["gate"], "tool": r["tool"], "status": r["status"]}
            for r in results
        ],
    }
    results_file = EVIDENCE_DIR / "harness-results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults saved to: {results_file}")
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
