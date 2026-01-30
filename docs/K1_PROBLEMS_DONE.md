# Grade 1 Math Problem Templates

## 1. Numbers

### 1.1 Counting Numbers

**Easy Template:**
```
Count the {{object_plural}}. How many are there?
[Show {{count}} images of {{object_singular}}]

Parameters:
- count: 1-10
- object_singular: "apple", "ball", "star", "car", "book"
- object_plural: plural form of object_singular

Example: Count the apples. How many are there? [Show 7 apple images]
Answer: 7
```

**Medium Template:**
```
There are {{count_a}} {{object_a_plural}} and {{count_b}} {{object_b_plural}}. 
Count all the objects. How many objects are there in total?

Parameters:
- count_a: 1-5
- count_b: 1-5
- count_a + count_b: ≤ 10
- object_a_singular/plural: "dog/dogs", "cat/cats", "bird/birds"
- object_b_singular/plural: "fish", "turtle/turtles", "rabbit/rabbits"

Example: There are 4 dogs and 3 cats. Count all the animals. How many animals are there in total?
Answer: 7
```

**Hard Template:**
```
Start at {{start_num}} and count up to {{end_num}}. 
Write the missing numbers: {{start_num}}, ___, ___, {{end_num}}

Parameters:
- start_num: 1-15
- end_num: start_num + 3 to start_num + 5
- Missing numbers calculated based on sequence

Example: Start at 6 and count up to 10. Write the missing numbers: 6, ___, ___, ___, 10
Answer: 7, 8, 9
```

### 1.2 Skip Counting

**Easy Template:**
```
Skip count by {{skip_value}}s. Fill in the blanks:
{{start}}, ___, {start + 2*skip_value}, ___, {start + 4*skip_value}

Parameters:
- skip_value: 2, 5, 10
- start: 0 or skip_value
- Generate 5 terms in sequence

Example: Skip count by 2s. Fill in the blanks: 2, ___, 6, ___, 10
Answer: 4, 8
```

**Medium Template:**
```
{{person_name}} is skip counting by {{skip_value}}s starting at {{start}}.
What are the next {{num_terms}} numbers {{person_name}} will say?

Parameters:
- skip_value: 2, 5, 10
- start: 0 or skip_value
- num_terms: 3-4
- person_name: "Sam", "Alex", "Maya", "Tom", "Lily"

Example: Sam is skip counting by 5s starting at 5. What are the next 3 numbers Sam will say?
Answer: 10, 15, 20
```

**Hard Template:**
```
Complete the pattern by skip counting:
{seq[0]}, {seq[1]}, ___, ___, {seq[4]}, ___
What number comes next? Is this skip counting by {{skip_value}}s?

Parameters:
- skip_value: 2, 5, 10
- seq: sequence with first 2 and 5th element shown
- Requires identifying the pattern

Example: Complete the pattern: 10, 20, ___, ___, 50, ___
Answer: 30, 40, 60 (Yes, skip counting by 10s)
```

### 1.3 Comparing Numbers

**Easy Template:**
```
Which number is bigger: {{num_a}} or {{num_b}}?

Parameters:
- num_a: 1-10
- num_b: 1-10
- num_a ≠ num_b

Example: Which number is bigger: 7 or 4?
Answer: 7
```

**Medium Template:**
```
Circle the {{comparison}} number: {{num_a}}, {{num_b}}, {{num_c}}

Parameters:
- comparison: "biggest", "smallest"
- num_a, num_b, num_c: 1-20
- All three numbers different

Example: Circle the biggest number: 8, 15, 12
Answer: 15
```

**Hard Template:**
```
Put these numbers in order from {{order_type}}: {{num_list}}

Parameters:
- order_type: "smallest to biggest", "biggest to smallest"
- num_list: 4-5 numbers between 1-20
- Numbers are shuffled

Example: Put these numbers in order from smallest to biggest: 14, 7, 19, 3, 11
Answer: 3, 7, 11, 14, 19
```

## 2. Addition

### 2.1 Addition Problems

**Easy Template:**
```
{{num_a}} + {{num_b}} = ?

Parameters:
- num_a: 1-5
- num_b: 1-5
- num_a + num_b ≤ 10

Example: 3 + 4 = ?
Answer: 7
```

**Medium Template:**
```
{{person_name}} has {{num_a}} {{object_plural}}. {{person_name}} gets {{num_b}} more {{object_plural}}.
How many {{object_plural}} does {{person_name}} have now?

Parameters:
- num_a: 1-10
- num_b: 1-10
- num_a + num_b ≤ 20
- person_name: "Emma", "Jake", "Mia", "Liam", "Zoe"
- object_singular/plural: "toy/toys", "sticker/stickers", "marble/marbles"

Example: Emma has 6 toys. Emma gets 4 more toys. How many toys does Emma have now?
Answer: 10
```

