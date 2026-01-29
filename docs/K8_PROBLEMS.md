# Grade 8 Math Problem Templates

## 1. Integers

### Introduction to Integers / Operations on Integers

**Easy**
```
{{name}} has {{a}} dollars in their bank account. They spend {{b}} dollars on a book and then deposit {{c}} dollars. What is their final balance?
# Constraints: a ∈ [-100, 100], b ∈ [1, |a|], c ∈ [1, 100]
# Answer: a - b + c
```

**Medium**
```
The temperature at midnight was {{a}}°C. By 6 AM, it dropped by {{b}}°C, then rose by {{c}}°C by noon, and dropped again by {{d}}°C by evening. What was the final temperature?
# Constraints: a ∈ [-20, 30], b ∈ [1, 15], c ∈ [1, 20], d ∈ [1, 15]
# Answer: a - b + c - d
```

**Hard**
```
Evaluate: {{a}} × ({{b}} - {{c}}) + {{d}} ÷ {{e}} - {{f}}
# Constraints: a ∈ [-10, 10]\{{0}}, b ∈ [-20, 20], c ∈ [-20, 20], d ∈ [-50, 50] (divisible by e), e ∈ [-10, 10]\{{0}}, f ∈ [-30, 30]
# Answer: a × (b - c) + d ÷ e - f
```

### Properties of Integers

**Easy**
```
Which property of integers is illustrated by the equation {{a}} + {{b}} = {{b}} + {{a}}?
# Constraints: a, b ∈ [-50, 50], a ≠ b
# Answer: Commutative Property of Addition
```

**Medium**
```
Using the distributive property, simplify: {{a}} × ({{b}} + {{c}})
# Constraints: a ∈ [-12, 12]\{{0}}, b ∈ [-20, 20], c ∈ [-20, 20]
# Answer: (a × b) + (a × c)
```

### Consecutive Integers

**Easy**
```
The sum of three consecutive integers is {{sum}}. Find the integers.
# Constraints: sum = 3n for some n ∈ [-30, 30], so sum ∈ {-90, -87, ..., 87, 90}
# Answer: (sum/3 - 1), (sum/3), (sum/3 + 1)
```

**Medium**
```
The sum of {{n}} consecutive even integers starting from {{start}} is what?
# Constraints: n ∈ [3, 10], start ∈ [-20, 20] (even)
# Answer: n × start + n × (n - 1)
```

**Hard**
```
Find three consecutive odd integers such that twice the smallest plus the largest equals {{result}}.
# Constraints: result = 3x + 4 where x is odd, so result ∈ {..., -5, -2, 1, 4, 7, ...}
# Let smallest = x, then 2x + (x + 4) = result → x = (result - 4) / 3
# Answer: x, x + 2, x + 4
```

---

## 2. Rational Numbers

### Representation and Operations

**Easy**
```
Express {{a}}/{{b}} as a decimal. Is it terminating or repeating?
# Constraints: a ∈ [-20, 20]\{{0}}, b ∈ [2, 20]\{{0}}, gcd(|a|, b) = 1
# Answer: a/b (decimal form), terminating if b has only factors 2 and 5
```

**Medium**
```
Arrange the following rational numbers in ascending order: {{a}}/{{b}}, {{c}}/{{d}}, {{e}}/{{f}}
# Constraints: a, c, e ∈ [-10, 10], b, d, f ∈ [2, 12] (positive)
# Answer: sorted list by decimal value
```

**Hard**
```
Find two rational numbers between {{a}}/{{b}} and {{c}}/{{d}}.
# Constraints: a/b < c/d, a, c ∈ [-10, 10], b, d ∈ [2, 10] (positive)
# Answer: Any two values strictly between a/b and c/d
```

### Properties of Rational Numbers

**Easy**
```
What is the additive inverse of {{a}}/{{b}}?
# Constraints: a ∈ [-20, 20]\{{0}}, b ∈ [2, 20]
# Answer: -a/b
```

