# Grade 2 Math Problem Templates

## 1. Numbers

### 1.1 Number Names

#### Easy
```
Template: Write the number name for {{number}}.
Constraints: number ∈ [1, 100]
Example: Write the number name for 47.
Answer: forty-seven
```

```
Template: What number is "{{number_word}}"?
Constraints: number_word represents integers [1, 100]
Example: What number is "sixty-three"?
Answer: 63
```

#### Medium
```
Template: {{name}} has {{number}} {{objects}}. Write this number in words.
Constraints: number ∈ [100, 999], objects ∈ {apples, stickers, marbles, crayons, coins}
Example: Emma has 254 stickers. Write this number in words.
Answer: two hundred fifty-four
```

```
Template: Circle all the numbers that match the word "{{number_word}}": {{option_a}}, {{option_b}}, {{option_c}}, {{option_d}}
Constraints: One correct answer, three distractors (off by ±1, ±10, or swapped digits)
Example: Circle all the numbers that match the word "seventy-two": 27, 72, 73, 720
Answer: 72
```

#### Hard
```
Template: Write these numbers in order from smallest to largest using their number names: {{word_a}}, {{word_b}}, {{word_c}}, {{word_d}}.
Constraints: words represent distinct 3-digit numbers
Example: Write in order: five hundred twelve, four hundred ninety-nine, five hundred twenty-one, four hundred eighty.
Answer: four hundred eighty, four hundred ninety-nine, five hundred twelve, five hundred twenty-one
```

---

### 1.2 Even and Odd Numbers

#### Easy
```
Template: Is {{number}} even or odd?
Constraints: number ∈ [1, 50]
Example: Is 17 even or odd?
Answer: odd
```

```
Template: Circle all the even numbers: {{num_1}}, {{num_2}}, {{num_3}}, {{num_4}}, {{num_5}}
Constraints: num_n ∈ [1, 30], mix of even/odd
Example: Circle all the even numbers: 4, 9, 12, 15, 22
Answer: 4, 12, 22
```

#### Medium
```
Template: {{name}} picked {{number}} {{objects}}. Can {{pronoun}} share them equally with {{pronoun_possessive}} friend without any left over? Why?
Constraints: number ∈ [10, 50], tests even/odd understanding
Example: Maya picked 23 strawberries. Can she share them equally with her friend without any left over? Why?
Answer: No, because 23 is an odd number.
```

```
Template: Fill in the missing numbers in this pattern of {{pattern_type}} numbers: {{num_1}}, {{num_2}}, ___, {{num_4}}, ___
Constraints: pattern_type ∈ {even, odd}, consecutive in pattern
Example: Fill in the missing numbers in this pattern of even numbers: 14, 16, ___, 20, ___
Answer: 18, 22
```

#### Hard
```
Template: {{name_1}} says that {{number_a}} + {{number_b}} will always be {{parity}}. Is {{pronoun}} correct? Explain using an example.
Constraints: Tests rules (even+even=even, odd+odd=even, even+odd=odd)
Example: Jake says that 15 + 9 will always be even. Is he correct? Explain.
Answer: Yes, he is correct. Odd + odd = even. 15 + 9 = 24, which is even.
```

```
Template: What is the largest {{parity}} number less than {{limit}}?
Constraints: parity ∈ {even, odd}, limit ∈ [50, 200]
Example: What is the largest odd number less than 86?
Answer: 85
```

---

### 1.3 Rounding Numbers

#### Easy
```
Template: Round {{number}} to the nearest ten.
Constraints: number ∈ [10, 99]
Example: Round 34 to the nearest ten.
Answer: 30
```

```
Template: Is {{number}} closer to {{lower_ten}} or {{upper_ten}}?
Constraints: lower_ten < number < upper_ten, bounds are multiples of 10
Example: Is 67 closer to 60 or 70?
Answer: 70
```

