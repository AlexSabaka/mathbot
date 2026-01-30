# Mathbot - AI Agent Guidelines

## Project Overview

Mathbot is a Python library that **procedurally generates multi-step math word problems** with realistic natural language context. It's designed to test LLM reasoning capabilities as well as general education and provide infinite problem variations with verifiable answers.

**Key Philosophy**: This is an agent-maintained project. Focus on extensibility, template diversity, and deterministic generation.

## Architecture

### Core Pattern: Template-Driven Generation

```
generate_problem() → TemplateGenerator → select template → render + compute answer → return dict
```

**IMPORTANT**: As of v0.1.2 (v2.0), this project uses a **YAML+Jinja2 template system**. There are NO Python family classes. All problem generation logic is in YAML template files with Jinja2 rendering.

### Key Files

| File | Purpose |
|------|---------|
| `src/generator.py` | Public API (`generate_problem`, `generate_problems`) |
| `src/template_generator.py` | Core generator - discovers templates, generates values, computes answers |
| `src/yaml_loader.py` | YAML parsing and validation with TemplateDefinition dataclass |
| `src/jinja_renderer.py` | Jinja2 environment with custom filters |
| `src/variable_generator.py` | Type-aware value generation with format constraints |
| `src/solution_evaluator.py` | Python solution execution with multi-answer support |
| `src/providers.py` | `MathProblemProvider` - Faker provider for domain data |
| `src/constants.py` | Configuration constants (grades, topics, families) |
| `src/templates/` | All `.yaml` template files organized by topic |
| `src/templates/SPEC.md` | **Template format specification (SOURCE OF TRUTH)** |

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
        "operations": List[str],
        "template_path": str  # Path to source template
    }
}
```

**Critical**: `expected_answer` is ALWAYS a string (e.g., "$6.94", "3/4", "3.75 hours")

## Template System

### Template Location & Naming

Templates organized by math topic:
```
src/templates/
├── SPEC.md          # Template format specification (SOURCE OF TRUTH)
├── arithmetic/      # Shopping, sequential purchases (10 templates)
├── geometry/        # Area, perimeter, shapes (5 templates)
├── measurement/     # Distance, time, travel (7 templates)
├── percentages/     # Growth, interest, discounts (6 templates)
└── ratios/          # Sharing, splitting (5 templates)
```

**Filename Convention:**
```
{grade}_{complexity}_{family}_{variant}.yaml
```

Examples:
- `k3_easy_sequential_01.yaml`
- `k7_medium_shopping_02.yaml`

### Template Structure

YAML templates have structured sections:

```yaml
metadata:
  id: k3_easy_sequential_01
  version: "1.0.0"
  author: Mathbot
  created: 2026-01-30
  grade: 3
  topic: arithmetic.shopping
  family: shopping
  difficulty: easy
  steps: 2
  tags: [shopping, money, addition]

variables:
  name:
    type: person
  qty:
    type: integer
    min: 2
    max: 5
  price:
    type: decimal
    format: money
    min: 3.0
    max: 8.0
    step: 0.25
  Answer:
    type: decimal
    format: money

template: |
  {{name}} bought {{qty}} items for {{price}} each.

solution: |
  total = qty * price
  Answer = round(total, 2)

tests:
  - seed: 12345
    expected:
      answer: "$15.00"
```

**Key Points:**
1. **metadata** - Template identification and classification
2. **variables** - Type definitions with constraints and formats
3. **template** - Jinja2 template text (supports filters, logic)
4. **solution** - Python code to compute answer(s)
5. **tests** - Seed-based test cases with expected answers
6. **For complete specification, see `src/templates/SPEC.md`**

### Variable Definition (YAML)

```yaml
variables:
  price:
    type: decimal
    format: money
    min: 5.0
    max: 20.0
    step: 0.25
  qty:
    type: integer
    min: 1
    max: 10
  name:
    type: person
  city:
    type: location
  discount:
    type: integer
    format: percentage
    min: 10
    max: 30
    step: 5
