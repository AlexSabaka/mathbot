# Mathbot Template System Reference

> **Version**: 2.0  
> **Last Updated**: 2026-01-30  
> **Purpose**: Complete specification for YAML-based procedural math problem generation

---

## 1. System Overview

Mathbot uses a **YAML-based template system** where each problem is defined as a structured YAML file containing:

1. **Metadata** - Grade level, topic, difficulty, authorship
2. **Variables** - Type-constrained data generation rules
3. **Template** - Jinja2 template for problem text
4. **Solution** - Pure Python code with injected variable context
5. **Tests** - Validation cases for regression testing

### Architecture

```
YAML Template File
–> [1] Generate Variables (based on constraints + seed)
   context = {name: "Sarah", price: 12.50, ...}
–> [2] Render Template (Jinja2 with context)
   problem_text = "Sarah bought 3 apples..."
–> [3] Execute Solution (Python exec with context)
   context['Answer'] = 37.50
–> [4] Format Answer (based on Answer variable constraints)
   "$37.50"
```

---

## 2. YAML Template Structure

### Complete Example

```yaml
metadata:
  id: k4_easy_splitting_01
  version: "1.0.0"
  author: Alex Sabaka
  created: 2026-01-30
  grade: 4
  topic: arithmetic.division
  family: splitting
  difficulty: easy
  culture: en-US
  steps: 2
  tags: [money, real-world, division]

variables:
  num_people:
    type: integer
    min: 2
    max: 6
    
  restaurant:
    type: item
    category: restaurant
    
  total:
    type: decimal
    format: money
    min: 20.00
    max: 200.00
    step: 5.00
    
  Answer:
    type: decimal
    format: money

template: |
  A group of {{num_people}} friends finish dinner at {{restaurant}}.
  The total bill comes to {{total}}, and they decide to split it equally.
  
  How much does each person pay?
  
  Please solve this problem and provide your final answer.

solution: |
  # All variables from 'variables' section are available
  per_person = total / num_people
  Answer = round(per_person, 2)

tests:
  - seed: 12345
    expected:
      num_people: 4
      restaurant: "The Golden Fork"
      total: "$80.00"
      answer: "$20.00"
  
  - seed: 67890
    expected:
      answer: "$35.75"
```

---

## 3. Metadata Section

### Required Fields

| Field        | Type   | Description                                      | Example                    |
|--------------|--------|--------------------------------------------------|----------------------------|
| `id`         | string | Unique template identifier                       | `k4_easy_splitting_01`     |
| `version`    | string | Semantic version (semver)                        | `"1.0.0"`                  |
| `author`     | string | Template creator name                            | `"Alex Sabaka"`            |
| `created`    | date   | Creation date (YYYY-MM-DD)                       | `2026-01-30`               |
| `grade`      | int    | Grade level (1-12)                               | `4`                        |
| `topic`      | string | Dot-separated topic hierarchy                    | `"arithmetic.division"`    |
| `family`     | string | Problem family/type                              | `"splitting"`              |
| `difficulty` | string | One of: `easy`, `medium`, `hard`                 | `"easy"`                   |
| `steps`      | int    | Number of computational steps                    | `2`                        |

### Optional Fields

| Field     | Type         | Description                           | Example            |
|-----------|--------------|---------------------------------------|--------------------|
| `culture` | string       | Locale for formatting (ISO 639-1)     | `"en-US"`          |
| `tags`    | list[string] | Searchable keywords                   | `["money", "time"]`|
| `notes`   | string       | Internal documentation                | `"Updated for..."`  |

### ID Naming Convention

Format: `{grade}_{difficulty}_{family}_{variant}`

Examples:
- `k3_easy_sequential_01`
- `k7_medium_growth_02`
- `k11_hard_calculus_05`

---

## 4. Variables Section

Each variable defines how a value is generated. Variables are injected into both the template and solution contexts.

### Basic Structure

```yaml
variables:
  variable_name:
    type: <type>
    # ... type-specific constraints
```

### Variable Types Reference

#### Numeric Types

**Integer**
```yaml
count:
  type: integer
  min: 1
  max: 10
  step: 1  # Optional, default 1
```