#### Medium
```
Template: {{name}} has {{number}} {{objects}}. About how many is that, rounded to the nearest ten?
Constraints: number ∈ [100, 500]
Example: Carlos has 247 baseball cards. About how many is that, rounded to the nearest ten?
Answer: 250
```

```
Template: Round {{number}} to the nearest hundred.
Constraints: number ∈ [100, 999]
Example: Round 682 to the nearest hundred.
Answer: 700
```

#### Hard
```
Template: A {{object}} costs ${{price}}. {{name}} wants to estimate if {{pronoun}} has enough money. Round the price to the nearest {{round_to}} to help estimate.
Constraints: price ∈ [1.00, 50.00], round_to ∈ {ten, dollar}
Example: A toy costs $37. Lily wants to estimate if she has enough money. Round the price to the nearest ten to help estimate.
Answer: $40
```

```
Template: {{name}} rounded a number to {{rounded_value}}. What are all the possible numbers {{pronoun}} could have started with? (Round to nearest ten)
Constraints: rounded_value is a multiple of 10 ∈ [20, 100]
Example: Sam rounded a number to 50. What are all possible numbers he could have started with?
Answer: 45, 46, 47, 48, 49, 50, 51, 52, 53, 54
```

---

## 2. Addition

### 2.1 Addition with Regrouping

#### Easy
```
Template: {{num_a}} + {{num_b}} = ___
Constraints: num_a, num_b ∈ [10, 50], sum requires single regrouping
Example: 28 + 15 = ___
Answer: 43
```

```
Template: {{name}} has {{num_a}} {{objects}}. {{pronoun}} gets {{num_b}} more. How many does {{pronoun}} have now?
Constraints: num_a, num_b ∈ [10, 40], requires regrouping ones
Example: Ben has 36 crayons. He gets 17 more. How many does he have now?
Answer: 53 crayons
```

#### Medium
```
Template: {{num_a}} + {{num_b}} = ___
Constraints: num_a, num_b ∈ [50, 200], may require regrouping in ones and tens
Example: 156 + 87 = ___
Answer: 243
```

```
Template: {{name_1}} collected {{num_a}} {{objects}}. {{name_2}} collected {{num_b}} {{objects}}. How many did they collect together?
Constraints: num_a, num_b ∈ [100, 300], requires multiple regroupings
Example: Sofia collected 178 seashells. Mia collected 245 seashells. How many did they collect together?
Answer: 423 seashells
```

#### Hard
```
Template: {{num_a}} + {{num_b}} + {{num_c}} = ___
Constraints: All three nums ∈ [50, 200], multiple regroupings
Example: 147 + 285 + 68 = ___
Answer: 500
```

```
Template: {{name}} needs {{target}} {{objects}} for a project. {{pronoun}} already has {{num_a}}. {{friend}} gave {{pronoun_obj}} {{num_b}} more. How many more does {{pronoun}} need?
Constraints: target > num_a + num_b, all values ∈ [50, 300]
Example: Ava needs 500 beads for a project. She already has 234. Her mom gave her 158 more. How many more does she need?
Answer: 108 beads (500 - 234 - 158 = 108 or 500 - 392 = 108)
```

---

### 2.2 Addition Table / Facts

#### Easy
```
Template: Complete the addition fact: {{num_a}} + {{num_b}} = ___
Constraints: num_a, num_b ∈ [0, 10]
Example: 7 + 5 = ___
Answer: 12
```

```
Template: Find the missing number: {{num_a}} + ___ = {{sum}}
Constraints: num_a ∈ [1, 10], sum ∈ [5, 18]
Example: 6 + ___ = 14
Answer: 8
```

#### Medium
```
Template: Fill in the missing numbers in this addition table row:
| + | {{col_1}} | {{col_2}} | {{col_3}} | {{col_4}} |
| {{row_num}} | ___ | ___ | ___ | ___ |
Constraints: columns and row ∈ [1, 10]
Example: 
| + | 3 | 5 | 7 | 9 |
| 6 | ___ | ___ | ___ | ___ |
Answer: 9, 11, 13, 15
```

