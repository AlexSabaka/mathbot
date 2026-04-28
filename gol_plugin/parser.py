"""Mathbot response parser — extract a candidate answer span from a model response.

End-first via parse_utils.re_search_last. Strategy order matches confidence:
  1. latex_boxed (0.95)        — \\boxed{X}
  2. final_answer_block (0.92) — multi-line content following an answer-label anchor line
  3. markdown_bold (0.90)      — **X** (skip header bolds, including colon-outside)
  4. answer_label (0.85)       — inline "answer:" / "final answer:" / "the answer is X"
  5. last_line (0.50)          — last non-empty line, fallback

Pre-process: strip end-of-turn tokenizer artifacts (`<turn|>`, `<|im_end|>`, …)
before any strategy runs.
"""

import re
from typing import Any, Dict, List, Optional

from src.plugins.base import ParsedAnswer, ResponseParser
from src.plugins.parse_utils import re_search_last


_LATEX_BOXED = re.compile(r"\\boxed\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}")
_MD_BOLD = re.compile(r"\*\*([^*\n]+?)\*\*")
# Allow optional `**` markers around the colon so `**Answer**: 3 jumps` and
# `Answer: **3 jumps**` both capture the value cleanly.
_ANSWER_LABEL = re.compile(
    r"(?:final\s+answer|the\s+answer\s+is|answer)\s*\*{0,2}\s*[:=]?\s*\*{0,2}\s*([^\n!?]+)",
    re.IGNORECASE,
)
_SENTENCE_END = re.compile(r"\.\s+")
# Strip surrounding `**…**` left in the answer-label capture (model emits
# `**42**` or `** 42 **` after the colon).
_BOLD_WRAPPER = re.compile(r"^\*+\s*|\s*\*+$")

# An anchor line: a line that ends in an answer-label phrase + colon
# (with optional bold/heading/bullet/step-number wrappers).
# Note: only horizontal whitespace is allowed inside `^…$` so the regex stays
# pinned to a single line — `\s*` would otherwise consume newlines and let the
# match start mid-content.
_FINAL_ANSWER_ANCHOR = re.compile(
    r"(?im)^[ \t]*"                               # optional indent
    r"(?:[#*\-•]+[ \t]*)*"                        # optional bullet/heading marks
    r"(?:\d+\.?[ \t]+)?"                          # optional step number "5. " / "5 "
    r"\*{0,2}[ \t]*"                              # optional opening **
    r"(?:final[ \t]+|the[ \t]+)?"                 # optional "final"/"the"
    r"(?:answer|output|conclusion|result|finding|verdict|solution)"
    r"[ \t]*\*{0,2}[ \t]*:[ \t]*\*{0,2}[ \t]*$"   # colon, optional close **, EOL
)
# Any bold-headed colon line — terminates a `final_answer_block` capture so the
# block doesn't bleed into "**Verification:**" / "**Justification:**" sections.
# Colon is REQUIRED — either inside (**X:**) or outside (**X**:) the bold —
# so a bare `**20, 30, 40, 50**` value line is not mistaken for a heading.
_HEADING_LINE = re.compile(
    r"(?m)^[ \t]*(?:[#*\-•]+[ \t]*)*(?:\d+\.?[ \t]+)?"
    r"\*{1,2}[^*\n]*?"
    r"(?::\*{1,2}|\*{1,2}[ \t]*:)"
    r"[ \t]*$"
)
# Horizontal rule / scene break.
_BLOCK_TERMINATOR = re.compile(r"\n\s*(?:---|\*\*\*|___)\s*\n")
# Tokenizer artifacts some local models emit at the end of a response.
_EOT_MARKERS_RE = re.compile(
    r"\s*(?:<turn\|>|<\|im_end\|>|<\|endoftext\|>|<\|eot_id\|>|</s>)\s*$"
)