**Decimal**
```yaml
price:
  type: decimal
  min: 5.00
  max: 50.00
  step: 0.25  # Optional, default 0.01
  format: money  # Optional: money, percentage, length, weight, temperature, area, volume
```

**Fraction**
```yaml
portion:
  type: fraction
  min: 1
  max: 4
  # Generates numerator/denominator pair
```

#### Name/Location Types

**Person**
```yaml
name:
  type: person
  # Generates: "Sarah", "Marcus", "Chen", etc.
```

**Location**
```yaml
city:
  type: location
  # Generates: "Springfield", "Dallas", etc.
```

**Store/Restaurant/Company**
```yaml
shop:
  type: store
  # Generates: "Johnson's Market", "Smith Boutique"

restaurant:
  type: restaurant
  # Generates: "The Golden Fork", "Mario's Cafe"

business:
  type: company
  # Generates: "Acme Corp", "Tech Solutions Inc"
```

#### Item Types

```yaml
item:
  type: item
  category: grocery  # grocery, electronics, clothing, book, online
  singular: true     # Optional, default false (returns plural)
```

**Categories:**
- `grocery` - "apples", "milk", "bread"
- `electronics` - "laptop", "headphones"
- `clothing` - "shirts", "jeans"
- `book` - "novels", "textbooks"
- `online` - "chargers", "games"

#### Time/Duration

```yaml
duration:
  type: time
  min: 0.25  # Hours (0.25 = 15 minutes)
  max: 5.0
  step: 0.25
  # Renders as: "2 hours 30 minutes"
```

#### Boolean

```yaml
has_discount:
  type: boolean
  probability: 0.5  # 50% chance of True
```

### Format Constraints

Format determines how values are rendered in templates:

| Format       | Applies To     | Example Output       |
|--------------|----------------|----------------------|
| `money`      | decimal        | `$42.50`             |
| `percentage` | int, decimal   | `25%`                |
| `ordinal`    | integer        | `3rd`, `21st`        |
| `length`     | decimal        | `12.5 miles` (US)    |
| `weight`     | decimal        | `5.2 kg`             |
| `temperature`| decimal        | `72°F` (US)          |

### The Answer Variable

**Every template must define at least one answer variable**. For single-answer problems, use `Answer`. For multi-answer problems (e.g., "find both area and perimeter"), use `Answer1`, `Answer2`, etc.

#### Single Answer

```yaml
Answer:
  type: decimal
  format: money
  # Solution must set: Answer = <numeric_value>
  # System formats as: "$42.50"
```

#### Multiple Answers

```yaml
# For problems requiring multiple answers
Answer1:
  type: integer
  # First answer (e.g., area)

Answer2:
  type: integer
  # Second answer (e.g., perimeter)

# Solution must set both:
# Answer1 = area_value
# Answer2 = perimeter_value
```

**Common Answer Formats:**

```yaml
# Money answer
Answer:
  type: decimal
  format: money

# Time answer
Answer:
  type: time

# Percentage answer  
Answer:
  type: integer
  format: percentage

# Plain number
Answer:
  type: integer

# Fraction
Answer:
  type: fraction

# Multiple numeric answers
Answer1:
  type: integer
Answer2:
  type: integer
```

---

## 5. Template Section (Jinja2)

The template section uses **Jinja2 syntax** for rendering problem text.

### Basic Variable Substitution

```jinja2
{{name}} bought {{quantity}} {{item}} for {{price}} each.
```

### Conditional Content

```jinja2
{% if has_discount %}
{{name}} received a {{discount}}% discount.
{% endif %}

{% if has_discount %}
The discount saved {{name}} some money.
{% else %}
{{name}} paid full price.
{% endif %}
```

### Loops

```jinja2
{% for i in range(num_days) %}
Day {{i+1}}: {{name}} worked {{hours}} hours.
{% endfor %}
```

### Helper Functions

Mathbot provides template helpers (from `template_helpers.py`):

```jinja2
{{#choice}}How much did they spend?|What was the total cost?{{/choice}}

{{#list_and}}apples, oranges, bananas{{/list_and}}
â†' "apples, oranges, and bananas"

{{#ordinal}}{{day}}{{/ordinal}}
â†' "3rd day"

{{#capitalize}}{{name}}{{/capitalize}}
```

