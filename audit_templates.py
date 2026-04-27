"""
mathbot template-corpus audit.

Reads a rendered-samples file (one block per template, separated by '=' lines)
and emits:
  - audit.csv         per-template flag report
  - audit_dupes.csv   near-duplicate pairs within the same (grade,topic,family) cell
  - audit_summary.txt aggregate stats and per-cell density

Usage:
  python audit_templates.py <samples.txt> <output_dir>

Honest scope: this audits *rendered* output, not YAML source. Variable-constraint
sanity, formatter logic, and test-case coverage are out of scope and need a
separate YAML-aware pass.
"""

from __future__ import annotations
import csv, difflib, re, sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# -- Spec-mandated families from MATHBOT_PROBLEMS_PROPOSAL.md, section 1.3.
# Templates matching these are *protected* from cull suggestions because the
# upper-grade build-out plan depends on them as foundation.
SPEC_MANDATED_FAMILIES = {
    "area_perimeter_chain", "compound_growth", "multi_person_sharing",
    "sequential_purchase", "rate_time",
}

# -- Known slug-normalization issues. Map current slug -> canonical.
# Picked the snake_case forms because they're the convention everywhere else.
SLUG_CANONICAL = {
    "shapes2d": "shapes_2d",
    "shapes3d": "shapes_3d",
}

# -- Unit format inconsistencies. The audit flags these but doesn't try to
# impose a choice -- decision is alex's. Currently both spellings appear.
UNIT_INCONSISTENT_PATTERNS = [
    (r"\bcubic\s+(cm|m|mm|km|in|ft|meters?|millimeters?|kilometers?)\b",
     "spelled_cubic"),
    (r"\bsquare(d)?\s+(cm|m|mm|km|in|ft|meters?|millimeters?|kilometers?)\b",
     "spelled_squared"),
]

# -- GSM8K-saturation patterns called out in the proposal (section 1.2).
# Adding more of these re-creates GSM8K's saturation pattern; flagging them
# helps alex see how much of the corpus is in this shape.
GSM8K_SATURATION_PATTERNS = [
    (r"\$\s*\d+\s*(bill|note)?\b.*\bchange\b|\bpaid (with|using).*\$",
     "money_change"),
    (r"\bplus\s+\w*\s*tax\b|\bsales\s+tax\b|\b\d+%\s+tax\b",
     "with_tax"),
    (r"\bif\s+\d+\s+(\w+\s+){0,3}cost\b|\bat\s+\$\d+\s+each\b",
     "items_at_price_each"),
]

# Threshold for SequenceMatcher to call two problems near-duplicates.
# Tuned by eyeballing -- 0.85 catches "Alice 5 apples / Bob 7 apples" twins
# without flooding on incidental phrasing overlap.
DUPE_THRESHOLD = 0.85

# Surface-length sanity bounds (chars in the prompt body, excluding metadata).
# Surface-length sanity bounds. Long-body catches accidental double-renders
# or concatenated test instructions; we deliberately don't enforce a min.
LONG_PROMPT_CHARS  = 800

BLOCK_SEP = "=" * 80
HEADER_SEP = "-" * 80


@dataclass
class Problem:
    pid: str
    template_path: str
    family: str
    complexity: int | None
    grade: str
    topic: str
    body: str
    answer: str
    steps: int | None
    operations: list[str]
    raw: str
    is_anchor: bool = False
    flags: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def cell(self) -> tuple[str, str, str]:
        return (self.grade, self.topic, self.family)


def parse(text: str) -> list[Problem]:
    """Pull blocks out of the dump. Each block looks like:
        ====...====
        Problem: <id>
        Template: <path>
        Family: ...
        Complexity: ...
        Grade: ...
        Topic: ...
        ----...----
        <prompt body, possibly multi-line>
        ----...----
        Answer: ...
        Steps: ...
        Operations: ...
        ====...====
    """
    problems: list[Problem] = []
    raw_blocks = [b.strip() for b in text.split(BLOCK_SEP) if "Problem:" in b]
    for raw in raw_blocks:
        # Split the inner bars to isolate the body from header/footer metadata.
        parts = [p.strip() for p in raw.split(HEADER_SEP)]
        # Expected: [header, body, footer] (sometimes >3 if the body itself has dashes).
        if len(parts) < 3:
            continue
        header = parts[0]
        # Body is everything between the first and last separator.
        body = HEADER_SEP.join(parts[1:-1]).strip() if len(parts) > 3 else parts[1]
        footer = parts[-1]

        def grab(pat, src=header, default=""):
            m = re.search(pat, src, re.M)
            return m.group(1).strip() if m else default

        pid = grab(r"^Problem:\s*(.+)$")
        tpl = grab(r"^Template:\s*(.+)$")
        fam = grab(r"^Family:\s*(.+)$")
        cx  = grab(r"^Complexity:\s*(\d+)\s*$")
        gr  = grab(r"^Grade:\s*(\S+)\s*$")
        tp  = grab(r"^Topic:\s*(\S+)\s*$")
        ans = grab(r"^Answer:\s*(.*)$", footer)
        st  = grab(r"^Steps:\s*(\d+)\s*$", footer)
        ops = grab(r"^Operations:\s*(.*)$", footer)
        op_list = [o.strip() for o in ops.split(",") if o.strip()] if ops else []

        problems.append(Problem(
            pid=pid, template_path=tpl, family=fam,
            complexity=int(cx) if cx.isdigit() else None,
            grade=gr, topic=tp, body=body, answer=ans,
            steps=int(st) if st.isdigit() else None,
            operations=op_list, raw=raw,
            is_anchor="_anchor" in tpl,
        ))
    return problems


