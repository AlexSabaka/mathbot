# Sandbox solution recipes

Copy-paste-able solution patterns. The sandbox surface is documented in SPEC.md §9 and CLAUDE.md "Solution sandbox reference"; this file is the practical "here's how you actually solve a quadratic" companion.

## What's available without import

```text
# builtins
abs round str int float min max sum pow len list range
sorted enumerate zip map filter any all

# math primitives (surfaced top-level)
math pi e
sqrt exp
sin cos tan asin acos atan atan2
log log2 log10
floor ceil
factorial comb perm
radians degrees
gcd lcm

# numeric / locale
Decimal number_to_words

# symbolic + statistical (namespaces)
sympy stats        # stats = scipy.stats

# pint backbone
ureg Q_ get_pint_unit
```

`from X import Y` works at runtime, but prefer the existing globals. If you need something not listed, the right move is to add it to `safe_globals` in `src/solution_evaluator.py`, not to import per-template.

## Recipe 1: simple arithmetic with formatted answer

```yaml
variables:
  price:    { type: money, min: 5, max: 50, step: 0.25 }
  quantity: { type: integer, min: 2, max: 10 }
  Answer:   { type: money }

template: |
  Sarah buys {{quantity}} items at {{price_formatted}} each. What does she pay?

solution: |
  Answer = price * quantity
```

The formatter handles the `$` and 2-decimal display from `Answer.type: money`.

## Recipe 2: pint dimensional arithmetic

For problems where the answer comes from combining quantities with different units. SPEC.md §8 + §9.2.

```yaml
metadata:
  unit_system: metric
variables:
  density: { type: density, min: 500, max: 2000 }       # kg/m³ for metric
  volume:  { type: volume, min: 1, max: 10 }            # liters for metric
  Answer:  { type: weight }                              # kg for metric

solution: |
  density_q = Q_(density, get_pint_unit('density', 'metric'))   # kg/m³
  volume_q  = Q_(volume,  get_pint_unit('volume',  'metric'))   # L
  Answer = density_q * volume_q
  # Carries kg·L/m³ ≡ kg dimensionally; formatter prints "X.XX kg"
```

The Quantity is unwrapped automatically by `quantity_to_canonical_magnitude`. No manual `.to('kg')` needed when the Answer's `(type, system)` resolves to a compatible canonical unit.

When you need an explicit unit conversion (e.g. m/s → km/h):

```yaml
variables:
  velocity: { type: decimal, unit: 'meter / second', min: 5, max: 25 }
  Answer:   { type: decimal, unit: 'kilometer / hour' }

solution: |
  v_q = Q_(velocity, velocity_unit)
  Answer = v_q.to('kilometer / hour').magnitude
```

## Recipe 3: quadratic with root rejection

For P-A3-style problems: set up a quadratic, solve, reject the non-physical root.

```yaml
variables:
  width_increment: { type: integer, min: 2, max: 8 }     # length = width + increment
  area:            { type: integer, choices: [70, 96, 120, 154] }
  Answer:          { type: integer }                      # the positive root (width)

solution: |
  # length = width + width_increment
  # area = width * (width + width_increment)
  # → width² + width_increment*width - area = 0
  
  a, b, c = 1, width_increment, -area
  discriminant = b*b - 4*a*c
  root_pos = (-b + sqrt(discriminant)) / (2*a)
  root_neg = (-b - sqrt(discriminant)) / (2*a)
  
  # Reject the negative root (non-physical for a width)
  Answer = int(round(root_pos))
```

For irrational roots (hard tier), use sympy and return an exact form or a 2-dp rounded value as a string. `sympy.simplify()` is expensive — call it once at the end, not per-step (TECHDEBT TD-2.2).

## Recipe 4: linear-system solve (P-A1)

Two unknowns from two purchase combinations.