class MathbotParser(ResponseParser):
    def parse(self, response: str, task_params: Dict[str, Any]) -> ParsedAnswer:
        if not response or not response.strip():
            return ParsedAnswer(
                value=None,
                raw_response=response or "",
                parse_strategy="empty",
                confidence=0.0,
                error="Empty response",
            )

        response = _EOT_MARKERS_RE.sub("", response)

        m = re_search_last(_LATEX_BOXED, response)
        if m:
            return ParsedAnswer(
                value=m.group(1).strip(),
                raw_response=response,
                parse_strategy="latex_boxed",
                confidence=0.95,
                char_start=m.start(1),
                char_end=m.end(1),
            )

        block = _final_answer_block(response)
        if block:
            value, start, end = block
            return ParsedAnswer(
                value=value,
                raw_response=response,
                parse_strategy="final_answer_block",
                confidence=0.92,
                char_start=start,
                char_end=end,
            )

        bold = _last_signal_bold(response)
        if bold:
            value, start, end = bold
            return ParsedAnswer(
                value=value,
                raw_response=response,
                parse_strategy="markdown_bold",
                confidence=0.90,
                char_start=start,
                char_end=end,
            )

        m = re_search_last(_ANSWER_LABEL, response)
        if m:
            captured = m.group(1)
            cleaned = _SENTENCE_END.split(captured, 1)[0]
            cleaned = _BOLD_WRAPPER.sub("", cleaned)
            cleaned = cleaned.strip().rstrip(".,;: ")
            if cleaned:
                offset = m.start(1) + (len(captured) - len(captured.lstrip()))
                return ParsedAnswer(
                    value=cleaned,
                    raw_response=response,
                    parse_strategy="answer_label",
                    confidence=0.85,
                    char_start=offset,
                    char_end=offset + len(cleaned),
                )

        for line in reversed(response.splitlines()):
            stripped = line.strip()
            if stripped:
                start = response.rfind(stripped)
                return ParsedAnswer(
                    value=stripped,
                    raw_response=response,
                    parse_strategy="last_line",
                    confidence=0.50,
                    char_start=start if start >= 0 else None,
                    char_end=(start + len(stripped)) if start >= 0 else None,
                )

        return ParsedAnswer(
            value=None,
            raw_response=response,
            parse_strategy="none",
            confidence=0.0,
            error="No answer span found",
        )

    def get_strategies(self) -> List[str]:
        return [
            "latex_boxed",
            "final_answer_block",
            "markdown_bold",
            "answer_label",
            "last_line",
        ]


def _final_answer_block(response: str) -> Optional[tuple[str, int, int]]:
    """Capture the block following the LAST answer-label anchor line.

    Stops at the next horizontal rule, the next anchor line, or end-of-response.
    Returns (block_text, char_start, char_end) or None when no anchor is present
    or the block is empty.
    """
    anchors = list(_FINAL_ANSWER_ANCHOR.finditer(response))
    if not anchors:
        return None

    last = anchors[-1]
    block_start = last.end()
    block = response[block_start:]

    # Stop at: another anchor line, a generic bold-heading line (Verification:,
    # Justification:, …), or a horizontal rule.
    cutoffs: list[int] = [len(block)]
    follow_anchors = list(_FINAL_ANSWER_ANCHOR.finditer(block))
    if follow_anchors:
        cutoffs.append(follow_anchors[0].start())
    follow_heading = _HEADING_LINE.search(block)
    if follow_heading:
        cutoffs.append(follow_heading.start())
    rule_match = _BLOCK_TERMINATOR.search(block)
    if rule_match:
        cutoffs.append(rule_match.start())

    block = block[: min(cutoffs)]
    stripped = block.strip("\n").rstrip()
    if not stripped:
        return None

    leading = len(block) - len(block.lstrip("\n"))
    abs_start = block_start + leading
    abs_end = abs_start + len(stripped)
    return stripped, abs_start, abs_end


def _last_signal_bold(response: str) -> Optional[tuple[str, int, int]]:
    """Walk **bold** matches end-first, skipping header-style bolds.

    A bold is a header (and thus skipped) if either:
      - its content ends with `:`            — `**Answer:**`
      - the next non-space char is `:`       — `**Answer**:`
    """
    last: Optional[tuple[str, int, int]] = None
    for m in _MD_BOLD.finditer(response):
        text = m.group(1).strip()
        if not text or text.endswith(":"):
            continue
        tail = response[m.end(): m.end() + 3]
        if re.match(r"\s*:", tail):
            continue
        last = (text, m.start(1), m.end(1))
    return last
