# 9th Grade Mathematics Problem Templates

## 1. Numbers

### 1.1 Operations with Integers

**Easy**
```
Calculate: {{a}} + {{b}} - {{c}}
# Constraints: a, b, c ∈ [-50, 50]
# Example: Calculate: -12 + 25 - 8
```

**Medium**
```
Evaluate: ({{a}} × {{b}}) ÷ {{c}} + {{d}}
# Constraints: a, b ∈ [-20, 20]; c divides (a × b) evenly; d ∈ [-30, 30]
# Example: Evaluate: (-6 × 4) ÷ 8 + 15
```

**Hard**
```
Simplify: [{{a}} - ({{b}} × {{c}})] ÷ {{d}} + {{e}} × {{f}}
# Constraints: a ∈ [-100, 100]; b, c ∈ [-10, 10]; d divides [a - (b × c)]; e, f ∈ [-15, 15]
# Example: Simplify: [48 - (-3 × 4)] ÷ 6 + (-2) × 5
```

### 1.2 Convert Decimal to Fraction

**Easy**
```
Convert {{decimal}} to a fraction in lowest terms.
# Constraints: decimal is terminating with 1-2 decimal places (e.g., 0.25, 0.8, 0.75)
# Example: Convert 0.625 to a fraction in lowest terms.
```

**Medium**
```
Express {{decimal}} as a fraction in simplest form.
# Constraints: decimal is terminating with 2-3 decimal places (e.g., 0.125, 0.375, 0.0625)
# Example: Express 0.4375 to a fraction in simplest form.
```

**Hard**
```
Convert the repeating decimal 0.{{non_repeat}}{{repeat_block}}̄ to a fraction.
# Constraints: non_repeat is 0-2 digits; repeat_block is 1-3 digits (overline indicates repeating)
# Example: Convert the repeating decimal 0.8̄3̄ to a fraction.
```

### 1.3 Square Roots

**Easy**
```
Find √{{perfect_square}}.
# Constraints: perfect_square ∈ {1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225}
# Example: Find √144.
```

**Medium**
```
Simplify √{{n}} where {{n}} = {{a}}² × {{b}}.
# Constraints: a ∈ [2, 12]; b is square-free (e.g., 2, 3, 5, 6, 7, 10, 11)
# Example: Simplify √72.
```

**Hard**
```
Simplify: {{a}}√{{b}} + {{c}}√{{d}} - {{e}}√{{f}}
# Constraints: b, d, f share a common radicand after simplification; a, c, e ∈ [1, 10]
# Example: Simplify: 3√50 + 2√18 - 4√8
```

### 1.4 Cube Roots

**Easy**
```
Find ∛{{perfect_cube}}.
# Constraints: perfect_cube ∈ {1, 8, 27, 64, 125, 216, 343, 512, 729, 1000}
# Example: Find ∛216.
```

**Medium**
```
Simplify ∛{{n}} where {{n}} = {{a}}³ × {{b}}.
# Constraints: a ∈ [2, 6]; b is cube-free
# Example: Simplify ∛250.
```

### 1.5 Rational vs Irrational Numbers

**Easy**
```
Classify each number as rational or irrational: {{a}}, √{{b}}, {{c}}/{{d}}, π
# Constraints: a is terminating/repeating decimal; b is non-perfect square; c, d ∈ integers
# Example: Classify each number as rational or irrational: 0.333..., √5, 7/8, π
```

**Medium**
```
Which of the following is irrational? 
A) √{{perfect_square}}  B) {{fraction}}  C) √{{non_perfect}}  D) {{terminating_decimal}}
# Constraints: perfect_square is a perfect square; non_perfect is not
# Example: Which is irrational? A) √49  B) 5/6  C) √13  D) 0.125
```

### 1.6 Adding/Subtracting Rational Numbers with Negatives

**Easy**
```
Calculate: {{a}}/{{b}} + ({{c}}/{{d}})
# Constraints: a, c ∈ [-20, 20]; b, d ∈ [2, 12]; include at least one negative
# Example: Calculate: 3/4 + (-5/6)
```

**Medium**
```
Simplify: {{a}}/{{b}} - {{c}}/{{d}} + {{e}}/{{f}}
# Constraints: denominators share common factors for LCD calculation practice
# Example: Simplify: -2/3 - 5/6 + 7/12
```

---

## 2. Expressions

### 2.1 Evaluating Expressions

**Easy**
```
Evaluate {{a}}x + {{b}} when x = {{x_val}}.
# Constraints: a ∈ [-10, 10]; b ∈ [-20, 20]; x_val ∈ [-5, 5]
# Example: Evaluate 3x + 7 when x = -2.
```

**Medium**
```
Evaluate {{a}}x² - {{b}}x + {{c}} when x = {{x_val}}.
# Constraints: a ∈ [1, 5]; b ∈ [-10, 10]; c ∈ [-15, 15]; x_val ∈ [-4, 4]
# Example: Evaluate 2x² - 5x + 3 when x = -3.
```

**Hard**
```
Evaluate ({{a}}x + {{b}}y) / ({{c}}x - {{d}}y) when x = {{x_val}} and y = {{y_val}}.
# Constraints: ensure denominator ≠ 0; result is integer or simple fraction
# Example: Evaluate (3x + 2y) / (x - 4y) when x = 6 and y = -3.
```

### 2.2 Distributive Property

**Easy**
```
Expand: {{a}}({{b}}x + {{c}})
# Constraints: a ∈ [-10, 10]; b ∈ [1, 10]; c ∈ [-15, 15]
# Example: Expand: 4(3x + 5)
```

**Medium**
```
Expand and simplify: {{a}}({{b}}x - {{c}}) + {{d}}({{e}}x + {{f}})
# Constraints: all coefficients ∈ [-10, 10], non-zero
# Example: Expand and simplify: 3(2x - 4) + 5(x + 2)
```