# -------------------- checks --------------------
# Each check appends to p.flags / p.notes. Order doesn't matter; flags are sets.

def check_unrendered_jinja(p: Problem) -> None:
    if re.search(r"\{\{[^}]+\}\}", p.body) or re.search(r"\{\{[^}]+\}\}", p.answer):
        p.flags.append("unrendered_jinja")
        p.notes.append("contains literal {{...}} -- template var didn't substitute")

def check_slug_canon(p: Problem) -> None:
    if p.family in SLUG_CANONICAL:
        p.flags.append("slug_noncanonical")
        p.notes.append(f"family '{p.family}' should be '{SLUG_CANONICAL[p.family]}'")

def check_units(p: Problem) -> None:
    blob = f"{p.body} {p.answer}"
    for pat, label in UNIT_INCONSISTENT_PATTERNS:
        if re.search(pat, blob, re.I):
            p.flags.append(f"unit_{label}")

def check_short_long_body(p: Problem) -> None:
    # The short-body check was tuned several times and kept producing false
    # positives (e.g. "2 + 1 = ?" is fine at k1, "Evaluate: 3^2" is fine at k6).
    # Empty-answer is a more reliable signal of parse/render failure.
    n = len(p.body)
    if n > LONG_PROMPT_CHARS:
        p.flags.append("body_too_long")
        p.notes.append(f"prompt is {n} chars; review for clarity")

def check_empty_answer(p: Problem) -> None:
    if not p.answer.strip():
        p.flags.append("empty_answer")

def check_steps_ops_consistency(p: Problem) -> None:
    # Soft sanity check. Steps should generally not exceed declared operations
    # by a wild margin, and shouldn't be 0 if any operations are declared.
    if p.steps is not None and p.operations and p.steps == 0:
        p.flags.append("zero_steps_with_ops")
    if p.steps is not None and p.steps > 12:
        p.flags.append("very_high_step_count")
        p.notes.append(f"steps={p.steps} is unusually high")

def check_gsm8k_saturation(p: Problem) -> None:
    """Flag patterns the proposal explicitly calls out as GSM8K-saturated.
    Not all of these are bad -- it's about distribution, not individual quality.
    But concentration of these patterns within a (grade,topic) cell is a smell.
    """
    blob = p.body.lower()
    for pat, label in GSM8K_SATURATION_PATTERNS:
        if re.search(pat, blob):
            p.flags.append(f"gsm8k_{label}")

def check_answer_units_match_topic(p: Problem) -> None:
    # Heuristic: geometry.area should typically have area units; volume problems
    # should have cubic units; rate problems should have rate-style units.
    fam = p.family
    ans = p.answer
    if "area" in fam and not re.search(r"(cm|m|mm|km|in|ft)\^?2|square|cm²|m²|mm²|km²", ans, re.I) \
            and not re.search(r"\d", ans):
        return  # no number, skip
    if fam.endswith("_area") or fam == "area":
        if not re.search(r"²|\^2|square|sq\.?", ans, re.I) and re.search(r"\d", ans):
            p.flags.append("area_no_squared_unit")
    if "volume" in fam:
        if not re.search(r"³|\^3|cubic", ans, re.I) and re.search(r"\d\s*(cm|m|mm|in|ft|l|ml)\b", ans, re.I):
            p.flags.append("volume_no_cubed_unit")


# -------------------- normalization for dupe detection --------------------

NUM_RE = re.compile(r"-?\$?\d+(?:\.\d+)?%?")
NAME_RE = re.compile(r"\b[A-Z][a-z]+\b")  # captures most first-name-like tokens
# (this *will* over-trigger on sentence-initial words like "Find", "Write" --
# that's actually fine for similarity purposes, since we apply the same
# transform to both sides of the comparison.)
WS_RE = re.compile(r"\s+")

