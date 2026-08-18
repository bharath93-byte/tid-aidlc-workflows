"""Compare two Allure result directories and produce a categorized failure report.

Usage:
    python compare_allure_results.py --baseline <dir> --target <dir> [--output <file>]

Reads *-result.json files from each directory, extracts test status,
and classifies tests into: new_failures, fixed, persistent_failures, stable_passing.
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from paths import default_analysis_dir


def is_failed(status: str) -> bool:
    return status in ("failed", "broken")


def load_allure_results(results_dir: str) -> dict[str, dict]:
    """Load all test results from an allure-results directory.

    Returns a dict keyed by test fullName with value containing status and metadata.
    """
    results = {}
    results_path = Path(results_dir)

    if not results_path.exists():
        print(f"ERROR: Directory not found: {results_dir}", file=sys.stderr)
        sys.exit(1)

    for file in results_path.rglob("*-result.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        full_name = data.get("fullName") or data.get("name", file.stem)
        test_name = data.get("name", "")
        status = data.get("status", "unknown")
        labels = {l["name"]: l["value"] for l in data.get("labels", [])}

        suite = labels.get("suite", "")
        parent_suite = labels.get("parentSuite", "")
        epic = labels.get("epic", "")
        feature = labels.get("feature", "")
        story = labels.get("story", "")

        status_details = data.get("statusDetails", {})
        message = status_details.get("message", "")
        trace = status_details.get("trace", "")

        results[full_name] = {
            "name": test_name,
            "fullName": full_name,
            "status": status,
            "suite": suite,
            "parentSuite": parent_suite,
            "epic": epic,
            "feature": feature,
            "story": story,
            "message": message[:500],
            "trace": trace[:1000],
        }

    return results


def compare_results(baseline: dict, target: dict) -> dict:
    """Compare baseline (main) results against target (branch) results."""
    all_tests = set(baseline.keys()) | set(target.keys())

    new_failures = []
    fixed_tests = []
    persistent_failures = []
    new_tests_failed = []
    new_tests_passed = []

    baseline_stats = defaultdict(int)
    target_stats = defaultdict(int)

    for status in baseline.values():
        baseline_stats[status["status"]] += 1
    for status in target.values():
        target_stats[status["status"]] += 1

    for test_id in all_tests:
        b = baseline.get(test_id)
        t = target.get(test_id)

        if b is None and t is not None:
            if is_failed(t["status"]):
                new_tests_failed.append(t)
                new_failures.append({
                    "test": t,
                    "baseline_status": "absent",
                    "target_status": t["status"],
                    "branch_only": True,
                })
            else:
                new_tests_passed.append(t)
            continue

        if t is None and b is not None:
            continue

        b_failed = is_failed(b["status"])
        t_failed = is_failed(t["status"])

        if not b_failed and t_failed:
            new_failures.append({
                "test": t,
                "baseline_status": b["status"],
                "target_status": t["status"],
                "branch_only": False,
            })
        elif b_failed and t["status"] == "passed":
            fixed_tests.append({
                "test": t,
                "baseline_status": b["status"],
                "target_status": t["status"],
            })
        elif b_failed and t_failed:
            persistent_failures.append({
                "test": t,
                "baseline_status": b["status"],
                "target_status": t["status"],
                "baseline_message": b.get("message", ""),
                "target_message": t.get("message", ""),
            })

    return {
        "summary": {
            "baseline": {
                "total": len(baseline),
                "passed": baseline_stats.get("passed", 0),
                "failed": baseline_stats.get("failed", 0),
                "broken": baseline_stats.get("broken", 0),
                "skipped": baseline_stats.get("skipped", 0),
            },
            "target": {
                "total": len(target),
                "passed": target_stats.get("passed", 0),
                "failed": target_stats.get("failed", 0),
                "broken": target_stats.get("broken", 0),
                "skipped": target_stats.get("skipped", 0),
            },
        },
        "new_failures": sorted(new_failures, key=lambda x: x["test"]["fullName"]),
        "fixed_tests": sorted(fixed_tests, key=lambda x: x["test"]["fullName"]),
        "persistent_failures": sorted(persistent_failures, key=lambda x: x["test"]["fullName"]),
        "new_tests_failed": sorted(new_tests_failed, key=lambda x: x["fullName"]),
        "new_tests_passed": sorted(new_tests_passed, key=lambda x: x["fullName"]),
        "counts": {
            "new_failures": len(new_failures),
            "fixed": len(fixed_tests),
            "persistent_failures": len(persistent_failures),
            "new_tests_failed": len(new_tests_failed),
            "new_tests_passed": len(new_tests_passed),
            "pr_introduced_failures": len(new_failures),
        },
    }


def print_summary(report: dict) -> None:
    """Print a human-readable summary to stdout."""
    s = report["summary"]
    c = report["counts"]

    print("=" * 70)
    print("TEST COMPARISON REPORT")
    print("=" * 70)
    print(f"\n{'Metric':<25} {'Main (baseline)':<20} {'Branch (target)':<20}")
    print("-" * 65)
    print(f"{'Total tests':<25} {s['baseline']['total']:<20} {s['target']['total']:<20}")
    print(f"{'Passed':<25} {s['baseline']['passed']:<20} {s['target']['passed']:<20}")
    print(f"{'Failed':<25} {s['baseline']['failed']:<20} {s['target']['failed']:<20}")
    print(f"{'Broken':<25} {s['baseline']['broken']:<20} {s['target']['broken']:<20}")
    print(f"{'Skipped':<25} {s['baseline']['skipped']:<20} {s['target']['skipped']:<20}")

    print(f"\n{'Category':<30} {'Count':<10}")
    print("-" * 40)
    print(f"{'PR-introduced failures':<30} {c['pr_introduced_failures']:<10}")
    print(f"{'  (regression failures)':<30} {c['new_failures'] - c['new_tests_failed']:<10}")
    print(f"{'  (new tests failed)':<30} {c['new_tests_failed']:<10}")
    print(f"{'Fixed tests (failed->passed)':<30} {c['fixed']:<10}")
    print(f"{'Persistent failures':<30} {c['persistent_failures']:<10}")
    print(f"{'New tests (passed)':<30} {c['new_tests_passed']:<10}")

    if report["new_failures"]:
        print(f"\n{'=' * 70}")
        print("NEW FAILURES (introduced by the PR)")
        print("=" * 70)
        for i, item in enumerate(report["new_failures"], 1):
            t = item["test"]
            label = "new test" if item.get("branch_only") else "regression"
            print(f"\n  {i}. {t['name']} [{label}]")
            print(f"     Full: {t['fullName']}")
            print(f"     Suite: {t['parentSuite']} > {t['suite']}")
            print(f"     Status: {item['baseline_status']} -> {item['target_status']}")
            if t["message"]:
                print(f"     Error: {t['message'][:200]}")

    if report["fixed_tests"]:
        print(f"\n{'=' * 70}")
        print("FIXED TESTS (failed on main, passed on branch)")
        print("=" * 70)
        for i, item in enumerate(report["fixed_tests"], 1):
            t = item["test"]
            print(f"  {i}. {t['name']} ({item['baseline_status']} -> {item['target_status']})")

    if report["persistent_failures"]:
        print(f"\n{'=' * 70}")
        print(f"PERSISTENT FAILURES (failed on both - {c['persistent_failures']} total)")
        print("=" * 70)
        for i, item in enumerate(report["persistent_failures"][:20], 1):
            t = item["test"]
            print(f"  {i}. {t['name']}")
            if t.get("message"):
                print(f"     Error: {t['message'][:150]}")
        if c["persistent_failures"] > 20:
            print(f"  ... and {c['persistent_failures'] - 20} more")

    print(f"\n{'=' * 70}")


def main():
    parser = argparse.ArgumentParser(description="Compare Allure test results between two runs")
    parser.add_argument("--baseline", required=True, help="Path to baseline (main) allure-results directory")
    parser.add_argument("--target", required=True, help="Path to target (branch) allure-results directory")
    parser.add_argument("--output", default=None, help="Path to write JSON comparison report")
    args = parser.parse_args()

    print(f"Loading baseline results from: {args.baseline}")
    baseline = load_allure_results(args.baseline)
    print(f"  Found {len(baseline)} test results")

    print(f"Loading target results from: {args.target}")
    target = load_allure_results(args.target)
    print(f"  Found {len(target)} test results")

    if not baseline:
        print("ERROR: No test results found in baseline directory", file=sys.stderr)
        sys.exit(1)
    if not target:
        print("ERROR: No test results found in target directory", file=sys.stderr)
        sys.exit(1)

    report = compare_results(baseline, target)
    print_summary(report)

    output_path = args.output or str(default_analysis_dir() / "comparison-report.json")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nFull report written to: {output_path}")


if __name__ == "__main__":
    main()