**Hard**
```
Expand and simplify: {{a}}({{b}}x² + {{c}}x - {{d}}) - {{e}}({{f}}x² - {{g}}x + {{h}})
# Constraints: coefficients ∈ [-8, 8], non-zero
# Example: Expand and simplify: 2(3x² + 4x - 5) - 3(x² - 2x + 1)
```

### 2.3 Rational Expressions

**Easy**
```
Simplify: {{a}}x / {{b}}x
# Constraints: a, b ∈ [2, 20]; x ≠ 0
# Example: Simplify: 12x / 4x
```

**Medium**
```
Simplify: ({{a}}x² - {{b}}x) / ({{c}}x)
# Constraints: c divides both a and b; x ≠ 0
# Example: Simplify: (6x² - 9x) / (3x)
```

**Hard**
```
Simplify: (x² - {{a}}²) / (x² + {{b}}x - {{c}}) where {{c}} = {{a}} × ({{a}} + {{b}})
# Constraints: numerator factors as (x-a)(x+a); denominator factors with (x+a) term
# Example: Simplify: (x² - 9) / (x² + 5x + 6)
```

### 2.4 Adding/Subtracting Rational Expressions

**Easy**
```
Add: {{a}}/x + {{b}}/x
# Constraints: a, b ∈ [-15, 15]
# Example: Add: 5/x + 3/x
```

**Medium**
```
Subtract: {{a}}/(x + {{b}}) - {{c}}/(x + {{d}})
# Constraints: b ≠ d; a, c ∈ [1, 10]; b, d ∈ [-8, 8]
# Example: Subtract: 3/(x + 2) - 5/(x - 1)
```

**Hard**
```
Simplify: {{a}}/(x - {{b}}) + {{c}}/(x + {{b}}) - {{d}}/(x² - {b²})
# Constraints: b² = b × b; expressions share common denominator (x² - b²)
# Example: Simplify: 2/(x - 3) + 4/(x + 3) - 5/(x² - 9)
```

### 2.5 Multiplying/Dividing Rational Expressions

**Medium**
```
Multiply: ({{a}}x/{{b}}) × ({{c}}/{{d}}x)
# Constraints: a, b, c, d ∈ [2, 12]; result simplifies nicely
# Example: Multiply: (6x/5) × (10/3x)
```

**Hard**
```
Divide: [(x² - {{a}}²) / (x + {{b}})] ÷ [(x - {{a}}) / {{c}}]
# Constraints: a ∈ [2, 10]; b, c ∈ [1, 8]
# Example: Divide: [(x² - 16) / (x + 5)] ÷ [(x - 4) / 3]
```

---

## 3. Coordinate Plane

### 3.1 Distance Between Two Points

**Easy**
```
Find the distance between points ({{x1}}, {{y1}}) and ({{x2}}, {{y2}}).
# Constraints: coordinates ∈ [-10, 10]; distance is whole number (Pythagorean triple)
# Example: Find the distance between points (1, 2) and (4, 6).
```

**Medium**
```
Find the distance between points ({{x1}}, {{y1}}) and ({{x2}}, {{y2}}). Leave answer in simplest radical form.
# Constraints: coordinates ∈ [-12, 12]; result involves square root
# Example: Find the distance between points (-3, 4) and (5, -2).
```

**Hard**
```
Point A is at ({{x1}}, {{y1}}). Point B is {{d}} units away from A along the line y = {{m}}x + {{b}}. Find the coordinates of B.
# Constraints: m is simple fraction; d results in rational coordinates
# Example: Point A is at (2, 3). Point B is 10 units away from A along the line y = (3/4)x + 1.5. Find the coordinates of B.
```

### 3.2 Midpoint Formula

**Easy**
```
Find the midpoint of the segment with endpoints ({{x1}}, {{y1}}) and ({{x2}}, {{y2}}).
# Constraints: coordinates ∈ [-20, 20]; sum of each coordinate pair is even
# Example: Find the midpoint of the segment with endpoints (2, 8) and (6, -4).
```

**Medium**
```
The midpoint of segment AB is ({{mx}}, {{my}}). If A = ({{x1}}, {{y1}}), find the coordinates of B.
# Constraints: all values are integers
# Example: The midpoint of segment AB is (5, -2). If A = (3, 4), find the coordinates of B.
```

**Hard**
```
Points A({{x1}}, {{y1}}), B({{x2}}, {{y2}}), and C({{x3}}, {{y3}}) form a triangle. Find the coordinates of the centroid.
# Constraints: coordinates ∈ [-15, 15]; (x1+x2+x3) and (y1+y2+y3) divisible by 3
# Example: Points A(3, 6), B(-3, 0), and C(6, -3) form a triangle. Find the coordinates of the centroid.
```

---

## 4. Linear Equations

### 4.1 One-Step Equations

**Easy**
```
Solve for x: x + {{a}} = {{b}}
# Constraints: a, b ∈ [-50, 50]
# Example: Solve for x: x + 7 = 15
```

**Easy (Variant)**
```
Solve for x: {{a}}x = {{b}}
# Constraints: a ∈ [-12, 12] (a ≠ 0); b is divisible by a
# Example: Solve for x: 5x = 35
```

### 4.2 Two-Step Equations

**Easy**
```
Solve for x: {{a}}x + {{b}} = {{c}}
# Constraints: a ∈ [2, 12]; (c - b) divisible by a
# Example: Solve for x: 3x + 7 = 22
```

**Medium**
```
Solve for x: {{a}}x - {{b}} = {{c}}x + {{d}}
# Constraints: a ≠ c; result is integer
# Example: Solve for x: 5x - 8 = 2x + 7
```

### 4.3 Multi-Step Equations