**Medium**
```
Simplify: ({{a}}/{{b}}) + ({{c}}/{{d}}) - ({{e}}/{{f}})
# Constraints: a, c, e ∈ [-15, 15], b, d, f ∈ [2, 12] (positive)
# Answer: Common denominator calculation
```

**Hard**
```
Verify the associative property: Does ({{a}}/{{b}} × {{c}}/{{d}}) × {{e}}/{{f}} = {{a}}/{{b}} × ({{c}}/{{d}} × {{e}}/{{f}})?
# Constraints: a, c, e ∈ [-10, 10]\{{0}}, b, d, f ∈ [2, 10]
# Answer: Yes, both equal (a×c×e)/(b×d×f)
```

---

## 3. Exponents

### Laws of Exponents

**Easy**
```
Simplify: {{base}}^{{a}} × {{base}}^{{b}}
# Constraints: base ∈ [2, 10], a ∈ [1, 6], b ∈ [1, 6]
# Answer: base^(a+b)
```

**Medium**
```
Simplify: ({{base}}^{{a}})^{{b}} ÷ {{base}}^{{c}}
# Constraints: base ∈ [2, 7], a ∈ [2, 5], b ∈ [2, 4], c ∈ [1, a×b-1]
# Answer: base^(a×b - c)
```

**Hard**
```
Simplify and express with positive exponents: ({{a}}^{{m}} × {{b}}^{{n}}) / ({{a}}^{{p}} × {{b}}^{{q}})
# Constraints: a, b ∈ [2, 10], a ≠ b, m, n, p, q ∈ [-5, 5]
# Answer: a^(m-p) × b^(n-q) with negative exponents converted
```

### Adding and Subtracting Exponents

**Easy**
```
Simplify: {{a}} × 10^{{m}} + {{b}} × 10^{{m}}
# Constraints: a, b ∈ [1, 9], m ∈ [2, 6]
# Answer: (a + b) × 10^m
```

**Medium**
```
Simplify: {{a}} × 10^{{m}} + {{b}} × 10^{{n}} where m > n
# Constraints: a, b ∈ [1, 9], m ∈ [3, 6], n ∈ [1, m-1]
# Answer: (a × 10^(m-n) + b) × 10^n
```

### Fractional Exponents

**Easy**
```
Evaluate: {{a}}^(1/2)
# Constraints: a ∈ {1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144}
# Answer: √a
```

**Medium**
```
Simplify: {{a}}^({{m}}/{{n}})
# Constraints: a ∈ {8, 16, 27, 32, 64, 81, 125, 256}, m ∈ [1, 4], n ∈ [2, 4], gcd(m,n) = 1
# Answer: (n√a)^m
```

**Hard**
```
Simplify: {{a}}^({{m}}/{{n}}) × {{a}}^({{p}}/{{q}})
# Constraints: a ∈ {4, 8, 9, 16, 27, 64}, m, p ∈ [1, 5], n, q ∈ [2, 4]
# Answer: a^(m/n + p/q)
```

---

## 4. Square and Cube Roots

### Square Roots

**Easy**
```
Find the square root of {{a}}.
# Constraints: a ∈ {1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225}
# Answer: √a
```

**Medium**
```
Simplify: √{{a}} + √{{b}} - √{{c}}
# Constraints: a, b, c ∈ {4, 9, 16, 25, 36, 49, 64, 81, 100}
# Answer: √a + √b - √c (numerical)
```

**Hard**
```
A square garden has an area of {{area}} square meters. A path of width {{w}} meters surrounds the garden. What is the total area including the path?
# Constraints: area ∈ {16, 25, 36, 49, 64, 81, 100, 121, 144}, w ∈ [1, 3]
# Answer: (√area + 2w)²
```

### Cube Roots

**Easy**
```
Find the cube root of {{a}}.
# Constraints: a ∈ {1, 8, 27, 64, 125, 216, 343, 512, 729, 1000}
# Answer: ³√a
```

