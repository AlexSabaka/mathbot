"""Serializers for `mathbot lint` / `mathbot health` output.

JSON is the canonical machine format (the only structured one shipped
in 5.7). Human output is a brief stderr summary line — no
text/CSV/Markdown alternatives.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from typing import Any, Dict, List

from .findings import Finding, Severity, count_by_severity


def lint_report(findings: List[Finding]) -> Dict[str, Any]:
    """Wrap findings + a small summary into one dict for JSON dumping."""
    counts = count_by_severity(findings)
    rules = Counter(f.rule for f in findings)
    return {
        "summary": {
            "errors": counts["error"],
            "warnings": counts["warning"],
            "info": counts["info"],
            "total": sum(counts.values()),
            "by_rule": dict(rules.most_common()),
        },
        "findings": [f.to_json_dict() for f in findings],
    }


def write_lint_summary(
    findings: List[Finding],
    templates_checked: int,
    out=sys.stderr,
) -> None:
    """One-line summary to stderr, plus the top rule breakdown.

        lint: 640 templates checked, 0 errors, 3 warnings, 12 info.
          warnings: 2× off_anchor_divergence, 1× body_too_long
          info: 11× gsm8k_items_at_price_each, 1× area_no_squared_unit
        Re-run with --json for full per-finding detail.
    """
    counts = count_by_severity(findings)
    print(
        f"lint: {templates_checked} templates checked, "
        f"{counts['error']} errors, {counts['warning']} warnings, "
        f"{counts['info']} info.",
        file=out,
    )
    for severity in ("error", "warning", "info"):
        sev_findings = [f for f in findings if f.severity == severity]
        if not sev_findings:
            continue
        rules = Counter(f.rule for f in sev_findings)
        breakdown = ", ".join(f"{n}× {rule}" for rule, n in rules.most_common(5))
        print(f"  {severity}s: {breakdown}", file=out)
    if findings:
        print("Re-run with --json for full per-finding detail.", file=out)


def emit_json(payload: Dict[str, Any], out=sys.stdout) -> None:
    """Pretty-print JSON for human inspection; jq still parses it fine."""
    json.dump(payload, out, indent=2, ensure_ascii=False)
    out.write("\n")
