"""Locale registry for language-aware template rendering."""

from .languages import LanguageSpec, get_language_spec, register_language

__all__ = ["LanguageSpec", "get_language_spec", "register_language"]
