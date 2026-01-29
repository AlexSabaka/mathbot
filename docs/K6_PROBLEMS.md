# 6th Grade Math Problem Templates

## 1. Numbers

### 1.1 Factors

**Easy**
> List all the factors of {{n}}.
> 
> *Parameters: n ∈ [12, 50], n should have 4-6 factors*

**Medium**
> {{name}} has {{n}} stickers and wants to arrange them in equal rows. What are all the possible ways {{name}} can arrange the stickers so each row has the same number?
> 
> *Parameters: n ∈ [24, 60], name ∈ [common names]*

**Hard**
> Find all the common factors of {{a}} and {{b}}.
> 
> *Parameters: a, b ∈ [20, 100], gcd(a,b) > 1*

---

### 1.2 Multiples

**Easy**
> List the first {{n}} multiples of {{k}}.
> 
> *Parameters: n ∈ [5, 10], k ∈ [3, 12]*

**Medium**
> A bus arrives at the station every {{a}} minutes. Another bus arrives every {{b}} minutes. If both buses arrive at {{time}}, when will they next arrive at the same time?
> 
> *Parameters: a, b ∈ [10, 30], time ∈ [valid times like "9:00 AM"]*

**Hard**
> {{name}} is skip counting by {{k}}. Will {{name}} say the number {{n}}? Explain your reasoning.
> 
> *Parameters: k ∈ [3, 9], n ∈ [50, 200], n may or may not be divisible by k*

---

### 1.3 Greatest Common Divisor (GCD)

**Easy**
> Find the greatest common factor of {{a}} and {{b}}.
> 
> *Parameters: a, b ∈ [12, 48], both should share factors > 1*

**Medium**
> {{name}} has {{a}} red marbles and {{b}} blue marbles. {{name}} wants to divide them into groups so that each group has the same number of red marbles and the same number of blue marbles, with no marbles left over. What is the greatest number of groups {{name}} can make?
> 
> *Parameters: a, b ∈ [18, 72], gcd(a,b) ≥ 6*

**Hard**
> A rectangular garden measures {{a}} feet by {{b}} feet. {{name}} wants to divide it into identical square plots with no leftover space. What is the largest possible side length for each square plot?
> 
> *Parameters: a, b ∈ [24, 120], gcd(a,b) ≥ 4*

---

### 1.4 Lowest Common Multiple (LCM)

**Easy**
> Find the least common multiple of {{a}} and {{b}}.
> 
> *Parameters: a, b ∈ [4, 15]*

**Medium**
> Hot dogs come in packages of {{a}}. Hot dog buns come in packages of {{b}}. What is the smallest number of hot dogs and buns you can buy so that you have an equal number of each?
> 
> *Parameters: a ∈ [6, 10], b ∈ [8, 12], a ≠ b*

**Hard**
> Three bells ring at intervals of {{a}}, {{b}}, and {{c}} minutes. If they all ring together at {{time}}, when will they next all ring together?
> 
> *Parameters: a, b, c ∈ [5, 20], time ∈ [valid times], lcm(a,b,c) ≤ 120*

---

### 1.5 Integers

**Easy**
> Order these integers from least to greatest: {{list_of_integers}}.
> 
> *Parameters: list_of_integers contains 5-7 integers ∈ [-20, 20], mix of positive and negative*

**Medium**
> The temperature at noon was {{a}}°F. By midnight, it had dropped {{b}} degrees. What was the temperature at midnight?
> 
> *Parameters: a ∈ [-5, 15], b ∈ [10, 25], result may be negative*

**Hard**
> A submarine is at {{a}} feet below sea level. It rises {{b}} feet, then descends {{c}} feet. What is the submarine's final position relative to sea level?
> 
> *Parameters: a ∈ [100, 500], b ∈ [50, 200], c ∈ [50, 200]*

---

### 1.6 Comparison of Rational Numbers

**Easy**
> Compare using <, >, or =: {{a}}/{{b}} ___ {{c}}/{{d}}
> 
> *Parameters: a, b, c, d ∈ [1, 12], fractions should be non-equivalent*

**Medium**
> Order from least to greatest: {{fraction_1}}, {{decimal_1}}, {{fraction_2}}, {{decimal_2}}
> 
> *Parameters: values ∈ [0, 2], mix of fractions and decimals that are close in value*

