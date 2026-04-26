"""Emit a long-format CSV of (grade, topic, family, difficulty) → template counts.

Sparse: empty cells are NOT emitted. Pivot externally to see gaps.
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

import click

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.yaml_loader import load_all_templates  # noqa: E402


@click.command()
@click.option(
    "--templates-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=REPO_ROOT / "src" / "templates",
    show_default=True,
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    default=Path("coverage.csv"),
    show_default=True,
)
def main(templates_dir: Path, output: Path) -> None:
    templates = load_all_templates(templates_dir)

    cells: dict[tuple, list[Path]] = defaultdict(list)
    for tpl in templates.values():
        key = (f"k{tpl.grade}", tpl.topic, tpl.family, tpl.difficulty)
        cells[key].append(tpl.file_path)

    rows = []
    anchors_total = 0
    variants_total = 0
    for (grade, topic, family, difficulty), paths in sorted(cells.items()):
        anchor_count = sum(1 for p in paths if p and p.name.endswith("_anchor.yaml"))
        variant_count = len(paths) - anchor_count
        anchors_total += anchor_count
        variants_total += variant_count
        rows.append(
            {
                "grade": grade,
                "topic": topic,
                "family": family,
                "difficulty": difficulty,
                "count": len(paths),
                "anchor_count": anchor_count,
                "variant_count": variant_count,
            }
        )

    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["grade", "topic", "family", "difficulty", "count", "anchor_count", "variant_count"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(
        f"wrote {len(rows)} rows to {output}; "
        f"{anchors_total} anchors / {variants_total} variants across {len(templates)} templates",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
