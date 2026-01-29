# Math Problem Template Reference

> **Purpose**: This document provides standardized conventions for procedurally generating math word problems across all grade levels (K1-K12).

---

## 1. Template Notation & Syntax

### Basic Syntax
- Variables denoted with `{variable_name}` or `{{variable_name}}`
- Constraints for each variable noted in comments
- `{variable:constraint}` — parameter with generation constraint
- `[option_a | option_b]` — random choice from options
- Comments in `<!-- -->` describe parameter constraints

### Notation Key
- `∈ [a, b]` — Integer range inclusive
- `∈ {x, y, z}` — Set of allowed values
- `<`, `>`, `≤`, `≥` — Relational constraints
- `\{0}` — Exclude zero
- `gcd(a, b) = 1` — Coprime constraint

---

## 2. Variable Types & Naming Conventions

### Standard Variable Types

| Variable Type | Syntax | Description | Example Values |
|---------------|--------|-------------|----------------|
| **Names** | `{{name}}`, `{{name_1}}` | Person's name | Sarah, Jake, Emma, Carlos |
| **Pronouns** | `{{pronoun}}`, `{{possessive}}` | Matching pronouns | he/she, his/her, their |
| **Whole Numbers** | `{{number}}`, `{{num_a}}` | Integers with constraints | 5, 12, 100 |
| **Decimals** | `{{decimal}}` | Decimal numbers | 3.75, 0.025, 12.5 |
| **Fractions** | `{{fraction}}` | Fractions | 2/3, 3/4, 5/8 |
| **Mixed Numbers** | `{{mixed_number}}` | Mixed numbers | 2 3/4, 1 5/8 |
| **Items** | `{{item}}`, `{{item_plural}}` | Objects (singular/plural) | book/books, apple/apples |
| **Places** | `{{place}}`, `{{city}}` | Location names | library, Chicago, park |
| **Units** | `{{unit}}` | Measurement unit | cm, meters, inches |
| **Variables** | `{{variable}}` | Algebraic variable | x, n, h, w |
| **Coordinates** | `{{x_coord}}`, `{{y_coord}}` | Coordinate values | 2, -3, 5 |
| **Shapes** | `{{shape}}`, `{{shape_3d}}` | Geometric shapes | circle, triangle, sphere |
| **Angles** | `{{angle}}` | Angle value | 45°, 90°, 120° |

### Naming Patterns
- `num_*` — Numerical values (e.g., `num_items`, `num_students`)
- `*_singular` / `*_plural` — Object names with grammatical forms
- `*_a`, `*_b`, `*_c` — Multiple similar variables for comparison
- `count_*` — Count values (e.g., `count_apples`)
- Descriptive names for geometry: `{{base}}`, `{{height}}`, `{{radius}}`
- Indexed variables: `{{a1}}`, `{{a2}}`, `{{a3}}` or `{{x_1}}`, `{{x_2}}`

---

## 3. Parameter Ranges & Value Libraries

### Number Ranges by Difficulty

| Difficulty | Whole Numbers | Fractions (denom) | Decimals (places) | Operations |
|------------|---------------|-------------------|-------------------|------------|
| **Easy**   | 1-100         | 2-10              | 1                 | Single operation |
| **Medium** | 10-1,000      | 4-12              | 2                 | Two operations |
| **Hard**   | 100-10,000    | 6-20              | 2-3               | Multi-step |

### Specific Parameter Types

| Type | Range/Values | Notes |
|------|--------------|-------|
| Small integers | 1-20 | For basic operations |
| Medium integers | 20-100 | For factors, multiples, GCD/LCM |
| Large integers | 100-1000 | For long division, real-world problems |
| Percentages | 1-100 | Common: 10, 20, 25, 50, 75 |
| Money | $0.01-$1000.00 | Always 2 decimal places |
| Coordinates | -10 to 10 | Keep reasonable for graphing |
| Temperatures | -20°F to 100°F | Realistic ranges |
| Algebraic coefficients | -20 to 20 | Integer coefficients |
| Probabilities/ratios | 0 to 1 | For probability problems |
| Special angles | 0°, 30°, 45°, 60°, 90°, 120° | Standard angles |
| Matrix dimensions | 2-4 | Keep computations reasonable |
| Integration bounds | -2 to 5 | Keep calculations tractable |
| Polynomial degrees | 2 to 4 | Higher gets tedious |