**Hard Template:**
```
{{person_a}} has {{num_a}} {{object_plural}}. {{person_b}} has {{num_b}} {{object_plural}}.
{{person_c}} has {{num_c}} {{object_plural}}. How many {{object_plural}} do they have altogether?

Parameters:
- num_a, num_b, num_c: 1-8
- num_a + num_b + num_c ≤ 20
- person_a, person_b, person_c: distinct names
- object_singular/plural: "crayon/crayons", "cookie/cookies", "pencil/pencils"

Example: Tom has 5 crayons. Sara has 7 crayons. Ben has 4 crayons. How many crayons do they have altogether?
Answer: 16
```

## 3. Subtraction

### 3.1 Subtraction Problems

**Easy Template:**
```
{{num_a}} - {{num_b}} = ?

Parameters:
- num_a: 2-10
- num_b: 1 to (num_a - 1)
- Result ≥ 0

Example: 8 - 3 = ?
Answer: 5
```

**Medium Template:**
```
{{person_name}} has {{num_a}} {{object_plural}}. {{person_name}} gives away {{num_b}} {{object_plural}}.
How many {{object_plural}} does {{person_name}} have left?

Parameters:
- num_a: 5-15
- num_b: 1 to num_a
- num_a - num_b ≥ 0
- person_name: "Noah", "Olivia", "Ethan", "Ava", "Mason"
- object_singular/plural: "balloon/balloons", "candy/candies", "flower/flowers"

Example: Noah has 12 balloons. Noah gives away 5 balloons. How many balloons does Noah have left?
Answer: 7
```

**Hard Template:**
```
There were {{num_a}} {{object_plural}} on the {{location}}. 
First, {{num_b}} {{object_plural}} {{action_past}}. Then, {{num_c}} more {{object_plural}} {{action_past}}.
How many {{object_plural}} are still on the {{location}}?

Parameters:
- num_a: 10-20
- num_b: 2-8
- num_c: 2-8
- num_a - num_b - num_c ≥ 0
- location: "table", "shelf", "tree", "plate"
- object_singular/plural: "apple/apples", "book/books", "bird/birds"
- action_past: "fell off", "were taken", "flew away", "were eaten"

Example: There were 15 apples on the table. First, 4 apples were taken. Then, 3 more apples were taken. How many apples are still on the table?
Answer: 8
```

## 4. Measurement

### 4.1 Length and Height

**Easy Template:**
```
Which object is {{comparison}}: the {{object_a}} or the {{object_b}}?
[Show two objects with visible size difference]

Parameters:
- comparison: "longer", "shorter", "taller"
- object_a: "pencil", "stick", "ribbon", "tree", "building"
- object_b: different from object_a

Example: Which object is longer: the pencil or the crayon?
Answer: [Based on image]
```

**Medium Template:**
```
Use {{object_plural}} to measure the {{item}}. The {{item}} is about ___ {{object_plural}} long.
[Show item with measurement objects]

Parameters:
- measuring_object_singular/plural: "paperclip/paperclips", "cube/cubes", "hand/hands"
- item: "book", "desk", "paper", "shoe"
- actual_length: 3-10

Example: Use paperclips to measure the book. The book is about ___ paperclips long.
Answer: 8 (based on actual measurement)
```

**Hard Template:**
```
{{object_a}} is {{count_a}} {{units}} long. {{object_b}} is {{count_b}} {{units}} long.
How much {{comparison}} is {{compared_object}}?

Parameters:
- object_a, object_b: "ribbon", "string", "rope", "path"
- count_a: 5-15
- count_b: 5-15
- count_a ≠ count_b
- units: "cubes", "blocks", "steps"
- comparison: "longer", "shorter"
- compared_object: object_a or object_b (whichever is longer/shorter)

Example: The red ribbon is 12 blocks long. The blue ribbon is 8 blocks long. How much longer is the red ribbon?
Answer: 4 blocks
```

### 4.2 Weight

**Easy Template:**
```
Which is heavier: a {{object_a}} or a {{object_b}}?

Parameters:
- object_a: "feather", "book", "apple", "shoe", "backpack"
- object_b: different from object_a with clearly different weight

Example: Which is heavier: a feather or a book?
Answer: book
```

**Medium Template:**
```
{{person_name}} puts {{num_a}} {{object_plural}} on one side of a balance scale.
What could {{person_name}} put on the other side to make it balance?
a) {{num_b}} {{object_plural}}
b) {{num_c}} {{object_plural}}

Parameters:
- num_a: 2-6
- num_b: num_a (correct answer)
- num_c: num_a ± (1-3) (incorrect)
- object_singular/plural: objects of uniform weight

Example: Sam puts 4 blocks on one side of a balance scale. What could Sam put on the other side to make it balance?
a) 4 blocks  b) 7 blocks
Answer: a) 4 blocks
```

## 5. Time

### 5.1 Reading Clocks

**Easy Template:**
```
What time is shown on the clock?
[Show clock with hour hand only or on the hour]

Parameters:
- hour: 1-12
- minute: 0 (on the hour)

Example: [Clock showing 3:00]
Answer: 3 o'clock
```