**Medium**
```
Solve for x: {{a}}({{b}}x + {{c}}) = {{d}}
# Constraints: d is divisible by a; (d/a - c) divisible by b
# Example: Solve for x: 4(2x + 3) = 28
```

**Hard**
```
Solve for x: {{a}}({{b}}x - {{c}}) + {{d}} = {{e}}({{f}}x + {{g}}) - {{h}}
# Constraints: result is integer or simple fraction
# Example: Solve for x: 3(2x - 5) + 4 = 2(x + 3) - 8
```

**Hard (Fractions)**
```
Solve for x: (x + {{a}})/{{b}} + (x - {{c}})/{{d}} = {{e}}
# Constraints: b, d ∈ [2, 8]; LCD exists; solution is integer
# Example: Solve for x: (x + 3)/4 + (x - 1)/6 = 5
```

### 4.4 Slope-Intercept Form

**Easy**
```
Write the equation of a line with slope {{m}} and y-intercept {{b}}.
# Constraints: m ∈ [-5, 5] (can be fraction like 2/3); b ∈ [-10, 10]
# Example: Write the equation of a line with slope 3/4 and y-intercept -2.
```

**Medium**
```
Convert {{a}}x + {{b}}y = {{c}} to slope-intercept form.
# Constraints: a, b, c ∈ [-12, 12]; b ≠ 0
# Example: Convert 3x + 4y = 12 to slope-intercept form.
```

**Medium (Variant)**
```
A line passes through ({{x1}}, {{y1}}) and ({{x2}}, {{y2}}). Write its equation in slope-intercept form.
# Constraints: slope is integer or simple fraction; y-intercept is integer
# Example: A line passes through (2, 5) and (4, 11). Write its equation in slope-intercept form.
```

### 4.5 Point-Slope Form

**Easy**
```
Write the equation in point-slope form for a line through ({{x1}}, {{y1}}) with slope {{m}}.
# Constraints: coordinates ∈ [-10, 10]; m is integer or simple fraction
# Example: Write the equation in point-slope form for a line through (3, -2) with slope 4.
```

**Medium**
```
Convert y - {{y1}} = {{m}}(x - {{x1}}) to slope-intercept form.
# Constraints: m can be fraction; result has integer y-intercept
# Example: Convert y - 5 = (2/3)(x - 6) to slope-intercept form.
```

### 4.6 Standard Form

**Medium**
```
Write y = {{m}}x + {{b}} in standard form Ax + By = C where A, B, C are integers.
# Constraints: m is fraction p/q; A, B, C should be coprime
# Example: Write y = (3/4)x - 2 in standard form Ax + By = C.
```

**Hard**
```
A line passes through ({{x1}}, {{y1}}) and ({{x2}}, {{y2}}). Write its equation in standard form Ax + By = C where A > 0.
# Constraints: result has integer coefficients
# Example: A line passes through (-2, 3) and (4, -1). Write its equation in standard form.
```

### 4.7 Parallel and Perpendicular Lines

**Medium**
```
Write the equation of a line parallel to y = {{m}}x + {{b1}} that passes through ({{x1}}, {{y1}}).
# Constraints: m is integer or simple fraction; result has integer y-intercept
# Example: Write the equation of a line parallel to y = 2x - 3 that passes through (4, 1).
```

**Medium**
```
Write the equation of a line perpendicular to y = {{m}}x + {{b1}} that passes through ({{x1}}, {{y1}}).
# Constraints: m = p/q where p, q ≠ 0; perpendicular slope is -q/p
# Example: Write the equation of a line perpendicular to y = (2/3)x + 4 that passes through (6, -1).
```

**Hard**
```
Line L1 passes through ({{x1}}, {{y1}}) and ({{x2}}, {{y2}}). Find the equation of line L2 that is perpendicular to L1 and passes through the midpoint of L1.
# Constraints: calculations yield integer or simple fraction results
# Example: Line L1 passes through (2, 4) and (6, 0). Find the equation of line L2 perpendicular to L1 passing through the midpoint.
```

---

## 5. Slope

### 5.1 Finding Slope from Two Points

**Easy**
```
Find the slope of the line passing through ({{x1}}, {{y1}}) and ({{x2}}, {{y2}}).
# Constraints: coordinates ∈ [-15, 15]; x1 ≠ x2; slope is integer
# Example: Find the slope of the line passing through (2, 3) and (5, 12).
```

**Medium**
```
Find the slope of the line passing through ({{x1}}, {{y1}}) and ({{x2}}, {{y2}}). Express as a fraction in lowest terms.
# Constraints: slope is non-integer rational
# Example: Find the slope of the line passing through (-3, 7) and (4, -2).
```

**Hard**
```
Points A({{x1}}, {{y1}}), B({{x2}}, {{y2}}), and C({{x3}}, {{y3}}) are given. Determine if they are collinear.
# Constraints: generate both collinear and non-collinear sets
# Example: Points A(1, 2), B(3, 6), and C(5, 10) are given. Determine if they are collinear.
```

### 5.2 Slope from Graph (Conceptual)

**Easy**
```
A line rises {{rise}} units for every {{run}} units it moves to the right. What is its slope?
# Constraints: rise, run ∈ [1, 12]; gcd for simplification
# Example: A line rises 6 units for every 4 units it moves to the right. What is its slope?
```

**Medium**
```
A line passes through the origin and point ({{x}}, {{y}}). Is the slope positive, negative, zero, or undefined?
# Constraints: generate cases for each type
# Example: A line passes through the origin and point (-4, 8). Is the slope positive, negative, zero, or undefined?
```

---

## 6. Systems of Linear Equations

### 6.1 Solving by Graphing (Setup)

**Easy**
```
Solve the system by graphing:
  y = {{m1}}x + {{b1}}
  y = {{m2}}x + {{b2}}
# Constraints: m1 ≠ m2; intersection at integer coordinates
# Example: y = 2x + 1, y = -x + 4
```

