"""`Finding` is the unit of audit output.

Both `mathbot lint` (per-template) and `mathbot health` (corpus) emit
lists of `Finding` objects, serialized to JSON via
[report.py](report.py). One per (template, rule, seed) triple — when
a rule fires across multiple seeds, each render gets its own finding
so authors can see exactly which seed surfaced the issue.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional


Severity = Literal["error", "warning", "info"]


@dataclass
class Finding:
    """One finding from a lint or health rule.

    `template_id` and `file` are populated for per-template findings;
    cross-template findings (e.g. an internal-contamination pair) carry
    the primary template here and stash the counterpart in `extra`.
    """
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


def count_by_severity(findings: List[Finding]) -> Dict[Severity, int]:
    """Tally findings by severity. Used for the stderr summary line."""
    counts: Dict[Severity, int] = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        counts[f.severity] += 1
    return counts
