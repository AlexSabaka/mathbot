"""Parse variable metadata from template variable names.

Variable naming convention:
    {{varname_type_constraint1_constraint2_...}}

Examples:
    {{price_decimal_money_min_5_max_20_step_025}}
    {{quantity_integer_min_1_max_10}}
    {{name_person}}
    {{city_location}}
    {{item_grocery_count_3}}
"""

import re
from typing import Dict, Any, List, Tuple


class VariableMetadata:
    """Parsed metadata for a template variable."""
    
    def __init__(self, full_name: str, short_name: str, var_type: str, constraints: Dict[str, Any]):
        self.full_name = full_name  # e.g., "price1_decimal_money_min_5_max_20"
        self.short_name = short_name  # e.g., "price1"
        self.var_type = var_type
        self.constraints = constraints
    
    # Backward compatibility
    @property
    def name(self):
        return self.short_name
    
    def __repr__(self):
        return f"VariableMetadata(full={self.full_name}, short={self.short_name}, type={self.var_type}, constraints={self.constraints})"


def parse_variable_name(variable: str) -> VariableMetadata:
    """Parse a variable name into its metadata components.
    
    Args:
        variable: Variable string like "price_decimal_money_min_5_max_20_step_025"
    
    Returns:
        VariableMetadata with parsed information
    
    Examples:
        >>> parse_variable_name("price_decimal_money_min_5_max_20")
        VariableMetadata(full='price_decimal_money_min_5_max_20', short='price', type='decimal_money', constraints={'min': 5.0, 'max': 20.0})
        
        >>> parse_variable_name("quantity_integer_min_1_max_10")
        VariableMetadata(full='quantity_integer_min_1_max_10', short='quantity', type='integer', constraints={'min': 1, 'max': 10})
    """
    full_name = variable
    parts = variable.split('_')
    
    if len(parts) < 2:
        # Simple variable with no metadata (shouldn't happen in new system)
        return VariableMetadata(full_name, variable, 'simple', {})
    
    # Known type keywords - find where the type starts
    TYPE_KEYWORDS = {
        'integer', 'decimal', 'money', 'person', 'name', 'location', 'city',
        'store', 'restaurant', 'company', 'weekday', 'season', 'time',
        'item', 'fraction', 'percentage', 'choices', 'simple'
    }
    
    # Find first type keyword
    type_idx = None
    for i, part in enumerate(parts):
        if part in TYPE_KEYWORDS:
            type_idx = i
            break
    
    if type_idx is None:
        # No type found, treat as simple
        return VariableMetadata(full_name, variable, 'simple', {})
    
    # Short name is everything before type
    short_name = '_'.join(parts[:type_idx])
    
    # Type is the keyword
    var_type = parts[type_idx]
    
    # Remaining parts are constraints
    constraints = {}
    i = type_idx + 1
    
    while i < len(parts):
        constraint_key = parts[i]
        
        # Handle different constraint patterns
        if constraint_key in ['min', 'max', 'step']:
            if i + 1 < len(parts):
                # Try to parse as number
                value_str = parts[i + 1]
                # Handle decimals like "025" → 0.25
                if var_type in ['decimal', 'money'] and len(value_str) >= 2 and value_str[0] == '0' and value_str != '0':
                    constraints[constraint_key] = float('0.' + value_str[1:])
                else:
                    try:
                        # Try integer first
                        if '.' not in value_str:
                            constraints[constraint_key] = int(value_str)
                        else:
                            constraints[constraint_key] = float(value_str)
                    except ValueError:
                        constraints[constraint_key] = value_str
                i += 2
            else:
                i += 1
                
        elif constraint_key == 'range':
            # range_X_Y format
            if i + 2 < len(parts):
                min_val = parts[i + 1]
                max_val = parts[i + 2]
                
                # Parse range values
                if var_type in ['decimal', 'money']:
                    # Handle decimal notation like "025" → 0.25
                    if len(min_val) >= 2 and min_val[0] == '0' and min_val != '0':
                        constraints['min'] = float('0.' + min_val[1:])
                    else:
                        constraints['min'] = float(min_val)
                    
                    if len(max_val) >= 2 and max_val[0] == '0' and max_val != '0':
                        constraints['max'] = float('0.' + max_val[1:])
                    else:
                        constraints['max'] = float(max_val)
                else:
                    constraints['min'] = int(min_val)
                    constraints['max'] = int(max_val)
                i += 3
            else:
                i += 1
                
        elif constraint_key == 'choices':
            # Collect all remaining parts as choices
            choices = parts[i + 1:]
            constraints['choices'] = choices
            break
            
        elif constraint_key == 'count':
            if i + 1 < len(parts):
                constraints['count'] = int(parts[i + 1])
                i += 2
            else:
                i += 1
                
        elif constraint_key == 'type':
            # Subtype (e.g., item_list_type_grocery)
            if i + 1 < len(parts):
                constraints['subtype'] = parts[i + 1]
                i += 2
            else:
                i += 1
        else:
            # Unknown constraint, skip
            i += 1
    
    # Combine type with subtype if present (e.g., "decimal_money" → "money")
    if var_type in ['decimal', 'integer'] and i > 2 and parts[2] in ['money']:
        var_type = f"{var_type}_{parts[2]}"
    
    return VariableMetadata(full_name, short_name, var_type, constraints)


def extract_variables_from_template(template_content: str) -> List[str]:
    """Extract all {{variable}} patterns from template content.
    
    Args:
        template_content: Mustache template string
    
    Returns:
        List of unique variable names (without {{ }})
    """
    # Match {{variable}} but not {{#section}}, {{/section}}, {{^inverted}}, {{!comment}}
    pattern = r'\{\{(?![#/\^!])([^}]+)\}\}'
    matches = re.findall(pattern, template_content)
    
    # Remove duplicates while preserving order, skip helpers
    seen = set()
    unique_vars = []
    helper_names = {'choice', 'plural', 'list_and', 'format_money', 'ordinal', 'capitalize', 'lower', 'upper'}
    
    for match in matches:
        var = match.strip()
        # Skip if it's a helper function
        if var not in helper_names and var not in seen:
            seen.add(var)
            unique_vars.append(var)
    
    return unique_vars


def parse_template_variables(template_content: str) -> List[VariableMetadata]:
    """Extract and parse all variables from a template.
    
    Args:
        template_content: Mustache template string
    
    Returns:
        List of VariableMetadata objects
    """
    variables = extract_variables_from_template(template_content)
    return [parse_variable_name(var) for var in variables]