### Value Libraries

**Names** (gender-neutral):
```
["Alex", "Jordan", "Sam", "Taylor", "Morgan", "Casey", "Riley", "Quinn", 
 "Jamie", "Drew", "Avery", "Blake", "Cameron", "Dakota", "Emery", "Parker"]
```

**Traditional Names**:
```
["Emma", "Liam", "Sophia", "Noah", "Olivia", "Aiden", "Mia", "Lucas", 
 "Sarah", "Jake", "Carlos"]
```

**Countable Objects**:
```
["marbles", "stickers", "cards", "coins", "stamps", "books", "pencils", 
 "cookies", "apples", "beads", "toys", "flowers"]
```

**Measurable Items**:
```
["ribbon", "rope", "string", "fabric", "wire"]
```

**Food Portions**:
```
["pizza", "cake", "pie", "chocolate bar"]
```

**K-2 Objects**:
```
Animals: ["dog", "cat", "bird", "fish", "rabbit", "turtle", "hamster"]
Foods: ["apple", "banana", "cookie", "candy", "grape", "orange"]
Toys: ["ball", "doll", "car", "block", "puzzle", "crayon"]
Colors: ["red", "blue", "green", "yellow", "orange", "purple", "pink"]
Shapes: ["circle", "square", "triangle", "rectangle", "star", "heart"]
```

**Locations**:
```
Places: ["library", "school", "park", "bakery", "farm", "store", "garden", 
         "theater", "stadium"]
Cities: ["Denver", "Chicago", "Miami", "Seattle", "Phoenix", "Boston", 
         "Atlanta", "Portland", "Dallas", "Minneapolis"]
```

**Units of Measurement**:
```
Length: cm, m, km, inches, feet, yards, miles
Weight: g, kg, pounds, ounces
Volume: mL, L, gallons, cubic cm, cubic m
Time: seconds, minutes, hours, days
```

### Constraint Format Examples
```
{a:10-99}                  → random integer from 10 to 99
{d:2|5|10}                 → random choice: 2, 5, or 10
{n:even:10-50}             → random even number from 10 to 50
{a:multiple_of_3:12-60}    → random multiple of 3 from 12 to 60
```

---

## 4. Difficulty Scaling Guidelines

### Complexity Progression

| Level | Numbers | Steps | Concepts | Context |
|-------|---------|-------|----------|---------|
| **Easy** | 1-100, friendly | Single operation | Concrete objects, direct application | Clear visual support |
| **Medium** | 10-1000, some unfriendly | 2-3 steps | Abstract concepts, formula manipulation | Basic word problems |
| **Hard** | 100-10000+ | Multi-step | Synthesis, proof elements, strategy selection | Real-world contexts |

### Scaling Strategies

Increase difficulty by:
- Using larger numbers or unfriendly values
- Adding more solution steps
- Combining multiple mathematical concepts
- Including real-world context and reasoning
- Adding nested functions or expressions
- Requiring strategy selection

---

## 5. Validation Rules & Constraints

### Mathematical Constraints

1. **Subtraction**: Ensure `number1 > number2` to avoid negative results (unless intended)
2. **Division**: Ensure clean division or specify remainder handling; avoid division by zero
3. **Fractions**:
   - For proper fractions: `numerator ≤ denominator`
   - Keep denominators ≤ 12 for easy problems
   - Ensure LCD calculations are grade-appropriate
4. **Geometry**:
   - Triangle Inequality: For sides a, b, c: `a + b > c`, `b + c > a`, `a + c > b`
   - Triangle angles: Must sum to 180°
   - Quadrilateral angles: Must sum to 360°
   - Keep dimensions reasonable for grade level