```
Template: Write two different addition facts that equal {{target}}.
Constraints: target ∈ [10, 18]
Example: Write two different addition facts that equal 13.
Answer: 6 + 7 = 13, 9 + 4 = 13 (multiple valid answers)
```

#### Hard
```
Template: Use the digits {{digit_a}}, {{digit_b}}, and {{digit_c}} to make two addition equations.
Constraints: digits ∈ [1, 9], digit_a + digit_b = digit_c or other valid combinations
Example: Use the digits 3, 5, and 8 to make two addition equations.
Answer: 3 + 5 = 8, 5 + 3 = 8
```

```
Template: {{name}} says that {{num_a}} + {{num_b}} = {{num_b}} + {{num_a}}. Is this always true? What property is this?
Constraints: num_a ≠ num_b, both ∈ [1, 20]
Example: Leo says that 8 + 5 = 5 + 8. Is this always true? What property is this?
Answer: Yes, this is always true. This is the Commutative Property of Addition.
```

---

## 3. Subtraction

### 3.1 Subtraction with Regrouping

#### Easy
```
Template: {{num_a}} - {{num_b}} = ___
Constraints: num_a ∈ [20, 50], num_b ∈ [5, 20], requires regrouping ones
Example: 42 - 17 = ___
Answer: 25
```

```
Template: {{name}} had {{num_a}} {{objects}}. {{pronoun}} gave away {{num_b}}. How many are left?
Constraints: num_a ∈ [30, 60], num_b < num_a, requires regrouping
Example: Zoe had 53 stickers. She gave away 28. How many are left?
Answer: 25 stickers
```

#### Medium
```
Template: {{num_a}} - {{num_b}} = ___
Constraints: num_a ∈ [100, 300], num_b ∈ [50, 150], requires regrouping ones and tens
Example: 231 - 154 = ___
Answer: 77
```

```
Template: {{name}} has ${{num_a}}. {{pronoun}} spends ${{num_b}} on a {{item}}. How much money does {{pronoun}} have left?
Constraints: num_a ∈ [50, 100], num_b < num_a, requires regrouping
Example: Noah has $80. He spends $34 on a book. How much money does he have left?
Answer: $46
```

#### Hard
```
Template: {{num_a}} - {{num_b}} = ___
Constraints: num_a ∈ [200, 500], contains zeros requiring multiple regroupings (e.g., 400 - 167)
Example: 305 - 178 = ___
Answer: 127
```

```
Template: A library had {{start}} books. On {{day_1}}, {{num_borrowed_1}} books were borrowed. On {{day_2}}, {{num_borrowed_2}} more were borrowed. How many books are in the library now?
Constraints: start ∈ [400, 600], num_borrowed_1, num_borrowed_2 ∈ [50, 150]
Example: A library had 500 books. On Monday, 123 books were borrowed. On Tuesday, 89 more were borrowed. How many books are in the library now?
Answer: 288 books
```

---

### 3.2 Subtraction Table / Facts

#### Easy
```
Template: {{num_a}} - {{num_b}} = ___
Constraints: num_a ∈ [5, 18], num_b ∈ [1, 10], num_b ≤ num_a
Example: 15 - 8 = ___
Answer: 7
```

```
Template: Find the missing number: ___ - {{num_b}} = {{difference}}
Constraints: num_b ∈ [1, 10], difference ∈ [1, 10]
Example: ___ - 6 = 9
Answer: 15
```

#### Medium
```
Template: Write a subtraction fact that is related to {{num_a}} + {{num_b}} = {{sum}}.
Constraints: Fact families, sums ∈ [10, 18]
Example: Write a subtraction fact that is related to 7 + 8 = 15.
Answer: 15 - 7 = 8 or 15 - 8 = 7
```

```
Template: Circle the subtraction facts that equal {{target}}: {{fact_a}}, {{fact_b}}, {{fact_c}}, {{fact_d}}
Constraints: Mix of correct and incorrect facts, target ∈ [3, 12]
Example: Circle the subtraction facts that equal 6: 14 - 8, 13 - 6, 15 - 9, 11 - 6
Answer: 14 - 8 = 6, 15 - 9 = 6
```