**Medium**
```
Simplify: ³√{{a}} × ³√{{b}}
# Constraints: a, b ∈ {8, 27, 64, 125, 216}
# Answer: ³√(a×b)
```

**Hard**
```
A cube-shaped water tank has a volume of {{v}} cubic feet. If the side length is increased by {{n}} feet, what is the new volume?
# Constraints: v ∈ {8, 27, 64, 125, 216, 343, 512}, n ∈ [1, 5]
# Answer: (³√v + n)³
```

---

## 5. Irrational Numbers

### Identification

**Easy**
```
Which of the following is irrational: {{a}}/{{b}}, √{{c}}, {{d}}?
# Constraints: a ∈ [-10, 10], b ∈ [1, 10], c ∈ {2, 3, 5, 6, 7, 8, 10, 11, 12} (non-perfect squares), d ∈ [-5, 5]
# Answer: √c
```

**Medium**
```
Determine whether √{{a}} + √{{b}} is rational or irrational.
# Constraints: a ∈ {2, 3, 5, 6, 7, 8}, b ∈ {2, 3, 5, 6, 7, 8}
# Answer: Irrational (sum of two different irrational square roots)
```

### Real-Life Applications

**Medium**
```
A circular pool has an area of {{a}}π square meters. What is the radius of the pool? Express your answer in exact form.
# Constraints: a ∈ {4, 9, 16, 25, 36, 49, 64, 81, 100}
# Answer: √a meters
```

**Hard**
```
The diagonal of a square is {{d}} cm. Find the exact area of the square.
# Constraints: d ∈ [5, 20]
# Answer: d²/2 cm²
```

---

## 6. Proportions

### Direct Proportion

**Easy**
```
If {{a}} {{item_plural}} cost ${{cost}}, how much do {{b}} {{item_plural}} cost?
# Constraints: a ∈ [2, 10], cost ∈ [5, 100], b ∈ [1, 20], item_plural ∈ ["apples", "books", "pens", "tickets"]
# Answer: (cost/a) × b
```

**Medium**
```
{{name}} can type {{a}} words in {{b}} minutes. At the same rate, how many words can they type in {{c}} minutes?
# Constraints: a ∈ [50, 200], b ∈ [2, 10], c ∈ [5, 30]
# Answer: (a/b) × c
```

**Hard**
```
The distance traveled by a car is directly proportional to time. If the car travels {{d1}} km in {{t1}} hours, how long will it take to travel {{d2}} km?
# Constraints: d1 ∈ [50, 200], t1 ∈ [1, 4], d2 ∈ [100, 500]
# Answer: (d2/d1) × t1 hours
```

### Inverse Proportion

**Easy**
```
If {{a}} workers can complete a job in {{b}} days, how many days will it take {{c}} workers to complete the same job?
# Constraints: a ∈ [2, 10], b ∈ [5, 20], c ∈ [2, 15], c ≠ a
# Answer: (a × b) / c days
```

**Medium**
```
A car traveling at {{v1}} km/h takes {{t}} hours to complete a journey. How fast must the car travel to complete the same journey in {{new_t}} hours?
# Constraints: v1 ∈ [40, 100], t ∈ [2, 6], new_t ∈ [1, 8], new_t ≠ t
# Answer: (v1 × t) / new_t km/h
```

**Hard**
```
{{a}} pipes can fill a tank in {{b}} hours. After {{c}} hours, {{d}} more pipes are added. How much longer will it take to fill the tank?
# Constraints: a ∈ [2, 6], b ∈ [4, 12], c ∈ [1, b-1], d ∈ [1, 4]
# Answer: ((b - c) × a) / (a + d) hours
```

### Compound Proportions

**Hard**
```
If {{a}} workers working {{h1}} hours per day can complete a project in {{d1}} days, how many days will {{b}} workers working {{h2}} hours per day need to complete the same project?
# Constraints: a ∈ [3, 10], h1 ∈ [6, 10], d1 ∈ [10, 30], b ∈ [2, 12], h2 ∈ [5, 12]
# Answer: (a × h1 × d1) / (b × h2) days
```