### 6.2 Solving by Substitution

**Easy**
```
Solve by substitution:
  y = {{a}}x + {{b}}
  {{c}}x + {{d}}y = {{e}}
# Constraints: result is integer pair
# Example: y = 2x - 3, 3x + 2y = 7
```

**Medium**
```
Solve by substitution:
  {{a}}x + {{b}}y = {{c}}
  {{d}}x - {{e}}y = {{f}}
# Constraints: one equation easily solved for a variable; integer solution
# Example: 2x + y = 8, 3x - 2y = 5
```

### 6.3 Solving by Elimination

**Medium**
```
Solve by elimination:
  {{a}}x + {{b}}y = {{c}}
  {{d}}x + {{e}}y = {{f}}
# Constraints: coefficients allow easy elimination; integer solution
# Example: 3x + 2y = 13, 5x - 2y = 3
```

**Hard**
```
Solve by elimination:
  {{a}}x + {{b}}y = {{c}}
  {{d}}x + {{e}}y = {{f}}
# Constraints: requires multiplying both equations; solution may be fractions
# Example: 4x + 3y = 10, 5x + 7y = 19
```

### 6.4 Consistent vs Inconsistent Systems

**Medium**
```
Classify the system as consistent (independent), consistent (dependent), or inconsistent:
  {{a}}x + {{b}}y = {{c}}
  {{d}}x + {{e}}y = {{f}}
# Constraints: generate all three types by controlling ratios
# Example: 2x + 4y = 8, x + 2y = 4 (dependent)
```

---

## 7. Geometry and Measurement

### 7.1 Area and Perimeter

**Easy**
```
Find the area and perimeter of a rectangle with length {{l}} and width {{w}}.
# Constraints: l, w ∈ [1, 50]; can include units (cm, m, in, ft)
# Example: Find the area and perimeter of a rectangle with length 12 cm and width 8 cm.
```

**Medium**
```
A triangle has base {{b}} and height {{h}}. Find its area.
# Constraints: b, h ∈ [1, 30]
# Example: A triangle has base 14 cm and height 9 cm. Find its area.
```

**Hard**
```
Find the area of a trapezoid with parallel sides of length {{a}} and {{b}}, and height {{h}}.
# Constraints: a, b ∈ [5, 25]; h ∈ [3, 15]
# Example: Find the area of a trapezoid with parallel sides 8 cm and 14 cm, and height 6 cm.
```

### 7.2 Surface Area and Volume

**Easy**
```
Find the volume of a rectangular prism with length {{l}}, width {{w}}, and height {{h}}.
# Constraints: l, w, h ∈ [1, 20]
# Example: Find the volume of a rectangular prism with length 5 cm, width 3 cm, and height 4 cm.
```

**Medium**
```
Find the surface area and volume of a cylinder with radius {{r}} and height {{h}}. (Use π ≈ 3.14)
# Constraints: r ∈ [1, 10]; h ∈ [2, 15]
# Example: Find the surface area and volume of a cylinder with radius 4 cm and height 10 cm.
```

**Hard**
```
A cone has radius {{r}} and height {{h}}. Find its volume and surface area. (Use π ≈ 3.14)
# Constraints: r, h form Pythagorean triple with slant height for clean calculation
# Example: A cone has radius 3 cm and height 4 cm. Find its volume and surface area.
```

### 7.3 Combination of Solids

**Hard**
```
A solid consists of a cylinder with radius {{r}} and height {{h1}} topped by a hemisphere of the same radius. Find the total volume.
# Constraints: r ∈ [2, 8]; h1 ∈ [5, 15]
# Example: A solid consists of a cylinder with radius 5 cm and height 10 cm topped by a hemisphere. Find the total volume.
```

### 7.4 Percent Error

**Medium**
```
The measured value is {{measured}} and the actual value is {{actual}}. Calculate the percent error.
# Constraints: values yield clean percentage
# Example: The measured value is 48 and the actual value is 50. Calculate the percent error.
```

### 7.5 Unit Conversion

**Easy**
```
Convert {{value}} {{unit1}} to {{unit2}}.
# Constraints: metric-to-metric or standard-to-standard; clean conversion
# Example: Convert 3.5 kilometers to meters.
```

**Medium**
```
A rectangle measures {{l}} inches by {{w}} inches. Find its area in square feet.
# Constraints: (l × w) divisible by 144
# Example: A rectangle measures 36 inches by 24 inches. Find its area in square feet.
```

---

## 8. Linear Inequalities

### 8.1 Solving One-Step Inequalities

**Easy**
```
Solve and graph: x + {{a}} < {{b}}
# Constraints: a, b ∈ [-20, 20]
# Example: Solve and graph: x + 5 < 12
```

**Easy (Variant)**
```
Solve and graph: {{a}}x ≥ {{b}}
# Constraints: a ∈ [2, 12]; b divisible by a; note inequality flip if a < 0
# Example: Solve and graph: 4x ≥ 20
```

### 8.2 Solving Two-Step Inequalities

**Medium**
```
Solve: {{a}}x + {{b}} ≤ {{c}}
# Constraints: (c - b) divisible by a
# Example: Solve: 3x + 8 ≤ 20
```

**Medium (Division by Negative)**
```
Solve: {{a}} - {{b}}x > {{c}}
# Constraints: b > 0; requires dividing by negative (flip inequality)
# Example: Solve: 15 - 3x > 6
```

### 8.3 Compound Inequalities

**Medium**
```
Solve: {{a}} < {{b}}x + {{c}} ≤ {{d}}
# Constraints: values yield clean integer boundaries
# Example: Solve: 5 < 2x + 1 ≤ 13
```

