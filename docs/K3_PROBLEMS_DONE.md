# Grade 3 Math Problem Templates

## 1. Addition

### Addition of 4 Digits

**Easy:**
```
{{name}} has {{number1}} stickers. {{name2}} gives {{name}} {{number2}} more stickers. 
How many stickers does {{name}} have now?

Parameters: number1 ∈ [1000-4999], number2 ∈ [1000-4999], sum < 10000
Example: number1=1234, number2=2341 → Answer: 3575
```

**Medium:**
```
The {{place}} library had {{number1}} books. This month, they received {{number2}} new books 
and {{number3}} donated books. How many books does the library have in total?

Parameters: number1 ∈ [1000-5000], number2 ∈ [1000-3000], number3 ∈ [500-2000]
Example: number1=2456, number2=1238, number3=876 → Answer: 4570
```

**Hard:**
```
{{name}}'s school is collecting cans for recycling. Grade 3 collected {{number1}} cans, 
Grade 4 collected {{number2}} cans, and Grade 5 collected {{number3}} cans. 
What is the total number of cans collected by all three grades?

Parameters: number1, number2, number3 ∈ [1000-3500], total < 10000
Example: number1=2145, number2=3267, number3=1589 → Answer: 7001
```

---

### Subtraction (4 Digits)

**Easy:**
```
{{name}} had {{number1}} {{object_plural}}. {{name}} gave away {{number2}} {{object_plural}}. 
How many {{object_plural}} does {{name}} have left?

Parameters: number1 ∈ [5000-9999], number2 ∈ [1000-4999], number1 > number2
Example: number1=7845, number2=2316 → Answer: 5529
```

**Medium:**
```
A toy store had {{number1}} toys in stock. They sold {{number2}} toys in the morning 
and {{number3}} toys in the afternoon. How many toys are left in the store?

Parameters: number1 ∈ [5000-9999], number2+number3 < number1
Example: number1=8500, number2=2145, number3=1876 → Answer: 4479
```

**Hard:**
```
{{name}} is saving for a bicycle that costs ${{number1}}. {{name}} has already saved ${{number2}}. 
{{name}}'s grandmother gave {{name}} ${{number3}}. How much more money does {{name}} need?

Parameters: number1 ∈ [1000-5000], number2+number3 < number1
Example: number1=2500, number2=1234, number3=456 → Answer: $810
```

---

## 2. Multiplication

### What is Multiplication (Basic Concept)

**Easy:**
```
{{name}} has {{number1}} bags. Each bag contains {{number2}} {{object_plural}}. 
How many {{object_plural}} does {{name}} have in all?

Parameters: number1 ∈ [2-5], number2 ∈ [2-10]
Example: number1=3, number2=5, object_plural=apples → Answer: 15 apples
```

**Medium:**
```
There are {{number1}} rows of {{object_plural}} in a garden. Each row has {{number2}} {{object_plural}}. 
How many {{object_plural}} are in the garden altogether?

Parameters: number1 ∈ [3-9], number2 ∈ [4-12]
Example: number1=6, number2=8, object_plural=flowers → Answer: 48 flowers
```

**Hard:**
```
{{name}} arranges {{object_plural}} in {{number1}} equal groups. If there are {{number2}} {{object_plural}} 
in each group, write a multiplication sentence and find the total number of {{object_plural}}.

Parameters: number1 ∈ [5-12], number2 ∈ [6-12]
Example: number1=7, number2=9 → Answer: 7 × 9 = 63
```

---

### Multiplication with Regrouping

**Easy:**
```
{{name}} buys {{number1}} packs of {{object_plural}}. Each pack has {{number2}} {{object_plural}}. 
How many {{object_plural}} did {{name}} buy in total?

Parameters: number1 ∈ [2-9], number2 ∈ [10-50]
Example: number1=4, number2=23 → Answer: 92
```