5. **Decimals**: Avoid results with more than 3 decimal places
6. **Money**: Use realistic prices and amounts, always 2 decimal places
7. **Domain Checks**: Ensure denominators ≠ 0, square roots of non-negatives, etc.
8. **Matrices**: Ensure nice determinants; if invertible matrix needed, ensure det ≠ 0

### Pre-Generation Validation
- Validate constraints before inserting values
- Ensure parameters yield real, finite answers
- Avoid trivial cases where answer is obviously 0 or 1
- For coprime requirements: `gcd(a, b) = 1`

### Post-Generation Validation
- Verify answer is "clean" (integer or simple fraction when appropriate)
- Validate generated problems produce grade-appropriate answers
- Regenerate if constraints produce invalid results
- Check unit consistency within problem

---

## 6. Natural Language Generation

### Writing Style Tips
- Use pronouns after first mention to vary sentence structure
- Include context (names, scenarios) to make problems engaging
- Vary action verbs: has, gets, gives, takes, finds, loses, counts, buys, sells
- Include diverse names and scenarios for inclusivity
- Ensure unit consistency throughout the problem

### Context Themes

Rotate through varied real-world contexts:
- **Food/Cooking**: recipes, sharing pizza/cookies, grocery shopping
- **Sports**: scores, statistics, team data
- **Money**: shopping, savings, discounts, sales
- **Travel**: distance, time, maps, planning
- **Nature**: gardens, animals, weather patterns
- **School**: grades, supplies, class data, schedules
- **Games**: points, cards, dice, strategies
- **Construction**: measurements, materials, planning
- **Science**: experiments, data collection, analysis
- **Physics**: motion, forces, energy
- **Economics**: costs, revenue, profit
- **Biology**: population, decay, growth

---

## 7. Answer Generation & Validation

### Answer Requirements
- Most answers can be computed programmatically
- Word problems require template-specific answer generators
- Multiple valid answers should be handled where applicable
- Answers should be grade-appropriate (avoid complex calculations for easy/medium)

### Answer Key Components
For each template, generate:
1. **Numeric answer(s)** with proper formatting
2. **Step-by-step solution** (optional, for verification)
3. **Common misconception flags** (optional, for educational use)

### Format Standards
- **Money**: "$42.50" (always 2 decimals)
- **Fractions**: "3/4" or "2 3/4" (mixed numbers)
- **Coordinates**: "(3, -2)"
- **Angles**: "45°"
- **Equations**: "y = 2x + 3"
- **Time**: "3 hours 15 minutes"

---

## 8. Implementation Notes

### General Principles
1. **Ensure Solvability**: Verify parameters yield valid, computable answers
2. **Avoid Trivial Cases**: Don't generate problems where answer is obviously 0 or 1
3. **Maintain Consistency**: All aspects of problem should be internally coherent
4. **Unit Consistency**: Use consistent units within a problem
5. **Context Variety**: Rotate through different scenarios for engagement
6. **Real-World Context**: Add application wrappers where appropriate

### Data Type Conventions

| Parameter Type | Format | Example |
|---------------|--------|---------|
| Integers | `{{length}}` | 15 |
| Fractions | `{{num}}/{{den}}` | 3/4 |
| Coordinates | `({{x}}, {{y}})` | (3, -2) |
| Angles | `{{angle}}°` | 45° |
| Expressions | `({{coeff}}x + {{const}})` | (2x + 5) |

### Constraint Documentation Format
```
<!-- constraint_description -->
```

Common constraint types:
- Value ranges: `[min, max]`
- Exclusions: `exclude value`
- Dependencies: `x depends on y`
- Validity conditions: `must satisfy condition`

---

## 9. References

This template reference supports the K1-K12 problem template files. See individual grade-level documents (K1_PROBLEMS.md through K12_PROBLEMS.md) for specific problem examples at each grade level.
