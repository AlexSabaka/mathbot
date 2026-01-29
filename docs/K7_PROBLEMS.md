# 7th Grade Math Problem Templates

## 1. Integers

### Positive and Negative Numbers

**Easy:**
> The temperature in {{city}} was {{a}}°C in the morning. By evening, it dropped by {{b}}°C. What is the temperature now?
> 
> *Constraints: a ∈ [-20, 30], b ∈ [1, 15], result can be negative*

**Medium:**
> {{name}} has \${{a}} in their bank account. They spend \${{b}} on {{item_1}} and \${{c}} on {{item_2}}. Then they deposit \${{d}}. What is their final balance?
> 
> *Constraints: a ∈ [50, 500], b + c < a, d ∈ [10, 100]*

**Hard:**
> A submarine is at {{a}} meters below sea level. It rises {{b}} meters, then dives {{c}} meters, and finally rises {{d}} meters. What is its final position relative to sea level?
> 
> *Constraints: a ∈ [100, 500], b, c, d ∈ [20, 150]*

---

### Absolute Value

**Easy:**
> What is the absolute value of {{a}}?
> 
> *Constraints: a ∈ [-100, 100]*

**Medium:**
> The elevation of {{location_1}} is {{a}} feet below sea level, and {{location_2}} is {{b}} feet above sea level. Which location has a greater absolute elevation?
> 
> *Constraints: a, b ∈ [1, 1000]*

**Hard:**
> Find all integers whose absolute value is less than {{a}} and greater than {{b}}.
> 
> *Constraints: a ∈ [5, 15], b ∈ [0, a-2]*

---

## 2. Operations with Integers

### Addition and Subtraction of Integers

**Easy:**
> Calculate: {{a}} + ({{b}})
> 
> *Constraints: a ∈ [-50, 50], b ∈ [-50, 50]*

**Medium:**
> A football team gained {{a}} yards on the first play, lost {{b}} yards on the second play, and gained {{c}} yards on the third play. What was their total yard change?
> 
> *Constraints: a, c ∈ [1, 30], b ∈ [1, 20]*

**Hard:**
> The temperature at midnight was {{a}}°C. Over the next {{n}} hours, the temperature changed by {{change_list}} degrees respectively each hour. What was the final temperature?
> 
> *Constraints: a ∈ [-20, 20], n ∈ [3, 6], change_list is array of n integers in [-10, 10]*

---

### Multiplication and Division of Integers

**Easy:**
> Calculate: {{a}} × ({{b}})
> 
> *Constraints: a ∈ [-12, 12], b ∈ [-12, 12]*

**Medium:**
> A scuba diver descends {{a}} feet per minute. After {{b}} minutes, what is the diver's position relative to the surface?
> 
> *Constraints: a ∈ [2, 10], b ∈ [3, 15]*

**Hard:**
> The product of three integers is {{product}}. Two of the integers are {{a}} and {{b}}. What is the third integer?
> 
> *Constraints: a, b ∈ [-20, 20] (non-zero), product = a × b × c where c ∈ [-20, 20]*

---

## 3. Decimals

### Place Value and Comparing Decimals

**Easy:**
> What digit is in the {{place}} place in the number {{decimal}}?
> 
> *Constraints: decimal has 3-4 decimal places, place ∈ {tenths, hundredths, thousandths}*

**Medium:**
> Arrange the following decimals from least to greatest: {{d1}}, {{d2}}, {{d3}}, {{d4}}
> 
> *Constraints: d1, d2, d3, d4 ∈ [0.001, 9.999], at least two share same integer part*

**Hard:**
> {{name}} ran the race in {{time_1}} seconds. {{name_2}} finished in {{time_2}} seconds. {{name_3}} finished in {{time_3}} seconds. Rank the runners from fastest to slowest and find the difference between the fastest and slowest times.
> 
> *Constraints: time values ∈ [10.00, 15.00] with 2 decimal places*

---

### Rounding Decimals

**Easy:**
> Round {{decimal}} to the nearest {{place}}.
> 
> *Constraints: decimal ∈ [0.001, 999.999], place ∈ {whole number, tenth, hundredth}*

**Medium:**
> A {{item}} costs ${{price}}. Round the price to the nearest cent, then to the nearest dime, and finally to the nearest dollar.
> 
> *Constraints: price ∈ [1.001, 99.999] with 3 decimal places*

**Hard:**
> {{name}} measured the length of a {{object}} as {{measurement}} {{unit}}. The measurement needs to be reported with {{n}} decimal places. What should {{name}} report, and what is the maximum possible error in this rounded measurement?
> 
> *Constraints: measurement ∈ [1.0001, 50.9999], n ∈ [1, 3]*