**Medium:**
```
A bookstore sells {{number1}} boxes of pencils. Each box contains {{number2}} pencils. 
How many pencils did the bookstore sell?

Parameters: number1 ∈ [3-9], number2 ∈ [25-99]
Example: number1=6, number2=47 → Answer: 282
```

**Hard:**
```
{{name}}'s bakery makes {{number1}} trays of {{object_plural}} every day. Each tray holds {{number2}} {{object_plural}}. 
How many {{object_plural}} does the bakery make in {{number3}} days?

Parameters: number1 ∈ [3-9], number2 ∈ [12-36], number3 ∈ [2-7]
Example: number1=5, number2=24, number3=3 → Answer: 360
```

---

### Area Model Multiplication

**Easy:**
```
Use the area model to find {{number1}} × {{number2}}.
Break {{number2}} into {{number2a}} + {{number2b}} and show your work.

Parameters: number1 ∈ [2-9], number2 ∈ [11-19], number2a=10, number2b=number2-10
Example: 4 × 13 = 4 × (10 + 3) = 40 + 12 = 52
```

**Medium:**
```
{{name}} wants to find {{number1}} × {{number2}} using the area model. 
Help {{name}} break apart {{number2}} into tens and ones to solve.

Parameters: number1 ∈ [3-9], number2 ∈ [20-50]
Example: 6 × 34 = 6 × (30 + 4) = 180 + 24 = 204
```

**Hard:**
```
A rectangular garden is {{number1}} meters wide and {{number2}} meters long. 
Use the area model to find the total area of the garden in square meters.

Parameters: number1 ∈ [5-9], number2 ∈ [23-48]
Example: 7 × 36 = 7 × (30 + 6) = 210 + 42 = 252 square meters
```

---

## 3. Division

### What is Division (Basic Concept)

**Easy:**
```
{{name}} has {{number1}} {{object_plural}} to share equally among {{number2}} friends. 
How many {{object_plural}} will each friend get?

Parameters: number1 ∈ [10-50], number2 ∈ [2-10], number1 divisible by number2
Example: number1=24, number2=4 → Answer: 6
```

**Medium:**
```
There are {{number1}} students in a class. The teacher divides them into {{number2}} equal groups. 
How many students are in each group?

Parameters: number1 ∈ [12-48], number2 ∈ [2-8], number1 divisible by number2
Example: number1=36, number2=6 → Answer: 6 students per group
```

**Hard:**
```
{{name}} has {{number1}} {{object_plural}}. {{name}} wants to put them in boxes with {{number2}} {{object_plural}} each. 
How many boxes does {{name}} need?

Parameters: number1 ∈ [20-100], number2 ∈ [4-12], number1 divisible by number2
Example: number1=72, number2=8 → Answer: 9 boxes
```

---

### Dividend, Divisor, Quotient and Remainder

**Easy:**
```
{{name}} divides {{number1}} {{object_plural}} equally among {{number2}} friends. 
What is the quotient? What is the remainder?

Parameters: number1 ∈ [10-50], number2 ∈ [3-9]
Example: 23 ÷ 4 → Quotient: 5, Remainder: 3
```

**Medium:**
```
In the division problem {{number1}} ÷ {{number2}} = {{quotient}} R {{remainder}}, identify:
a) The dividend  b) The divisor  c) The quotient  d) The remainder

Parameters: number1 ∈ [20-100], number2 ∈ [3-12]
Example: 47 ÷ 6 = 7 R 5 → Dividend: 47, Divisor: 6, Quotient: 7, Remainder: 5
```

**Hard:**
```
{{name}} has {{number1}} stickers. {{name}} puts {{number2}} stickers on each page of an album. 
How many full pages can {{name}} fill? How many stickers will be left over?

Parameters: number1 ∈ [30-100], number2 ∈ [4-12]
Example: number1=67, number2=8 → Answer: 8 full pages, 3 stickers left over
```

---

### Long Division

