#!/usr/bin/env python3
"""Surgically refresh `tests[].expected.answer` values in YAML templates.

The schema refactor changed the seed→variable RNG mapping. Templates still
generate correct math problems, but the embedded test cases hold stale
expected values. This script regenerates each test's expected answer using
the live generator and rewrites only that field, preserving comments,
key order, quoting, and whitespace via ruamel.yaml round-trip mode.

Usage:
    uv run python scripts/refresh_test_answers.py --dry-run
    uv run python scripts/refresh_test_answers.py --filter 'arithmetic/k3*'
    uv run python scripts/refresh_test_answers.py --apply
"""

import argparse
import sys
from pathlib import Path

from ruamel.yaml import YAML

# Import after argparse so --help is fast even if src/ has issues
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.yaml_loader import YAMLLoader  # noqa: E402
from src.template_generator import TemplateGenerator  # noqa: E402


def regenerate_template(template_path: Path, generator: TemplateGenerator,
                        loader: YAMLLoader) -> tuple[int, int, int, list[str]]:
    """Regenerate test answers for one template.

    Returns (updated, unchanged, errored, messages).
    """
    template = loader.load_template(template_path)
    if not template or not template.tests:
        return 0, 0, 0, []

    yaml_rt = YAML(typ='rt')
    yaml_rt.preserve_quotes = True
    yaml_rt.indent(mapping=2, sequence=4, offset=2)
    yaml_rt.width = 4096
    with template_path.open('r', encoding='utf-8') as f:
        data = yaml_rt.load(f)

    if 'tests' not in data:
        return 0, 0, 0, []

    updated = unchanged = errored = 0
    messages: list[str] = []

    for i, (yaml_tc, tc) in enumerate(zip(data['tests'], template.tests)):
        seed = tc.seed
        try:
            problem = generator._generate_from_template(template, seed=seed,
                                                         template_path=template_path)
            actual = str(problem['task_params']['expected_answer'])
        except Exception as e:
            errored += 1
            messages.append(f"  err  test[{i}] seed={seed}: {type(e).__name__}: {e}")
            continue

        old_answer = ''
        expected = yaml_tc.get('expected', {})
        if isinstance(expected, dict):
            old_answer = str(expected.get('answer', ''))

        if str(old_answer).strip() == actual.strip():
            unchanged += 1
            continue

        # Rewrite expected.answer
        if 'expected' not in yaml_tc or not isinstance(yaml_tc['expected'], dict):
            errored += 1
            messages.append(f"  err  test[{i}] seed={seed}: missing expected dict")
            continue
        # Remove legacy multi-answer keys (answer1, answer2, ...) so we don't
        # leave duplicate state alongside the unified `answer` field.
        for k in list(yaml_tc['expected'].keys()):
            if isinstance(k, str) and k.startswith('answer') and k != 'answer' and k[6:].isdigit():
                del yaml_tc['expected'][k]
        yaml_tc['expected']['answer'] = actual
        updated += 1
        messages.append(f"  upd  test[{i}] seed={seed}: {old_answer!r} → {actual!r}")

    if updated > 0:
        # Write back
        with template_path.open('w', encoding='utf-8') as f:
            yaml_rt.dump(data, f)

    return updated, unchanged, errored, messages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--templates-dir', type=Path, default=Path('src/templates'),
                        help='Directory containing YAML templates (default: src/templates)')
    parser.add_argument('--filter', type=str, default='**/*.yaml',
                        help='Glob filter relative to templates-dir (default: **/*.yaml)')
    parser.add_argument('--apply', action='store_true',
                        help='Apply edits (default: dry-run)')
    parser.add_argument('--dry-run', action='store_true',
                        help='(Default) Preview without writing')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print per-test messages')
    args = parser.parse_args()

    if not args.apply:
        print("DRY RUN — pass --apply to actually rewrite files.\n")

    templates_dir: Path = args.templates_dir.resolve()
    files = sorted(templates_dir.glob(args.filter))
    if not files:
        print(f"No templates matched filter '{args.filter}' under {templates_dir}")
        return 1

    loader = YAMLLoader()
    generator = TemplateGenerator(templates_dir=templates_dir)

    total_files_changed = 0
    total_updated = 0
    total_unchanged = 0
    total_errored = 0

    for path in files:
        # Run regeneration; if not applying, capture results but discard writes
        if args.apply:
            upd, unc, err, msgs = regenerate_template(path, generator, loader)
        else:
            # Patch-style dry-run: load template, but don't write
            template = loader.load_template(path)
            if not template or not template.tests:
                continue
            upd = unc = err = 0
            msgs: list[str] = []
            for i, tc in enumerate(template.tests):
                try:
                    problem = generator._generate_from_template(template, seed=tc.seed,
                                                                 template_path=path)
                    actual = str(problem['task_params']['expected_answer'])
                except Exception as e:
                    err += 1
                    msgs.append(f"  err  test[{i}] seed={tc.seed}: {type(e).__name__}: {e}")
                    continue
                expected = tc.expected.get('answer') if isinstance(tc.expected, dict) else tc.expected
                if str(expected).strip() == actual.strip():
                    unc += 1
                else:
                    upd += 1
                    msgs.append(f"  upd  test[{i}] seed={tc.seed}: {expected!r} → {actual!r}")

        if upd > 0 or err > 0:
            rel = path.relative_to(templates_dir)
            print(f"{rel}  upd={upd} unc={unc} err={err}")
            if args.verbose or err > 0:
                for m in msgs:
                    print(m)

        if upd > 0:
            total_files_changed += 1
        total_updated += upd
        total_unchanged += unc
        total_errored += err

    print(f"\nSummary: {total_files_changed} files changed, "
          f"{total_updated} test answers updated, "
          f"{total_unchanged} unchanged, {total_errored} errored.")
    if not args.apply and total_updated > 0:
        print("Run with --apply to write changes.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
