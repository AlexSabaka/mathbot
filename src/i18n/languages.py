"""Per-language grammar primitives used by Jinja filters and variable formatters.

A `LanguageSpec` bundles the small set of callables that diverge per
language: pluralization, ordinal display, and number-to-words. Filters
look up a spec at render time using the template's `language` field.

Phase 5 ships an `en` spec only (matching pre-i18n behaviour). Adding a
new language is a matter of writing a spec and calling
`register_language(...)`; no changes to renderer or template code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict

import inflect


@dataclass(frozen=True)
class LanguageSpec:
    """Grammar callables for a single language."""

    code: str
    plural: Callable[[str, int], str]
    ordinal: Callable[[int], str]
    number_to_words: Callable[[int], str]


_REGISTRY: Dict[str, LanguageSpec] = {}


def register_language(spec: LanguageSpec) -> None:
    """Register a language spec, replacing any prior entry with the same code."""
    _REGISTRY[spec.code] = spec


def get_language_spec(code: str) -> LanguageSpec:
    """Look up the spec for a language code, falling back to 'en'."""
    if code in _REGISTRY:
        return _REGISTRY[code]
    return _REGISTRY["en"]


# --- English spec (built from inflect) --------------------------------------

_inflect_en = inflect.engine()


def _en_plural(word: str, count: int = 2) -> str:
    return _inflect_en.plural(word, count)


def _en_ordinal(n: int) -> str:
    return _inflect_en.ordinal(n)


def _en_number_to_words(n: int) -> str:
    return _inflect_en.number_to_words(n, andword="")


register_language(LanguageSpec(
    code="en",
    plural=_en_plural,
    ordinal=_en_ordinal,
    number_to_words=_en_number_to_words,
))