**Easy:**
```
Use long division to solve: {{number1}} ÷ {{number2}}

Parameters: number1 ∈ [20-99], number2 ∈ [2-9], clean division
Example: 84 ÷ 4 = 21
```

**Medium:**
```
{{name}} has {{number1}} {{object_plural}} to pack into boxes of {{number2}}. 
Use long division to find how many full boxes {{name}} can make.

Parameters: number1 ∈ [100-500], number2 ∈ [2-9]
Example: 156 ÷ 6 = 26 boxes
```

**Hard:**
```
A factory produces {{number1}} {{object_plural}} in a week. If the {{object_plural}} are packed 
in cartons of {{number2}}, how many full cartons can be made? How many {{object_plural}} remain?

Parameters: number1 ∈ [200-999], number2 ∈ [3-9]
Example: 847 ÷ 7 = 121 cartons, 0 remaining
```

---

## 4. Fractions

### What is Fractions

**Easy:**
```
{{name}} cuts a pizza into {{denominator}} equal slices and eats {{numerator}} slices. 
What fraction of the pizza did {{name}} eat?

Parameters: denominator ∈ [2,3,4,6,8], numerator < denominator
Example: denominator=8, numerator=3 → Answer: 3/8
```

**Medium:**
```
A chocolate bar is divided into {{denominator}} equal pieces. {{name}} gives away {{numerator}} pieces. 
What fraction of the chocolate bar did {{name}} give away? What fraction is left?

Parameters: denominator ∈ [4,5,6,8,10], numerator < denominator
Example: denominator=6, numerator=4 → Gave away: 4/6, Left: 2/6
```

**Hard:**
```
{{name}} has a ribbon that is {{denominator}} inches long. {{name}} uses {{numerator}} inches for a project. 
Express the used portion as a fraction. Express the remaining portion as a fraction.

Parameters: denominator ∈ [6,8,10,12], numerator < denominator
Example: denominator=10, numerator=7 → Used: 7/10, Remaining: 3/10
```

---

### Types of Fractions

**Easy:**
```
Identify if the fraction {{numerator}}/{{denominator}} is a proper fraction or improper fraction.

Parameters: numerator ∈ [1-15], denominator ∈ [2-10]
Example: 7/4 → Improper fraction (numerator > denominator)
Example: 3/5 → Proper fraction (numerator < denominator)
```

**Medium:**
```
{{name}} ate {{whole}} whole pizzas and {{numerator}}/{{denominator}} of another pizza. 
Write this as a mixed number and as an improper fraction.

Parameters: whole ∈ [1-5], numerator ∈ [1-7], denominator ∈ [2-8], numerator < denominator
Example: whole=2, numerator=3, denominator=4 → Mixed: 2 3/4, Improper: 11/4
```

**Hard:**
```
Convert the improper fraction {{numerator}}/{{denominator}} to a mixed number.

Parameters: numerator ∈ [7-30], denominator ∈ [2-8], numerator > denominator
Example: 17/5 → 3 2/5
```

---

### Fractions on a Number Line

**Easy:**
```
Draw a number line from 0 to 1. Divide it into {{denominator}} equal parts. 
Mark the point that represents {{numerator}}/{{denominator}}.

Parameters: denominator ∈ [2,3,4,5], numerator ≤ denominator
Example: Mark 2/4 on a number line divided into 4 parts
```

**Medium:**
```
A number line is divided into {{denominator}} equal parts between 0 and 1. 
Point A is at {{numerator}}/{{denominator}}. How many jumps from 0 is Point A?

Parameters: denominator ∈ [3,4,5,6,8], numerator < denominator
Example: denominator=6, numerator=4 → 4 jumps from 0
```

**Hard:**
```
On a number line from 0 to 2, mark the position of {{whole}} {{numerator}}/{{denominator}}.

Parameters: whole ∈ [0-1], denominator ∈ [2,3,4,5,6], numerator < denominator
Example: Mark 1 3/4 on a number line from 0 to 2
```

---

### Comparing Fractions