```yaml
variables:
  qty_a1:  { type: integer, min: 2, max: 5 }
  qty_b1:  { type: integer, min: 2, max: 5 }
  qty_a2:  { type: integer, min: 2, max: 5 }
  qty_b2:  { type: integer, min: 2, max: 5 }
  price_a: { type: money, min: 1, max: 10, step: 0.25 }   # ground truth
  price_b: { type: money, min: 1, max: 10, step: 0.25 }
  Answer1: { type: money }   # price_a (what the student solves for)
  Answer2: { type: money }

template: |
  {% set total1 = (qty_a1 * price_a + qty_b1 * price_b) | round(2) %}
  {% set total2 = (qty_a2 * price_a + qty_b2 * price_b) | round(2) %}
  A school orders {{qty_a1}} calculators and {{qty_b1}} protractors for ${{total1}},
  and {{qty_a2}} calculators and {{qty_b2}} protractors for ${{total2}}.
  Find each price.

solution: |
  # Solve via sympy to handle the system cleanly.
  a, b = sympy.symbols('a b', positive=True)
  total1 = qty_a1 * price_a + qty_b1 * price_b
  total2 = qty_a2 * price_a + qty_b2 * price_b
  sol = sympy.solve([qty_a1 * a + qty_b1 * b - total1,
                     qty_a2 * a + qty_b2 * b - total2], [a, b])
  Answer1 = float(sol[a])
  Answer2 = float(sol[b])
```

Note the pattern: ground-truth `price_a` and `price_b` are generated; the totals are computed in the template (so they appear in the problem text); the solution rederives the prices via sympy as if the student didn't know them. This is the right discipline — the solver pretends not to know what the generator knows.

**Parameter constraints to keep arithmetic clean:** choose coefficient quantities such that the determinant `qty_a1 * qty_b2 - qty_a2 * qty_b1` is in `{±1, ±2, ±3}`. Otherwise prices come out fractional in unfortunate ways. The proposal entry for P-A1 spells this out.

## Recipe 5: working-backwards / inverse problem

Find the input given the output. P-A2 / P-SP1 / P-SP4 territory.

```yaml
variables:
  spent_fraction: { type: choice, choices: ["1/3", "1/4", "2/5", "3/8"] }
  remaining_after_extra: { type: money, min: 10, max: 50, step: 0.50 }
  extra_spent: { type: money, min: 5, max: 20, step: 0.50 }
  Answer: { type: money }

template: |
  Maria spent {{spent_fraction}} of her money on a book, then spent
  {{extra_spent_formatted}} more on a notebook. She has {{remaining_after_extra_formatted}} left.
  How much did she start with?

solution: |
  # Working backwards:
  # initial - (spent_fraction * initial) - extra_spent = remaining_after_extra
  # initial * (1 - spent_fraction) = remaining_after_extra + extra_spent
  # initial = (remaining_after_extra + extra_spent) / (1 - spent_fraction)
  
  num, den = spent_fraction.split('/')
  fraction = int(num) / int(den)
  Answer = (remaining_after_extra + extra_spent) / (1 - fraction)
```

If you want the spent fraction as a sympy `Rational` for exactness:

```python
fraction = sympy.Rational(int(num), int(den))
Answer = float((remaining_after_extra + extra_spent) / (1 - fraction))
```

## Recipe 6: bar-model invariant (P-SP1 constant-total)

The Singapore "model method" — identify the conservation law before computing.

```yaml
variables:
  ratio_a: { type: integer, choices: [3, 4, 5] }
  ratio_b: { type: integer, choices: [2, 3] }
  transfer: { type: integer, choices: [12, 18, 24, 30] }
  Answer1: { type: integer }       # Anna's original
  Answer2: { type: integer }       # Ben's original

template: |
  {# Constraint: after transfer the ratio is 1:1, meaning Anna and Ben end equal. #}
  {# Total is conserved: anna + ben = const. #}
  {# anna_initial = ratio_a * unit; ben_initial = ratio_b * unit #}
  {# anna_initial - transfer = ben_initial + transfer #}
  {# → (ratio_a - ratio_b) * unit = 2 * transfer #}
  {# → unit = 2 * transfer / (ratio_a - ratio_b) #}
  {% set unit_value = (2 * transfer) // (ratio_a - ratio_b) %}
  {% set anna_initial = ratio_a * unit_value %}
  {% set ben_initial = ratio_b * unit_value %}
  Anna and Ben have stickers in ratio {{ratio_a}}:{{ratio_b}}. After Anna gives
  {{transfer}} stickers to Ben, they have the same number. How many did each have originally?

solution: |
  unit_value = (2 * transfer) // (ratio_a - ratio_b)
  Answer1 = ratio_a * unit_value
  Answer2 = ratio_b * unit_value
```