**Hard**
```
Solve: {{a}}x - {{b}} < {{c}} OR {{d}}x + {{e}} > {{f}}
# Constraints: solutions don't overlap (for OR) or do (for AND)
# Example: Solve: 2x - 3 < 7 OR 3x + 1 > 16
```

### 8.4 Graphing Linear Inequalities in Two Variables

**Medium**
```
Graph the inequality: y > {{m}}x + {{b}}
# Constraints: m is integer or simple fraction; b ∈ [-6, 6]
# Example: Graph the inequality: y > 2x - 3
```

**Hard**
```
Graph the system of inequalities:
  y ≤ {{m1}}x + {{b1}}
  y > {{m2}}x + {{b2}}
# Constraints: lines intersect in visible region
# Example: y ≤ x + 4, y > -2x + 1
```

---

## 9. Sets

### 9.1 Set Operations

**Easy**
```
Let A = {{set_a}} and B = {{set_b}}. Find A ∪ B.
# Constraints: sets have 3-6 elements; some overlap
# Example: Let A = {1, 3, 5, 7} and B = {2, 3, 4, 5}. Find A ∪ B.
```

**Easy (Variant)**
```
Let A = {{set_a}} and B = {{set_b}}. Find A ∩ B.
# Example: Let A = {1, 3, 5, 7} and B = {2, 3, 4, 5}. Find A ∩ B.
```

**Medium**
```
Let U = {{universal}}, A = {{set_a}}. Find A' (complement of A).
# Constraints: A ⊆ U
# Example: Let U = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}, A = {2, 4, 6, 8}. Find A'.
```

**Hard**
```
Let U = {{universal}}, A = {{set_a}}, B = {{set_b}}. Find (A ∪ B)'.
# Example: Let U = {1,2,3,4,5,6,7,8,9,10}, A = {1,2,3,4}, B = {3,4,5,6}. Find (A ∪ B)'.
```

### 9.2 Set-Builder Notation

**Medium**
```
Write in set-builder notation: {{set_elements}}
# Constraints: elements follow clear pattern
# Example: Write in set-builder notation: {2, 4, 6, 8, 10}
# Answer: {x | x = 2n, n ∈ ℤ, 1 ≤ n ≤ 5}
```

**Medium (Variant)**
```
List the elements of: {x | x ∈ ℤ, {{a}} ≤ x < {{b}}}
# Constraints: b - a ∈ [4, 10]
# Example: List the elements of: {x | x ∈ ℤ, -3 ≤ x < 4}
```

---

## 10. Proportional Relationships

### 10.1 Direct Proportion

**Easy**
```
If y varies directly with x, and y = {{y1}} when x = {{x1}}, find y when x = {{x2}}.
# Constraints: y1/x1 is integer or simple fraction; result is clean
# Example: If y varies directly with x, and y = 12 when x = 4, find y when x = 7.
```

**Medium**
```
The cost C varies directly with the number of items n. If {{n1}} items cost ${{c1}}, how much do {{n2}} items cost?
# Constraints: c1/n1 is clean; c1, c2 reasonable dollar amounts
# Example: If 5 items cost $35, how much do 12 items cost?
```

### 10.2 Inverse Proportion

**Medium**
```
If y varies inversely with x, and y = {{y1}} when x = {{x1}}, find y when x = {{x2}}.
# Constraints: y1 × x1 = k yields integer; k/x2 is integer or simple fraction
# Example: If y varies inversely with x, and y = 8 when x = 3, find y when x = 6.
```

**Hard**
```
{{n1}} workers can complete a job in {{d1}} days. How many days would it take {{n2}} workers?
# Constraints: n1 × d1 is divisible by n2
# Example: 6 workers can complete a job in 12 days. How many days would it take 9 workers?
```

### 10.3 Constant of Proportionality

**Easy**
```
Find the constant of proportionality: y = {{k}}x
# Constraints: k is visible coefficient
# Example: Find the constant of proportionality: y = 7x
```

**Medium**
```
The table shows a proportional relationship. Find the constant of proportionality.
| x | {{x1}} | {{x2}} | {{x3}} |
| y | {{y1}} | {{y2}} | {{y3}} |
# Constraints: y/x is constant
# Example: x: 2, 5, 8 and y: 6, 15, 24. Find k.
```

---

## 11. Exponents and Powers

### 11.1 Basic Exponents

**Easy**
```
Evaluate: {{base}}^{{exp}}
# Constraints: base ∈ [-10, 10]; exp ∈ [2, 5]; result manageable
# Example: Evaluate: 3^4
```

### 11.2 Negative Exponents

**Easy**
```
Simplify: {{base}}^{{neg_exp}}
# Constraints: base ∈ [2, 10]; neg_exp ∈ [-4, -1]
# Example: Simplify: 5^(-2)
```

**Medium**
```
Simplify: ({{a}}/{{b}})^{{neg_exp}}
# Constraints: a, b ∈ [2, 8]; neg_exp ∈ [-3, -1]
# Example: Simplify: (2/3)^(-3)
```

### 11.3 Laws of Exponents

**Easy**
```
Simplify using exponent laws: {{base}}^{{a}} × {{base}}^{{b}}
# Constraints: base ∈ [2, 10]; a, b ∈ [-5, 8]
# Example: Simplify: 2^3 × 2^5
```

**Medium**
```
Simplify: ({{base}}^{{a}})^{{b}}
# Constraints: base ∈ [2, 6]; |a × b| ≤ 12
# Example: Simplify: (3^2)^4
```

**Medium (Division)**
```
Simplify: {{base}}^{{a}} ÷ {{base}}^{{b}}
# Constraints: base ∈ [2, 10]; a > b for positive result
# Example: Simplify: 5^7 ÷ 5^3
```

**Hard**
```
Simplify: ({{a}}^{{m}} × {{a}}^{{n}}) / {{a}}^{{p}}
# Constraints: m + n > p for positive exponent result
# Example: Simplify: (x^5 × x^3) / x^4
```