**Medium Template:**
```
The clock shows {{time}}. What time will it be in {{hours}} hour(s)?

Parameters:
- time: hour from 1-11 (o'clock)
- hours: 1-3
- Result wraps around 12 if needed

Example: The clock shows 4 o'clock. What time will it be in 2 hours?
Answer: 6 o'clock
```

**Hard Template:**
```
{{person_name}}'s {{activity}} starts at {{start_time}} and lasts for {{duration}} hour(s).
What time does the {{activity}} end?

Parameters:
- person_name: "Lucy", "Max", "Bella", "Ryan", "Chloe"
- activity: "class", "game", "movie", "party"
- start_time: 1-10 o'clock
- duration: 1-3 hours
- end_time must be ≤ 12 o'clock

Example: Lucy's party starts at 2 o'clock and lasts for 3 hours. What time does the party end?
Answer: 5 o'clock
```

### 5.2 Days, Weeks, and Months

**Easy Template:**
```
How many days are in one week?

Parameters:
- Fixed answer: 7

Answer: 7 days
```

**Medium Template:**
```
Today is {{day}}. What day will it be {{num_days}} day(s) from now?

Parameters:
- day: "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
- num_days: 1-7
- Calculate forward in week cycle

Example: Today is Monday. What day will it be 3 days from now?
Answer: Thursday
```

**Hard Template:**
```
{{person_name}} goes to {{activity}} every {{day}}. 
If today is {{current_day}}, how many more days until {{person_name}} goes to {{activity}} again?

Parameters:
- person_name: "Daniel", "Sophia", "James", "Emily"
- activity: "swimming class", "piano lesson", "art class", "soccer practice"
- day: any day of week
- current_day: any day of week (different from day)
- Calculate days between

Example: Daniel goes to swimming class every Wednesday. If today is Friday, how many more days until Daniel goes to swimming class again?
Answer: 5 days
```

## 6. Patterns

### 6.1 Visual and Number Patterns

**Easy Template:**
```
What comes next in the pattern?
{{elem_1}}, {{elem_2}}, {{elem_1}}, {{elem_2}}, ___

Parameters:
- elem_1, elem_2: shapes, colors, or numbers
- AB pattern

Example: What comes next? red, blue, red, blue, ___
Answer: red
```

**Medium Template:**
```
Complete the pattern:
{seq[0]}, {seq[1]}, {seq[2]}, ___, ___, ___

Parameters:
- Pattern types: AAB, ABB, ABC
- Elements: colors, shapes, numbers, letters
- 3 elements shown, 3 to find

Example: Complete the pattern: circle, circle, square, ___, ___, ___
Answer: circle, circle, square
```

**Hard Template:**
```
Look at the pattern: {{sequence}}
What is the pattern rule? What are the next {{num_terms}} items?

Parameters:
- sequence: 4-5 elements with clear rule
- Pattern types: growing patterns, ABCD, number sequences
- num_terms: 2-3
- Requires identifying rule

Example: Look at the pattern: 1, 3, 5, 7, 9
What is the pattern rule? What are the next 2 numbers?
Answer: Add 2 each time (or odd numbers). Next numbers: 11, 13
```

### 6.2 Shape Patterns

**Easy Template:**
```
Which shape is different?
[Show {{shape_a}}, {{shape_a}}, {{shape_a}}, {{shape_b}}]

Parameters:
- shape_a: "circle", "square", "triangle", "rectangle"
- shape_b: different from shape_a
- 3 of shape_a, 1 of shape_b

Example: Which shape is different? [Show 3 circles and 1 square]
Answer: square
```

**Medium Template:**
```
Copy and continue the pattern: [Show pattern with {{length}} repeating units]
Draw the next {{num_draws}} shapes.

Parameters:
- pattern: 2-3 shape repeating unit
- length: 2-3 complete units shown
- num_draws: 2-4 shapes

Example: [Show: triangle, square, triangle, square, triangle, square]
Draw the next 2 shapes.
Answer: triangle, square
```

**Hard Template:**
```
{{person_name}} is making a pattern with {{object_plural}}.
The pattern is: {{pattern_desc}}
If {{person_name}} has used {{num_used}} {{object_plural}} so far, 
what is the {{nth}} {{object_singular}}?

Parameters:
- person_name: "Grace", "Owen", "Hannah", "Isaac"
- object_singular/plural: "bead/beads", "block/blocks", "button/buttons"
- pattern_desc: description of repeating pattern (e.g., "red, blue, blue")
- num_used: 6-12
- nth: num_used + 1 to num_used + 4

Example: Grace is making a pattern with beads. The pattern is: red, blue, blue, red, blue, blue... If Grace has used 9 beads so far, what is the 10th bead?
Answer: red (pattern repeats every 3, 9÷3=3 complete cycles, 10th starts new cycle)
```