**Hard**
> {{name_1}} ran {{a}}/{{b}} of a mile. {{name_2}} ran {{decimal}} of a mile. {{name_3}} ran {{c}}/{{d}} of a mile. Who ran the farthest? Who ran the shortest distance?
> 
> *Parameters: all values convert to decimals ∈ [0.4, 0.9], values should be distinct*

---

### 1.7 Division in Math

**Easy**
> Divide: {{a}} ÷ {{b}}
> 
> *Parameters: a ∈ [20, 100], b ∈ [2, 10], a divisible by b*

**Medium**
> {{name}} has {{a}} cookies to share equally among {{b}} friends. How many cookies does each friend get? Are there any left over?
> 
> *Parameters: a ∈ [25, 100], b ∈ [3, 9], a not necessarily divisible by b*

**Hard**
> A factory produces {{a}} items per day. If each box holds {{b}} items, how many boxes are needed to pack one day's production? How many items will be in the partially filled box?
> 
> *Parameters: a ∈ [100, 500], b ∈ [12, 36], a mod b ≠ 0*

---

### 1.8 Long Division

**Easy**
> Use long division to find: {{a}} ÷ {{b}}
> 
> *Parameters: a ∈ [100, 500], b ∈ [5, 15], clean division*

**Medium**
> Divide {{a}} by {{b}}. Express your answer as a quotient with a remainder.
> 
> *Parameters: a ∈ [500, 2000], b ∈ [15, 40], remainder ≠ 0*

**Hard**
> A school has {{a}} students going on a field trip. Each bus holds {{b}} students. How many buses are needed, and how many empty seats will there be on the last bus?
> 
> *Parameters: a ∈ [200, 800], b ∈ [35, 55]*

---

### 1.9 Exponents

**Easy**
> Evaluate: {{b}}^{{n}}
> 
> *Parameters: b ∈ [2, 5], n ∈ [2, 4]*

**Medium**
> Write {{a}} as a power of {{b}}.
> 
> *Parameters: a ∈ {8, 16, 27, 32, 64, 81, 125, 243}, b is the corresponding base*

**Hard**
> A bacteria colony doubles every hour. If there are {{a}} bacteria at the start, write an expression using exponents for the number of bacteria after {{n}} hours. Then calculate the result.
> 
> *Parameters: a ∈ [10, 100], n ∈ [3, 6]*

---

## 2. Order of Operations

### 2.1 Order of Operations / PEMDAS

**Easy**
> Evaluate: {{a}} + {{b}} × {{c}}
> 
> *Parameters: a, b, c ∈ [2, 10]*

**Medium**
> Evaluate: ({{a}} + {{b}}) × {{c}} − {{d}}
> 
> *Parameters: a, b, c, d ∈ [2, 12], result should be positive*

**Hard**
> Evaluate: {{a}} + {{b}}² × ({{c}} − {{d}}) ÷ {{e}}
> 
> *Parameters: a ∈ [5, 20], b ∈ [2, 5], c, d ∈ [2, 15] where c > d, e divides evenly into b²×(c−d)*

**Hard (Variation 2)**
> Insert parentheses to make this equation true: {{a}} + {{b}} × {{c}} − {{d}} = {{target}}
> 
> *Parameters: Generate expression first, then calculate different possible targets based on parentheses placement*

---

## 3. Fractions

### 3.1 Fractions (Basic Operations)

**Easy**
> Add: {{a}}/{{b}} + {{c}}/{{b}}
> 
> *Parameters: a, c ∈ [1, 5], b ∈ [6, 12], same denominator*

**Medium**
> Subtract: {{a}}/{{b}} − {{c}}/{{d}}
> 
> *Parameters: a/b > c/d, b and d are different but have common multiples ≤ 24*

**Hard**
> {{name}} ate {{a}}/{{b}} of a pizza. {{name_2}} ate {{c}}/{{d}} of the same pizza. What fraction of the pizza did they eat together? What fraction is left?
> 
> *Parameters: a/b + c/d < 1, b ≠ d*

---

### 3.2 Simplest Form of Fraction

**Easy**
> Simplify the fraction {{a}}/{{b}} to its lowest terms.
> 
> *Parameters: a, b ∈ [4, 50], gcd(a,b) > 1*

**Medium**
> {{name}} answered {{a}} questions correctly out of {{b}} total questions. Write this as a fraction in simplest form.
> 
> *Parameters: a < b, a, b ∈ [12, 50], gcd(a,b) ≥ 4*