### Template Requirements

1. Must end with: `"Please solve this problem and provide your final answer."`
2. Use clear, age-appropriate language for grade level
3. Provide sufficient context
4. Ask a specific question
5. Use variables, not hardcoded values

---

## 6. Solution Section (Pure Python)

The solution section contains **pure Python code** that computes the answer. All variables from the `variables` section are injected into the execution context.

### Execution Model

```python
# 1. Generate variables
context = generate_variables(yaml['variables'], seed=12345)
# context = {'num_people': 4, 'total': 80.00, ...}

# 2. Execute solution with context
safe_globals = {'round': round, 'abs': abs, ...}  # Restricted builtins
exec(yaml['solution'], safe_globals, context)

# 3. Extract answer
answer_value = context['Answer']  # Must be set by solution

# 4. Format answer based on Answer variable definition
formatted_answer = format_answer(answer_value, yaml['variables']['Answer'])
# â†' "$20.00"
```

### Solution Requirements

1. **Must set `Answer` variable** - the final result
2. **Use injected variable names** directly (no special syntax)
3. **Show clear computational steps** for readability
4. **Use comments** to explain multi-step logic
5. **Don't format Answer** - system handles formatting based on variable definition

### Available Builtins

Solutions have access to:
- Math: `round()`, `abs()`, `min()`, `max()`, `sum()`, `pow()`
- Type conversion: `int()`, `float()`, `str()`
- `Decimal` for precise money calculations
- Helper functions from `template_helpers.py`

### Examples

**Simple Calculation**
```python
# Single-step division
per_person = total / num_people
Answer = round(per_person, 2)
```

**Multi-step with Conditionals**
```python
# Calculate subtotal
subtotal = quantity * price

# Apply discount if applicable
if has_discount:
    discount_amount = subtotal * (discount / 100)
    total = subtotal - discount_amount
else:
    total = subtotal

# Add tax
tax_amount = total * (tax_rate / 100)
final_total = total + tax_amount

Answer = round(final_total, 2)
```

**Complex Multi-year Calculation**
```python
# Year 1
balance = principal * (1 + rate1 / 100)

# Year 2
balance = balance * (1 + rate2 / 100)

# Optional deposit after year 2
if has_deposit:
    balance = balance + deposit_amount

# Optional withdrawal
if has_withdrawal:
    balance = balance - withdrawal_amount

# Year 3
balance = balance * (1 + rate3 / 100)

Answer = round(balance, 2)
```

**Using Decimal for Precision**
```python
from decimal import Decimal

# Convert to Decimal for money operations
price_decimal = Decimal(str(price))
quantity_decimal = Decimal(str(quantity))

total = price_decimal * quantity_decimal
Answer = float(total)  # Convert back for formatting
```

---

## 7. Tests Section

Tests validate template correctness and prevent regressions.

### Structure

```yaml
tests:
  - seed: 12345
    expected:
      # Can specify individual variables
      num_people: 4
      restaurant: "The Golden Fork"
      total: "$80.00"
      # Must specify answer
      answer: "$20.00"
  
  - seed: 67890
    expected:
      # Or just validate the answer
      answer: "$35.75"
  
  - seed: 99999
    expected:
      answer: "$112.33"
    notes: "Edge case: max values"
```

### Test Execution

```bash
# Run tests for a template
mathbot test templates/k4_easy_splitting_01.yaml

# Run all tests
mathbot test --all

# Add new test case
mathbot test templates/k4_easy_splitting_01.yaml --generate-test --seed 55555
```

---

## 8. Complete Advanced Example

