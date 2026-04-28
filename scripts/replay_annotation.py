"""Replay the gol_eval annotation results through the new parser/evaluator.

Reads one or more `results_*.json.gz` files, re-parses every `output.raw_response`
with the current `MathbotParser`+`MathbotEvaluator`, and reports old vs new
correctness counts plus regressions.

Usage:
  uv run python scripts/replay_annotation.py /path/to/results_*.json.gz [...]

This is a one-off verification tool, not part of the production codebase.
"""

import gzip
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GOL_EVAL_ROOT = Path("/Volumes/2TB/repos/gol_eval")
sys.path.insert(0, str(REPO_ROOT / "gol_plugin"))
sys.path.insert(0, str(GOL_EVAL_ROOT))

from evaluator import MathbotEvaluator  # noqa: E402
from parser import MathbotParser  # noqa: E402


def replay(paths: list[Path]) -> dict:
    parser = MathbotParser()
    evaluator = MathbotEvaluator()

    total = 0
    old_correct = 0
    new_correct = 0
    regressions: list[dict] = []
    new_wins: list[dict] = []
    still_wrong: list[dict] = []
    old_strategies: Counter[str] = Counter()
    new_strategies: Counter[str] = Counter()

    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            data = json.load(fh)
        for case in data.get("results", []):
            total += 1
            inp = case.get("input") or {}
            out = case.get("output") or {}
            ev_old = case.get("evaluation") or {}
            task_params = inp.get("task_params") or {}
            expected = task_params.get("expected_answer")
            if expected is None:
                continue
            if "raw_response" not in out:
                continue

            parsed = parser.parse(out["raw_response"], task_params)
            ev_new = evaluator.evaluate(parsed, expected, task_params)

            old_strategies[out["parse_strategy"]] += 1
            new_strategies[parsed.parse_strategy] += 1
            if ev_old["correct"]:
                old_correct += 1
            if ev_new.correct:
                new_correct += 1

            payload = {
                "model": data.get("model_info", {}).get("model_name", path.stem),
                "test_id": case["test_id"],
                "expected": expected,
                "old_parsed": out["parsed_answer"],
                "old_strategy": out["parse_strategy"],
                "new_parsed": parsed.value,
                "new_strategy": parsed.parse_strategy,
            }
            if ev_old["correct"] and not ev_new.correct:
                regressions.append(payload)
            elif not ev_old["correct"] and ev_new.correct:
                new_wins.append(payload)
            elif not ev_old["correct"] and not ev_new.correct:
                still_wrong.append(payload)

    return {
        "total": total,
        "old_correct": old_correct,
        "new_correct": new_correct,
        "old_strategies": dict(old_strategies.most_common()),
        "new_strategies": dict(new_strategies.most_common()),
        "regressions": regressions,
        "new_wins": new_wins,
        "still_wrong": still_wrong,
    }


def main() -> None:
    paths = [Path(p) for p in sys.argv[1:]]
    if not paths:
        print("Usage: replay_annotation.py <results_*.json.gz> ...", file=sys.stderr)
        sys.exit(1)

    report = replay(paths)
    total = report["total"]
    print(f"\n=== Replay across {len(paths)} files ({total} cases) ===")
    print(f"  old correct: {report['old_correct']}/{total} = {report['old_correct']/total:.1%}")
    print(f"  new correct: {report['new_correct']}/{total} = {report['new_correct']/total:.1%}")
    print(f"  regressions (was correct, now wrong): {len(report['regressions'])}")
    print(f"  new wins      (was wrong, now correct): {len(report['new_wins'])}")
    print(f"  still wrong   (wrong before and after): {len(report['still_wrong'])}")

    print("\nold strategy distribution:")
    for k, v in report["old_strategies"].items():
        print(f"  {str(k):>22s}: {v}")
    print("new strategy distribution:")
    for k, v in report["new_strategies"].items():
        print(f"  {str(k):>22s}: {v}")

    if report["regressions"]:
        print("\n=== REGRESSIONS ===")
        for r in report["regressions"][:25]:
            print(f"  [{r['model']}] {r['test_id']}  expected={r['expected']!r}")
            print(f"    old: {r['old_parsed']!r}  via {r['old_strategy']}")
            print(f"    new: {r['new_parsed']!r}  via {r['new_strategy']}")

    if report["still_wrong"]:
        print(f"\n=== STILL WRONG (sample of 15 of {len(report['still_wrong'])}) ===")
        for r in report["still_wrong"][:15]:
            print(f"  [{r['model']}] {r['test_id']}  expected={r['expected']!r}")
            print(f"    new: {r['new_parsed']!r}  via {r['new_strategy']}")


if __name__ == "__main__":
    main()