---

### Converting Fractions and Decimals

**Easy:**
> Convert {{numerator}}/{{denominator}} to a decimal.
> 
> *Constraints: denominator ∈ {2, 4, 5, 8, 10, 20, 25}, numerator < denominator*

**Medium:**
> Convert {{decimal}} to a fraction in lowest terms.
> 
> *Constraints: decimal is terminating with 1-3 decimal places*

**Hard:**
> {{name_1}} ate {{fraction}} of a pizza. {{name_2}} ate {{decimal}} of the same-sized pizza. Who ate more, and by how much?
> 
> *Constraints: fraction and decimal should convert to comparable but different values*

---

## 4. Operations with Decimals

### Addition and Subtraction

**Easy:**
> Calculate: {{a}} + {{b}}
> 
> *Constraints: a, b ∈ [0.1, 99.99] with varying decimal places*

**Medium:**
> {{name}} bought a {{item_1}} for ${{price_1}} and a {{item_2}} for ${{price_2}}. They paid with a ${{bill}} bill. How much change did they receive?
> 
> *Constraints: price_1 + price_2 < bill, bill ∈ {10, 20, 50, 100}*

**Hard:**
> A rectangle has a perimeter of {{perimeter}} cm. If the length is {{length}} cm, what is the width?
> 
> *Constraints: perimeter ∈ [10.0, 100.0], length < perimeter/2*

---

### Multiplying Decimals

**Easy:**
> Calculate: {{a}} × {{b}}
> 
> *Constraints: a ∈ [0.1, 9.9], b ∈ [1, 10]*

**Medium:**
> {{name}} worked {{hours}} hours at ${{rate}} per hour. How much did they earn?
> 
> *Constraints: hours ∈ [1.5, 40.0], rate ∈ [8.50, 25.00]*

**Hard:**
> A rectangular garden has dimensions {{length}} m by {{width}} m. If fertilizer costs ${{cost}} per square meter, how much will it cost to fertilize the entire garden?
> 
> *Constraints: length, width ∈ [2.5, 20.0], cost ∈ [0.50, 5.00]*

---

### Dividing Decimals

**Easy:**
> Calculate: {{a}} ÷ {{b}}
> 
> *Constraints: a ∈ [1, 100], b ∈ [0.1, 10], result is terminating decimal*

**Medium:**
> {{name}} has {{total}} meters of ribbon to make {{count}} identical bows. How much ribbon will each bow use?
> 
> *Constraints: total ∈ [5.0, 50.0], count ∈ [3, 12]*

**Hard:**
> A car traveled {{distance}} km using {{fuel}} liters of fuel. Another car traveled {{distance_2}} km using {{fuel_2}} liters. Which car is more fuel-efficient, and by how much (in km per liter)?
> 
> *Constraints: distances ∈ [100, 500], fuels ∈ [8, 40]*

---

## 5. Fractions

### Types of Fractions

**Easy:**
> Identify whether {{numerator}}/{{denominator}} is a proper fraction, improper fraction, or mixed number.
> 
> *Constraints: numerator, denominator ∈ [1, 20]*

**Medium:**
> Convert {{whole}} {{numerator}}/{{denominator}} to an improper fraction.
> 
> *Constraints: whole ∈ [1, 10], numerator < denominator, denominator ∈ [2, 12]*

**Hard:**
> Simplify {{numerator}}/{{denominator}} to its lowest terms and express it as a mixed number if applicable.
> 
> *Constraints: numerator ∈ [10, 100], denominator ∈ [2, 50], GCD > 1*

---

### Equivalent Fractions

**Easy:**
> Find an equivalent fraction to {{numerator}}/{{denominator}} with a denominator of {{new_denom}}.
> 
> *Constraints: new_denom is a multiple of denominator*

**Medium:**
> Are {{n1}}/{{d1}} and {{n2}}/{{d2}} equivalent fractions? Show your reasoning.
> 
> *Constraints: fractions may or may not be equivalent*

**Hard:**
> Find the missing value: {{n1}}/{{d1}} = {{n2}}/? = ?/{{d3}}
> 
> *Constraints: all three fractions should be equivalent*

---

## 6. Operations with Fractions

### Addition and Subtraction

**Easy:**
> Calculate: {{n1}}/{{d}} + {{n2}}/{{d}}
> 
> *Constraints: same denominator, d ∈ [2, 12], result < 2*

**Medium:**
> Calculate: {{n1}}/{{d1}} + {{n2}}/{{d2}}
> 
> *Constraints: different denominators with common LCM, result simplifies*