#### Hard
```
Template: Complete the fact family for {{num_a}}, {{num_b}}, and {{sum}}:
___ + ___ = ___
___ + ___ = ___
___ - ___ = ___
___ - ___ = ___
Constraints: num_a + num_b = sum, all ∈ [1, 10]
Example: Complete the fact family for 4, 9, and 13.
Answer: 4 + 9 = 13, 9 + 4 = 13, 13 - 4 = 9, 13 - 9 = 4
```

```
Template: If {{num_a}} - {{variable}} = {{difference}}, what is {{variable}} + {{num_c}}?
Constraints: num_a ∈ [10, 20], variable is unknown, num_c ∈ [1, 10]
Example: If 16 - n = 9, what is n + 5?
Answer: n = 7, so 7 + 5 = 12
```

---

## 4. Units and Metric Units

### 4.1 Metric System (Length, Mass)

#### Easy
```
Template: How many centimeters are in {{number}} meter(s)?
Constraints: number ∈ [1, 5]
Example: How many centimeters are in 2 meters?
Answer: 200 centimeters
```

```
Template: Which unit would you use to measure a {{object}}: centimeters, meters, or kilometers?
Constraints: object size varies (pencil → cm, classroom → m, road → km)
Example: Which unit would you use to measure a pencil: centimeters, meters, or kilometers?
Answer: centimeters
```

#### Medium
```
Template: {{name}}'s {{object_a}} is {{length_a}} cm long. {{possessive}} {{object_b}} is {{length_b}} cm long. How much longer is the {{longer_object}}?
Constraints: lengths ∈ [10, 100] cm
Example: Mia's ribbon is 85 cm long. Her string is 47 cm long. How much longer is the ribbon?
Answer: 38 cm longer
```

```
Template: Convert: {{value}} {{unit_from}} = ___ {{unit_to}}
Constraints: unit conversions within metric (mm↔cm, cm↔m, g↔kg, mL↔L)
Example: Convert: 350 cm = ___ m ___ cm
Answer: 3 m 50 cm
```

#### Hard
```
Template: {{name}} ran {{distance_a}} meters in the morning and {{distance_b}} meters in the afternoon. How many kilometers did {{pronoun}} run in total?
Constraints: distances sum to values convertible to km (e.g., 1000m = 1km)
Example: Ethan ran 800 meters in the morning and 1,200 meters in the afternoon. How many kilometers did he run in total?
Answer: 2 kilometers (2,000 meters = 2 km)
```

```
Template: A {{object}} weighs {{mass}} grams. How many of these {{object_plural}} would it take to weigh {{target}} kilogram(s)?
Constraints: mass ∈ [100, 500], target ∈ [1, 3]
Example: A apple weighs 200 grams. How many apples would it take to weigh 1 kilogram?
Answer: 5 apples (1 kg = 1,000 g; 1,000 ÷ 200 = 5)
```

---

### 4.2 Measurement of Area

#### Easy
```
Template: Count the square units to find the area of this shape:
[Grid representation with {{rows}} rows and {{cols}} columns]
Constraints: rows, cols ∈ [2, 5]
Example: Count the square units: [3 × 4 grid]
Answer: 12 square units
```

```
Template: Which shape has more area, a rectangle with {{squares_a}} squares or a rectangle with {{squares_b}} squares?
Constraints: squares_a ≠ squares_b, both ∈ [6, 20]
Example: Which shape has more area, a rectangle with 15 squares or a rectangle with 12 squares?
Answer: The rectangle with 15 squares
```

#### Medium
```
Template: A rectangle is {{length}} units long and {{width}} units wide. What is its area?
Constraints: length, width ∈ [2, 10]
Example: A rectangle is 7 units long and 4 units wide. What is its area?
Answer: 28 square units
```

