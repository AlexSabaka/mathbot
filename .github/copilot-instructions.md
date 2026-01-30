# Mathbot - AI Agent Guidelines

## Project Overview

Mathbot is a Python library that **procedurally generates multi-step math word problems** with realistic natural language context. It's designed to test LLM reasoning capabilities as well as general education and provide infinite problem variations with verifiable answers.

**Key Philosophy**: This is an agent-maintained project. Focus on extensibility, template diversity, and deterministic generation.

## Architecture

### Core Pattern: Template-Driven Generation

```
generate_problem() → TemplateGenerator → select template → render + compute answer → return dict
```

**IMPORTANT**: As of v2.0, this project uses a **pure template-driven system**. There are NO Python family classes. All problem generation logic is in Mustache templates.

### Key Files

| File | Purpose |
|------|---------|
| `src/generator.py` | Public API (`generate_problem`, `generate_problems`) |
| `src/template_generator.py` | Core generator - discovers templates, generates values, computes answers |
| `src/variable_parser.py` | Parses variable metadata from template names |
| `src/solution_evaluator.py` | Evaluates solution expressions after `---` separator |
| `src/template_helpers.py` | Mustache helper lambdas (choice, plural, etc.) |
| `src/providers.py` | `MathProblemProvider` - Faker provider for domain data |
| `src/constants.py` | Configuration constants (grades, topics, families) |
| `src/templates/` | All `.mustache` template files organized by topic |

### Output Structure (Critical)

All problems return this exact dict structure:
```python
{
    "test_id": "math_0001_family_name",
    "task_type": "multi_step_math",
    "config_name": "descriptive_config",
    "problem": "Natural language problem text",
    "task_params": {
        "complexity": int(1-3),
        "grade": str,
        "math_topic": List[str],
        "problem_family": str,
        "num_steps": int,
        "expected_answer": str,  # Always string with units
        "operations": List[str]
    }
}
```

**Critical**: `expected_answer` is ALWAYS a string (e.g., "$6.94", "3/4", "3.75 hours")

## Template System

### Template Location & Naming

Templates organized by math topic:
```
src/templates/
├── arithmetic/      # Shopping, sequential purchases
├── geometry/        # Area, perimeter, shapes
├── measurement/     # Distance, time, travel
├── percentages/     # Growth, interest, discounts
└── ratios/          # Sharing, splitting
```

**Filename Convention:**
```
{grade}_{complexity}_{family}_{variant}.mustache
```

Examples:
- `k3_easy_sequential_01.mustache`
- `k7_medium_shopping_02.mustache`

### Template Structure

Every template has TWO sections separated by `---`:

```mustache
{{name_person}} bought {{qty_integer_min_2_max_5}} {{item_item_type_grocery}} for {{price_decimal_money_min_3_max_8}} each.

Please solve this problem and provide your final answer.
---
total = {{qty}} * {{price}}
Answer = total
```

**Key Points:**
1. **Problem text** (above `---`) uses **full variable names** with metadata
2. **Solution section** (below `---`) uses **short variable names**
3. The `Answer = ` line determines the expected answer
4. Always include "Please solve this problem and provide your final answer."

### Variable Naming Convention

```
{{varname_type_constraint1_constraint2_...}}
```

**Examples:**

| Full Variable Name | Short Name | Type | Generated Value |
|-------------------|------------|------|-----------------|
| `{{price_decimal_money_min_5_max_20_step_025}}` | `price` | money | `$12.50` |
| `{{qty_integer_min_1_max_10}}` | `qty` | integer | `5` |
| `{{name_person}}` | `name` | person | `James` |
| `{{city_location}}` | `city` | location | `Springfield` |
| `{{discount_percentage_min_10_max_30_step_5}}` | `discount` | percentage | `15` |

**Important**: For step values with decimals, omit decimal point: `step_025` = 0.25

### Available Variable Types

| Type | Constraints | Example Output |
|------|-------------|----------------|
| `integer` | `min`, `max` | `5`, `42` |
| `decimal_money` / `money` | `min`, `max`, `step` | `$12.50` |
| `percentage` | `min`, `max`, `step` | `15`, `20` |
| `person` / `name` | (none) | `James`, `Sarah` |
| `location` / `city` | (none) | `Springfield` |
| `store` | (none) | `Johnson's Market` |
| `weekday` / `season` / `time` | (none) | `Monday`, `spring`, `morning` |
| `item` | `type_grocery/online/electronics` | `apples`, `laptop` |

### Template Helpers

```mustache
{{#choice}}Option A|Option B|Option C{{/choice}}  → Random selection
{{#plural}}apple{{/plural}}                        → "apples"
{{#list_and}}a, b, c{{/list_and}}                 → "a, b, and c"
{{#format_money}}12.5{{/format_money}}            → "$12.50"
```

### Solution Section Rules

1. Use **short variable names** (without metadata)
2. Final line must be `Answer = expression`
3. Available functions: `round()`, `str()`, `int()`, `float()`, `min()`, `max()`, `sum()`, `pow()`
4. Money values auto-convert: `$12.50` → `12.50`
5. For formatted output: `Answer = '$' + str(round(total, 2))`

## Adding New Templates

### Step-by-Step

1. Create file: `src/templates/{topic}/{grade}_{complexity}_{family}_{variant}.mustache`
2. Write problem text with full variable names
3. Add `---` separator
4. Write solution expressions with short variable names
5. End with `Answer = ` line
6. Test: `mathbot generate --grade {grade} --topic {topic}`