**Hard:**
> {{name}} studied for {{mixed_1}} hours on Monday and {{mixed_2}} hours on Tuesday. How many total hours did they study? Express your answer as a mixed number in simplest form.
> 
> *Constraints: mixed numbers with different denominators*

---

### Multiplication of Fractions

**Easy:**
> Calculate: {{n1}}/{{d1}} × {{n2}}/{{d2}}
> 
> *Constraints: small numerators and denominators ∈ [1, 6]*

**Medium:**
> A recipe calls for {{fraction}} cup of flour. If {{name}} wants to make {{multiplier}} times the recipe, how much flour is needed?
> 
> *Constraints: fraction is simple, multiplier ∈ {1/2, 2, 3, 2½}*

**Hard:**
> A rectangular field is {{mixed_1}} km long and {{mixed_2}} km wide. What is the area of the field in square kilometers? Express as a mixed number.
> 
> *Constraints: mixed numbers that multiply to give interesting result*

---

### Division of Fractions

**Easy:**
> Calculate: {{n1}}/{{d1}} ÷ {{n2}}/{{d2}}
> 
> *Constraints: result is whole number or simple fraction*

**Medium:**
> {{name}} has {{total}} pounds of {{item}} to divide equally into bags of {{portion}} pound each. How many bags can they fill?
> 
> *Constraints: total ∈ [2, 10], portion is simple fraction*

**Hard:**
> A board is {{mixed_length}} feet long. It needs to be cut into pieces that are {{mixed_piece}} feet long each. How many complete pieces can be cut, and how much board is left over?
> 
> *Constraints: mixed numbers, result has remainder*

---

## 7. Rational Numbers

### Identifying and Comparing

**Easy:**
> Is {{number}} a rational number? Explain why or why not.
> 
> *Constraints: number ∈ {fractions, decimals, integers, √2, π, 0}*

**Medium:**
> Order the following rational numbers from least to greatest: {{n1}}/{{d1}}, -{{n2}}/{{d2}}, {{decimal}}, -{{n3}}/{{d3}}
> 
> *Constraints: mix of positive and negative, some equivalent to compare*

**Hard:**
> Find three rational numbers between {{n1}}/{{d1}} and {{n2}}/{{d2}}.
> 
> *Constraints: fractions are close together, requiring careful selection*

---

### Operations on Rational Numbers

**Easy:**
> Calculate: -{{n1}}/{{d1}} × {{n2}}/{{d2}}
> 
> *Constraints: small values, result simplifies*

**Medium:**
> The temperature dropped by {{fraction_1}} degrees per hour for {{hours}} hours. What was the total temperature change?
> 
> *Constraints: fraction_1 involves simple values*

**Hard:**
> Evaluate: ({{n1}}/{{d1}} + {{n2}}/{{d2}}) ÷ ({{n3}}/{{d3}} - {{n4}}/{{d4}})
> 
> *Constraints: result is defined (no division by zero) and simplifies*

---

## 8. Exponents

### Basic Exponents

**Easy:**
> Evaluate: {{base}}^{{exp}}
> 
> *Constraints: base ∈ [2, 10], exp ∈ [2, 4]*

**Medium:**
> Write {{large_number}} as a power of {{base}}.
> 
> *Constraints: large_number is a perfect power of base*

**Hard:**
> A bacteria colony doubles every hour. If there are {{initial}} bacteria at the start, how many will there be after {{hours}} hours?
> 
> *Constraints: initial ∈ [1, 100], hours ∈ [3, 8]*

---

### Laws of Exponents

**Easy:**
> Simplify: {{base}}^{{a}} × {{base}}^{{b}}
> 
> *Constraints: base ∈ [2, 10], a, b ∈ [1, 5]*

**Medium:**
> Simplify: ({{base}}^{{a}})^{{b}}
> 
> *Constraints: base ∈ [2, 5], a, b ∈ [2, 4]*

**Hard:**
> Simplify and evaluate: ({{base_1}}^{{a}} × {{base_1}}^{{b}}) ÷ {{base_1}}^{{c}}
> 
> *Constraints: a + b > c, final result is reasonable*

---

### Negative Exponents

**Easy:**
> Evaluate: {{base}}^{-exp}
> 
> *Constraints: base ∈ [2, 10], exp ∈ [1, 3]*

**Medium:**
> Write {{fraction}} as a power with a negative exponent.
> 
> *Constraints: fraction = 1/base^n for integer base and n*

**Hard:**
> Simplify: {{base}}^{{a}} × {{base}}^{-b} ÷ {{base}}^{-c}
> 
> *Constraints: result can be positive or negative exponent*

---

## 9. Ratio and Proportion