**Hard**
> A recipe calls for {{a}}/{{b}} cup of flour. {{name}} wants to make {{n}} batches. How much flour is needed? Express your answer in simplest form.
> 
> *Parameters: a, b ∈ [2, 8], n ∈ [2, 5], (a×n)/b should simplify*

---

### 3.3 Division of Fractions

**Easy**
> Divide: {{a}}/{{b}} ÷ {{c}}/{{d}}
> 
> *Parameters: a, b, c, d ∈ [2, 8], result should simplify to reasonable number*

**Medium**
> How many pieces of rope {{a}}/{{b}} meter long can be cut from a rope that is {{c}}/{{d}} meters long?
> 
> *Parameters: c/d > a/b, result is whole number*

**Hard**
> {{name}} has {{a}} cups of sugar. Each batch of cookies requires {{b}}/{{c}} cup of sugar. How many full batches can {{name}} make? How much sugar will be left over?
> 
> *Parameters: a ∈ [3, 8], b, c ∈ [2, 6], result has remainder*

---

### 3.4 Reciprocal of Fractions

**Easy**
> What is the reciprocal of {{a}}/{{b}}?
> 
> *Parameters: a, b ∈ [2, 15], a ≠ b*

**Medium**
> Find the reciprocal of {{whole_number}} {{a}}/{{b}}. Express your answer as an improper fraction.
> 
> *Parameters: whole_number ∈ [2, 5], a < b, a, b ∈ [2, 8]*

**Hard**
> What number multiplied by {{a}}/{{b}} equals 1? Verify your answer.
> 
> *Parameters: a, b ∈ [3, 12]*

---

## 4. Decimals

### 4.1 Decimals (Basic)

**Easy**
> Write {{a}}/{{b}} as a decimal.
> 
> *Parameters: b ∈ {2, 4, 5, 10, 20, 25}, fraction converts to terminating decimal*

**Medium**
> Round {{decimal}} to the nearest {{place}}.
> 
> *Parameters: decimal has 3-4 decimal places, place ∈ ["tenth", "hundredth", "whole number"]*

**Hard**
> Arrange in order from least to greatest: {{decimal_1}}, {{decimal_2}}, {{decimal_3}}, {{decimal_4}}
> 
> *Parameters: decimals ∈ [0.1, 2.0] with varying decimal places, some close in value*

---

### 4.2 Addition and Subtraction of Decimals

**Easy**
> Add: {{a}} + {{b}}
> 
> *Parameters: a, b are decimals with 1-2 decimal places, a, b ∈ [1.0, 20.0]*

**Medium**
> {{name}} bought a notebook for ${{a}} and a pen for ${{b}}. {{name}} paid with a ${{c}} bill. How much change did {{name}} receive?
> 
> *Parameters: a, b ∈ [1.00, 10.00], c ∈ {10, 20}, c > a + b*

**Hard**
> A tank contains {{a}} liters of water. {{name}} adds {{b}} liters, then removes {{c}} liters, then adds {{d}} liters. How much water is in the tank now?
> 
> *Parameters: a ∈ [50.0, 100.0], b, c, d ∈ [5.0, 30.0], all with 1-2 decimal places*

---

### 4.3 Multiplying Decimals by Power of 10

**Easy**
> Multiply: {{decimal}} × 10
> 
> *Parameters: decimal ∈ [0.01, 10.0] with 2-3 decimal places*

**Medium**
> Multiply: {{decimal}} × {{power_of_10}}
> 
> *Parameters: decimal ∈ [0.001, 5.0], power_of_10 ∈ {10, 100, 1000}*

**Hard**
> A factory produces {{decimal}} kilograms of product per second. How many kilograms are produced in {{n}} seconds? (Note: {{n}} = {{power_of_10}})
> 
> *Parameters: decimal ∈ [0.01, 1.0], power_of_10 ∈ {100, 1000, 10000}*

---

### 4.4 Dividing Decimals

**Easy**
> Divide: {{a}} ÷ {{b}}
> 
> *Parameters: a ∈ [1.0, 20.0], b ∈ [2, 5], result is terminating decimal*

**Medium**
> Divide: {{decimal}} ÷ {{divisor_decimal}}
> 
> *Parameters: both are decimals, divisor ∈ [0.1, 2.0], result is reasonable*