**Parameter constraint to make this work:** `(2 * transfer) % (ratio_a - ratio_b) == 0`, otherwise `unit_value` isn't an integer and the problem doesn't have a clean answer. Constrain `transfer` choices to be divisible by `(ratio_a - ratio_b)`.

This is the kind of constraint where `choices: [...]` for `transfer` is better than `min`/`max` — you can hand-pick values that always produce integer answers.

## Recipe 7: multi-stage state tracking (P-SP2 with tier crossing)

```yaml
variables:
  budget: { type: money, choices: [80, 100, 120, 150] }
  shirt_price: { type: money, choices: [12, 15, 18] }
  shirt_count: { type: integer, choices: [3, 4] }
  jeans_price: { type: money, choices: [30, 34, 40] }
  belt_price: { type: money, choices: [10, 12, 15] }
  discount_threshold: { type: money, choices: [80, 100] }
  discount_rate: { type: percentage, choices: [8, 10, 12] }
  Answer1: { type: money }   # final paid
  Answer2: { type: money }   # remaining budget

template: |
  A shopper has {{budget_formatted}}.
  Stage 1: buys {{shirt_count}} shirts at {{shirt_price_formatted}} each.
  Stage 2: with remaining budget, buys jeans at {{jeans_price_formatted}}, then a belt at {{belt_price_formatted}}.
  Stage 3: at checkout, a {{discount_rate}}% discount applies if the pre-discount total exceeds {{discount_threshold_formatted}}.
  How much does she pay, and how much does she have left?

solution: |
  pre_discount_total = shirt_count * shirt_price + jeans_price + belt_price
  if pre_discount_total > discount_threshold:
      paid = pre_discount_total * (1 - discount_rate / 100)
  else:
      paid = pre_discount_total
  Answer1 = round(paid, 2)
  Answer2 = round(budget - paid, 2)
```

The tier crossing is the conditional discount. Without it, this is a flat "buy A, buy B, buy C, total" — the GSM8K-saturated antipattern the proposal explicitly forbids.

## Recipe 8: compound growth with variable rates (P-SP4)

```yaml
variables:
  principal: { type: money, choices: [1000, 2500, 5000, 10000] }
  rate1: { type: percentage, min: 3, max: 8 }
  rate2: { type: percentage, min: 3, max: 8 }
  rate3: { type: percentage, min: -2, max: 5 }   # Year 3 may be negative
  Answer: { type: money }

template: |
  An investment of {{principal_formatted}} grows by {{rate1}}% in year 1,
  {{rate2}}% in year 2, and {{'gains' if rate3 > 0 else 'loses'}} {{rate3 | abs}}% in year 3.
  What is the value at the end of year 3?

solution: |
  value = principal * (1 + rate1/100) * (1 + rate2/100) * (1 + rate3/100)
  Answer = round(value, 2)
```

The negative-rate year is the structural twist — pure compounding with constant positive rates is the GSM8K-saturated pattern. Per-period varying rates exercise the "track state across N stages" reasoning.

## Recipe 9: rate combination (P-SP3 work-rate)

```yaml
variables:
  time_a: { type: integer, choices: [4, 6, 8, 12] }       # pipe A fills tank in `time_a` hours
  time_b: { type: integer, choices: [3, 4, 6, 9] }
  time_c: { type: integer, choices: [12, 18, 24] }        # pipe C drains
  Answer: { type: time }                                    # combined fill time

template: |
  Pipe A fills a tank in {{time_a}} hours, pipe B in {{time_b}} hours.
  Pipe C drains it in {{time_c}} hours. With all three open, how long to fill from empty?

solution: |
  # Combined rate (in tanks per hour) = 1/time_a + 1/time_b - 1/time_c
  combined_rate = sympy.Rational(1, time_a) + sympy.Rational(1, time_b) - sympy.Rational(1, time_c)
  Answer = float(1 / combined_rate)
```