### Ratios

**Easy:**
> In a class, there are {{boys}} boys and {{girls}} girls. What is the ratio of boys to girls in simplest form?
> 
> *Constraints: boys, girls ∈ [5, 30], GCD > 1*

**Medium:**
> A recipe uses {{flour}} cups of flour and {{sugar}} cups of sugar. If {{name}} uses {{new_flour}} cups of flour, how much sugar should they use to maintain the same ratio?
> 
> *Constraints: values allow clean proportion*

**Hard:**
> Three numbers are in the ratio {{a}}:{{b}}:{{c}}. If their sum is {{sum}}, find each number.
> 
> *Constraints: sum is divisible by (a + b + c)*

---

### Direct Proportion

**Easy:**
> If {{a}} {{item_plural}} cost ${{cost}}, how much do {{b}} {{item_plural}} cost?
> 
> *Constraints: b/a gives clean ratio*

**Medium:**
> A car travels {{distance_1}} km in {{time_1}} hours. At the same speed, how long will it take to travel {{distance_2}} km?
> 
> *Constraints: proportions work out to reasonable times*

**Hard:**
> {{workers_1}} workers can complete a job in {{days_1}} days. If they work at the same rate, how many days would it take {{workers_2}} workers to complete {{fraction}} of the same job?
> 
> *Constraints: involves inverse proportion concept*

---

### Inverse Proportion

**Easy:**
> If {{a}} workers can complete a task in {{b}} days, how many days would it take {{c}} workers?
> 
> *Constraints: a × b = c × result, result is integer*

**Medium:**
> A car traveling at {{speed_1}} km/h takes {{time_1}} hours to reach a destination. How long would the trip take at {{speed_2}} km/h?
> 
> *Constraints: speed × time = constant*

**Hard:**
> A pipe can fill a tank in {{time_1}} hours. A second pipe can fill the same tank in {{time_2}} hours. How long would it take to fill the tank if both pipes are used together?
> 
> *Constraints: times that give reasonable combined time*

---

## 10. Algebraic Expressions

### Evaluating Expressions

**Easy:**
> If x = {{x_val}}, evaluate: {{a}}x + {{b}}
> 
> *Constraints: a, b, x_val ∈ [-10, 10]*

**Medium:**
> If a = {{a_val}} and b = {{b_val}}, evaluate: {{coef_1}}a² + {{coef_2}}b - {{coef_3}}
> 
> *Constraints: values give integer result*

**Hard:**
> If x = {{x_val}} and y = {{y_val}}, evaluate: ({{coef_1}}x - {{coef_2}}y)² + {{coef_3}}xy
> 
> *Constraints: values manageable for calculation*

---

### Simplifying Expressions

**Easy:**
> Simplify: {{a}}x + {{b}}x
> 
> *Constraints: a, b ∈ [-10, 10]*

**Medium:**
> Simplify: {{a}}x + {{b}}y - {{c}}x + {{d}}y
> 
> *Constraints: coefficients ∈ [-12, 12]*

**Hard:**
> Simplify: {{a}}(x + {{b}}) - {{c}}({{d}}x - {{e}})
> 
> *Constraints: coefficients ∈ [-5, 10], result has x and constant term*

---

### Types of Expressions

**Easy:**
> Identify whether {{expression}} is a monomial, binomial, trinomial, or polynomial.
> 
> *Constraints: expression has 1-5 terms*

**Medium:**
> Write a trinomial with variable {{var}}, where the coefficient of the squared term is {{a}}, the linear coefficient is {{b}}, and the constant is {{c}}.
> 
> *Constraints: a, b, c ∈ [-10, 10], a ≠ 0*

**Hard:**
> Find the sum of the polynomial {{poly_1}} and the polynomial {{poly_2}}. Identify what type of polynomial the result is.
> 
> *Constraints: polynomials of degree 2-3*

---

## 11. Linear Equations

### One-Step Equations

**Easy:**
> Solve for x: x + {{a}} = {{b}}
> 
> *Constraints: a, b ∈ [-20, 20]*

**Easy (Variant):**
> Solve for x: {{a}}x = {{b}}
> 
> *Constraints: b is divisible by a*

---

### Two-Step Equations

**Medium:**
> Solve for x: {{a}}x + {{b}} = {{c}}
> 
> *Constraints: (c - b) is divisible by a*

**Medium (Word Problem):**
> {{name}} has ${{initial}}. They earn ${{rate}} for each {{task}} they complete. After completing some {{task_plural}}, they have ${{total}}. How many {{task_plural}} did they complete?
> 
> *Constraints: (total - initial) / rate is positive integer*

---