**Easy:**
```
Compare the fractions using >, <, or =: {{numerator1}}/{{denominator}} and {{numerator2}}/{{denominator}}

Parameters: denominator ∈ [3-10], numerator1 ≠ numerator2, both < denominator
Example: 3/8 and 5/8 → 3/8 < 5/8
```

**Medium:**
```
{{name}} ate {{numerator1}}/{{denominator1}} of a cake. {{name2}} ate {{numerator2}}/{{denominator2}} of the same-sized cake. 
Who ate more cake?

Parameters: fractions with same denominator or easy visual comparison
Example: 2/5 vs 3/5 → name2 ate more
```

**Hard:**
```
Compare: {{numerator1}}/{{denominator1}} and {{numerator2}}/{{denominator2}}. 
Which fraction is greater? Explain your reasoning.

Parameters: different denominators requiring common denominator
Example: 2/3 vs 3/4 → 2/3 = 8/12, 3/4 = 9/12, so 3/4 > 2/3
```

---

### Ordering Fractions

**Easy:**
```
Put these fractions in order from least to greatest: 
{{numerator1}}/{{denominator}}, {{numerator2}}/{{denominator}}, {{numerator3}}/{{denominator}}

Parameters: same denominator ∈ [4-10], different numerators
Example: 5/8, 2/8, 7/8 → 2/8, 5/8, 7/8
```

**Medium:**
```
{{name}} drank {{numerator1}}/{{denominator}} of a bottle of water in the morning, 
{{numerator2}}/{{denominator}} in the afternoon, and {{numerator3}}/{{denominator}} in the evening. 
Order these amounts from least to greatest.

Parameters: same denominator, different numerators
Example: 3/6, 5/6, 1/6 → 1/6, 3/6, 5/6
```

**Hard:**
```
Order these fractions from greatest to least: 
{{numerator1}}/{{denominator1}}, {{numerator2}}/{{denominator2}}, {{numerator3}}/{{denominator3}}

Parameters: fractions with denominators 2,3,4,6 that can be compared
Example: 1/2, 2/3, 3/4 → 3/4, 2/3, 1/2
```

---

## 5. Mensuration

### Area

**Easy:**
```
Find the area of a rectangle with length {{length}} {{unit}} and width {{width}} {{unit}}.

Parameters: length ∈ [2-12], width ∈ [2-10], unit ∈ [cm, m, inches, feet]
Example: length=6, width=4, unit=cm → Area = 24 square cm
```

**Medium:**
```
{{name}}'s rectangular garden is {{length}} meters long and {{width}} meters wide. 
What is the area of the garden?

Parameters: length ∈ [5-20], width ∈ [3-15]
Example: length=12, width=8 → Area = 96 square meters
```

**Hard:**
```
A rectangular room is {{length}} feet long and {{width}} feet wide. 
{{name}} wants to cover the floor with square tiles that are 1 foot × 1 foot. 
How many tiles does {{name}} need?

Parameters: length ∈ [8-20], width ∈ [6-15]
Example: length=15, width=10 → 150 tiles needed
```

---

### Perimeter

**Easy:**
```
Find the perimeter of a rectangle with length {{length}} {{unit}} and width {{width}} {{unit}}.

Parameters: length ∈ [3-15], width ∈ [2-10], unit ∈ [cm, m, inches, feet]
Example: length=7, width=4, unit=cm → Perimeter = 22 cm
```

**Medium:**
```
{{name}} wants to put a fence around a rectangular yard that is {{length}} meters long and {{width}} meters wide. 
How many meters of fencing does {{name}} need?

Parameters: length ∈ [10-30], width ∈ [5-20]
Example: length=20, width=15 → Perimeter = 70 meters of fencing
```

**Hard:**
```
A rectangular picture frame has a perimeter of {{perimeter}} inches. 
If the length is {{length}} inches, what is the width?

Parameters: perimeter ∈ [20-60], length < perimeter/2
Example: perimeter=36, length=12 → Width = 6 inches
```

