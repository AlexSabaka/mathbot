"""Jinja2 renderer with custom filters and helpers for mathbot v2.0.

Locale-aware filters (`plural`, `ordinal`, `number_to_words`) read the
`language` variable from the rendering context and dispatch to the
appropriate `LanguageSpec`. Templates without a `language` get the `en`
spec (current behaviour). See `src.i18n.languages`.
"""

import random

from jinja2 import Environment, BaseLoader, pass_context
from jinja2.runtime import Context
from typing import Any

from .i18n import get_language_spec


def _ctx_language(ctx: Context) -> str:
    """Read `language` from the rendering context, defaulting to 'en'."""
    return ctx.get("language", "en") or "en"


def choice_filter(options: str) -> str:
    """Select a random option from pipe-separated choices.

    Example: {{ "Option A|Option B|Option C" | choice }}
    """
    choices = [opt.strip() for opt in options.split('|')]
    return random.choice(choices)


@pass_context
def plural_filter(ctx: Context, word: str, count: int = 2) -> str:
    """Convert word to plural form using the active language's rules.

    Example: {{ "apple" | plural }}
    """
    return get_language_spec(_ctx_language(ctx)).plural(word, count)


def list_and_filter(items: Any) -> str:
    """Join list with commas and 'and' before last item.

    Example: {{ ["a", "b", "c"] | list_and }} → "a, b, and c"
    """
    if isinstance(items, str):
        items = [item.strip() for item in items.split(',')]

    if not items:
        return ""
    if len(items) == 1:
        return str(items[0])
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"

    return ", ".join(str(item) for item in items[:-1]) + f", and {items[-1]}"


def format_money_filter(value: float) -> str:
    """Format number as money.

    Example: {{ 12.5 | format_money }} → "$12.50"
    """
    return f"${value:.2f}"


@pass_context
def ordinal_filter(ctx: Context, number: int) -> str:
    """Convert number to ordinal form using the active language's rules.

    Example: {{ 3 | ordinal }} → "3rd"
    """
    return get_language_spec(_ctx_language(ctx)).ordinal(int(number))


@pass_context
def number_to_words_filter(ctx: Context, number: int) -> str:
    """Convert number to word form using the active language's rules.

    Example: {{ 254 | number_to_words }} → "two hundred fifty-four"
    """
    return get_language_spec(_ctx_language(ctx)).number_to_words(int(number))


def capitalize_filter(text: str) -> str:
    """Capitalize first letter of text.

    Example: {{ "hello" | capitalize }} → "Hello"
    """
    return text.capitalize()


class JinjaRenderer:
    """Jinja2 template renderer with mathbot-specific filters."""

    def __init__(self):
        """Initialize Jinja2 environment with custom filters."""
        self.env = Environment(
            loader=BaseLoader(),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Register filters (the locale-aware ones decorated with
        # @pass_context will receive the rendering context as first arg).
        self.env.filters['choice'] = choice_filter
        self.env.filters['plural'] = plural_filter
        self.env.filters['list_and'] = list_and_filter
        self.env.filters['format_money'] = format_money_filter
        self.env.filters['ordinal'] = ordinal_filter
        self.env.filters['number_to_words'] = number_to_words_filter
        self.env.filters['capitalize'] = capitalize_filter

        # Locale-agnostic filters are also exposed as global callables so
        # templates can use them as `{{ choice("A|B") }}`. Locale-aware
        # filters are filter-only; if a template needs them as functions,
        # it can do `{{ 3 | ordinal }}` which threads context correctly.
        self.env.globals['choice'] = choice_filter
        self.env.globals['list_and'] = list_and_filter
        self.env.globals['format_money'] = format_money_filter

    def render(self, template_text: str, context: dict) -> str:
        """Render a template with the given context.

        Args:
            template_text: Jinja2 template string
            context: Dictionary of variables to inject

        Returns:
            Rendered template string
        """
        template = self.env.from_string(template_text)
        return template.render(context)

    def validate_template(self, template_text: str) -> tuple[bool, str]:
        """Validate that a template is valid Jinja2 syntax.

        Args:
            template_text: Template string to validate

        Returns:
            (is_valid, error_message) tuple
        """
        try:
            self.env.from_string(template_text)
            return True, ""
        except Exception as e:
            return False, str(e)