### Multi-Step Equations

**Hard:**
> Solve for x: {{a}}x + {{b}} = {{c}}x + {{d}}
> 
> *Constraints: a ≠ c, solution is integer or simple fraction*

**Hard:**
> Solve for x: {{a}}(x + {{b}}) = {{c}}(x - {{d}}) + {{e}}
> 
> *Constraints: solution is integer*

**Hard (Word Problem):**
> {{name_1}} and {{name_2}} are saving money. {{name_1}} has ${{initial_1}} and saves ${{rate_1}} per week. {{name_2}} has ${{initial_2}} and saves ${{rate_2}} per week. After how many weeks will they have the same amount?
> 
> *Constraints: rates differ, initial amounts differ, solution is positive integer*

---

### Equations with Fractions

**Medium:**
> Solve for x: x/{{a}} + {{b}} = {{c}}
> 
> *Constraints: a ∈ [2, 10], solution is integer*

**Hard:**
> Solve for x: ({{a}}x + {{b}})/{{c}} = {{d}}
> 
> *Constraints: solution is integer or simple fraction*

**Hard:**
> Solve for x: {{n1}}/{{d1}}x - {{n2}}/{{d2}} = {{n3}}/{{d3}}
> 
> *Constraints: solution is integer or simple fraction*

---

## 12. Linear Equations in Two Variables

### Writing Equations

**Easy:**
> Write an equation relating x and y: The sum of x and y is {{sum}}.
> 
> *Constraints: sum ∈ [5, 100]*

**Medium:**
> {{name}} bought {{a}} notebooks and {{b}} pens for ${{total}}. If each notebook costs $x and each pen costs $y, write an equation to represent this situation.
> 
> *Constraints: a, b ∈ [1, 10], total is reasonable*

---

### Finding Solutions

**Medium:**
> Find three solutions to the equation: {{a}}x + {{b}}y = {{c}}
> 
> *Constraints: integer solutions exist*

**Hard:**
> Solve the system:
> {{a1}}x + {{b1}}y = {{c1}}
> {{a2}}x + {{b2}}y = {{c2}}
> 
> *Constraints: unique integer solution*

**Hard (Word Problem):**
> The sum of two numbers is {{sum}} and their difference is {{diff}}. Find the two numbers.
> 
> *Constraints: (sum + diff) is even*

---

## 13. Inequalities

### Writing and Solving Inequalities

**Easy:**
> Solve: x + {{a}} > {{b}}
> 
> *Constraints: a, b ∈ [-10, 20]*

**Medium:**
> Solve and graph on a number line: {{a}}x - {{b}} ≤ {{c}}
> 
> *Constraints: solution is integer or simple fraction*

**Hard:**
> {{name}} has ${{budget}} to spend. They want to buy a {{item_1}} that costs ${{fixed_cost}} and some {{item_2_plural}} that cost ${{variable_cost}} each. Write and solve an inequality to find the maximum number of {{item_2_plural}} they can buy.
> 
> *Constraints: budget > fixed_cost, answer is positive integer*

---

### Compound Inequalities

**Hard:**
> Solve: {{a}} < {{b}}x + {{c}} ≤ {{d}}
> 
> *Constraints: solution interval is non-empty*

**Hard:**
> The perimeter of a rectangle must be at least {{min_p}} cm and at most {{max_p}} cm. If the length is {{length}} cm, what are the possible values for the width?
> 
> *Constraints: solution gives positive width values*

---

## 14. Geometry - Triangles

### Types and Properties

**Easy:**
> A triangle has angles measuring {{a}}°, {{b}}°, and {{c}}°. Classify this triangle by its angles.
> 
> *Constraints: a + b + c = 180*

**Medium:**
> Two angles of a triangle measure {{a}}° and {{b}}°. Find the third angle and classify the triangle.
> 
> *Constraints: a + b < 180*

**Hard:**
> In triangle ABC, angle A is {{mult}} times angle B, and angle C is {{diff}}° more than angle B. Find all three angles.
> 
> *Constraints: mult × B + B + (B + diff) = 180, B is positive integer*

---

### Triangle Inequality Theorem

**Medium:**
> Can a triangle have sides of length {{a}} cm, {{b}} cm, and {{c}} cm? Explain using the Triangle Inequality Theorem.
> 
> *Constraints: may or may not satisfy theorem*

**Hard:**
> Two sides of a triangle have lengths {{a}} cm and {{b}} cm. What are the possible lengths for the third side?
> 
> *Constraints: a, b ∈ [3, 20]*

---

### Area and Perimeter of Triangles

**Easy:**
> Find the area of a triangle with base {{b}} cm and height {{h}} cm.
> 
> *Constraints: b, h ∈ [2, 20]*