def normalize_for_dupes(text: str) -> str:
    """Reduce a problem statement to its structural skeleton for similarity
    comparison. Replaces numbers with <N> and capitalized words with <W>,
    then collapses whitespace.
    """
    t = NUM_RE.sub("<N>", text)
    t = NAME_RE.sub("<W>", t)
    t = WS_RE.sub(" ", t).strip().lower()
    return t


def _base_template_id(pid: str) -> str:
    """Strip the multi-tier `__<tier>` suffix from a pid.

    Phase 5.7 templates can declare `metadata.difficulty_tiers` and render
    the same source at multiple tiers. Each render carries a `__<tier>`
    suffix on the test_id so dataset consumers can distinguish rows. For
    audit purposes those rows share one template — so dupe detection and
    `structurally_flat_difficulty` should treat them as a single source,
    not separate templates that happen to look alike.
    """
    for tier in ("__easy", "__medium", "__hard"):
        if pid.endswith(tier):
            return pid[: -len(tier)]
    return pid


def find_near_dupes(problems: list[Problem], threshold: float = DUPE_THRESHOLD
                    ) -> list[tuple[str, str, float, str, str]]:
    """Find near-duplicate pairs WITHIN the same (grade,topic,family) cell.
    Returns list of (pid_a, pid_b, similarity, cell_label, dupe_kind).

    dupe_kind is one of:
      - 'same_difficulty'      : both problems share complexity tier
      - 'cross_difficulty'     : problems span complexity tiers (0.95+ here
                                  means the difficulty axis is fake -- only
                                  number ranges differ, not problem structure)

    Pairs from the same base template (multi-tier renders of one source —
    see `_base_template_id`) are skipped: they are *intended* to look alike
    across tiers, since the same YAML produces all of them.
    """
    by_cell: dict[tuple, list[Problem]] = defaultdict(list)
    for p in problems:
        by_cell[p.cell].append(p)

    pairs = []
    for cell, group in by_cell.items():
        if len(group) < 2:
            continue
        norms = [(p, normalize_for_dupes(p.body)) for p in group]
        for i in range(len(norms)):
            for j in range(i + 1, len(norms)):
                p_a, p_b = norms[i][0], norms[j][0]
                if _base_template_id(p_a.pid) == _base_template_id(p_b.pid):
                    continue
                ratio = difflib.SequenceMatcher(
                    None, norms[i][1], norms[j][1], autojunk=False
                ).ratio()
                if ratio >= threshold:
                    kind = ("cross_difficulty"
                            if p_a.complexity != p_b.complexity
                            else "same_difficulty")
                    pairs.append((
                        p_a.pid, p_b.pid, round(ratio, 3),
                        f"{cell[0]}.{cell[1]}.{cell[2]}",
                        kind,
                    ))
                    # tag the underlying problems so it surfaces in audit.csv
                    if ratio >= 0.95 and kind == "cross_difficulty":
                        for p in (p_a, p_b):
                            if "structurally_flat_difficulty" not in p.flags:
                                p.flags.append("structurally_flat_difficulty")
                                p.notes.append(
                                    f"identical structure to a different-tier "
                                    f"problem in same family (sim={ratio:.2f})"
                                )
    return sorted(pairs, key=lambda x: -x[2])


# -------------------- distribution analytics --------------------

def cell_density_report(problems: list[Problem]) -> str:
    """Print per-cell counts and flag over-densified cells. The proposal calls
    out k6 as 33% of the corpus with k6.algebra at ~57 templates -- those are
    the cells where culling has the most leverage."""
    cells = Counter(p.cell for p in problems)
    grades = ["k1","k2","k3","k4","k5","k6","k7","k8","k9","k10","k11","k12"]
    topics = sorted({p.topic for p in problems if p.topic})
    grade_topic = Counter((p.grade, p.topic) for p in problems)

    out = []
    out.append("=== GRADE x TOPIC DENSITY ===")
    out.append(f"{'topic':<14}" + "".join(f"{g:>5}" for g in grades) + f"{'TOT':>6}")
    for t in topics:
        row = [grade_topic.get((g, t), 0) for g in grades]
        cells_str = "".join(f"{n:>5}" if n else f"{'.':>5}" for n in row)
        out.append(f"{t:<14}{cells_str}{sum(row):>6}")
    out.append("")
    out.append("=== TOP 20 OVER-DENSIFIED (grade,topic,family) CELLS ===")
    for cell, n in cells.most_common(20):
        if n >= 5:
            g, t, f = cell
            protected = " [SPEC-MANDATED]" if f in SPEC_MANDATED_FAMILIES else ""
            out.append(f"  {n:>3}  {g:>3}.{t:<14}.{f}{protected}")
    out.append("")
    out.append("=== SINGLETON FAMILIES (n=1, candidates for either build-out or cut) ===")
    fam_counts = Counter(p.family for p in problems)
    singletons = sorted([f for f, n in fam_counts.items() if n == 1])
    for f in singletons:
        protected = " [SPEC-MANDATED]" if f in SPEC_MANDATED_FAMILIES else ""
        out.append(f"  {f}{protected}")
    return "\n".join(out)