**Hard**
> {{name}} drove {{a}} miles using {{b}} gallons of gas. How many miles per gallon did {{name}}'s car get? Round to the nearest hundredth.
> 
> *Parameters: a ∈ [100.0, 400.0], b ∈ [5.0, 20.0], both with 1 decimal place*

---

## 5. Ratios, Proportions, and Percentage

### 5.1 Percentage

**Easy**
> What is {{p}}% of {{n}}?
> 
> *Parameters: p ∈ {10, 20, 25, 50, 75}, n ∈ [20, 200]*

**Medium**
> A shirt originally costs ${{a}}. It is on sale for {{p}}% off. What is the sale price?
> 
> *Parameters: a ∈ [20, 100], p ∈ {10, 15, 20, 25, 30, 40, 50}*

**Hard**
> {{name}} scored {{a}} points out of {{b}} possible points on a test. What percentage did {{name}} score? A score of {{p}}% is needed to pass. Did {{name}} pass?
> 
> *Parameters: a < b, a, b ∈ [50, 100], p ∈ [60, 80]*

---

### 5.2 Fraction to Percentage

**Easy**
> Convert {{a}}/{{b}} to a percentage.
> 
> *Parameters: b ∈ {2, 4, 5, 10, 20, 25, 50}, fraction converts to whole number percentage*

**Medium**
> {{name}} read {{a}} pages of a {{b}}-page book. What percentage of the book has {{name}} read?
> 
> *Parameters: a < b, a divides evenly or results in common decimal*

**Hard**
> In a class of {{n}} students, {{a}} students have brown hair, {{b}} students have black hair, and the rest have other hair colors. What percentage of students have each hair color?
> 
> *Parameters: n ∈ [20, 40], a + b < n, all result in reasonable percentages*

---

### 5.3 Decimal to Percentage

**Easy**
> Convert {{decimal}} to a percentage.
> 
> *Parameters: decimal ∈ [0.01, 0.99] with 1-2 decimal places*

**Medium**
> A baseball player has a batting average of {{decimal}}. What is this as a percentage?
> 
> *Parameters: decimal ∈ [0.200, 0.400] (typical batting averages)*

**Hard**
> Three students scored {{d1}}, {{d2}}, and {{d3}} on a test where 1.0 is a perfect score. Convert each to a percentage and rank them from highest to lowest.
> 
> *Parameters: d1, d2, d3 ∈ [0.70, 0.99], distinct values*

---

### 5.4 Ratio

**Easy**
> Write the ratio of {{a}} to {{b}} in three different ways.
> 
> *Parameters: a, b ∈ [2, 20]*

**Medium**
> In a bag of marbles, there are {{a}} red marbles and {{b}} blue marbles. What is the ratio of red marbles to total marbles? Simplify if possible.
> 
> *Parameters: a, b ∈ [6, 24], gcd(a, a+b) > 1 for simplification*

**Hard**
> The ratio of boys to girls in a class is {{a}}:{{b}}. If there are {{n}} students in total, how many boys and how many girls are there?
> 
> *Parameters: a, b ∈ [2, 5], n is divisible by (a+b), n ∈ [20, 40]*

---

### 5.5 Proportions

**Easy**
> Solve for x: {{a}}/{{b}} = x/{{c}}
> 
> *Parameters: a, b, c ∈ [2, 20], x should be whole number*

**Medium**
> If {{a}} pencils cost ${{b}}, how much would {{c}} pencils cost?
> 
> *Parameters: a ∈ [3, 8], b ∈ [2.00, 10.00], c ∈ [10, 25]*

**Hard**
> A map has a scale of {{a}} inch = {{b}} miles. If two cities are {{c}} inches apart on the map, what is the actual distance between them? If the actual distance between two other cities is {{d}} miles, how far apart are they on the map?
> 
> *Parameters: a ∈ {0.5, 1, 2}, b ∈ [10, 50], c ∈ [3, 10], d ∈ [100, 500]*

---

## 6. Algebra

### 6.1 Variable in Math

**Easy**
> If {{var}} = {{n}}, what is the value of {{var}} + {{a}}?
> 
> *Parameters: var ∈ {x, y, n, m}, n, a ∈ [1, 20]*

**Medium**
> {{name}} has {{var}} apples. {{name}} buys {{a}} more apples and then gives {{b}} apples to a friend. Write an expression for how many apples {{name}} has now.
> 
> *Parameters: var ∈ {x, n}, a, b ∈ [2, 10]*