---

## 7. Percentages

### Basic Percentage

**Easy**
```
What is {{p}}% of {{n}}?
# Constraints: p ∈ [5, 100], n ∈ [10, 1000]
# Answer: (p/100) × n
```

**Medium**
```
{{a}} is what percent of {{b}}?
# Constraints: a ∈ [1, 500], b ∈ [10, 1000], a ≤ b
# Answer: (a/b) × 100 %
```

### Percentage Change

**Easy**
```
A shirt originally priced at ${{original}} is now sold for ${{new}}. Find the percentage {{change_type}}.
# Constraints: original ∈ [20, 200], new ∈ [15, 250], change_type = "increase" if new > original else "decrease"
# Answer: |new - original| / original × 100 %
```

**Medium**
```
{{name}}'s score improved from {{a}} to {{b}}. What was the percentage increase in their score?
# Constraints: a ∈ [40, 90], b ∈ [a+1, 100]
# Answer: ((b - a) / a) × 100 %
```

**Hard (Successive Percentage Change)**
```
A population of {{p}} increases by {{a}}% in the first year and then decreases by {{b}}% in the second year. What is the population after two years?
# Constraints: p ∈ [1000, 100000], a ∈ [5, 30], b ∈ [5, 25]
# Answer: p × (1 + a/100) × (1 - b/100)
```

### Discount

**Easy**
```
A {{item}} is marked at ${{marked}}. If a discount of {{d}}% is offered, what is the selling price?
# Constraints: item ∈ ["laptop", "phone", "TV", "jacket"], marked ∈ [50, 2000], d ∈ [5, 50]
# Answer: marked × (1 - d/100)
```

**Medium**
```
After a {{d}}% discount, a {{item}} costs ${{final}}. What was the original price?
# Constraints: item ∈ ["bicycle", "camera", "watch"], d ∈ [10, 40], final ∈ [50, 500]
# Answer: final / (1 - d/100)
```

**Hard**
```
A store offers successive discounts of {{d1}}% and {{d2}}% on an item marked at ${{marked}}. What is the final price and the single equivalent discount?
# Constraints: marked ∈ [100, 1000], d1 ∈ [10, 30], d2 ∈ [5, 20]
# Answer: Price = marked × (1 - d1/100) × (1 - d2/100); Equivalent discount = (1 - (1-d1/100)(1-d2/100)) × 100 %
```

---

## 8. Equations

### One-Step Equations

**Easy**
```
Solve for x: x + {{a}} = {{b}}
# Constraints: a ∈ [-20, 20], b ∈ [-30, 30]
# Answer: x = b - a
```

**Easy**
```
Solve for x: {{a}}x = {{b}}
# Constraints: a ∈ [-12, 12]\{{0}}, b ∈ [-60, 60] (divisible by a)
# Answer: x = b / a
```

### Multi-Step Equations

**Medium**
```
Solve for x: {{a}}x + {{b}} = {{c}}
# Constraints: a ∈ [-10, 10]\{{0}}, b ∈ [-20, 20], c ∈ [-50, 50]
# Answer: x = (c - b) / a
```

**Hard**
```
Solve for x: {{a}}(x + {{b}}) = {{c}}x + {{d}}
# Constraints: a ∈ [2, 8], b ∈ [-10, 10], c ∈ [1, 7], c ≠ a, d ∈ [-30, 30]
# Answer: x = (d - a×b) / (a - c)
```

### Inequalities

**Easy**
```
Solve the inequality: x + {{a}} < {{b}}
# Constraints: a ∈ [-15, 15], b ∈ [-20, 20]
# Answer: x < b - a
```

**Medium**
```
Solve the inequality: {{a}}x - {{b}} ≥ {{c}}
# Constraints: a ∈ [2, 10], b ∈ [1, 20], c ∈ [-30, 30]
# Answer: x ≥ (c + b) / a
```