```yaml
metadata:
  id: k9_hard_growth_05
  version: "1.0.0"
  author: Alex Sabaka
  created: 2026-01-30
  grade: 9
  topic: algebra.compound_interest
  family: growth
  difficulty: hard
  culture: en-US
  steps: 6
  tags: [finance, interest, multi-step]

variables:
  name:
    type: person
  
  principal:
    type: decimal
    format: money
    min: 500
    max: 5000
    step: 25
  
  rate1:
    type: integer
    format: percentage
    min: 3
    max: 8
  
  rate2:
    type: integer
    format: percentage
    min: 3
    max: 8
  
  rate3:
    type: integer
    format: percentage
    min: 3
    max: 8
  
  has_deposit:
    type: boolean
    probability: 0.4
  
  deposit_amount:
    type: decimal
    format: money
    min: 100
    max: 1000
    step: 25
  
  has_withdrawal:
    type: boolean
    probability: 0.3
  
  withdrawal_amount:
    type: decimal
    format: money
    min: 50
    max: 500
    step: 25
  
  Answer:
    type: decimal
    format: money

template: |
  {{name}} opens a savings account with an initial deposit of {{principal}}.
  
  During the first year, the account earns {{rate1}}% interest.
  
  In the second year, the interest rate changes to {{rate2}}%, which is applied to the current balance.
  
  {% if has_deposit %}
  After receiving the second year's interest, {{name}} adds {{deposit_amount}} to the account.
  {% endif %}
  
  {% if has_withdrawal %}
  Following the second year's interest payment, {{name}} makes a withdrawal of {{withdrawal_amount}}.
  {% endif %}
  
  The third year brings {{rate3}}% interest on the current balance.
  
  What is the total amount in {{name}}'s account after three years?
  
  Please solve this problem and provide your final answer.

solution: |
  # Year 1: Apply first interest rate
  balance = principal * (1 + rate1 / 100)
  
  # Year 2: Apply second interest rate
  balance = balance * (1 + rate2 / 100)
  
  # Optional deposit after year 2
  if has_deposit:
      balance = balance + deposit_amount
  
  # Optional withdrawal after year 2
  if has_withdrawal:
      balance = balance - withdrawal_amount
  
  # Year 3: Apply third interest rate
  balance = balance * (1 + rate3 / 100)
  
  # Set final answer
  Answer = round(balance, 2)

tests:
  - seed: 12345
    expected:
      answer: "$1876.50"
    notes: "Base case with deposit"
  
  - seed: 67890
    expected:
      answer: "$3421.25"
    notes: "High principal, no transactions"
  
  - seed: 11111
    expected:
      answer: "$1234.56"
    notes: "With withdrawal"
```

---

## 9. Validation Rules

### Template Validation

When validating a template, the system checks:

1. **YAML syntax** is valid
2. **Required metadata fields** are present
3. **All variable types** are recognized
4. **Constraint combinations** are valid
   - `step` must evenly divide `(max - min)`
   - `format: ordinal` only for integers
   - `format: money` only for decimals
   - Boolean can't have min/max
   - Fraction can't have step
5. **Answer variable** is defined
6. **Template section** is valid Jinja2
7. **Solution section** compiles as Python
8. **Solution sets Answer** variable
9. **Test cases** execute successfully

### Common Validation Errors

```yaml
# ERROR: step doesn't divide range evenly
price:
  type: decimal
  min: 5.00
  max: 20.00
  step: 0.30  # 15.00 / 0.30 = 50 ✓
  
# ERROR: ordinal on non-integer
day:
  type: decimal
  format: ordinal  # ✗ ordinal only works on integers

# ERROR: missing Answer variable
variables:
  price:
    type: decimal
  # Missing: Answer definition ✗

# ERROR: solution doesn't set Answer
solution: |
  total = price * quantity
  # Missing: Answer = total ✗
```

---

## 10. CLI Usage

### Generate Problems

```bash
# Generate single problem
mathbot generate --template templates/k4_easy_splitting_01.yaml --seed 12345

# Generate batch
mathbot generate --template templates/k4_easy_splitting_01.yaml --count 10 --output problems.json

# Generate from grade/topic
mathbot generate --grade 4 --topic arithmetic --count 50
```

### Validate Templates

```bash
# Validate single template
mathbot validate templates/k4_easy_splitting_01.yaml

# Validate all templates
mathbot validate --all

# Validate with warnings
mathbot validate --strict templates/k9_hard_growth_05.yaml
```

### Test Templates

```bash
# Run tests
mathbot test templates/k4_easy_splitting_01.yaml

# Generate test case
mathbot test templates/k4_easy_splitting_01.yaml --add-test --seed 99999

# Update expected values
mathbot test templates/k4_easy_splitting_01.yaml --update-expected
```

### Convert Legacy Templates