**Medium:**
> A triangle has sides of {{a}} cm, {{b}} cm, and {{c}} cm. Find its perimeter. If the height to the longest side is {{h}} cm, find the area.
> 
> *Constraints: valid triangle, height given*

**Hard:**
> The perimeter of an isosceles triangle is {{perimeter}} cm. If the base is {{base}} cm, find the length of each equal side and the area if the height is {{height}} cm.
> 
> *Constraints: (perimeter - base) is even*

---

## 15. Geometry - Quadrilaterals

### Area of Rectangles and Squares

**Easy:**
> Find the area of a rectangle with length {{l}} cm and width {{w}} cm.
> 
> *Constraints: l, w ∈ [2, 50]*

**Medium:**
> A rectangular garden has an area of {{area}} m² and a length of {{length}} m. Find the width and perimeter of the garden.
> 
> *Constraints: area is divisible by length*

**Hard:**
> A rectangular pool is surrounded by a walkway that is {{walk_width}} m wide. If the pool is {{pool_l}} m by {{pool_w}} m, what is the area of the walkway?
> 
> *Constraints: all values ∈ [2, 30]*

---

### Area of Parallelograms

**Easy:**
> Find the area of a parallelogram with base {{b}} cm and height {{h}} cm.
> 
> *Constraints: b, h ∈ [3, 25]*

**Medium:**
> A parallelogram has an area of {{area}} cm² and a base of {{base}} cm. Find the height.
> 
> *Constraints: area divisible by base*

**Hard:**
> The base of a parallelogram is {{mult}} times its height. If the area is {{area}} cm², find the base and height.
> 
> *Constraints: area = mult × h², h is integer*

---

### Area of Trapezoids

**Easy:**
> Find the area of a trapezoid with parallel sides {{a}} cm and {{b}} cm, and height {{h}} cm.
> 
> *Constraints: a, b, h ∈ [3, 20]*

**Medium:**
> A trapezoid has an area of {{area}} cm². If the parallel sides are {{a}} cm and {{b}} cm, find the height.
> 
> *Constraints: area = (a + b) × h / 2, h is integer*

**Hard:**
> One parallel side of a trapezoid is {{diff}} cm longer than the other. The height is {{h}} cm and the area is {{area}} cm². Find the lengths of the parallel sides.
> 
> *Constraints: solve 2·area = (x + x + diff)·h*

---

### Area of Rhombus

**Medium:**
> Find the area of a rhombus with diagonals of length {{d1}} cm and {{d2}} cm.
> 
> *Constraints: d1, d2 ∈ [4, 24]*

**Hard:**
> A rhombus has a perimeter of {{perimeter}} cm. If one diagonal is {{d1}} cm, find the other diagonal and the area. (Use that diagonals bisect each other at right angles)
> 
> *Constraints: side = perimeter/4, use Pythagorean theorem*

---

## 16. Geometry - Circles

### Circumference

**Easy:**
> Find the circumference of a circle with radius {{r}} cm. (Use π = {{pi_approx}})
> 
> *Constraints: r ∈ [1, 20], pi_approx ∈ {3.14, 22/7, π}*

**Medium:**
> A circular track has a diameter of {{d}} meters. How far does {{name}} travel if they run around the track {{laps}} times?
> 
> *Constraints: d ∈ [50, 400], laps ∈ [1, 10]*

**Hard:**
> The circumference of a circle is {{C}} cm. Find the radius and diameter.
> 
> *Constraints: C/π gives nice value*

---

### Area of Circle

**Easy:**
> Find the area of a circle with radius {{r}} cm. (Use π = {{pi_approx}})
> 
> *Constraints: r ∈ [1, 15]*

**Medium:**
> A circular pizza has a diameter of {{d}} inches. What is the area of the pizza?
> 
> *Constraints: d ∈ [8, 24]*

**Hard:**
> A circular garden has an area of {{area}} m². A path {{width}} m wide is built around it. What is the area of the path?
> 
> *Constraints: original radius can be derived from area*

---

## 17. Geometry - Angles

### Complementary and Supplementary Angles

**Easy:**
> Find the complement of a {{angle}}° angle.
> 
> *Constraints: angle ∈ [1, 89]*

**Easy (Variant):**
> Find the supplement of a {{angle}}° angle.
> 
> *Constraints: angle ∈ [1, 179]*

**Medium:**
> Two complementary angles are in the ratio {{a}}:{{b}}. Find both angles.
> 
> *Constraints: 90 is divisible by (a + b)*

