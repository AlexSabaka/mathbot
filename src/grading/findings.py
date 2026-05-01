"""`GradeFinding` is the unit of grader output.

Mirrors `src.audit.findings.Finding` so downstream tooling can consume
both audit and grading streams the same way. One finding per (template,
rubric_item, seed) — when a rubric item fails on multiple seeds, each
seed gets its own finding so authors can see exactly which render
surfaced the issue.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional


Severity = Literal["error", "warning", "info"]


@dataclass
class GradeFinding:
    """One verdict from one rubric item against one render."""
    rule: str
    severity: Severity
    template_id: str
    file: str
    message: str
    seed: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_json_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "rule": self.rule,
            "severity": self.severity,
            "template_id": self.template_id,
            "file": self.file,
            "message": self.message,
        }
        if self.seed is not None:
            out["seed"] = self.seed
        if self.extra:
            out["extra"] = self.extra
        return out


def count_by_severity(findings: List[GradeFinding]) -> Dict[Severity, int]:
    counts: Dict[Severity, int] = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        counts[f.severity] += 1
    return counts