```bash
# Convert Mustache to YAML
mathbot convert mustache-to-yaml templates/legacy/*.mustache --output templates/yaml/
```

---

## 11. Grade Level Guidelines

### Grade Ranges

| CLI Grade    | K-Grades       | Focus Areas                                      |
|--------------|----------------|--------------------------------------------------|
| `elementary` | k1-k5          | Basic arithmetic, counting, simple word problems |
| `middle`     | k6-k8          | Fractions, decimals, percentages, ratios         |
| `high`       | k9-k12         | Algebra, geometry, trigonometry, calculus        |

### Complexity by Grade

**Grades 1-3 (Steps: 1-2)**
- Single operation problems
- Small numbers (< 100)
- Visual/concrete contexts

**Grades 4-6 (Steps: 2-4)**
- Multi-operation problems
- Larger numbers, decimals
- Real-world scenarios

**Grades 7-9 (Steps: 3-6)**
- Abstract reasoning
- Percentages, ratios
- Word problems with multiple variables

**Grades 10-12 (Steps: 5-10)**
- Complex multi-step problems
- Algebraic expressions
- Calculus, advanced topics

---

## 12. Best Practices

### Template Design

✅ **DO:**
- Use realistic values for grade level
- Ensure "nice" answers (avoid long decimals)
- Include sufficient context in problem text
- Use diverse names/locations for cultural representation
- Write clear, step-by-step solutions
- Add comments in solution code
- Test with multiple seeds

❌ **DON'T:**
- Hardcode names, places, or items
- Use overly complex language for grade
- Create problems with ambiguous answers
- Skip validation tests
- Use magic numbers without explanation
- Over-constrain variables (too narrow ranges)

### Solution Code Style

```python
# GOOD: Clear, commented, step-by-step
# Calculate cost per item
item_cost = price * quantity

# Apply discount
if has_discount:
    discount_amount = item_cost * (discount / 100)
    item_cost = item_cost - discount_amount

# Add tax
tax_amount = item_cost * (tax_rate / 100)
final_cost = item_cost + tax_amount

Answer = round(final_cost, 2)
```

```python
# BAD: Single line, unclear
Answer = round(((price * quantity) * (1 - (discount / 100 if has_discount else 0))) * (1 + tax_rate / 100), 2)
```

### Testing Strategy

- **Minimum 3 test cases** per template
- Test edge cases (min/max values)
- Test conditional branches (if/else paths)
- Verify answer formatting
- Check for floating-point precision issues

---

## 13. Future Enhancements

### Planned Features

- [ ] Template composition (extends/includes)
- [ ] Variable dependencies (conditional generation)
- [ ] Multi-language support (i18n)
- [ ] Visual/diagram generation
- [ ] Interactive problem variants
- [ ] Accessibility features (alt text, screen reader support)
- [ ] Template analytics (difficulty scoring, success rates)

### Under Consideration

- Custom helper functions per template
- LaTeX math rendering in templates
- Answer explanation generation
- Adaptive difficulty based on performance
- Collaborative template editing
- Template marketplace

---

## Appendix A: Quick Reference

### Minimal Template

```yaml
metadata:
  id: k1_easy_addition_01
  version: "1.0.0"
  author: Your Name
  created: 2026-01-30
  grade: 1
  topic: arithmetic.addition
  family: basic
  difficulty: easy
  steps: 1

variables:
  a:
    type: integer
    min: 1
    max: 10
  b:
    type: integer
    min: 1
    max: 10
  Answer:
    type: integer

template: |
  What is {{a}} + {{b}}?
  
  Please solve this problem and provide your final answer.

solution: |
  Answer = a + b

tests:
  - seed: 12345
    expected:
      answer: "7"
```

### Common Variable Patterns

```yaml
# Money variable
price:
  type: decimal
  format: money
  min: 5.00
  max: 50.00
  step: 0.25

# Percentage
discount:
  type: integer
  format: percentage
  min: 5
  max: 50
  step: 5

# Time duration
hours:
  type: time
  min: 0.5
  max: 8.0
  step: 0.5

# Person with pronoun access
name:
  type: person
  # In template: {{name}}, {{name_pronoun}}, {{name_possessive}}

# Item (plural by default)
item:
  type: item
  category: grocery
```

---
