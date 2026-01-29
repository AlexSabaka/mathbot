# Multi-Step Math Problem Generator - Project Specification

## Overview

A standalone Python library for generating procedurally-created, multi-step math word problems with natural language context. Designed to test LLM procedural reasoning and state tracking capabilities.

## Project Goals

- Generate infinite variations of multi-step math problems
- Support configurable complexity, grade levels, math topics, and problem families
- Produce problems with verifiable correct answers
- Provide reproducible generation via seeds

## Dependencies

```python
# Required
faker>=20.0.0  # For realistic fake data (names, cities, items, etc.)
names>=0.3.0   # For generating person names
```

Use `uv` and `pyproject.toml` for project configuration.

## Core Features

### 1. Problem Generation Parameters

All parameters are **optional** and can be combined freely:

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `complexity` | int | 1-3 | Difficulty level (1=easy, 2=medium, 3=hard) |
| `grade` | str | "elementary", "middle", "high", "college", "university" | Educational level |
| `math_topic` | str | See below | Primary mathematical concept |
| `problem_family` | str | See below | Problem template category |
| `num_steps` | int | 1-10 | Number of operations to solve (can vary slightly) |
| `seed` | int | any | For reproducible generation |

### 2. Math Topics (MVP)

1. **arithmetic** - Basic operations (add, subtract, multiply, divide)
2. **percentages** - Percentage calculations, increases, decreases
3. **fractions** - Fraction operations
4. **ratios** - Ratio and proportion problems
5. **algebra** - Linear equations, systems of equations, simple expressions
6. **geometry** - Area, perimeter, volume calculations
7. **quadratics** - Quadratic equations and parabolas
8. **derivatives** - Basic derivatives, rates of change
9. **powers_logs** - Exponents, roots, logarithms

**Note:** Not all topics are appropriate for all grades. Generator should handle this gracefully (e.g., derivatives problems "max out" at high school level even if requested for elementary).

### 3. Problem Families (MVP)

1. **sequential_purchase** - Multi-step shopping scenarios with costs, discounts
2. **rate_time** - Distance, speed, time problems with multiple segments
3. **compound_growth** - Interest, investment, growth over multiple periods
4. **multi_person_sharing** - Splitting amounts among people with ratios/percentages
5. **area_perimeter_chain** - Geometry problems with shape transformations

Each family should:

- Support multiple grade levels (some may "max out" at certain grades)
- Have 5-10 template variations for diversity
- Generate coherent problems with realistic values

### 4. Output Format

Problems must follow this exact structure:

```json
{
  "test_id": "math_0001_sequential_purchase",
  "task_type": "multi_step_math",
  "config_name": "purchase_medium_arithmetic",
  "problem": "Sarah goes shopping in Seattle.\n- She buys 5 apples at $1.20 each\n- She buys 3 oranges at $0.80 each with discount of 10%\n- She gets a 15% discount on the total\nHow much does Sarah spend?\n\nPlease solve this problem and provide your final answer.",
  "task_params": {
    "complexity": 2,
    "grade": "middle",
    "math_topic": ["arithmetic", "percentages"],
    "problem_family": "sequential_purchase",
    "num_steps": 5,
    "expected_answer": "$6.94",
    "operations": ["multiply", "multiply", "percentage_decrease", "add", "percentage_decrease"]
  },
}
```

**Key Points:**

- `expected_answer` is a **string** that includes units, formatting, etc.
- Answer can be: numbers, fractions ("3/4"), mixed numbers ("2 1/2"), currency ("$42.50"), time ("3 hours 15 minutes"), equations ("y = 2x + 3"), etc.
- `operations` lists the operations needed (for debugging/analysis)
- NO intermediate steps exposed in output (kept internal for now)

### 5. API Design

#### Single Problem Generation

```python
from math_problem_generator import generate_problem

problem = generate_problem(
    complexity=2,
    grade='middle',
    math_topic='arithmetic',
    problem_family='sequential_purchase',
    num_steps=3,
    seed=42
)
# Returns: dict with structure shown above
```

#### Batch Generation

```python
from math_problem_generator import generate_problems

problems = generate_problems(
    n=100,
    complexity=2,
    grade='middle',
    math_topic='arithmetic',
    problem_family='sequential_purchase',
    num_steps=3,
    avoid_duplicates=True  # Try to avoid exact duplicate problems
)
# Returns: list of dicts
```

#### Optional: Get Available Options

```python
from math_problem_generator import get_available_options

options = get_available_options()
# Returns: {
#   'math_topics': ['arithmetic', 'percentages', ...],
#   'problem_families': ['sequential_purchase', ...],
#   'grades': ['elementary', 'middle', 'high', 'college']
# }
```

## Implementation Requirements

### 6. Problem Quality Constraints

All generated problems MUST:

1. **Have a valid solution** - Verify answer is computable
2. **Use reasonable numbers** - No weird values like $7.3333... for prices
3. **Be coherent** - Names, items, locations should make sense together
4. **Have appropriate precision** - Money: 2 decimals, time: sensible units, etc.
5. **Ensure positive intermediate values** - Avoid negative quantities where inappropriate
6. **Match grade level** - Elementary shouldn't have calculus, etc.

### 7. Randomization Requirements

- **Deterministic from seed** - Same seed → same problem
- **Template selection** - Randomly choose from available templates
- **Value generation** - Randomize all numbers, names, items, locations
- **Duplicate avoidance** - In batch mode, try to generate unique problems (different numbers/contexts)

### 8. Natural Language Templates

Each problem family should have **5-10 variations** initially:

**Example for sequential_purchase:**

1. "Shopping at store" template
2. "Online order" template
3. "Grocery shopping with list" template
4. "Electronics purchase" template
5. "Clothing store with sale" template

Templates should use:

- `faker` for realistic data (cities, company names, etc.)
- `names` for person names
- Contextually appropriate items (apples in grocery, laptops in electronics, etc.)

### 9. Package Structure

```
math_problem_generator/
├── __init__.py
├── generator.py          # Main API (generate_problem, generate_problems)
├── families/
│   ├── __init__.py
│   ├── sequential_purchase.py
│   ├── rate_time.py
│   ├── compound_growth.py
│   ├── multi_person_sharing.py
│   └── area_perimeter_chain.py
├── templates/
│   └── [template definitions or inline in families]
├── utils.py              # Helper functions (rounding, validation, etc.)
└── constants.py          # Available options, mappings
```

## Success Criteria

### MVP Success (Phase 1)

- ✅ All 5 problem families implemented
- ✅ All 9 math topics supported (where appropriate)
- ✅ Single and batch generation working
- ✅ Output format matches gol-eval structure
- ✅ Seed-based reproducibility works
- ✅ 5+ template variations per family
- ✅ All generated problems have valid solutions
- ✅ No duplicate problems in batch (when possible)

### Quality Checks

- Generated problems are grammatically correct
- Numbers are realistic and appropriate for context
- Answers are precisely correct
- Grade/topic/family combinations work sensibly
- Complexity scaling is noticeable (easy vs hard)

## Example Problems by Family

### 1. Sequential Purchase (Elementary + Arithmetic)

```
Emily goes shopping in Portland.
- She buys 4 notebooks at $2.50 each
- She buys 2 pencil cases at $3.00 each
How much does Emily spend?

Expected answer: "$16.00"
Operations: multiply, multiply, add
Steps: 3
```

### 2. Rate/Time (Middle + Arithmetic)

```
James drives from Boston to Hartford.
- He drives 80 miles at 40 mph
- He stops for lunch for 1 hour
- He drives 60 miles at 30 mph
How long does the entire trip take?

Expected answer: "5 hours"
Operations: divide, add, divide, add
Steps: 4
```

### 3. Compound Growth (High + Percentages)

```
Maria invests $1000 in a savings account.
- Year 1: earns 5% interest
- Year 2: earns 6% interest
- At end of year 2, she withdraws $200
How much money does Maria have?

Expected answer: "$915.00"
Operations: percentage_increase, percentage_increase, subtract
Steps: 3
```

### 4. Multi-Person Sharing (Middle + Ratios)

```
Three friends split a restaurant bill of $150 in the ratio 2:3:5.
How much does each person pay?

Expected answer: "Person 1: $30.00, Person 2: $45.00, Person 3: $75.00"
Operations: ratio_split
Steps: 2
```

### 5. Area/Perimeter Chain (High + Geometry)

```
A rectangular garden has length 15m and width 10m.
- Calculate the area
- If we create a square with the same area, what is the side length?
- What is the perimeter of this square?

Expected answer: "Side length: 12.25m, Perimeter: 49.0m"
Operations: multiply, sqrt, multiply
Steps: 3
```

## Non-Goals (Out of Scope for MVP)

- ❌ Answer verification/parsing of LLM responses
- ❌ Integration with gol-eval (this is standalone)
- ❌ Intermediate step tracking/verification
- ❌ GUI or web interface
- ❌ Problem difficulty estimation beyond explicit complexity parameter
- ❌ Multi-language support (English only for MVP)
- ❌ Image-based problems (geometry diagrams, etc.)

## Future Enhancements (Post-MVP)

- More problem families (mixing liquids, work problems, probability)
- More template variations per family (50+ templates)
- Advanced math topics (trigonometry, statistics, matrices)
- Problem difficulty auto-tuning
- Export to various formats (LaTeX, PDF, etc.)
- Integration hooks for gol-eval

## Development Notes

- Start with `sequential_purchase` family to validate architecture
- Test with various parameter combinations
- Ensure answer validation logic is solid
- Document edge cases (division by zero, etc.)
- Keep templates simple initially, expand later
- Focus on correctness over diversity in MVP

---

**Ready for implementation!** This specification should be sufficient for a coding agent to build the MVP.