### Template Checklist

- [ ] Filename follows `{grade}_{complexity}_{family}_{variant}.mustache`
- [ ] Variables use proper metadata syntax
- [ ] Solution section uses short names only
- [ ] Includes "Please solve this problem and provide your final answer."
- [ ] `Answer = ` produces correct result
- [ ] Realistic value ranges for grade level

### Example Complete Template

```mustache
{{name_person}} goes shopping at {{store_store}} in {{city_location}}.

They buy {{qty1_integer_min_2_max_5}} {{item1_item_type_grocery_plural}} at {{price1_decimal_money_min_1_max_5_step_025}} each and {{qty2_integer_min_2_max_5}} {{item2_item_type_grocery_plural}} at {{price2_decimal_money_min_2_max_6_step_025}} each.

{{#choice}}How much does {{name_person}} spend in total?|What is the total cost?{{/choice}}

Please solve this problem and provide your final answer.
---
cost1 = {{qty1}} * {{price1}}
cost2 = {{qty2}} * {{price2}}
total = cost1 + cost2
Answer = total
```

## Key Constants & Mappings

### Grade Mapping

| CLI Grade | K-Grades Matched |
|-----------|------------------|
| `elementary` | k1, k2, k3, k4, k5 |
| `middle` | k6, k7, k8 |
| `high` | k9, k10, k11, k12 |

### Family Aliases (Backward Compatibility)

| Old Name | New Internal Name |
|----------|-------------------|
| `sequential_purchase` | `shopping` |
| `rate_time` | `travel` |
| `compound_growth` | `growth` |
| `multi_person_sharing` | `sharing` |
| `area_perimeter_chain` | `geometry` |

The generator accepts both old and new names and maps output back to old names.

## Development Workflow

```bash
# Install (uses uv for dependency management)
uv sync

# Run tests
pytest

# Generate sample problems (CLI testing)
mathbot generate -c 2 -g middle -t arithmetic
mathbot generate -s 42 -o json --file problem.json

# List available options
mathbot list
```

**Entry point**: `mathbot` command defined in `pyproject.toml` → `src.cli:main`

## Common Issues & Solutions

### "Answer computation failed"

**Cause**: Template's solution section has errors
**Solutions**:
1. Check solution section uses SHORT variable names (without metadata)
2. Verify variable names in solution match those in problem text
3. Check for unsupported functions (only basic math + round, str, int, float allowed)
4. Ensure `Answer = ` line exists

### Template Not Being Selected

**Cause**: Template filename doesn't match criteria
**Solutions**:
1. Verify filename format: `{grade}_{complexity}_{family}_{variant}.mustache`
2. Check template is in correct topic directory
3. Verify grade/complexity match request

### Variable Placeholders Showing `[name]`

**Cause**: Variable type not recognized
**Solutions**:
1. Add proper type metadata: `{{name_person}}` not just `{{name}}`
2. Check type is in TYPE_KEYWORDS list in variable_parser.py

### Tests Failing After Template Changes

**Cause**: Python bytecode cache or old templates
**Solutions**:
1. Clear cache: `find . -type d -name "__pycache__" -exec rm -rf {} +`
2. Verify old template directories are removed
3. Check template content matches expected format

## Utility Functions (src/utils.py)

```python
from src.utils import round_money, generate_price, generate_percentage

round_money(12.567)              # Returns "$12.57"
generate_price(5, 20, step=0.25) # Returns price like 12.75
generate_percentage(5, 50, step=5)  # Returns 5, 10, 15, ..., or 50
```

**Critical**: Use `Decimal` for money calculations to avoid floating-point errors.

## MathProblemProvider (src/providers.py)

```python
# Item tuples: (plural, singular, min_price, max_price)
fake.grocery_items(count=3)
fake.online_items(count=2)
fake.electronics_items(count=2)

# Context data
fake.weekday()          # "Monday"
fake.season()           # "spring"
fake.time_of_day()      # "morning"
fake.store_name()       # "Johnson's Market"

# Numeric generators
fake.price(min=5, max=20, step=0.25)
fake.percentage(min=5, max=50, step=5)
```

## Testing Patterns

- Test both single generation (`generate_problem`) and batch (`generate_problems`)
- Always test reproducibility: `seed=X` should produce identical output
- Test parameter validation (invalid complexity, grades, topics)
- Family-specific tests should check answer format ($ for money, "hours" for time)

## Common Pitfalls

1. ❌ **Don't hardcode text in Python** - All narratives in templates
2. ❌ **Don't use floating-point for money** - Use `Decimal` or `round_money()`
3. ❌ **Don't forget solution section** - Templates without `---` won't compute answers
4. ❌ **Don't mix full/short names** - Full in problem, short in solution
5. ❌ **Don't use loops in templates** - Current system doesn't support `{{#items}}` loops
6. ✅ **DO include "Please solve this problem"** - Tests expect this text
7. ✅ **DO use deterministic seeds** - Same seed → identical output
8. ✅ **DO test new templates** - Run `mathbot generate` with matching parameters

## Documentation

- [docs/INDEX.md](docs/INDEX.md) - Complete template variable reference
- [CHANGELOG.md](CHANGELOG.md) - Project history and changes
- [README.md](README.md) - User-facing documentation