Using `sympy.Rational` keeps the fractions exact through the addition; the final division produces a clean float for `time` formatting. Constrain `choices` so the LCM of the three reciprocals is a small integer — e.g. all from `{4, 6, 8, 12}` — for clean answers.

## Recipe 10: probability with conditional structure (P-S2)

```yaml
variables:
  prevalence: { type: percentage, choices: [1, 2, 4, 5] }
  sensitivity: { type: percentage, choices: [92, 95, 97, 99] }
  specificity: { type: percentage, choices: [90, 95, 97, 98] }
  Answer: { type: percentage }   # P(disease | positive test)

template: |
  In a population, {{prevalence}}% have a disease. A test correctly identifies
  {{sensitivity}}% of true cases (sensitivity) and correctly clears {{specificity}}%
  of healthy people (specificity). If a person tests positive, what is the probability
  they actually have the disease?

solution: |
  # Bayes: P(D|+) = P(+|D) * P(D) / P(+)
  # P(+) = P(+|D) * P(D) + P(+|~D) * P(~D)
  p_d = prevalence / 100
  p_pos_given_d = sensitivity / 100
  p_pos_given_not_d = 1 - specificity / 100
  p_pos = p_pos_given_d * p_d + p_pos_given_not_d * (1 - p_d)
  posterior = p_pos_given_d * p_d / p_pos
  Answer = round(posterior * 100, 1)
```

The base-rate-fallacy framing (low prevalence, high sensitivity, surprisingly low posterior) is the structural twist that GSM8K never tests.

## Recipe 11: scipy.stats for inferential problems

```yaml
# Normal-distribution z-test, one-sample.
variables:
  sample_mean: { type: decimal, min: 102, max: 108, step: 0.5 }
  population_mean: { type: integer, choices: [100] }
  population_sd: { type: decimal, choices: [12, 15, 18] }
  sample_size: { type: integer, choices: [25, 36, 49, 64] }
  Answer: { type: decimal }   # z-score

solution: |
  se = population_sd / sqrt(sample_size)
  z = (sample_mean - population_mean) / se
  Answer = round(z, 2)
  # For a p-value: stats.norm.cdf(-abs(z)) * 2 (two-tailed)
```

For binomial / Poisson / chi-square, use `stats.binom`, `stats.poisson`, `stats.chi2` directly. They're pure-Python, no I/O, safe in the sandbox.

## Multi-answer pipe-join

When the problem asks for multiple answers, declare `Answer1`, `Answer2`, ... (no `Answer`). The CLI joins formatted values with `" | "` for `expected_answer`:

```yaml
variables:
  Answer1: { type: money }       # final paid
  Answer2: { type: integer }     # items purchased
  Answer3: { type: money }       # remaining budget

solution: |
  Answer1 = total_paid
  Answer2 = num_items
  Answer3 = budget - total_paid

tests:
  - seed: 12345
    expected:
      answer: "$73.50 | 5 | $26.50"
```

The fixture has a single `answer:` field with pipes; legacy `answer1:`, `answer2:` keys are ignored.

## Things to avoid

- **Don't `import` per-template** — use sandbox globals. If something's missing, add it to `safe_globals` in `src/solution_evaluator.py`.
- **Don't call `sympy.simplify()` in a loop** — worst-case cubic complexity; once at the end is fine.
- **Don't mix `sympy.Symbol` with regular floats casually** — expression trees balloon. If you start symbolic, stay symbolic until the final `float(...)`.
- **Don't compute display strings in solution** — the formatter handles unit suffixes and decimal places. Just assign the magnitude.
- **Don't seed `random` inside solution code** — the variable-generation seeding is upstream; introducing more entropy inside the solution breaks reproducibility.
