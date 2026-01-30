"""Mustache template helper functions (lambdas) for enhanced template capabilities."""

import random
import inflect
from typing import Any, Callable


# Initialize inflect engine for pluralization
_inflect = inflect.engine()


def create_choice_helper(seed: int = None) -> Callable:
    """Create a helper that randomly chooses from pipe-separated options.
    
    Usage in template:
        {{#choice}}Option A|Option B|Option C{{/choice}}
    
    Returns one of the options randomly.
    """
    def choice_helper(text: str, render: Callable) -> str:
        # Render the text first (in case it contains variables)
        rendered = render(text)
        
        # Split by pipe and choose
        options = [opt.strip() for opt in rendered.split('|')]
        if not options:
            return ''
        
        return random.choice(options)
    
    return choice_helper


def create_plural_helper() -> Callable:
    """Create a helper that pluralizes English words.
    
    Usage in template:
        {{#plural}}apple{{/plural}} → "apples"
        {{#plural}}box{{/plural}} → "boxes"
    """
    def plural_helper(text: str, render: Callable) -> str:
        rendered = render(text).strip()
        return _inflect.plural(rendered)
    
    return plural_helper


def create_list_and_helper() -> Callable:
    """Create a helper that formats a list with commas and 'and'.
    
    Usage in template:
        {{#list_and}}item1, item2, item3{{/list_and}} → "item1, item2, and item3"
    """
    def list_and_helper(text: str, render: Callable) -> str:
        rendered = render(text).strip()
        
        # Split by comma
        items = [item.strip() for item in rendered.split(',') if item.strip()]
        
        if len(items) == 0:
            return ''
        elif len(items) == 1:
            return items[0]
        elif len(items) == 2:
            return f"{items[0]} and {items[1]}"
        else:
            return ', '.join(items[:-1]) + f", and {items[-1]}"
    
    return list_and_helper


def create_format_money_helper() -> Callable:
    """Create a helper that formats numbers as money.
    
    Usage in template:
        {{#format_money}}12.5{{/format_money}} → "$12.50"
    """
    def format_money_helper(text: str, render: Callable) -> str:
        rendered = render(text).strip()
        
        try:
            value = float(rendered)
            return f"${value:.2f}"
        except ValueError:
            return rendered
    
    return format_money_helper


def create_ordinal_helper() -> Callable:
    """Create a helper that converts numbers to ordinal form.
    
    Usage in template:
        {{#ordinal}}1{{/ordinal}} → "1st"
        {{#ordinal}}2{{/ordinal}} → "2nd"
    """
    def ordinal_helper(text: str, render: Callable) -> str:
        rendered = render(text).strip()
        
        try:
            num = int(rendered)
            return _inflect.ordinal(num)
        except ValueError:
            return rendered
    
    return ordinal_helper


def create_capitalize_helper() -> Callable:
    """Create a helper that capitalizes text.
    
    Usage in template:
        {{#capitalize}}hello world{{/capitalize}} → "Hello World"
    """
    def capitalize_helper(text: str, render: Callable) -> str:
        rendered = render(text).strip()
        return rendered.title()
    
    return capitalize_helper


def create_lower_helper() -> Callable:
    """Create a helper that lowercases text.
    
    Usage in template:
        {{#lower}}HELLO WORLD{{/lower}} → "hello world"
    """
    def lower_helper(text: str, render: Callable) -> str:
        rendered = render(text).strip()
        return rendered.lower()
    
    return lower_helper


def create_upper_helper() -> Callable:
    """Create a helper that uppercases text.
    
    Usage in template:
        {{#upper}}hello world{{/upper}} → "HELLO WORLD"
    """
    def upper_helper(text: str, render: Callable) -> str:
        rendered = render(text).strip()
        return rendered.upper()
    
    return upper_helper


def get_all_helpers(seed: int = None) -> dict:
    """Get all template helpers as a dictionary for Chevron.
    
    Args:
        seed: Optional random seed for reproducibility
    
    Returns:
        Dictionary mapping helper names to helper functions
    """
    if seed is not None:
        random.seed(seed)
    
    return {
        'choice': create_choice_helper(seed),
        'plural': create_plural_helper(),
        'list_and': create_list_and_helper(),
        'format_money': create_format_money_helper(),
        'ordinal': create_ordinal_helper(),
        'capitalize': create_capitalize_helper(),
        'lower': create_lower_helper(),
        'upper': create_upper_helper(),
    }