**Hard**
```
Solve the compound inequality: {{a}} < {{b}}x + {{c}} ≤ {{d}}
# Constraints: a ∈ [-20, 10], b ∈ [2, 8], c ∈ [-10, 10], d ∈ [a+1, 30]
# Answer: (a - c) / b < x ≤ (d - c) / b
```

---

## 9. Lines and Angles

### Types of Lines

**Easy**
```
Lines AB and CD are {{relationship}}. If they are cut by a transversal, which pairs of angles are equal?
# Constraints: relationship ∈ ["parallel", "perpendicular"]
# Answer: Depends on relationship; parallel → corresponding angles, alternate angles; perpendicular → all angles are 90°
```

### Types of Angles

**Easy**
```
Classify an angle measuring {{angle}}°.
# Constraints: angle ∈ [1, 359]
# Answer: acute (0<x<90), right (90), obtuse (90<x<180), straight (180), reflex (180<x<360)
```

**Medium**
```
An angle measures {{a}}° more than its complement. Find the angle.
# Constraints: a ∈ [2, 80] (even preferred for cleaner answer)
# Answer: (90 + a) / 2 degrees
```

**Hard**
```
An angle is {{a}}° less than {{multiplier}} times its supplement. Find the angle.
# Constraints: a ∈ [10, 50], multiplier ∈ [2, 4]
# Answer: (180 × multiplier - a) / (multiplier + 1) degrees
```

---

## 10. Angle Relationships

### Complementary and Supplementary Angles

**Easy**
```
Find the complement of {{a}}°.
# Constraints: a ∈ [1, 89]
# Answer: 90 - a degrees
```

**Easy**
```
Find the supplement of {{a}}°.
# Constraints: a ∈ [1, 179]
# Answer: 180 - a degrees
```

**Medium**
```
Two complementary angles are in the ratio {{m}}:{{n}}. Find both angles.
# Constraints: m ∈ [1, 8], n ∈ [1, 8], m ≠ n
# Answer: 90m/(m+n) and 90n/(m+n) degrees
```

### Angles Formed by Parallel Lines and Transversal

**Medium**
```
Two parallel lines are cut by a transversal. If one of the corresponding angles is {{a}}°, find all eight angles formed.
# Constraints: a ∈ [30, 150]
# Answer: Four angles of a° and four angles of (180 - a)°
```

**Hard**
```
In the figure, lines l and m are parallel. If ∠1 = ({{a}}x + {{b}})° and ∠2 = ({{c}}x + {{d}})°, and they are {{relationship}}, find x.
# Constraints: a ∈ [2, 5], b ∈ [5, 30], c ∈ [2, 5], d ∈ [5, 30], relationship ∈ ["corresponding angles", "alternate interior angles", "co-interior angles"]
# Answer: If equal (corresponding/alternate): x = (d - b)/(a - c); If supplementary (co-interior): x = (180 - b - d)/(a + c)
```

### Vertical Angles

**Medium**
```
Two lines intersect. One pair of vertical angles measures ({{a}}x + {{b}})° and ({{c}}x + {{d}})°. Find the value of x and the measure of each angle.
# Constraints: a ∈ [2, 6], b ∈ [5, 40], c ∈ [1, 5], c < a, d ∈ [10, 50], d > b
# Answer: x = (d - b) / (a - c); angle = a × x + b
```

---

## 11. Linear Equations

### Linear Equations in One Variable

**Easy**
```
Solve: {{a}}x + {{b}} = {{c}}
# Constraints: a ∈ [2, 12], b ∈ [-20, 20], c ∈ [-50, 50]
# Answer: x = (c - b) / a
```

**Medium**
```
Solve: {{a}}x - {{b}} = {{c}}x + {{d}}
# Constraints: a ∈ [3, 10], b ∈ [1, 20], c ∈ [1, a-1], d ∈ [1, 30]
# Answer: x = (d + b) / (a - c)
```

