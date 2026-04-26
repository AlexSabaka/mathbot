"""Extract a candidate answer string from a free-form model response."""

import re

LATEX_BOXED = re.compile(r"\\boxed\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}")
MD_BOLD = re.compile(r"\*\*([^*\n]+?)\*\*")
ANSWER_LABEL = re.compile(
    r"(?:final\s+answer|the\s+answer\s+is|answer)\s*[:=]?\s*([^\n!?]+)",
    re.IGNORECASE,
)
_SENTENCE_END = re.compile(r"\.\s+")


def extract_answer(response: str) -> tuple[str | None, str]:
    """Return (extracted, strategy). Strategies tried in order; first hit wins."""
    if not response or not response.strip():
        return None, "empty"

    matches = LATEX_BOXED.findall(response)
    if matches:
        return matches[-1].strip(), "latex_boxed"

    bold_matches = MD_BOLD.findall(response)
    if bold_matches:
        return bold_matches[-1].strip(), "md_bold"

    label_matches = ANSWER_LABEL.findall(response)
    if label_matches:
        candidate = _SENTENCE_END.split(label_matches[-1], 1)[0]
        return candidate.strip().rstrip(".,;: "), "answer_label"

    lines = [ln.strip() for ln in response.splitlines() if ln.strip()]
    if lines:
        return lines[-1], "last_line"

    return None, "none"
