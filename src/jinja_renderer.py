"""Jinja2 renderer with custom filters and helpers for mathbot v2.0."""

import random
import inflect
from jinja2 import Environment, BaseLoader, TemplateNotFound
from typing import Any, List


# Initialize inflect engine
p = inflect.engine()


def choice_filter(options: str) -> str:
    """Select a random option from pipe-separated choices.
    
    Example: {{ "Option A|Option B|Option C" | choice }}
    """
    choices = [opt.strip() for opt in options.split('|')]
    return random.choice(choices)


def plural_filter(word: str, count: int = 2) -> str:
    """Convert word to plural form.
    
    Example: {{ "apple" | plural }}
    """
    return p.plural(word, count)


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


def ordinal_filter(number: int) -> str:
    """Convert number to ordinal form.
    
    Example: {{ 3 | ordinal }} → "3rd"
    """
    return p.ordinal(number)


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
        
        # Register filters
        self.env.filters['choice'] = choice_filter
        self.env.filters['plural'] = plural_filter
        self.env.filters['list_and'] = list_and_filter
        self.env.filters['format_money'] = format_money_filter
        self.env.filters['ordinal'] = ordinal_filter
        self.env.filters['capitalize'] = capitalize_filter
        
        # Register global functions (can be used without filter syntax)
        self.env.globals['choice'] = choice_filter
        self.env.globals['plural'] = plural_filter
        self.env.globals['list_and'] = list_and_filter
        self.env.globals['format_money'] = format_money_filter
        self.env.globals['ordinal'] = ordinal_filter
    
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
