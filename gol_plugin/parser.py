"""Mathbot response parser — extract a candidate answer span from a model response.

End-first via parse_utils.re_search_last. Strategy order matches confidence:
  1. latex_boxed (0.95) — \\boxed{X}
  2. markdown_bold (0.90) — **X** (skip header bolds ending with ":")
  3. answer_label (0.85) — "answer:", "final answer:", "the answer is X"
  4. last_line (0.50) — last non-empty line, fallback
"""

import re
from typing import Any, Dict, List

from src.plugins.base import ParsedAnswer, ResponseParser
from src.plugins.parse_utils import re_search_last


_LATEX_BOXED = re.compile(r"\\boxed\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}")
_MD_BOLD = re.compile(r"\*\*([^*\n]+?)\*\*")
_ANSWER_LABEL = re.compile(
    r"(?:final\s+answer|the\s+answer\s+is|answer)\s*[:=]?\s*([^\n!?]+)",
    re.IGNORECASE,
)
_SENTENCE_END = re.compile(r"\.\s+")


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
            cleaned = _SENTENCE_END.split(captured, 1)[0].strip().rstrip(".,;: ")
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
        return ["latex_boxed", "markdown_bold", "answer_label", "last_line"]


def _last_signal_bold(response: str) -> tuple[str, int, int] | None:
    """Walk **bold** matches end-first, skipping header-style bolds (ending ':')."""
    last: tuple[str, int, int] | None = None
    for m in _MD_BOLD.finditer(response):
        text = m.group(1).strip()
        if not text or text.endswith(":"):
            continue
        last = (text, m.start(1), m.end(1))
    return last