**Hard:**
> The supplement of an angle is {{mult}} times its complement. Find the angle.
> 
> *Constraints: 180 - x = mult(90 - x), solution in (0, 90)*

---

### Vertical and Adjacent Angles

**Medium:**
> Two vertical angles are formed by intersecting lines. If one angle is ({{a}}x + {{b}})° and the other is ({{c}}x + {{d}})°, find x and the measure of the angles.
> 
> *Constraints: a ≠ c, solution gives angle in (0, 180)*

**Hard:**
> Two adjacent angles on a straight line are in the ratio {{a}}:{{b}}. Find both angles, then find the angle vertical to the smaller angle.
> 
> *Constraints: 180 is divisible by (a + b)*

---

## 18. 3D Shapes - Volume

### Cubes and Cuboids

**Easy:**
> Find the volume of a cube with side length {{s}} cm.
> 
> *Constraints: s ∈ [2, 15]*

**Medium:**
> A rectangular box has dimensions {{l}} cm × {{w}} cm × {{h}} cm. What is its volume?
> 
> *Constraints: l, w, h ∈ [2, 30]*

**Hard:**
> A cube has a volume of {{volume}} cm³. Find the side length, then calculate the surface area.
> 
> *Constraints: volume is a perfect cube*

---

### Cylinders

**Easy:**
> Find the volume of a cylinder with radius {{r}} cm and height {{h}} cm.
> 
> *Constraints: r ∈ [2, 10], h ∈ [5, 20]*

**Medium:**
> A cylindrical water tank has a diameter of {{d}} meters and height of {{h}} meters. How many liters of water can it hold? (1 m³ = 1000 liters)
> 
> *Constraints: d, h ∈ [1, 10]*

**Hard:**
> Two cylinders have the same volume. Cylinder A has radius {{r1}} cm and height {{h1}} cm. Cylinder B has radius {{r2}} cm. Find the height of Cylinder B.
> 
> *Constraints: r1² × h1 = r2² × h2, h2 is reasonable*

---

### Cones and Spheres

**Medium:**
> Find the volume of a cone with radius {{r}} cm and height {{h}} cm.
> 
> *Constraints: r ∈ [3, 12], h ∈ [5, 20]*

**Medium (Variant):**
> Find the volume of a sphere with radius {{r}} cm.
> 
> *Constraints: r ∈ [2, 10]*

**Hard:**
> A cone and a sphere have the same radius of {{r}} cm. If they have equal volumes, find the height of the cone.
> 
> *Constraints: (1/3)πr²h = (4/3)πr³, so h = 4r*

---

### Pyramids and Prisms

**Medium:**
> Find the volume of a rectangular pyramid with base dimensions {{l}} cm × {{w}} cm and height {{h}} cm.
> 
> *Constraints: l, w, h ∈ [3, 15]*

**Medium (Variant):**
> Find the volume of a triangular prism with a triangular base of base {{b}} cm and height {{h_tri}} cm, and a prism length of {{length}} cm.
> 
> *Constraints: values ∈ [3, 20]*

**Hard:**
> A square pyramid has a base side of {{s}} cm and a volume of {{volume}} cm³. Find the height of the pyramid.
> 
> *Constraints: volume = (1/3) × s² × h, h is integer*

---

## 19. 3D Shapes - Surface Area

### Cubes and Cuboids

**Easy:**
> Find the surface area of a cube with side length {{s}} cm.
> 
> *Constraints: s ∈ [2, 15]*

**Medium:**
> A gift box has dimensions {{l}} cm × {{w}} cm × {{h}} cm. How much wrapping paper is needed to cover it completely (ignoring overlap)?
> 
> *Constraints: l, w, h ∈ [5, 40]*

**Hard:**
> A cube and a rectangular prism have the same surface area. The cube has side {{s}} cm. The prism has a square base with side {{base}} cm. Find the height of the prism.
> 
> *Constraints: 6s² = 2×base² + 4×base×h, h is positive*

---

### Cylinders

**Medium:**
> Find the total surface area of a cylinder with radius {{r}} cm and height {{h}} cm.
> 
> *Constraints: r ∈ [2, 10], h ∈ [5, 20]*

**Hard:**
> A label covers the curved surface area of a cylindrical can. If the can has diameter {{d}} cm and height {{h}} cm, what is the area of the label?
> 
> *Constraints: curved SA = π × d × h*

---

### Spheres and Cones

**Medium:**
> Find the surface area of a sphere with radius {{r}} cm.
> 
> *Constraints: r ∈ [2, 12]*

**Hard:**
> Find the total surface area of a cone with radius {{r}} cm and slant height {{l}} cm.
> 
> *Constraints: l > r, SA = πr² + πrl*