### 11.4 Rational/Fractional Exponents

**Medium**
```
Evaluate: {{base}}^1/{{n}}
# Constraints: base is perfect nth power
# Example: Evaluate: 27^(1/3)
```

**Hard**
```
Simplify: {{base}}^{{m}}/{{n}}
# Constraints: base is perfect nth power; m, n ∈ [2, 4]
# Example: Simplify: 16^(3/4)
```

---

## 12. Scientific Notation

### 12.1 Converting to Scientific Notation

**Easy**
```
Write {{number}} in scientific notation.
# Constraints: number is large (> 1000) or small (< 0.01)
# Example: Write 45,000,000 in scientific notation.
```

**Easy (Variant)**
```
Write {{decimal}} in scientific notation.
# Example: Write 0.00032 in scientific notation.
```

### 12.2 Converting from Scientific Notation

**Easy**
```
Write {{coeff}} × 10^{{exp}} in standard form.
# Constraints: coeff ∈ [1, 10); exp ∈ [-8, 8]
# Example: Write 3.7 × 10^5 in standard form.
```

### 12.3 Operations with Scientific Notation

**Medium**
```
Multiply: ({{a}} × 10^{{m}}) × ({{b}} × 10^{{n}})
# Constraints: a, b ∈ [1, 10); result should be in proper scientific notation
# Example: Multiply: (3.2 × 10^4) × (2.5 × 10^3)
```

**Medium**
```
Divide: ({{a}} × 10^{{m}}) ÷ ({{b}} × 10^{{n}})
# Example: Divide: (8.4 × 10^7) ÷ (2.1 × 10^3)
```

**Hard**
```
Add: ({{a}} × 10^{{m}}) + ({{b}} × 10^{{n}})
# Constraints: |m - n| ≤ 3 for reasonable calculation
# Example: Add: (3.5 × 10^5) + (2.8 × 10^4)
```

---

## 13. Sequences

### 13.1 Arithmetic Sequences

**Easy**
```
Find the next three terms: {{a1}}, {{a2}}, {{a3}}, ...
# Constraints: common difference d ∈ [-10, 10]
# Example: Find the next three terms: 5, 9, 13, ...
```

**Medium**
```
In an arithmetic sequence, a₁ = {{a1}} and d = {{d}}. Find a_{{n}}.
# Constraints: n ∈ [5, 20]; result is manageable
# Example: In an arithmetic sequence, a₁ = 7 and d = 4. Find a₁₅.
```

**Hard**
```
In an arithmetic sequence, a_{{m}} = {{am}} and a_{{n}} = {{an}}. Find a₁ and d.
# Constraints: m < n; clean solution
# Example: In an arithmetic sequence, a₅ = 17 and a₁₂ = 38. Find a₁ and d.
```

### 13.2 Geometric Sequences

**Easy**
```
Find the next three terms: {{a1}}, {{a2}}, {{a3}}, ...
# Constraints: common ratio r ∈ {2, 3, 1/2, 1/3, -2}
# Example: Find the next three terms: 3, 6, 12, ...
```

**Medium**
```
In a geometric sequence, a₁ = {{a1}} and r = {{r}}. Find a_{{n}}.
# Constraints: n ∈ [4, 8]; result manageable
# Example: In a geometric sequence, a₁ = 2 and r = 3. Find a₆.
```

**Hard**
```
In a geometric sequence, a_{{m}} = {{am}} and a_{{n}} = {{an}}. Find r and a₁.
# Constraints: m < n; r is integer or simple fraction
# Example: In a geometric sequence, a₂ = 6 and a₅ = 162. Find r and a₁.
```

### 13.3 Sequence Formulas

**Medium**
```
Find the sum of the first {{n}} terms of the arithmetic sequence where a₁ = {{a1}} and d = {{d}}.
# Constraints: sum yields integer
# Example: Find the sum of the first 20 terms where a₁ = 3 and d = 5.
```

**Hard**
```
Find the sum of the first {{n}} terms of the geometric sequence where a₁ = {{a1}} and r = {{r}}.
# Constraints: r ≠ 1; result is integer or simple fraction
# Example: Find the sum of the first 6 terms where a₁ = 4 and r = 2.
```

---

## 14. Polynomials

### 14.1 Adding and Subtracting Polynomials

**Easy**
```
Add: ({{a}}x² + {{b}}x + {{c}}) + ({{d}}x² + {{e}}x + {{f}})
# Constraints: coefficients ∈ [-12, 12]
# Example: Add: (3x² + 5x - 2) + (2x² - 3x + 7)
```

**Medium**
```
Subtract: ({{a}}x² + {{b}}x + {{c}}) - ({{d}}x² + {{e}}x + {{f}})
# Example: Subtract: (5x² - 2x + 8) - (3x² + 4x - 1)
```

### 14.2 Multiplying Polynomials

**Easy**
```
Multiply: {{a}}x({{b}}x + {{c}})
# Constraints: a, b, c ∈ [-10, 10]
# Example: Multiply: 3x(2x + 5)
```

**Medium**
```
Multiply: ({{a}}x + {{b}})({{c}}x + {{d}})
# Constraints: FOIL practice; coefficients ∈ [-8, 8]
# Example: Multiply: (2x + 3)(4x - 5)
```

**Hard**
```
Multiply: ({{a}}x + {{b}})({{c}}x² + {{d}}x + {{e}})
# Constraints: binomial × trinomial
# Example: Multiply: (x + 2)(x² - 3x + 4)
```

### 14.3 Dividing Polynomials

**Medium**
```
Divide: ({{a}}x³ + {{b}}x² + {{c}}x) ÷ {{d}}x
# Constraints: d divides a, b, c evenly
# Example: Divide: (6x³ + 9x² - 3x) ÷ 3x
```