**Hard**
> The length of a rectangle is {{var}} and the width is {{a}} less than the length. Write expressions for the perimeter and area of the rectangle.
> 
> *Parameters: var ∈ {L, x}, a ∈ [2, 8]*

---

### 6.2 Expression and Equation

**Easy**
> Solve for {{var}}: {{var}} + {{a}} = {{b}}
> 
> *Parameters: var ∈ {x, y, n}, a ∈ [3, 20], b ∈ [10, 50], b > a*

**Medium**
> Solve for {{var}}: {{a}}{{var}} − {{b}} = {{c}}
> 
> *Parameters: a ∈ [2, 8], b ∈ [5, 20], c ∈ [1, 50], solution is whole number*

**Hard**
> {{name}} is {{a}} years older than {{name_2}}. The sum of their ages is {{sum}}. How old is each person?
> 
> *Parameters: a ∈ [2, 10], sum ∈ [20, 60], both ages are positive integers*

---

### 6.3 Equivalent Expressions

**Easy**
> Are these expressions equivalent? {{a}}{{var}} + {{b}}{{var}} and {{c}}{{var}}
> 
> *Parameters: a + b may or may not equal c, var ∈ {x, y, n}*

**Medium**
> Write an equivalent expression for: {{a}}({{var}} + {{b}})
> 
> *Parameters: a ∈ [2, 8], b ∈ [1, 10], var ∈ {x, y}*

**Hard**
> Which expression is NOT equivalent to the others? 
> A) {{a}}({{var}} + {{b}}) 
> B) {{a}}{{var}} + {{ab}} 
> C) {{c}}{{var}} + {{d}}
> 
> *Parameters: a, b ∈ [2, 6], ab = a × b, c and d chosen so one doesn't match*

---

### 6.4 Simplifying Algebraic Expressions

**Easy**
> Simplify: {{a}}{{var}} + {{b}}{{var}}
> 
> *Parameters: a, b ∈ [2, 10], var ∈ {x, y, n}*

**Medium**
> Simplify: {{a}}{{var}} + {{b}} + {{c}}{{var}} − {{d}}
> 
> *Parameters: a, c ∈ [2, 8], b, d ∈ [1, 15], b > d for positive constant*

**Hard**
> Simplify: {{a}}({{var}} + {{b}}) + {{c}}{{var}} − {{d}}
> 
> *Parameters: a, c ∈ [2, 5], b, d ∈ [1, 10]*

---

### 6.5 Factoring Expressions

**Easy**
> Factor out the greatest common factor: {{a}}{{var}} + {{b}}
> 
> *Parameters: a, b ∈ [4, 24], gcd(a, b) ≥ 2*

**Medium**
> Factor completely: {{a}}{{var}} + {{a}}{{b}}
> 
> *Parameters: a ∈ [3, 12], b ∈ [2, 10]*

**Hard**
> Factor: {{a}}{{var}}² + {{b}}{{var}}
> 
> *Parameters: a, b ∈ [4, 20], gcd(a, b) ≥ 2*

---

### 6.6 Inequalities on Number Line

**Easy**
> Graph on a number line: {{var}} > {{a}}
> 
> *Parameters: var ∈ {x, n}, a ∈ [-5, 10]*

**Medium**
> Solve and graph: {{var}} + {{a}} ≤ {{b}}
> 
> *Parameters: a ∈ [2, 10], b ∈ [5, 20], b > a*

**Hard**
> {{name}} needs to score at least {{a}} points to win a prize. {{name}} currently has {{b}} points. Write and solve an inequality to find how many more points {{name}} needs. Graph the solution.
> 
> *Parameters: a ∈ [50, 100], b ∈ [20, 45]*

---

## 7. Coordinate Plane

### 7.1 Coordinate Axes / Coordinate Plane

**Easy**
> Plot the point ({{a}}, {{b}}) on a coordinate plane. In which quadrant is the point located?
> 
> *Parameters: a, b ∈ [-10, 10], both non-zero for clear quadrant*

**Medium**
> Point A is at ({{a}}, {{b}}). Point B is {{c}} units to the right and {{d}} units up from Point A. What are the coordinates of Point B?
> 
> *Parameters: a, b ∈ [-5, 5], c, d ∈ [2, 8]*