**Hard**
```
Solve: ({{a}}x + {{b}}) / {{c}} = ({{d}}x - {{e}}) / {{f}}
# Constraints: a, d ∈ [2, 6], b, e ∈ [1, 15], c, f ∈ [2, 5]
# Answer: x = (c × e + f × b) / (f × a - c × d)  [assuming f×a ≠ c×d]
```

### Linear Equations in Two Variables

**Easy**
```
Find the value of y when x = {{x_val}} in the equation {{a}}x + {{b}}y = {{c}}.
# Constraints: a ∈ [1, 5], b ∈ [1, 5], c ∈ [10, 50], x_val ∈ [0, 10]
# Answer: y = (c - a × x_val) / b
```

**Medium**
```
A {{item1}} costs ${{p}} and a {{item2}} costs ${{q}}. {{name}} spent ${{total}} buying some of each. If they bought {{n}} {{item1_plural}}, how many {{item2_plural}} did they buy?
# Constraints: p ∈ [2, 10], q ∈ [3, 15], n ∈ [1, 10], total = p×n + q×m for some integer m
# Answer: m = (total - p × n) / q
```

**Hard**
```
Solve the system of equations:
{{a1}}x + {{b1}}y = {{c1}}
{{a2}}x + {{b2}}y = {{c2}}
# Constraints: a1, a2, b1, b2 ∈ [1, 6], c1, c2 ∈ [5, 30], (a1×b2 ≠ a2×b1 for unique solution)
# Answer: Using elimination or substitution
```

---

## 12. Functions

### Domain and Range

**Easy**
```
What is the domain of f(x) = x + {{a}}?
# Constraints: a ∈ [-20, 20]
# Answer: All real numbers
```

**Medium**
```
Find the domain and range of f(x) = √(x - {{a}}).
# Constraints: a ∈ [-10, 10]
# Answer: Domain: x ≥ a; Range: y ≥ 0
```

**Hard**
```
Find the domain of f(x) = {{a}} / (x² - {{b}}).
# Constraints: a ∈ [1, 10], b ∈ {1, 4, 9, 16, 25} (perfect squares)
# Answer: All real numbers except x = ±√b
```

### Linear Functions

**Easy**
```
Evaluate f({{x_val}}) if f(x) = {{m}}x + {{b}}.
# Constraints: m ∈ [-5, 5], b ∈ [-10, 10], x_val ∈ [-10, 10]
# Answer: m × x_val + b
```

**Medium**
```
The function f(x) = {{m}}x + {{b}} passes through the point ({{x1}}, {{y1}}). Find the value of b.
# Constraints: m ∈ [-5, 5]\{{0}}, x1 ∈ [-5, 5], y1 ∈ [-20, 20], b = y1 - m × x1
# Answer: b = y1 - m × x1
```

**Hard**
```
A linear function passes through the points ({{x1}}, {{y1}}) and ({{x2}}, {{y2}}). Find the function in slope-intercept form.
# Constraints: x1, x2 ∈ [-5, 5], x1 ≠ x2, y1, y2 ∈ [-10, 10]
# Answer: m = (y2 - y1) / (x2 - x1); b = y1 - m × x1; f(x) = mx + b
```

---

## 13. Scientific Notation

**Easy**
```
Write {{n}} in scientific notation.
# Constraints: n ∈ [1000, 99999999] or n ∈ [0.000001, 0.01]
# Answer: a × 10^b where 1 ≤ a < 10
```

**Medium**
```
Simplify and express in scientific notation: ({{a}} × 10^{{m}}) × ({{b}} × 10^{{n}})
# Constraints: a, b ∈ [1.0, 9.9] (one decimal), m, n ∈ [-5, 8]
# Answer: (a × b) × 10^(m + n), adjusted to proper form
```