**Hard**
```
Divide: ({{a}}x² + {{b}}x + {{c}}) ÷ ({{d}}x + {{e}})
# Constraints: division is exact (no remainder)
# Example: Divide: (2x² + 7x + 3) ÷ (x + 3)
```

### 14.4 Factoring Polynomials

**Easy (GCF)**
```
Factor completely: {{a}}x² + {{b}}x
# Constraints: gcd(a, b) > 1
# Example: Factor completely: 6x² + 9x
```

**Medium (Trinomial)**
```
Factor: x² + {{b}}x + {{c}}
# Constraints: factors into (x + p)(x + q) where p + q = b, pq = c
# Example: Factor: x² + 7x + 12
```

**Hard (Leading Coefficient ≠ 1)**
```
Factor: {{a}}x² + {{b}}x + {{c}}
# Constraints: factors into (px + q)(rx + s) with integer values
# Example: Factor: 2x² + 7x + 3
```

**Hard (Difference of Squares)**
```
Factor: {{a}}²x² - {{b}}²
# Constraints: a, b ∈ [2, 10]
# Example: Factor: 9x² - 25
```

### 14.5 Degree of Polynomial

**Easy**
```
Find the degree of: {{a}}x^{{n}} + {{b}}x^{{m}} + {{c}}x^{{p}} + {{d}}
# Constraints: n > m > p ≥ 0
# Example: Find the degree of: 4x⁵ + 2x³ - 7x + 9
```

---

## 15. Quadratic Equations

### 15.1 Solving by Factoring

**Easy**
```
Solve by factoring: x² + {{b}}x + {{c}} = 0
# Constraints: factors with integer roots
# Example: Solve by factoring: x² + 5x + 6 = 0
```

**Medium**
```
Solve by factoring: {{a}}x² + {{b}}x + {{c}} = 0
# Constraints: a ∈ [2, 4]; integer roots
# Example: Solve by factoring: 2x² + 5x - 3 = 0
```

### 15.2 Solving by Completing the Square

**Medium**
```
Solve by completing the square: x² + {{b}}x + {{c}} = 0
# Constraints: b is even for clean calculation
# Example: Solve by completing the square: x² + 6x - 7 = 0
```

**Hard**
```
Solve by completing the square: {{a}}x² + {{b}}x + {{c}} = 0
# Constraints: a ∈ [2, 4]; b divisible by 2a
# Example: Solve by completing the square: 2x² + 8x - 10 = 0
```

### 15.3 Quadratic Formula

**Medium**
```
Solve using the quadratic formula: x² + {{b}}x + {{c}} = 0
# Constraints: discriminant is perfect square for rational roots
# Example: Solve using the quadratic formula: x² - 5x + 6 = 0
```

**Hard**
```
Solve using the quadratic formula: {{a}}x² + {{b}}x + {{c}} = 0. Express in simplest radical form if necessary.
# Constraints: discriminant may not be perfect square
# Example: Solve using the quadratic formula: 2x² + 3x - 4 = 0
```

### 15.4 Graphing Quadratic Functions

**Medium**
```
Find the vertex and axis of symmetry of y = x² + {{b}}x + {{c}}.
# Constraints: -b/2 is integer; vertex has integer coordinates
# Example: Find the vertex and axis of symmetry of y = x² - 4x + 3.
```

**Hard**
```
For y = {{a}}x² + {{b}}x + {{c}}, find: (a) vertex, (b) axis of symmetry, (c) y-intercept, (d) x-intercepts.
# Constraints: clean calculations
# Example: For y = 2x² - 8x + 6, find vertex, axis of symmetry, y-intercept, and x-intercepts.
```

---

## 16. Absolute Value

### 16.1 Solving Absolute Value Equations

**Easy**
```
Solve: |x| = {{a}}
# Constraints: a > 0
# Example: Solve: |x| = 7
```

**Medium**
```
Solve: |x + {{a}}| = {{b}}
# Constraints: a ∈ [-10, 10]; b > 0
# Example: Solve: |x + 3| = 8
```

**Hard**
```
Solve: |{{a}}x - {{b}}| = {{c}}
# Constraints: solutions are integers or simple fractions
# Example: Solve: |2x - 5| = 9
```

**Hard (Variant)**
```
Solve: |{{a}}x + {{b}}| = |{{c}}x + {{d}}|
# Constraints: yields two distinct solutions
# Example: Solve: |2x + 1| = |x - 4|
```

---

## 17. Function Transformations

### 17.1 Translations

**Easy**
```
The graph of y = f(x) is shifted {{h}} units {{h_dir}} and {{k}} units {{k_dir}}. Write the transformed equation.
# Constraints: h, k ∈ [1, 10]; h_dir ∈ {left, right}; k_dir ∈ {up, down}
# Example: The graph of y = f(x) is shifted 3 units right and 5 units up. Write the transformed equation.
```

**Medium**
```
Describe the transformation from y = x² to y = (x - {{h}})² + {{k}}.
# Constraints: h, k ∈ [-8, 8]
# Example: Describe the transformation from y = x² to y = (x - 4)² + 2.
```

### 17.2 Reflections and Stretches

**Medium**
```
Describe the transformation from y = |x| to y = {{a}}|x - {{h}}| + {{k}}.
# Constraints: a ∈ {-2, -1, 1/2, 1, 2, 3}; h, k ∈ [-5, 5]
# Example: Describe the transformation from y = |x| to y = -2|x + 3| - 1.
```

**Hard**
```
Write the equation of y = x² after: (1) vertical stretch by factor {{a}}, (2) reflection over {{axis}}, (3) shift {{h}} units {{h_dir}}, (4) shift {{k}} units {{k_dir}}.
# Constraints: a ∈ [2, 4]; axis ∈ {x-axis, y-axis}
# Example: Write the equation of y = x² after: vertical stretch by 2, reflection over x-axis, shift 3 right, shift 4 up.
```