---

## 6. Lines

### Line Segment

**Easy:**
```
Draw a line segment AB that is {{length}} cm long.

Parameters: length ∈ [2-10]
Example: Draw line segment AB = 5 cm
```

**Medium:**
```
{{name}} draws a line segment from point {{point1}} to point {{point2}}. 
The line segment is {{length}} inches long. 
If {{name}} marks a point {{point3}} exactly in the middle, how far is point {{point3}} from each end?

Parameters: length ∈ [4-20] (even numbers), point1/point2/point3 = A/B/C etc.
Example: length=8, points A,B,C → C is 4 inches from each end
```

**Hard:**
```
Line segment {{segment1}} is {{length1}} cm long. Line segment {{segment2}} is {{length2}} cm long. 
What is the total length if you join them end-to-end? 
What is the difference in their lengths?

Parameters: length1, length2 ∈ [3-15]
Example: AB=7cm, CD=12cm → Total: 19cm, Difference: 5cm
```

---

### Types of Lines

**Easy:**
```
Look at the two lines. Are they parallel, perpendicular, or intersecting?
Line 1: {{description1}}
Line 2: {{description2}}

Parameters: description templates for horizontal/vertical/diagonal orientations
Example: "Two railroad tracks running side by side" → Parallel
```

**Medium:**
```
In your classroom, find an example of:
a) {{line_type1}} lines
b) {{line_type2}} lines

Parameters: line_type ∈ [parallel, perpendicular, intersecting]
Example: Parallel lines → edges of a door; Perpendicular lines → corner of a desk
```

**Hard:**
```
{{name}} draws two lines that intersect at point {{point}}. 
If the lines are perpendicular, what is the measure of each angle formed at point {{point}}?

Parameters: point ∈ [A-Z]
Example: Perpendicular lines at point P → Four 90° angles
```

---

## 7. Angles

### Types of Angles

**Easy - Acute Angle:**
```
{{name}} opens a book partially. The angle between the cover and the first page is {{angle}}°. 
What type of angle is this?

Parameters: angle ∈ [10-89]
Example: angle=45° → Acute angle
```

**Easy - Right Angle:**
```
Look at the corner of a {{object}}. What type of angle does it form? 
How many degrees is this angle?

Parameters: object ∈ [book, door, window, paper, desk]
Example: corner of a book → Right angle, 90°
```

**Easy - Obtuse Angle:**
```
An angle measures {{angle}}°. Is it an acute, right, or obtuse angle?

Parameters: angle ∈ [91-179]
Example: angle=120° → Obtuse angle
```

**Medium:**
```
Classify each angle as acute, right, obtuse, or straight:
a) {{angle1}}°  b) {{angle2}}°  c) {{angle3}}°  d) {{angle4}}°

Parameters: angle1 ∈ [1-89], angle2 = 90, angle3 ∈ [91-179], angle4 = 180
Example: 35°=acute, 90°=right, 145°=obtuse, 180°=straight
```

**Hard:**
```
{{name}} turns {{direction}} from facing {{direction1}} to facing {{direction2}}. 
What type of angle did {{name}} turn through? 
Estimate the measure of the angle.

Parameters: directions ∈ [North, South, East, West, etc.]
Example: Facing North, turns to face East → Right angle, 90°
```

---

### Reflex and Complete Angles

**Medium:**
```
An angle measures {{angle}}°. What type of angle is it?

Parameters: angle ∈ [181-359] for reflex, 360 for complete
Example: 270° → Reflex angle
Example: 360° → Complete angle
```

**Hard:**
```
{{name}} spins in a circle and stops after turning {{angle}}°. 
What type of angle did {{name}} turn through? 
Is {{name}} facing the same direction as before?

Parameters: angle ∈ [270, 300, 330, 360]
Example: 360° → Complete angle, facing same direction
Example: 270° → Reflex angle, facing different direction
```
