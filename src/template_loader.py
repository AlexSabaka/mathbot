"""Template loader for Mustache templates."""

import os
import chevron
from typing import Dict, Any


class TemplateLoader:
    """Load and render Mustache templates for problem generation."""
    
    def __init__(self, template_dir: str = None):
        """Initialize template loader.
        
        Args:
            template_dir: Directory containing templates. Defaults to src/templates.
        """
        if template_dir is None:
            # Get the directory of this file, then go to templates
            current_dir = os.path.dirname(os.path.abspath(__file__))
            template_dir = os.path.join(current_dir, 'templates')
        
        self.template_dir = template_dir
        self._cache = {}
    
    def load_template(self, family_name: str, template_name: str) -> str:
        """Load a template file.
        
        Args:
            family_name: Name of the problem family (e.g., 'sequential_purchase')
            template_name: Name of the template file (e.g., 'grocery_shopping')
            
        Returns:
            Template content as string
        """
        cache_key = f"{family_name}/{template_name}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        template_path = os.path.join(
            self.template_dir, 
            family_name, 
            f"{template_name}.mustache"
        )
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        self._cache[cache_key] = template_content
        return template_content
    
    def render(self, family_name: str, template_name: str, context: Dict[str, Any]) -> str:
        """Load and render a template with given context.
        
        Args:
            family_name: Name of the problem family
            template_name: Name of the template file
            context: Dictionary of variables to substitute in template
            
        Returns:
            Rendered template as string
        """
        template = self.load_template(family_name, template_name)
        return chevron.render(template, context)
    
    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """Render a template string with given context.
        
        Args:
            template_string: Template content as string
            context: Dictionary of variables to substitute
            
        Returns:
            Rendered template as string
        """
        return chevron.render(template_string, context)