**Hard**
> A rectangle has vertices at ({{a}}, {{b}}), ({{c}}, {{b}}), ({{c}}, {{d}}), and ({{a}}, {{d}}). What is the perimeter and area of the rectangle?
> 
> *Parameters: a < c, b < d, values ∈ [-8, 8], differences should give nice numbers*

**Hard (Variation 2)**
> Plot these points and identify the shape they form: ({{x1}}, {{y1}}), ({{x2}}, {{y2}}), ({{x3}}, {{y3}}), ({{x4}}, {{y4}})
> 
> *Parameters: Points form a recognizable shape (rectangle, square, parallelogram)*

---

## 8. Geometry

### 8.1 2D Shapes

**Easy**
> A {{shape}} has {{n}} sides. What is the name of this shape?
> 
> *Parameters: n ∈ [3, 8], shape matches n*

**Medium**
> How many lines of symmetry does a regular {{shape}} have?
> 
> *Parameters: shape ∈ ["triangle", "square", "pentagon", "hexagon", "octagon"]*

**Hard**
> {{name}} says that all {{shape_1}}s are {{shape_2}}s, but not all {{shape_2}}s are {{shape_1}}s. Is this statement true or false? Explain.
> 
> *Parameters: shape pairs like (square, rectangle), (rhombus, parallelogram)*

---

### 8.2 Area of 2D Shapes

**Easy (Triangle)**
> Find the area of a triangle with base {{b}} units and height {{h}} units.
> 
> *Parameters: b, h ∈ [4, 20], b × h is even for clean answer*

**Easy (Rectangle)**
> Find the area of a rectangle with length {{l}} units and width {{w}} units.
> 
> *Parameters: l, w ∈ [5, 25]*

**Medium (Parallelogram)**
> A parallelogram has a base of {{b}} cm and a height of {{h}} cm. Find its area.
> 
> *Parameters: b ∈ [6, 18], h ∈ [4, 15]*

**Medium (Trapezoid)**
> Find the area of a trapezoid with parallel sides of {{a}} m and {{b}} m, and a height of {{h}} m.
> 
> *Parameters: a, b ∈ [5, 20], h ∈ [4, 12], (a+b) is even*

**Hard**
> {{name}}'s garden is shaped like a {{shape}} with {{dimension_description}}. If {{name}} wants to cover the entire garden with mulch, and one bag of mulch covers {{cover_area}} square feet, how many bags does {{name}} need?
> 
> *Parameters: Various shapes with appropriate dimensions, cover_area ∈ [10, 25]*

---

### 8.3 Area of Composite Shapes

**Easy**
> Find the area of an L-shaped figure made of two rectangles. Rectangle 1: {{l1}} × {{w1}}. Rectangle 2: {{l2}} × {{w2}}.
> 
> *Parameters: l1, w1, l2, w2 ∈ [3, 12]*

**Medium**
> A rectangular yard measures {{l}} ft by {{w}} ft. A square patio measuring {{s}} ft by {{s}} ft is built in one corner. What is the area of the yard NOT covered by the patio?
> 
> *Parameters: l, w ∈ [20, 50], s ∈ [8, 15], s < min(l, w)*

**Hard**
> A figure is made of a rectangle {{l}} cm by {{w}} cm with a semicircle of diameter {{w}} cm attached to one end. Find the total area. (Use π ≈ 3.14)
> 
> *Parameters: l ∈ [10, 20], w ∈ [6, 14], w is even*

---

### 8.4 Surface Area

**Easy**
> Find the surface area of a cube with side length {{s}} units.
> 
> *Parameters: s ∈ [3, 12]*

**Medium**
> Find the surface area of a rectangular prism with length {{l}}, width {{w}}, and height {{h}}.
> 
> *Parameters: l, w, h ∈ [3, 15]*

**Hard**
> {{name}} is wrapping a gift box that measures {{l}} inches by {{w}} inches by {{h}} inches. How many square inches of wrapping paper are needed to cover the entire box with no overlap?
> 
> *Parameters: l, w, h ∈ [6, 18]*

---

### 8.5 Volume

**Easy**
> Find the volume of a cube with side length {{s}} cm.
> 
> *Parameters: s ∈ [2, 10]*

**Medium**
> Find the volume of a rectangular prism with length {{l}} m, width {{w}} m, and height {{h}} m.
> 
> *Parameters: l, w, h ∈ [2, 12]*