```
Template: {{name}}'s {{object}} is {{length_a}} cm long and {{width_a}} cm wide. What is the area?
Constraints: length, width ∈ [3, 12]
Example: Lily's book cover is 8 cm long and 5 cm wide. What is the area?
Answer: 40 square centimeters
```

#### Hard
```
Template: {{name}} wants to cover a {{object}} that is {{length}} cm by {{width}} cm with square tiles that are {{tile_size}} cm on each side. How many tiles does {{pronoun}} need?
Constraints: length, width divisible by tile_size
Example: Jake wants to cover a table that is 12 cm by 8 cm with square tiles that are 2 cm on each side. How many tiles does he need?
Answer: 24 tiles (Area = 96 sq cm; each tile = 4 sq cm; 96 ÷ 4 = 24)
```

```
Template: A large rectangle is made up of {{small_rect_count}} smaller rectangles. Each small rectangle has an area of {{small_area}} square units. What is the area of the large rectangle?
Constraints: small_rect_count ∈ [2, 6], small_area ∈ [4, 12]
Example: A large rectangle is made up of 4 smaller rectangles. Each small rectangle has an area of 6 square units. What is the area of the large rectangle?
Answer: 24 square units
```

---

## 5. Shapes

### 5.1 2D Shapes

#### Easy
```
Template: How many sides does a {{shape}} have?
Constraints: shape ∈ {triangle, square, rectangle, pentagon, hexagon, octagon}
Example: How many sides does a hexagon have?
Answer: 6 sides
```

```
Template: Name a shape that has {{num_sides}} sides.
Constraints: num_sides ∈ [3, 8]
Example: Name a shape that has 5 sides.
Answer: pentagon
```

#### Medium
```
Template: {{name}} drew a shape with {{num_sides}} sides and {{num_corners}} corners. What shape did {{pronoun}} draw?
Constraints: num_sides = num_corners for polygons
Example: Ava drew a shape with 4 sides and 4 corners. All sides are the same length. What shape did she draw?
Answer: square (or rhombus, accept both)
```

```
Template: How is a {{shape_a}} different from a {{shape_b}}? Name {{num_differences}} difference(s).
Constraints: shape pairs with notable differences
Example: How is a square different from a rectangle? Name 1 difference.
Answer: A square has all equal sides; a rectangle has 2 pairs of equal sides (or: a square has 4 equal sides, a rectangle doesn't have to).
```

#### Hard
```
Template: {{name}} cut a {{original_shape}} in half with a straight line. What two shapes could {{pronoun}} make?
Constraints: original_shape ∈ {square, rectangle, circle}
Example: Leo cut a square in half with a straight line. What two shapes could he make?
Answer: Two rectangles (horizontal/vertical cut) or two triangles (diagonal cut)
```

```
Template: Sort these shapes into two groups based on their properties: {{shape_list}}. Explain your sorting rule.
Constraints: shape_list includes 4-6 shapes with sortable properties
Example: Sort these shapes: triangle, rectangle, pentagon, square, hexagon, rhombus. Explain your rule.
Answer: Possible groupings include: shapes with 4 sides (rectangle, square, rhombus) vs. other (triangle, pentagon, hexagon); OR shapes with all equal sides vs. not all equal sides.
```

---

### 5.2 3D Shapes

#### Easy
```
Template: What 3D shape is a {{real_object}} shaped like?
Constraints: real_object maps to basic 3D shapes (ball→sphere, box→rectangular prism, can→cylinder)
Example: What 3D shape is a soup can shaped like?
Answer: cylinder
```

```
Template: How many faces does a {{shape_3d}} have?
Constraints: shape_3d ∈ {cube, rectangular prism, cylinder, cone, sphere, pyramid}
Example: How many faces does a cube have?
Answer: 6 faces
```

#### Medium
```
Template: A {{shape_3d}} has {{num_faces}} faces, {{num_edges}} edges, and {{num_vertices}} vertices. What shape is it?
Constraints: Accurate counts for 3D shapes
Example: A 3D shape has 6 faces, 12 edges, and 8 vertices. What shape is it?
Answer: cube (or rectangular prism)
```