---

## 20. Statistics - Measures of Central Tendency

### Mean

**Easy:**
> Find the mean of: {{list_of_numbers}}
> 
> *Constraints: 4-7 numbers ∈ [1, 100], sum divisible by count*

**Medium:**
> {{name}}'s test scores are {{score_list}}. What score does {{name}} need on the next test to have a mean of {{target_mean}}?
> 
> *Constraints: target achievable with realistic score*

**Hard:**
> The mean of {{n}} numbers is {{mean}}. When {{new_num}} is added to the set, the new mean is {{new_mean}}. Find {{new_num}}.
> 
> *Constraints: n × mean + new_num = (n+1) × new_mean*

---

### Median

**Easy:**
> Find the median of: {{list_of_numbers}}
> 
> *Constraints: 5-9 numbers, odd count for simple case*

**Medium:**
> Find the median of: {{list_of_numbers}}
> 
> *Constraints: even count, requires averaging middle two*

**Hard:**
> A set of {{n}} numbers has a median of {{median}}. If {{new_num}} is added, what is the new median?
> 
> *Constraints: n is small (5-7), requires reasoning about position*

---

### Mode

**Easy:**
> Find the mode of: {{list_of_numbers}}
> 
> *Constraints: clear single mode*

**Medium:**
> Find the mode(s) of: {{list_of_numbers}}
> 
> *Constraints: bimodal case*

**Hard:**
> The ages of {{n}} people are {{list}}. What age(s) should one more person be to make the mode {{target_mode}}?
> 
> *Constraints: requires strategic thinking*

---

### Combined Statistics

**Hard:**
> A data set has mean {{mean}}, median {{median}}, and mode {{mode}}. If the data set contains {{n}} values and you know {{partial_list}}, find the remaining values.
> 
> *Constraints: solvable with given constraints*

---

## 21. Probability

### Basic Probability

**Easy:**
> A bag contains {{red}} red marbles, {{blue}} blue marbles, and {{green}} green marbles. What is the probability of drawing a {{target_color}} marble?
> 
> *Constraints: total marbles ∈ [5, 30], probability simplifies*

**Medium:**
> A standard die is rolled. What is the probability of rolling a number {{condition}}?
> 
> *Constraints: condition ∈ {greater than 3, less than 5, even, odd, prime}*

**Hard:**
> A card is drawn from a standard deck of 52 cards. What is the probability that it is a {{condition}}?
> 
> *Constraints: condition ∈ {red face card, heart or spade, number less than 5}*

---

### Compound Probability (Independent Events)

**Medium:**
> A coin is flipped {{n}} times. What is the probability of getting heads all {{n}} times?
> 
> *Constraints: n ∈ [2, 5]*

**Hard:**
> A bag has {{red}} red and {{blue}} blue marbles. A marble is drawn, replaced, and another marble is drawn. What is the probability that both marbles are {{color}}?
> 
> *Constraints: probability simplifies nicely*

---

### Compound Probability (Dependent Events)

**Medium:**
> A bag has {{red}} red and {{blue}} blue marbles. A marble is drawn and NOT replaced, then another marble is drawn. What is the probability that both marbles are red?
> 
> *Constraints: red ≥ 2, total reasonable*

**Hard:**
> There are {{n}} students in a class, including {{name_1}} and {{name_2}}. If {{k}} students are randomly selected for a project, what is the probability that both {{name_1}} and {{name_2}} are selected?
> 
> *Constraints: n ∈ [10, 30], k ∈ [2, 5]*

---

## 22. Graphs and Data

### Reading and Interpreting Graphs

**Easy:**
> *[Include bar graph data]* According to the bar graph, how many {{items}} were sold on {{day}}?
> 
> *Constraints: provide clear data points*

**Medium:**
> *[Include line graph data showing temperature over time]* Between which two consecutive hours did the temperature change the most? By how much?
> 
> *Constraints: clear inflection points*

**Hard:**
> *[Include data for circle/pie chart]* A survey of {{total}} students showed their favorite subjects. If {{angle}}° of the circle represents {{subject}}, how many students chose {{subject}}? What fraction is this?
> 
> *Constraints: angle divides evenly into 360°*

---

### Creating Graphs

**Medium:**
> {{name}} recorded the number of books read each month: {{data_list}}. Create a bar graph to represent this data. What was the mean number of books read per month?
> 
> *Constraints: 4-6 data points*

**Hard:**
> A class recorded test scores: {{score_ranges_and_frequencies}}. Create a histogram with intervals of {{interval}} points. Which interval has the highest frequency?
> 
> *Constraints: data spans 50-100 range typically*
