#!/usr/bin/env python3
"""Dump one rendered sample per template into the audit format.

Equivalent to the loop in `sample_all.sh` (`mathbot generate --input ...`)
but pays the template-loader/Faker startup cost once instead of per
template — ~30s vs many minutes for the full corpus.

For multi-tier templates, dumps one block per tier so the audit sees the
full spread of problem shapes the corpus can produce.

Usage:
    uv run python scripts/dump_all_samples.py > all_samples.txt
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.template_generator import TemplateGenerator  # noqa: E402

BLOCK_SEP = "=" * 80
HEADER_SEP = "-" * 80


def dump(problem: dict) -> None:
    p = problem
    tp = p["task_params"]
    print(BLOCK_SEP)
    print(f"Problem: {p['test_id']}")
    print(f"Template: {p['template_path']}")
    print(f"Family: {tp['problem_family']}")
    print(f"Complexity: {tp['complexity']}")
    print(f"Grade: {tp['grade']}")
    print(f"Topic: {tp['math_topic'][0]}")
    print(HEADER_SEP)
    print(p["problem"])
    print(HEADER_SEP)
    print(f"Answer: {tp['expected_answer']}")
    print(f"Steps: {tp['num_steps']}")
    print(f"Operations: {', '.join(tp['operations'])}")


def main() -> int:
    gen = TemplateGenerator(seed=12345)

    for tid, template in sorted(gen.templates.items()):
        path = gen.template_paths[tid]
        tiers = template.difficulty_tiers or [template.difficulty]
        complexity_map = {"easy": 1, "medium": 2, "hard": 3}
        for tier in tiers:
            try:
                problem = gen._generate_from_template(
                    template,
                    seed=12345,
                    template_path=path,
                    requested_complexity=complexity_map[tier],
                )
                dump(problem)
            except Exception as e:  # noqa: BLE001
                print(
                    f"# error rendering {tid} at tier={tier}: {type(e).__name__}: {e}",
                    file=sys.stderr,
                )

    print(BLOCK_SEP)
    return 0


if __name__ == "__main__":
    sys.exit(main())