---

## 18. Statistics

### 18.1 Mean, Median, Mode

**Easy**
```
Find the mean, median, and mode: {{data_set}}
# Constraints: 5-9 values; at least one repeated for mode; values ∈ [1, 100]
# Example: Find the mean, median, and mode: 12, 15, 18, 15, 22, 15, 19
```

**Medium**
```
The mean of {{n}} numbers is {{mean}}. If one number, {{removed}}, is removed, what is the new mean?
# Constraints: calculations yield clean decimal or integer
# Example: The mean of 5 numbers is 24. If the number 30 is removed, what is the new mean of the remaining 4 numbers?
```

### 18.2 Quartiles and IQR

**Medium**
```
Find Q1, Q2 (median), Q3, and the IQR for: {{data_set}}
# Constraints: 8-12 ordered values
# Example: Find Q1, Q2, Q3, and IQR for: 4, 7, 10, 12, 15, 18, 21, 24, 27, 30
```

**Hard**
```
Identify any outliers in the data set using the 1.5×IQR rule: {{data_set}}
# Constraints: include potential outliers
# Example: Identify outliers: 2, 5, 7, 8, 9, 10, 11, 12, 15, 32
```

---

## 19. Probability

### 19.1 Basic Probability

**Easy**
```
A bag contains {{r}} red, {{b}} blue, and {{g}} green marbles. What is the probability of drawing a {{color}} marble?
# Constraints: r, b, g ∈ [2, 10]
# Example: A bag contains 5 red, 3 blue, and 4 green marbles. What is the probability of drawing a blue marble?
```

**Medium**
```
A standard die is rolled. What is the probability of rolling a number {{condition}}?
# Constraints: condition ∈ {"greater than 3", "less than 5", "even", "prime", "divisible by 3"}
# Example: A standard die is rolled. What is the probability of rolling a prime number?
```

### 19.2 Independent and Dependent Events

**Medium**
```
A coin is flipped and a die is rolled. What is the probability of getting {{coin_outcome}} and {{die_outcome}}?
# Constraints: coin_outcome ∈ {heads, tails}; die_outcome describes a die result
# Example: What is the probability of getting heads and a number greater than 4?
```

**Hard**
```
A bag contains {{r}} red and {{b}} blue marbles. Two marbles are drawn {{with_without}} replacement. What is the probability that both are {{color}}?
# Constraints: with_without ∈ {with, without}
# Example: A bag contains 6 red and 4 blue marbles. Two are drawn without replacement. What is the probability both are red?
```

### 19.3 Conditional Probability

**Hard**
```
In a class, {{a}}% of students play sports and {{b}}% play both sports and music. Given that a student plays sports, what is the probability they also play music?
# Constraints: b ≤ a; clean percentage result
# Example: 60% of students play sports and 24% play both sports and music. Given that a student plays sports, what is the probability they also play music?
```

---

## 20. Permutations and Combinations

### 20.1 Counting Principle

**Easy**
```
A restaurant offers {{m}} main courses and {{s}} side dishes. How many different meals can be created?
# Constraints: m, s ∈ [3, 10]
# Example: A restaurant offers 5 main courses and 4 side dishes. How many different meals can be created?
```

### 20.2 Permutations

**Medium**
```
How many ways can {{n}} people line up in a row?
# Constraints: n ∈ [4, 8]
# Example: How many ways can 6 people line up in a row?
```

**Medium (Variant)**
```
How many ways can you arrange {{r}} books from a shelf of {{n}} books?
# Constraints: r < n; r ∈ [2, 5]; n ∈ [5, 10]
# Example: How many ways can you arrange 3 books from a shelf of 8 books?
```

### 20.3 Combinations

**Medium**
```
How many ways can you choose {{r}} students from a class of {{n}} students?
# Constraints: r ∈ [2, 5]; n ∈ [8, 15]
# Example: How many ways can you choose 4 students from a class of 12?
```

**Hard**
```
A committee of {{total}} people must include {{m}} from group A ({{a}} people) and {{n}} from group B ({{b}} people). How many committees are possible?
# Constraints: m ≤ a; n ≤ b; total = m + n
# Example: A committee of 5 must include 2 from group A (6 people) and 3 from group B (8 people). How many committees are possible?
```

---

## 21. Matrices

### 21.1 Matrix Addition and Subtraction

**Easy**
```
Add the matrices:
[{{a11}} {{a12}}]   [{{b11}} {{b12}}]
[{{a21}} {{a22}}] + [{{b21}} {{b22}}]
# Constraints: all entries ∈ [-10, 10]
# Example: Add: [2 5; -3 4] + [1 -2; 6 3]
```

### 21.2 Scalar Multiplication

**Easy**
```
Multiply: {{k}} × [{{a11}} {{a12}}]
            [{{a21}} {{a22}}]
# Constraints: k ∈ [-5, 5]; entries ∈ [-10, 10]
# Example: Multiply: 3 × [2 -1; 4 5]
```

### 21.3 Matrix Multiplication

**Medium**
```
Multiply the matrices:
[{{a11}} {{a12}}]   [{{b11}} {{b12}}]
[{{a21}} {{a22}}] × [{{b21}} {{b22}}]
# Constraints: entries ∈ [-5, 5] for manageable calculation
# Example: Multiply: [2 3; 1 4] × [5 -1; 2 3]
```

**Hard**
```
Multiply the matrices:
[{{a11}} {{a12}} {{a13}}]   [{{b11}}]
[{{a21}} {{a22}} {{a23}}] × [{{b21}}]
                      [{{b31}}]
# Constraints: 2×3 matrix times 3×1 matrix
# Example: Multiply: [1 2 3; 4 5 6] × [2; -1; 3]
```