```
Template: Which 3D shapes can roll: {{shape_a}}, {{shape_b}}, {{shape_c}}, {{shape_d}}?
Constraints: mix of shapes that roll (curved faces) and don't (flat faces only)
Example: Which 3D shapes can roll: cube, cylinder, sphere, pyramid?
Answer: cylinder, sphere
```

#### Hard
```
Template: {{name}} stacked {{num_cubes}} cubes in a row, then put {{num_cubes_on_top}} cube(s) on top. How many faces can you see from the outside? (Not counting the bottom)
Constraints: Basic composite shape counting
Example: Max stacked 3 cubes in a row, then put 1 cube on top of the middle cube. How many faces can you see from the outside?
Answer: 18 visible faces (requires spatial reasoning)
```

```
Template: If you unfold a {{shape_3d}}, what 2D shapes would you see in the net?
Constraints: shape_3d ∈ {cube, cylinder, cone, rectangular prism, pyramid}
Example: If you unfold a cube, what 2D shapes would you see in the net?
Answer: 6 squares
```

```
Template: A {{shape_3d_a}} and a {{shape_3d_b}} both have a {{common_feature}}. What other 3D shape also has this feature?
Constraints: common_feature ∈ {circular face, flat face, curved surface, vertices}
Example: A cylinder and a cone both have a circular face. What other 3D shape also has this feature?
Answer: Possible answers: sphere (curved, no flat circular face shown), or any shape with a circular base
```

---

## 6. Calendars

### 6.1 Days, Weeks, Months

#### Easy
```
Template: How many days are in a week?
Example: How many days are in a week?
Answer: 7 days
```

```
Template: What day comes {{direction}} {{day_of_week}}?
Constraints: direction ∈ {before, after}, day_of_week ∈ {Sunday, Monday, ..., Saturday}
Example: What day comes after Wednesday?
Answer: Thursday
```

```
Template: How many months are in a year?
Example: How many months are in a year?
Answer: 12 months
```

#### Medium
```
Template: {{month}} has {{num_days}} days. If {{month}} starts on a {{start_day}}, what day of the week will {{month}} {{end_date}} be?
Constraints: Accurate day counts for months
Example: June has 30 days. If June 1st is a Monday, what day of the week will June 15th be?
Answer: Monday (15 - 1 = 14 days = 2 weeks exactly)
```

```
Template: {{name}}'s birthday is on {{month}} {{date}}. {{event}} is {{num_weeks}} weeks later. What is the date of {{event}}?
Constraints: num_weeks ∈ [1, 4], date calculations within same month when possible
Example: Mia's birthday is on March 5th. Her party is 2 weeks later. What is the date of her party?
Answer: March 19th
```

#### Hard
```
Template: There are {{num_days}} days until {{event}}. Today is {{current_date}}. What date is {{event}}?
Constraints: num_days ∈ [10, 60], may cross month boundaries
Example: There are 23 days until the school play. Today is April 10th. What date is the school play?
Answer: May 3rd
```

```
Template: {{name}} has soccer practice every {{day_of_week}}. How many times will {{pronoun}} have soccer practice in {{month}}?
Constraints: month varies, requires counting specific weekdays
Example: Ethan has soccer practice every Tuesday. How many times will he have soccer practice in October?
Answer: 4 or 5 times (depending on the year/what day October 1st falls on—template should specify the year or starting day)
```

```
Template: {{name_1}} started reading a book on {{start_date}}. {{name_1}} finished {{num_days}} days later. {{name_2}} started the same book on {{start_date_2}} and took {{num_days_2}} days. Who finished first?
Constraints: Different start dates and durations to compare
Example: Lily started reading a book on February 20th. She finished 12 days later. Noah started the same book on February 25th and took 5 days. Who finished first?
Answer: Noah finished first (Feb 25 + 5 = March 2; Feb 20 + 12 = March 4)
```