**Hard**
```
Calculate ({{a}} × 10^{{m}}) / ({{b}} × 10^{{n}}) and express the answer in scientific notation.
# Constraints: a, b ∈ [1.0, 9.9], m ∈ [3, 10], n ∈ [-5, 5]
# Answer: (a / b) × 10^(m - n), adjusted to proper form
```

---

## 14. Unitary Method

**Easy**
```
If {{a}} {{item_plural}} cost ${{cost}}, what is the cost of 1 {{item_singular}}?
# Constraints: a ∈ [2, 12], cost ∈ [10, 100] (divisible by a), item_singular/plural pairs
# Answer: cost / a
```

**Medium**
```
{{a}} machines can produce {{b}} items in {{c}} hours. How many items can {{d}} machines produce in {{e}} hours?
# Constraints: a ∈ [2, 8], b ∈ [100, 1000], c ∈ [2, 8], d ∈ [3, 12], e ∈ [3, 12]
# Answer: (b / (a × c)) × d × e
```

**Hard**
```
If {{a}} people can complete {{b}} tasks in {{c}} days working {{h}} hours per day, how many people are needed to complete {{d}} tasks in {{e}} days working {{g}} hours per day?
# Constraints: a ∈ [3, 10], b ∈ [5, 20], c ∈ [4, 10], h ∈ [6, 10], d ∈ [10, 30], e ∈ [3, 8], g ∈ [8, 12]
# Answer: (a × c × h × d) / (b × e × g)
```

---

## 15. Coordinate Plane

**Easy**
```
Plot the point ({{x}}, {{y}}) and identify which quadrant it lies in.
# Constraints: x ∈ [-10, 10]\{{0}}, y ∈ [-10, 10]\{{0}}
# Answer: Quadrant I (x>0, y>0), II (x<0, y>0), III (x<0, y<0), IV (x>0, y<0)
```

**Medium**
```
Find the distance between points A({{x1}}, {{y1}}) and B({{x2}}, {{y2}}).
# Constraints: x1, y1, x2, y2 ∈ [-10, 10]
# Answer: √[(x2-x1)² + (y2-y1)²]
```

**Hard**
```
Find the coordinates of the midpoint and the distance between P({{x1}}, {{y1}}) and Q({{x2}}, {{y2}}).
# Constraints: x1, y1, x2, y2 ∈ [-10, 10]
# Answer: Midpoint = ((x1+x2)/2, (y1+y2)/2); Distance = √[(x2-x1)² + (y2-y1)²]
```

---

## 16. Pythagorean Theorem

**Easy**
```
A right triangle has legs of length {{a}} and {{b}}. Find the length of the hypotenuse.
# Constraints: a, b ∈ [3, 20]
# Answer: √(a² + b²)
```

**Medium**
```
A ladder {{c}} meters long is placed against a wall. The foot of the ladder is {{a}} meters from the wall. How high up the wall does the ladder reach?
# Constraints: c ∈ [5, 15], a ∈ [3, c-1]
# Answer: √(c² - a²) meters
```

**Hard**
```
In a right triangle, one leg is {{a}} cm and the hypotenuse is {{b}} cm longer than the other leg. Find the lengths of all sides.
# Constraints: a ∈ [5, 12], b ∈ [1, 5]
# Let other leg = x. Then a² + x² = (x + b)²
# Answer: x = (a² - b²) / (2b); sides are a, x, x + b
```

### Pythagorean Triples

**Medium**
```
Determine if ({{a}}, {{b}}, {{c}}) is a Pythagorean triple.
# Constraints: a, b, c ∈ [3, 50], a < b < c
# Answer: Yes if a² + b² = c², No otherwise
```

**Hard**
```
Generate a Pythagorean triple using m = {{m}} and n = {{n}} where m > n > 0.
# Constraints: m ∈ [2, 10], n ∈ [1, m-1]
# Answer: a = m² - n², b = 2mn, c = m² + n²
```

---

## 17. Slope of a Line