# -------------------- main pipeline --------------------

def run_all_checks(p: Problem) -> None:
    check_unrendered_jinja(p)
    check_slug_canon(p)
    check_units(p)
    check_short_long_body(p)
    check_empty_answer(p)
    check_steps_ops_consistency(p)
    check_gsm8k_saturation(p)
    check_answer_units_match_topic(p)


def suggest_action(p: Problem) -> str:
    """Triage suggestion. Conservative: 'review' is the default for anything
    flagged; 'fix' for purely mechanical issues (Jinja, slug); 'keep' for clean
    templates. Never auto-suggests 'cut' -- that's alex's call."""
    if not p.flags:
        return "keep"
    only_mechanical = all(f.startswith(("slug_", "unit_")) or f == "unrendered_jinja"
                         for f in p.flags)
    if only_mechanical:
        return "fix"
    return "review"


def write_csv(path: Path, problems: list[Problem]) -> None:
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([
            "pid", "grade", "topic", "family", "complexity",
            "is_anchor", "spec_mandated_family",
            "n_flags", "flags", "notes",
            "suggested_action", "body_chars", "answer",
        ])
        for p in problems:
            w.writerow([
                p.pid, p.grade, p.topic, p.family, p.complexity,
                "Y" if p.is_anchor else "N",
                "Y" if p.family in SPEC_MANDATED_FAMILIES else "N",
                len(p.flags),
                "; ".join(sorted(set(p.flags))),
                " | ".join(p.notes),
                suggest_action(p),
                len(p.body),
                p.answer[:120],
            ])


def write_dupe_csv(path: Path, dupes: list[tuple]) -> None:
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["pid_a", "pid_b", "similarity", "cell", "kind"])
        for row in dupes:
            w.writerow(row)


def write_summary(path: Path, problems: list[Problem],
                  dupes: list[tuple]) -> None:
    flag_counter: Counter[str] = Counter()
    for p in problems:
        for f in p.flags:
            flag_counter[f] += 1
    actions = Counter(suggest_action(p) for p in problems)

    out = []
    out.append(f"# mathbot template audit -- {len(problems)} problems\n")
    out.append("## Triage suggestions")
    for act, n in actions.most_common():
        out.append(f"  {act:<10} {n:>4}  ({100*n/len(problems):.1f}%)")
    out.append("")
    out.append("## Flag frequencies")
    for flag, n in flag_counter.most_common():
        out.append(f"  {flag:<32} {n:>4}")
    out.append("")
    out.append(f"## Near-duplicate pairs (within same grade.topic.family cell, "
               f"similarity >= {DUPE_THRESHOLD})")
    same_diff = [d for d in dupes if d[4] == "same_difficulty"]
    cross_diff = [d for d in dupes if d[4] == "cross_difficulty"]
    out.append(f"  total pairs:           {len(dupes)}")
    out.append(f"  same-difficulty:       {len(same_diff)}  (true dupe candidates)")
    out.append(f"  cross-difficulty:      {len(cross_diff)}  (signals fake difficulty tiering)")
    if dupes:
        out.append("  top 15:")
        for pid_a, pid_b, ratio, cell, kind in dupes[:15]:
            out.append(f"    {ratio:.2f}  [{kind:>17}]  {cell}")
            out.append(f"           {pid_a}")
            out.append(f"           {pid_b}")
    out.append("")
    out.append(cell_density_report(problems))
    path.write_text("\n".join(out))


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python audit_templates.py <samples.txt> <output_dir>",
              file=sys.stderr)
        return 1
    src = Path(argv[1])
    out = Path(argv[2])
    out.mkdir(parents=True, exist_ok=True)

    text = src.read_text()
    problems = parse(text)
    print(f"parsed {len(problems)} problems")

    for p in problems:
        run_all_checks(p)

    dupes = find_near_dupes(problems)
    print(f"found {len(dupes)} near-duplicate pairs")

    write_csv(out / "audit.csv", problems)
    write_dupe_csv(out / "audit_dupes.csv", dupes)
    write_summary(out / "audit_summary.txt", problems, dupes)
    print(f"wrote {out}/audit.csv, audit_dupes.csv, audit_summary.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