**Hard**
> An aquarium measures {{l}} inches long, {{w}} inches wide, and {{h}} inches tall. If the aquarium is filled to {{fraction}} of its height with water, how many cubic inches of water are in the tank?
> 
> *Parameters: l, w, h ∈ [12, 36], fraction ∈ ["3/4", "2/3", "4/5"]*

---

## 9. Statistics

### 9.1 Mean, Median, and Mode

**Easy**
> Find the mean of this data set: {{list_of_numbers}}
> 
> *Parameters: 5-7 numbers ∈ [10, 50], sum divisible by count*

**Medium**
> Find the mean, median, and mode of: {{list_of_numbers}}
> 
> *Parameters: 7-9 numbers ∈ [1, 20], at least one repeated value*

**Hard**
> {{name}}'s test scores are: {{score_1}}, {{score_2}}, {{score_3}}, {{score_4}}. What score does {{name}} need on the fifth test to have a mean score of {{target_mean}}?
> 
> *Parameters: scores ∈ [60, 95], target_mean ∈ [75, 90], required fifth score should be achievable (≤ 100)*

---

### 9.2 Range in Statistics

**Easy**
> Find the range of this data set: {{list_of_numbers}}
> 
> *Parameters: 5-8 numbers ∈ [5, 50]*

**Medium**
> The high temperatures for a week were: {{temp_list}}°F. What is the range of temperatures?
> 
> *Parameters: 7 temperatures ∈ [50, 95]*

**Hard**
> Data Set A: {{list_A}}. Data Set B: {{list_B}}. Which data set has a greater range? What does this tell you about the spread of the data?
> 
> *Parameters: Both sets have 6-8 numbers, different ranges*

---

### 9.3 Bar Graphs

**Easy**
> A bar graph shows: {{category_1}}: {{value_1}}, {{category_2}}: {{value_2}}, {{category_3}}: {{value_3}}. How many more does {{category_1}} have than {{category_3}}?
> 
> *Parameters: 3-4 categories, values ∈ [10, 100]*

**Medium**
> Create the data for a bar graph based on this information: {{name}}'s class voted on their favorite {{topic}}. {{a}} students chose {{option_1}}, {{b}} students chose {{option_2}}, and {{c}} students chose {{option_3}}. What is the total number of students? Which option was most popular?
> 
> *Parameters: a, b, c ∈ [5, 25], topic ∈ ["fruit", "sport", "color", "season"]*

**Hard**
> A bar graph shows monthly sales. {{month_1}}: ${{a}}, {{month_2}}: ${{b}}, {{month_3}}: ${{c}}, {{month_4}}: ${{d}}. What is the mean monthly sales? What is the percent increase from {{month_1}} to {{month_4}}?
> 
> *Parameters: 4 consecutive months, values ∈ [1000, 5000]*

---

### 9.4 Histograms

**Easy**
> A histogram shows test scores. {{range_1}}: {{count_1}} students, {{range_2}}: {{count_2}} students, {{range_3}}: {{count_3}} students. How many students took the test?
> 
> *Parameters: ranges like "60-69", "70-79", "80-89", counts ∈ [3, 15]*

**Medium**
> Data: {{list_of_values}}. Create intervals of width {{width}} starting at {{start}} and determine how many values fall into each interval.
> 
> *Parameters: 15-20 values ∈ [0, 100], width ∈ [10, 20], start ∈ [0, 10]*

**Hard**
> A histogram shows ages of people at a park. Describe what the histogram would look like if: {{age_data_description}}. Which interval would have the tallest bar?
> 
> *Parameters: age_data_description describes a scenario like "mostly families with young children"*

---

### 9.5 Frequency Tables

**Easy**
> Create a frequency table for this data: {{list_of_repeated_values}}
> 
> *Parameters: 15-25 values with 4-6 unique values, clear repetition*

**Medium**
> A frequency table shows: Value {{v1}} appears {{f1}} times, value {{v2}} appears {{f2}} times, value {{v3}} appears {{f3}} times. What is the mean of this data?
> 
> *Parameters: 3-4 values and frequencies, total count = sum of frequencies*

**Hard**
> {{name}} recorded the number of {{item}} seen each day for {{n}} days: {{data_list}}. Create a frequency table and determine the mode. What fraction of days did {{name}} see exactly {{k}} {{item}}?
> 
> *Parameters: n ∈ [14, 21], values ∈ [0, 10], k is a value in the data*