**Easy**
```
Find the slope of the line passing through ({{x1}}, {{y1}}) and ({{x2}}, {{y2}}).
# Constraints: x1, x2 ∈ [-10, 10], x1 ≠ x2, y1, y2 ∈ [-10, 10]
# Answer: (y2 - y1) / (x2 - x1)
```

**Medium**
```
A line has a slope of {{m}} and passes through point ({{x1}}, {{y1}}). Find the y-intercept.
# Constraints: m ∈ [-5, 5]\{{0}}, x1 ∈ [-5, 5], y1 ∈ [-10, 10]
# Answer: b = y1 - m × x1
```

**Hard**
```
Line L₁ passes through ({{x1}}, {{y1}}) and ({{x2}}, {{y2}}). Line L₂ passes through ({{x3}}, {{y3}}) and ({{x4}}, {{y4}}). Are the lines parallel, perpendicular, or neither?
# Constraints: all coordinates ∈ [-10, 10], x1 ≠ x2, x3 ≠ x4
# Answer: Parallel if m1 = m2; Perpendicular if m1 × m2 = -1; Neither otherwise
```

---

## 18. Word Problems - Mixed Applications

### Age Problems

**Easy**
```
{{name}} is {{a}} years old. In {{b}} years, how old will they be?
# Constraints: a ∈ [5, 60], b ∈ [1, 30]
# Answer: a + b years
```

**Medium**
```
{{name1}} is {{a}} years older than {{name2}}. If the sum of their ages is {{s}}, find their ages.
# Constraints: a ∈ [2, 20], s ∈ [20, 100], s > 2a
# Answer: name2 = (s - a) / 2; name1 = (s + a) / 2
```

**Hard**
```
{{a}} years ago, {{name1}} was {{m}} times as old as {{name2}}. Now {{name1}} is {{n}} times as old as {{name2}}. Find their present ages.
# Constraints: a ∈ [2, 10], m ∈ [3, 6], n ∈ [2, m-1]
# Let name2's current age = x. Then (nx - a) = m(x - a)
# Answer: name2 = a(m - 1) / (m - n); name1 = n × name2
```

### Distance-Speed-Time

**Easy**
```
A car travels at {{speed}} km/h for {{time}} hours. How far does it travel?
# Constraints: speed ∈ [30, 120], time ∈ [1, 8]
# Answer: speed × time km
```

**Medium**
```
{{name}} travels from City A to City B at {{v1}} km/h and returns at {{v2}} km/h. If the total distance is {{d}} km each way, find the average speed for the entire journey.
# Constraints: v1 ∈ [40, 80], v2 ∈ [50, 100], d ∈ [50, 200]
# Answer: 2 × v1 × v2 / (v1 + v2) km/h
```

**Hard**
```
Two trains start from stations {{d}} km apart and travel toward each other. The first train travels at {{v1}} km/h and the second at {{v2}} km/h. How long until they meet, and how far from the first station?
# Constraints: d ∈ [100, 500], v1 ∈ [40, 100], v2 ∈ [50, 120]
# Answer: Time = d / (v1 + v2) hours; Distance from first station = v1 × time km
```

### Work Problems

**Easy**
```
{{name}} can complete a job in {{a}} hours. What fraction of the job can they complete in 1 hour?
# Constraints: a ∈ [2, 12]
# Answer: 1/a
```

**Medium**
```
{{name1}} can complete a task in {{a}} hours and {{name2}} can complete it in {{b}} hours. How long will it take them working together?
# Constraints: a ∈ [4, 12], b ∈ [3, 10], a ≠ b
# Answer: (a × b) / (a + b) hours
```

**Hard**
```
{{name1}} and {{name2}} together can complete a job in {{t}} hours. {{name1}} alone takes {{a}} hours more than {{name2}} alone. Find the time each takes individually.
# Constraints: t ∈ [4, 10], a ∈ [2, 8]
# Let name2's time = x. Then 1/x + 1/(x+a) = 1/t → solve quadratic
# Answer: name2 = (-a + √(a² + 4at)) / 2; name1 = name2 + a
```