```

**Generated Values:**
- `price` → `$12.50` (formatted in template as `{{price}}`)
- `qty` → `5` (raw integer)
- `name` → `"James"` (random person name)
- `city` → `"Springfield"` (random location)
- `discount` → `15` (displayed as `{{discount}}%` in template)

**Important**: Variables with `format` constraints get both raw value (for logic) and formatted value (for display with `_formatted` suffix)

### Available Variable Types

| Type | Constraints | Example Output |
|------|-------------|----------------|
| `integer` | `min`, `max`, `step` | `5`, `42` |
| `decimal` | `min`, `max`, `step` | `12.50`, `3.75` |
| `fraction` | `min`, `max` | `3/4`, `2/5` |
| `person` | (none) | `James`, `Sarah` |
| `location` | (none) | `Springfield`, `New York` |
| `store` | (none) | `Johnson's Market` |
| `restaurant` | (none) | `Mario's Bistro` |
| `company` | (none) | `Tech Solutions Inc` |
| `weekday` | (none) | `Monday`, `Friday` |
| `season` | (none) | `spring`, `winter` |
| `time` | `min`, `max`, `step` | `2.5` (hours) |
| `item` | `category: grocery/electronics/etc.` | `apples`, `laptop` |
| `boolean` | (none) | `True`, `False` |
| `string` | `choices: [...]` | Custom options |

### Available Format Constraints

| Format | Adds | Example |
|--------|------|----------|
| `money` | `$` | `$12.50` |
| `percentage` | (number only, template adds %) | `15` |
| `ordinal` | ordinal suffix | `3rd`, `21st` |
| `length` | meters | `45m` (input), `62 meters` (answer) |
| `weight` | kilograms | `75kg` |
| `temperature` | Fahrenheit | `72.5°F` |
| `area` | square meters | `238 square meters` |
| `volume` | cubic meters | `150 cubic meters` |
| `speed` | mph | `65.00 mph` |

### Jinja2 Filters

```jinja2
{{ "Option A|Option B|Option C" | choice }}  → Random selection
{{ "apple" | plural }}                        → "apples"
{{ ["a", "b", "c"] | list_and }}             → "a, b, and c"
{{ 12.5 | format_money }}                     → "$12.50"
{{ 3 | ordinal }}                             → "3rd"
{{ 254 | number_to_words }}                   → "two hundred fifty-four"
{{ "hello" | capitalize }}                    → "Hello"
```

**Jinja2 Logic Support:**
```jinja2
{% if condition %}
  Text when true
{% else %}
  Text when false
{% endif %}

{% set calculated_value = var1 + var2 %}
{{ calculated_value }}
```

### Solution Section Rules

1. **Python code** executed in safe environment
2. Access variables by name (e.g., `price`, `qty`)
3. Single answer: `Answer = expression`
4. Multiple answers: `Answer1 = expr1`, `Answer2 = expr2`, `Answer3 = expr3`
5. Available functions: `abs()`, `round()`, `str()`, `int()`, `float()`, `min()`, `max()`, `sum()`, `pow()`, `len()`, `list()`, `range()`, `sorted()`, `enumerate()`, `zip()`, `map()`, `filter()`, `any()`, `all()`, `math.*`
6. Answer formatting determined by Answer variable's `format` specification
7. Example:
```python
total = qty * price
Answer = round(total, 2)  # Format applied based on Answer's format: money
```

### Multi-Answer Problems

For problems requiring multiple outputs (e.g., area AND perimeter):

```yaml
variables:
  Answer1:
    type: integer
    format: area
  Answer2:
    type: integer
    format: length

solution: |
  area = length * width
  perimeter = 2 * (length + width)
  Answer1 = area
  Answer2 = perimeter

tests:
  - seed: 12345
    expected:
      answer: "238 square meters | 62 meters"
```

Output format: `"Answer1 | Answer2 | Answer3"` with proper formatting applied to each.

## Adding New Templates

### Step-by-Step

1. Create file: `src/templates/{topic}/{grade}_{complexity}_{family}_{variant}.yaml`
2. Define metadata section (id, grade, topic, family, difficulty, steps)
3. Define variables section with types and constraints
4. Write template section using Jinja2 syntax
5. Write solution section with Python code
6. Add Answer variable(s) with appropriate format
7. Add test cases with seeds and expected answers
8. Test: `mathbot generate --input src/templates/{topic}/{file}.yaml`
9. Validate: `mathbot generate --grade {grade} --topic {topic}`

### Template Checklist

- [ ] Filename follows `{grade}_{complexity}_{family}_{variant}.yaml`
- [ ] All YAML sections present: metadata, variables, template, solution, tests
- [ ] Variables have proper type and constraints
- [ ] Answer variable(s) have appropriate format specification
- [ ] Solution uses raw variable names and produces correct Answer
- [ ] Test cases provided with seeds and expected answers
- [ ] Realistic value ranges for grade level
- [ ] Follows specification in `src/templates/SPEC.md`

