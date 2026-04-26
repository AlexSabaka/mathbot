"""Ollama eval loop for mathbot.

Sequential pipeline:
  for i in range(count):
    1. generate_problem(seed=seed+i, **filters)
    2. POST to Ollama → response
    3. extract_answer(response) → candidate span + strategy
    4. compare(extracted, expected, response) → correct?
    5. append JSONL record
"""

import datetime as _dt
import json
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

import click

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SCRIPTS_DIR))

from src.generator import generate_problem  # noqa: E402

from _eval import classify_shape, compare, extract_answer  # noqa: E402
from _ollama import ollama_generate  # noqa: E402


DEFAULT_SYSTEM_PROMPT = (
    "Solve the math problem step by step. "
    "Put your final answer inside \\boxed{}."
)


@click.command()
@click.option("--model", required=True, help="Ollama model name (e.g. 'qwen2.5:1.5b').")
@click.option("--count", default=20, show_default=True, help="Number of problems to run.")
@click.option("--seed", default=1, show_default=True, help="Starting seed.")
@click.option("--grade", default=None, help="Filter: grade (k1..k12, or elementary/middle/high).")
@click.option("--topic", "math_topic", default=None, help="Filter: topic prefix (e.g. arithmetic).")
@click.option("--family", "problem_family", default=None, help="Filter: problem family.")
@click.option("--difficulty", "complexity", type=int, default=None, help="Filter: complexity (1=easy, 2=medium, 3=hard).")
@click.option("--system-prompt-file", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None)
@click.option("--system-prompt", default=DEFAULT_SYSTEM_PROMPT, show_default=False)
@click.option("--timeout", default=120.0, show_default=True, help="Per-call timeout (seconds).")
@click.option("--host", default="http://localhost:11434", show_default=True)
@click.option(
    "--output", "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="JSONL output path. Default: runs/run_<model>_<timestamp>.jsonl",
)
def main(
    model: str,
    count: int,
    seed: int,
    grade: str | None,
    math_topic: str | None,
    problem_family: str | None,
    complexity: int | None,
    system_prompt_file: Path | None,
    system_prompt: str,
    timeout: float,
    host: str,
    output: Path | None,
) -> None:
    if system_prompt_file:
        system_prompt = system_prompt_file.read_text(encoding="utf-8").strip()

    if output is None:
        ts = _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        safe_model = model.replace("/", "_").replace(":", "_")
        output = REPO_ROOT / "runs" / f"run_{safe_model}_{ts}.jsonl"
        output.parent.mkdir(parents=True, exist_ok=True)

    filters = {
        "grade": grade,
        "math_topic": math_topic,
        "problem_family": problem_family,
        "complexity": complexity,
    }
    filters_active = {k: v for k, v in filters.items() if v is not None}

    print(
        f"running {count} problems × {model} → {output}\n"
        f"  filters: {filters_active or 'none (full random)'}\n"
        f"  system: {system_prompt[:100]}{'…' if len(system_prompt) > 100 else ''}",
        file=sys.stderr,
    )

    correct_count = 0
    error_count = 0
    latencies: list[int] = []
    strategy_counter: Counter[str] = Counter()
    shape_correct: dict[str, list[bool]] = {}

    with open(output, "w", encoding="utf-8") as f:
        for i in range(count):
            iter_seed = seed + i
            try:
                problem = generate_problem(seed=iter_seed, **filters)
            except Exception as e:
                error_count += 1
                f.write(json.dumps({"iter": i, "seed": iter_seed, "error": f"generate: {e}"}) + "\n")
                f.flush()
                print(f"  [{i+1}/{count}] generate failed: {e}", file=sys.stderr)
                continue

            expected = problem["task_params"]["expected_answer"]
            shape = classify_shape(expected)

            try:
                response, latency_ms = ollama_generate(
                    model=model,
                    prompt=problem["problem"],
                    system=system_prompt,
                    host=host,
                    timeout=timeout,
                )
            except Exception as e:
                error_count += 1
                f.write(json.dumps({"iter": i, "seed": iter_seed, "test_id": problem["test_id"], "error": f"ollama: {e}"}) + "\n")
                f.flush()
                print(f"  [{i+1}/{count}] ollama failed: {e}", file=sys.stderr)
                continue

            extracted, extract_strategy = extract_answer(response)
            correct, reason = compare(extracted, expected, response)

            if correct:
                correct_count += 1
            latencies.append(latency_ms)
            strategy_counter[extract_strategy] += 1
            shape_correct.setdefault(shape, []).append(correct)

            record = {
                "iter": i,
                "seed": iter_seed,
                "model": model,
                "test_id": problem["test_id"],
                "problem": problem["problem"],
                "expected": expected,
                "answer_shape": shape,
                "response": response,
                "latency_ms": latency_ms,
                "extracted": extracted,
                "extract_strategy": extract_strategy,
                "correct": correct,
                "reason": reason,
                "filters": filters_active,
                "ts": _dt.datetime.now(tz=_dt.timezone.utc).isoformat(),
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()

            mark = "✓" if correct else "✗"
            print(
                f"  [{i+1}/{count}] {mark} {problem['test_id']:<55} "
                f"{latency_ms:>6}ms  shape={shape}  strategy={extract_strategy}",
                file=sys.stderr,
            )

    n_done = correct_count + (len(latencies) - correct_count)
    print(file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    if n_done:
        accuracy = correct_count / n_done
        print(f"accuracy: {correct_count}/{n_done} = {accuracy:.1%}", file=sys.stderr)
    if latencies:
        print(
            f"latency: mean={statistics.mean(latencies):.0f}ms  "
            f"p95={_p(latencies, 0.95):.0f}ms  max={max(latencies)}ms",
            file=sys.stderr,
        )
    if errors := error_count:
        print(f"errors: {errors}", file=sys.stderr)
    if strategy_counter:
        print("by extract_strategy: " + ", ".join(f"{k}={v}" for k, v in strategy_counter.most_common()), file=sys.stderr)
    if shape_correct:
        print("by answer_shape:", file=sys.stderr)
        for shape, results in sorted(shape_correct.items()):
            n = len(results)
            c = sum(results)
            print(f"  {shape:<22} {c}/{n} = {c/n:.0%}", file=sys.stderr)
    print(f"log: {output}", file=sys.stderr)


def _p(values: list[int], pct: float) -> float:
    s = sorted(values)
    if not s:
        return 0.0
    k = (len(s) - 1) * pct
    f = int(k)
    c = min(f + 1, len(s) - 1)
    if f == c:
        return float(s[f])
    return s[f] + (s[c] - s[f]) * (k - f)


if __name__ == "__main__":
    main()