### Example Complete Template

```yaml
metadata:
  id: k3_easy_shopping_01
  version: "1.0.0"
  author: Mathbot
  created: 2026-01-30
  grade: 3
  topic: arithmetic.shopping
  family: shopping
  difficulty: easy
  steps: 3
  culture: en-US
  tags: [shopping, money, addition, multiplication]

variables:
  name:
    type: person
  store:
    type: store
  city:
    type: location
  qty1:
    type: integer
    min: 2
    max: 5
  item1:
    type: item
    category: grocery
  price1:
    type: decimal
    format: money
    min: 1.0
    max: 5.0
    step: 0.25
  qty2:
    type: integer
    min: 2
    max: 5
  item2:
    type: item
    category: grocery
  price2:
    type: decimal
    format: money
    min: 2.0
    max: 6.0
    step: 0.25
  Answer:
    type: decimal
    format: money

template: |
  {{name}} goes shopping at {{store}} in {{city}}.
  
  They buy {{qty1}} {{item1}} at {{price1}} each and {{qty2}} {{item2}} at {{price2}} each.
  
  {{ "How much does " ~ name ~ " spend in total?|What is the total cost?" | choice }}

solution: |
  cost1 = qty1 * price1
  cost2 = qty2 * price2
  total = cost1 + cost2
  Answer = round(total, 2)

tests:
  - seed: 12345
    expected:
      answer: "$15.75"
  - seed: 67890
    expected:
      answer: "$22.50"
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
mathbot generate --input src/templates/arithmetic/k3_easy_sequential_01.yaml

# List available options
mathbot list
```

**Entry point**: `mathbot` command defined in `pyproject.toml` → `src.cli:main`

## Common Issues & Solutions

### "Answer computation failed"

**Cause**: Solution section has errors
**Solutions**:
1. Check solution uses raw variable names matching `variables:` section
2. Verify all referenced variables are defined
3. Check for unsupported functions (only basic math + round, str, int, float allowed)
4. Ensure `Answer = ` line exists (or Answer1, Answer2, etc. for multi-answer)
5. Verify Answer variable(s) defined in `variables:` section

### Template Not Being Selected

**Cause**: Template filename or metadata doesn't match criteria
**Solutions**:
1. Verify filename format: `{grade}_{complexity}_{family}_{variant}.yaml`
2. Check template is in correct topic directory
3. Verify metadata.grade and metadata.difficulty match request
4. Ensure YAML is valid (run `mathbot generate --input {file}` to test)

### Variable Not Rendering Correctly

**Cause**: Variable not defined or wrong type
**Solutions**:
1. Ensure variable defined in `variables:` section
2. Check type is valid (see Available Variable Types)
3. For formatted values, use `{{var_formatted}}` if you need both raw and formatted
4. Verify YAML syntax is correct (proper indentation)

### Tests Failing After Template Changes

**Cause**: Test expectations don't match new output
**Solutions**:
1. Update test expected answers to match new format
2. Verify template test cases with `mathbot generate --input {file} -s {seed}`
3. Check YAML validation passes (no errors on load)
4. Clear pytest cache: `pytest --cache-clear`

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
- Use `--input` flag to test specific templates during development

## Common Pitfalls

1. **DON'T hardcode text in Python** - All narratives in YAML templates
2. **DON'T use floating-point for money** - Use `round()` in solution, format handles display
3. **DON'T forget Answer variable** - Must be defined in variables section
4. **DON'T use f-strings for multi-answer** - Use Answer1, Answer2, Answer3 instead
5. **DON'T forget format constraints** - Answer variables should specify format (money, percentage, etc.)
6. **DO include "Please solve this problem"** - Tests expect this text
7. **DO use deterministic seeds** - Same seed → identical output
8. **DO test new templates** - Run `mathbot generate --input {file}` first
9. **DO follow SPEC.md** - `src/templates/SPEC.md` is the source of truth
10. **DO use Jinja2 logic** - Templates support {% if %}, {% set %}, filters

## Documentation

- **[src/templates/SPEC.md](src/templates/SPEC.md)** - Complete template format specification **(SOURCE OF TRUTH)**
- [CHANGELOG.md](CHANGELOG.md) - Project history and changes
- [README.md](README.md) - User-facing documentation
- [docs/K{1-12}_PROBLEMS.md](docs/) - Grade-level example problems
