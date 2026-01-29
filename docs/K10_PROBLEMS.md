# Grade 10 Math Problem Templates

## 1. Basics of Geometry

### 1.1 Points, Lines, and Segments

**Easy**: Points A, B, and C are collinear. If AB = {{length_AB}} units and BC = {{length_BC}} units, and B is between A and C, find the length of AC.
<!-- length_AB: integer [2, 20], length_BC: integer [2, 20] -->

**Medium**: Three points P({{x1}}, {{y1}}), Q({{x2}}, {{y2}}), and R({{x3}}, {{y3}}) are given. Determine whether these points are collinear.
<!-- x1, y1, x2, y2: integers [-10, 10], x3, y3: calculated to be collinear or not -->

**Hard**: A line segment AB has length {{total_length}} units. Points C and D divide AB internally in the ratios {{ratio1_m}}:{{ratio1_n}} and {{ratio2_m}}:{{ratio2_n}} respectively from A. Find the distance CD.
<!-- total_length: integer [20, 100], ratios: integers [1, 5] -->

### 1.2 Parallel and Perpendicular Lines

**Easy**: Line L₁ has slope {{slope1}}. What is the slope of a line parallel to L₁? What is the slope of a line perpendicular to L₁?
<!-- slope1: rational number, fraction form {{num}}/{{den}} where den ≠ 0 -->

**Medium**: Line L₁ passes through points ({{x1}}, {{y1}}) and ({{x2}}, {{y2}}). Line L₂ passes through ({{x3}}, {{y3}}) and ({{x4}}, {{y4}}). Determine if L₁ and L₂ are parallel, perpendicular, or neither.
<!-- coordinates: integers [-10, 10] -->

**Hard**: Find the equation of a line that passes through point ({{px}}, {{py}}) and is perpendicular to the line {{a}}x + {{b}}y + {{c}} = 0.
<!-- px, py: integers [-10, 10], a, b: integers [-5, 5] (b ≠ 0), c: integer [-20, 20] -->

---

## 2. Angles

### 2.1 Types and Measurement of Angles

**Easy**: An angle measures {{angle}}°. Classify this angle as acute, right, obtuse, straight, or reflex.
<!-- angle: integer [1, 359], exclude 90, 180 for variety -->

**Medium**: Two angles are complementary. If one angle is {{multiplier}} times the other, find both angles.
<!-- multiplier: integer [2, 8] or fraction like 3/2 -->

**Hard**: Three angles are in the ratio {{ratio_a}}:{{ratio_b}}:{{ratio_c}}. If these angles are supplementary (sum to 180°), find the measure of each angle.
<!-- ratio_a, ratio_b, ratio_c: integers [1, 10], ensure sum divides 180 -->

### 2.2 Angles Formed by Parallel Lines and Transversal

**Easy**: Two parallel lines are cut by a transversal. If one of the corresponding angles measures {{angle}}°, find the measure of its corresponding angle on the other parallel line.
<!-- angle: integer [30, 150] -->

**Medium**: Lines l and m are parallel, cut by transversal t. If one interior angle on the same side of the transversal measures ({{coeff}}x + {{const1}})° and the other measures ({{coeff2}}x + {{const2}})°, find the value of x.
<!-- coeff, coeff2: integers [1, 5], const1, const2: integers [-20, 60], ensure valid solution -->

**Hard**: In the figure, AB ∥ CD ∥ EF. If ∠ABG = {{angle1}}° and ∠GEF = {{angle2}}°, find ∠BGE.
<!-- angle1: integer [40, 80], angle2: integer [40, 80] -->

### 2.3 Angle Bisector

**Easy**: An angle measures {{angle}}°. What is the measure of each angle formed when this angle is bisected?
<!-- angle: even integer [20, 160] -->

**Medium**: The angle bisector of ∠ABC divides it into two equal parts. If one part measures ({{coeff}}x + {{const}})° and the full angle is {{total}}°, find x.
<!-- coeff: integer [2, 5], const: integer [-10, 20], total: even integer [60, 160] -->

---

## 3. Triangles

### 3.1 Triangle Classification

**Easy**: A triangle has sides measuring {{side_a}} cm, {{side_b}} cm, and {{side_c}} cm. Classify this triangle based on its sides.
<!-- sides must satisfy triangle inequality, choose for scalene/isosceles/equilateral -->

**Medium**: A triangle has angles measuring {{angle_a}}°, {{angle_b}}°, and {{angle_c}}°. Classify this triangle based on its angles and verify the angle sum property.
<!-- angle_a + angle_b + angle_c = 180, choose for acute/right/obtuse -->

### 3.2 Pythagoras Theorem

**Easy**: In a right triangle, the two legs measure {{leg_a}} cm and {{leg_b}} cm. Find the length of the hypotenuse.
<!-- leg_a, leg_b: integers from Pythagorean triples or arbitrary [3, 20] -->

**Medium**: A ladder {{ladder_length}} m long leans against a wall. If the foot of the ladder is {{base_distance}} m from the wall, how high up the wall does the ladder reach?
<!-- ladder_length: integer [5, 25], base_distance < ladder_length -->

**Hard**: In triangle ABC, angle B = 90°. If AB = {{ab}} cm, BC = {{bc}} cm, and D is a point on AC such that BD ⊥ AC, find the length of BD.
<!-- ab, bc: integers [6, 15], creates clean calculation -->

### 3.3 Basic Proportionality Theorem (Thales' Theorem)

**Easy**: In triangle ABC, DE is parallel to BC where D is on AB and E is on AC. If AD = {{ad}} cm, DB = {{db}} cm, and AE = {{ae}} cm, find EC.
<!-- ad, db, ae: integers [2, 12], proportional -->

**Medium**: In triangle PQR, a line parallel to QR intersects PQ at X and PR at Y. If PX = {{px}} cm, XQ = {{xq}} cm, and PY = {{py}} cm, find YR. Also, if QR = {{qr}} cm, find XY.
<!-- px, xq, py: integers [2, 10], qr: integer [8, 20] -->

**Hard**: In triangle ABC, D and E are points on AB and AC respectively such that DE ∥ BC. If AD = ({{coeff1}}x - {{const1}}) cm, DB = ({{coeff2}}x + {{const2}}) cm, AE = {{ae}} cm, and EC = {{ec}} cm, find the value of x.
<!-- coefficients and constants chosen to give integer solution -->

### 3.4 Mid-Point Theorem

**Easy**: In triangle ABC, D and E are midpoints of AB and AC respectively. If BC = {{bc}} cm, find DE.
<!-- bc: even integer [8, 30] -->

**Medium**: In triangle PQR, M is the midpoint of PQ and N is the midpoint of PR. If MN = {{mn}} cm, find QR. Also, prove that MN ∥ QR.
<!-- mn: integer [4, 15] -->

### 3.5 Congruence of Triangles

**Easy**: Triangle ABC has AB = {{ab}} cm, BC = {{bc}} cm, and ∠B = {{angle_b}}°. Triangle DEF has DE = {{de}} cm, EF = {{ef}} cm, and ∠E = {{angle_e}}°. Are these triangles congruent? If yes, by which criterion?
<!-- Choose values to make congruent by SAS or not congruent -->

**Medium**: In triangles ABC and PQR: AB = {{ab}} cm, BC = {{bc}} cm, AC = {{ac}} cm, PQ = {{pq}} cm, QR = {{qr}} cm, PR = {{pr}} cm. Determine if the triangles are congruent and state the criterion.
<!-- Choose for SSS congruence or not -->

**Hard**: In quadrilateral ABCD, AB = CD and AD = BC. Prove that triangles ABD and CDB are congruent. If AB = {{ab}} cm, AD = {{ad}} cm, and BD = {{bd}} cm, find all side lengths of the quadrilateral.
<!-- ab, ad, bd satisfying triangle inequality -->

---

## 4. Quadrilaterals

### 4.1 Parallelogram

**Easy**: A parallelogram has a base of {{base}} cm and a height of {{height}} cm. Find its area.
<!-- base, height: integers [5, 25] -->

**Medium**: In parallelogram ABCD, AB = {{ab}} cm, BC = {{bc}} cm, and the height corresponding to base AB is {{height}} cm. Find the area and perimeter of the parallelogram.
<!-- ab, bc, height: integers [5, 20] -->

**Hard**: The diagonals of a parallelogram are {{diag1}} cm and {{diag2}} cm, and they intersect at angle {{angle}}°. Find the area of the parallelogram.
<!-- diag1, diag2: integers [8, 20], angle: integer [30, 90] -->

### 4.2 Rectangle

**Easy**: A rectangle has length {{length}} cm and width {{width}} cm. Find its area and perimeter.
<!-- length, width: integers [5, 30] -->

**Medium**: The perimeter of a rectangle is {{perimeter}} cm. If its length is {{multiplier}} times its width, find the dimensions of the rectangle.
<!-- perimeter: integer divisible appropriately, multiplier: integer [2, 5] or fraction -->

**Hard**: A rectangle has a diagonal of length {{diagonal}} cm and the angle between the diagonal and the longer side is {{angle}}°. Find the dimensions of the rectangle.
<!-- diagonal: integer [10, 25], angle: integer [20, 40] -->

### 4.3 Square

**Easy**: A square has a side length of {{side}} cm. Find its area, perimeter, and diagonal length.
<!-- side: integer [4, 20] -->

**Medium**: The diagonal of a square is {{diagonal}} cm. Find the side length and area of the square.
<!-- diagonal: integer [8, 28], preferably multiples of √2 for clean answers -->

### 4.4 Rhombus

**Easy**: A rhombus has diagonals of length {{diag1}} cm and {{diag2}} cm. Find its area.
<!-- diag1, diag2: even integers [6, 24] -->

**Medium**: A rhombus has a side of {{side}} cm and one diagonal of {{diag1}} cm. Find the length of the other diagonal and the area.
<!-- side, diag1 chosen so other diagonal is integer (Pythagorean relationship) -->

**Hard**: The diagonals of a rhombus are in the ratio {{ratio_d1}}:{{ratio_d2}}. If the area of the rhombus is {{area}} cm², find the length of each diagonal.
<!-- ratio_d1, ratio_d2: integers [2, 5], area chosen for integer results -->

### 4.5 Trapezium (Trapezoid)

**Easy**: A trapezium has parallel sides of length {{parallel1}} cm and {{parallel2}} cm, and a height of {{height}} cm. Find its area.
<!-- parallel1, parallel2, height: integers [5, 25] -->

**Medium**: The area of a trapezium is {{area}} cm². If the parallel sides are {{parallel1}} cm and {{parallel2}} cm, find the height.
<!-- area divisible by sum of parallel sides for integer height -->

**Hard**: In trapezium ABCD, AB ∥ CD where AB = {{ab}} cm and CD = {{cd}} cm. The non-parallel sides AD = {{ad}} cm and BC = {{bc}} cm. Find the height and area of the trapezium.
<!-- Values chosen for clean calculation, possibly isosceles trapezium -->

### 4.6 Kite

**Easy**: A kite has diagonals of length {{diag1}} cm and {{diag2}} cm. Find its area.
<!-- diag1, diag2: integers [6, 20] -->

**Medium**: A kite has two pairs of consecutive equal sides: {{side1}} cm and {{side2}} cm. If one diagonal is {{diag1}} cm, find the other diagonal and the area.
<!-- Pythagorean relationship for clean answers -->

---

## 5. Circles

### 5.1 Basic Circle Calculations

**Easy**: A circle has a radius of {{radius}} cm. Find its diameter, circumference, and area. (Use π = {{pi_approx}})
<!-- radius: integer [3, 15], pi_value: 3.14 or 22/7 -->

**Medium**: The circumference of a circle is {{circumference}} cm. Find its radius and area.
<!-- circumference: multiple of π for clean answer -->

**Hard**: A circle has an area of {{area}} cm². Find its radius, diameter, and circumference.
<!-- area: multiple of π for clean answer, e.g., 154 when π = 22/7 -->

### 5.2 Arc and Sector

**Easy**: A sector of a circle with radius {{radius}} cm has a central angle of {{angle}}°. Find the arc length.
<!-- radius: integer [5, 20], angle: integer [30, 180] -->

**Medium**: Find the area of a sector with radius {{radius}} cm and central angle {{angle}}°.
<!-- radius, angle as above -->

**Hard**: An arc of a circle subtends an angle of {{angle}}° at the center. If the arc length is {{arc_length}} cm, find the radius of the circle and the area of the corresponding sector.
<!-- arc_length and angle chosen for integer radius -->

### 5.3 Chord

**Easy**: A chord of length {{chord}} cm is at a distance of {{distance}} cm from the center of the circle. Find the radius of the circle.
<!-- chord, distance: integers forming Pythagorean triple -->

**Medium**: Two chords AB and CD of a circle intersect at point P inside the circle. If AP = {{ap}} cm, PB = {{pb}} cm, and CP = {{cp}} cm, find PD.
<!-- ap × pb = cp × pd, choose for integer pd -->

**Hard**: A chord of length {{chord}} cm is drawn in a circle of radius {{radius}} cm. Find the length of the arc cut off by this chord (for the minor arc).
<!-- chord < 2×radius, choose for meaningful central angle -->

### 5.4 Tangent and Secant

**Easy**: From an external point, a tangent of length {{tangent}} cm is drawn to a circle of radius {{radius}} cm. Find the distance from the external point to the center.
<!-- tangent, radius forming Pythagorean triple -->

**Medium**: From point P outside a circle, a tangent PA and a secant PBC are drawn. If PA = {{pa}} cm, PB = {{pb}} cm, find PC. (B is closer to P than C)
<!-- PA² = PB × PC, choose for integer PC -->

**Hard**: Two tangents are drawn from an external point P to a circle with center O and radius {{radius}} cm. If the angle between the tangents is {{angle}}°, find the length of each tangent and the distance OP.
<!-- radius: integer [5, 15], angle: integer [40, 120] -->

### 5.5 Circle Theorems

**Easy**: An inscribed angle subtends an arc of {{arc_angle}}°. What is the measure of the inscribed angle?
<!-- arc_angle: even integer [60, 300] -->

**Medium**: In a circle, chord AB subtends an angle of {{center_angle}}° at the center. What angle does it subtend at a point on the major arc?
<!-- center_angle: integer [60, 160] -->

**Hard**: In a cyclic quadrilateral ABCD, ∠A = {{angle_a}}° and ∠B = {{angle_b}}°. Find ∠C and ∠D.
<!-- angle_a: integer [70, 110], angle_b: integer [70, 110] -->

---

## 6. Polygons

### 6.1 Interior and Exterior Angles

**Easy**: Find the sum of interior angles of a polygon with {{n}} sides.
<!-- n: integer [5, 12] -->

**Medium**: Each interior angle of a regular polygon measures {{interior_angle}}°. How many sides does the polygon have?
<!-- interior_angle: valid value like 120, 135, 140, 144, 150, 156, 160 -->

**Hard**: The interior angles of a {{n}}-sided polygon are in arithmetic progression. If the smallest angle is {{smallest}}° and the common difference is {{diff}}°, verify that these form a valid polygon and find the largest angle.
<!-- n, smallest, diff chosen so sum = (n-2)×180 and all angles are valid -->

### 6.2 Regular Polygon Properties

**Easy**: A regular hexagon has a side length of {{side}} cm. Find its perimeter.
<!-- side: integer [4, 15] -->

**Medium**: Find the area of a regular hexagon with side length {{side}} cm.
<!-- side: integer [4, 12] -->

**Hard**: A regular {{n}}-gon is inscribed in a circle of radius {{radius}} cm. Find the side length and area of the polygon.
<!-- n: integer [5, 10], radius: integer [8, 15] -->

---

## 7. Surface Area and Volume

### 7.1 Cube

**Easy**: A cube has an edge length of {{edge}} cm. Find its surface area and volume.
<!-- edge: integer [3, 15] -->

**Medium**: The surface area of a cube is {{surface_area}} cm². Find its edge length and volume.
<!-- surface_area: perfect square × 6, like 54, 96, 150, 216, 294, 384, 486, 600 -->

**Hard**: The volume of a cube is {{volume}} cm³. Find the total surface area and the length of the space diagonal.
<!-- volume: perfect cube like 27, 64, 125, 216, 343, 512, 729 -->

### 7.2 Cuboid

**Easy**: A cuboid has dimensions {{length}} cm × {{width}} cm × {{height}} cm. Find its surface area and volume.
<!-- length, width, height: integers [3, 15] -->

**Medium**: A cuboid has a volume of {{volume}} cm³. If its length is {{length}} cm and width is {{width}} cm, find its height and surface area.
<!-- volume = length × width × height, choose for integer height -->

**Hard**: The surface area of a cuboid is {{surface_area}} cm². If the dimensions are in the ratio {{ratio_l}}:{{ratio_w}}:{{ratio_h}}, find the dimensions and volume.
<!-- ratio integers [1, 4], surface_area chosen for integer dimensions -->

### 7.3 Cylinder

**Easy**: A cylinder has radius {{radius}} cm and height {{height}} cm. Find its curved surface area, total surface area, and volume.
<!-- radius, height: integers [3, 12] -->

**Medium**: The volume of a cylinder is {{volume}} cm³ and its height is {{height}} cm. Find the radius and curved surface area.
<!-- volume = πr²h, choose for integer or simple radical radius -->

**Hard**: A cylinder has a total surface area of {{total_sa}} cm² and height equal to its diameter. Find the radius, height, and volume.
<!-- total_sa chosen for clean calculation -->

### 7.4 Cone

**Easy**: A cone has base radius {{radius}} cm and height {{height}} cm. Find its slant height and volume.
<!-- radius, height forming Pythagorean triple with slant height -->

**Medium**: A cone has a curved surface area of {{csa}} cm² and slant height of {{slant}} cm. Find the radius and volume.
<!-- csa = πrl, choose for integer radius -->

**Hard**: The volume of a cone is {{volume}} cm³ and the ratio of its radius to height is {{ratio_r}}:{{ratio_h}}. Find the radius, height, and total surface area.
<!-- volume and ratios chosen for clean answers -->

### 7.5 Sphere

**Easy**: A sphere has radius {{radius}} cm. Find its surface area and volume.
<!-- radius: integer [3, 10] -->

**Medium**: The surface area of a sphere is {{surface_area}} cm². Find its radius and volume.
<!-- surface_area = 4πr², choose for integer radius -->

**Hard**: A sphere and a cube have the same surface area. If the edge of the cube is {{edge}} cm, find the radius of the sphere and compare their volumes.
<!-- edge: integer [6, 12] -->

### 7.6 Hemisphere

**Easy**: A solid hemisphere has radius {{radius}} cm. Find its curved surface area, total surface area, and volume.
<!-- radius: integer [3, 12] -->

**Medium**: A hemispherical bowl has an inner radius of {{radius}} cm. Find the capacity of the bowl in liters. (1000 cm³ = 1 liter)
<!-- radius: integer [7, 21] -->

### 7.7 Frustum of a Cone

**Medium**: A frustum of a cone has radii {{r1}} cm and {{r2}} cm (top and bottom) and height {{height}} cm. Find its volume.
<!-- r1 < r2, integers [3, 10], height: integer [5, 15] -->

**Hard**: A frustum has slant height {{slant}} cm with top radius {{r1}} cm and bottom radius {{r2}} cm. Find its curved surface area, total surface area, and volume.
<!-- r2 - r1 and slant form Pythagorean relationship with height -->

### 7.8 Combination of Solids

**Medium**: A solid is made up of a cylinder of radius {{radius}} cm and height {{height_cyl}} cm, surmounted by a cone of the same radius and height {{height_cone}} cm. Find the total surface area and volume of the solid.
<!-- radius: integer [3, 8], heights: integers [5, 12] -->

**Hard**: A solid consists of a hemisphere of radius {{radius}} cm mounted on a cylinder of the same radius and height {{height}} cm, with a cone of the same radius and height {{cone_height}} cm mounted on top of the cylinder. Find the total surface area and volume.
<!-- radius: integer [3, 7], heights: integers [5, 10] -->

---

## 8. Coordinate Geometry

### 8.1 Distance Formula

**Easy**: Find the distance between points A({{x1}}, {{y1}}) and B({{x2}}, {{y2}}).
<!-- coordinates: integers [-10, 10] -->

**Medium**: Point P({{px}}, {{py}}) is equidistant from A({{ax}}, {{ay}}) and B({{bx}}, {{by}}). Find the relationship between {{px}} and {{py}}.
<!-- coordinates: integers [-10, 10] -->

**Hard**: Find the point on the x-axis that is equidistant from A({{ax}}, {{ay}}) and B({{bx}}, {{by}}).
<!-- ay and by both non-zero, coordinates integers [-10, 10] -->

### 8.2 Section Formula

**Easy**: Find the coordinates of the point that divides the line segment joining A({{x1}}, {{y1}}) and B({{x2}}, {{y2}}) internally in the ratio {{m}}:{{n}}.
<!-- coordinates: integers [-10, 10], m, n: integers [1, 5] -->

**Medium**: The point P({{px}}, {{py}}) divides the line segment joining A({{x1}}, {{y1}}) and B({{x2}}, {{y2}}) internally. Find the ratio in which P divides AB.
<!-- P lies between A and B on the line -->

**Hard**: Find the coordinates of the points of trisection of the line segment joining A({{x1}}, {{y1}}) and B({{x2}}, {{y2}}).
<!-- coordinates: integers [-12, 12] -->

### 8.3 Midpoint Formula

**Easy**: Find the midpoint of the line segment joining A({{x1}}, {{y1}}) and B({{x2}}, {{y2}}).
<!-- coordinates: integers [-10, 10], preferably even for clean midpoint -->

**Medium**: If M({{mx}}, {{my}}) is the midpoint of segment AB where A = ({{ax}}, {{ay}}), find the coordinates of B.
<!-- coordinates: integers [-10, 10] -->

### 8.4 Slope of a Line

**Easy**: Find the slope of the line passing through points A({{x1}}, {{y1}}) and B({{x2}}, {{y2}}).
<!-- coordinates: integers [-10, 10], x1 ≠ x2 -->

**Medium**: A line passes through ({{x1}}, {{y1}}) and has slope {{slope}}. Find the y-intercept of this line.
<!-- slope: rational number, coordinates: integers [-10, 10] -->

**Hard**: Three points A({{x1}}, {{y1}}), B({{x2}}, {{y2}}), and C({{x3}}, {{y3}}) are given. Find the slopes of sides AB, BC, and CA, and determine if triangle ABC is a right triangle.
<!-- one pair of slopes should multiply to -1 for right triangle, or not for non-right -->

### 8.5 Equation of a Line

**Easy**: Find the equation of the line with slope {{slope}} and y-intercept {{intercept}}.
<!-- slope: rational, intercept: integer [-10, 10] -->

**Medium**: Find the equation of the line passing through ({{x1}}, {{y1}}) and ({{x2}}, {{y2}}).
<!-- coordinates: integers [-10, 10] -->

**Hard**: Find the equation of the line that is perpendicular to {{a}}x + {{b}}y + {{c}} = 0 and passes through the point of intersection of the lines {{a1}}x + {{b1}}y + {{c1}} = 0 and {{a2}}x + {{b2}}y + {{c2}} = 0.
<!-- coefficients: integers [-5, 5], lines should intersect -->

### 8.6 Area of Triangle

**Easy**: Find the area of the triangle with vertices A({{x1}}, {{y1}}), B({{x2}}, {{y2}}), and C({{x3}}, {{y3}}).
<!-- coordinates chosen for clean area (integer or simple fraction) -->

**Medium**: The vertices of a triangle are A({{x1}}, {{y1}}), B({{x2}}, {{y2}}), and C({{x3}}, {{y3}}). Find the area and determine if the points are collinear.
<!-- one set collinear (area = 0), one set not collinear -->

**Hard**: Find the value of k if the area of the triangle with vertices ({{x1}}, {{y1}}), (k, {{y2}}), and ({{x3}}, {{y3}}) is {{area}} square units.
<!-- coordinates and area chosen for clean k value -->

---

## 9. Conic Sections

### 9.1 Circle

**Easy**: Write the equation of a circle with center ({{h}}, {{k}}) and radius {{r}}.
<!-- h, k: integers [-10, 10], r: integer [2, 10] -->

**Medium**: Find the center and radius of the circle: x² + y² + {{d}}x + {{e}}y + {{f}} = 0.
<!-- d, e, f chosen so d²/4 + e²/4 - f > 0 (valid circle) -->

**Hard**: Find the equation of the circle passing through points ({{x1}}, {{y1}}), ({{x2}}, {{y2}}), and ({{x3}}, {{y3}}).
<!-- three non-collinear points with integer coordinates -->

### 9.2 Parabola

**Easy**: Identify the vertex, axis of symmetry, and direction of opening for the parabola y = (x - {{h}})² + {{k}}.
<!-- h, k: integers [-5, 5] -->

**Medium**: Find the vertex, focus, and directrix of the parabola y = {{a}}(x - {{h}})² + {{k}}.
<!-- a: rational non-zero, h, k: integers [-5, 5] -->

**Hard**: A parabola has vertex at ({{h}}, {{k}}) and passes through point ({{px}}, {{py}}). Find its equation.
<!-- coordinates chosen for clean coefficient a -->

---

## 10. Vectors

### 10.1 Basic Vector Operations

**Easy**: Find the magnitude of vector **v** = {{i_comp}}**i** + {{j_comp}}**j**.
<!-- i_comp, j_comp: integers [-10, 10] -->

**Medium**: Given vectors **a** = {{a1}}**i** + {{a2}}**j** and **b** = {{b1}}**i** + {{b2}}**j**, find **a** + **b**, **a** - **b**, and {{scalar}}**a**.
<!-- components: integers [-8, 8], scalar: integer [2, 5] -->

**Hard**: Find the unit vector in the direction of **v** = {{i_comp}}**i** + {{j_comp}}**j** + {{k_comp}}**k**.
<!-- components chosen for clean magnitude like 3-4-5, 5-12-13, or √2, √3 results -->

### 10.2 Dot Product

**Easy**: Find the dot product of **a** = {{a1}}**i** + {{a2}}**j** and **b** = {{b1}}**i** + {{b2}}**j**.
<!-- components: integers [-8, 8] -->

**Medium**: Find the angle between vectors **a** = {{a1}}**i** + {{a2}}**j** and **b** = {{b1}}**i** + {{b2}}**j**.
<!-- components chosen for common angle like 0°, 30°, 45°, 60°, 90°, 120°, 180° -->

**Hard**: For what value of {{var}} are the vectors **a** = {{a1}}**i** + {{var}}**j** + {{a3}}**k** and **b** = {{b1}}**i** + {{b2}}**j** + {{b3}}**k** perpendicular?
<!-- coefficients chosen for integer solution -->

### 10.3 Cross Product

**Easy**: Find the cross product of **a** = {{a1}}**i** + {{a2}}**j** + {{a3}}**k** and **b** = {{b1}}**i** + {{b2}}**j** + {{b3}}**k**.
<!-- components: integers [-5, 5] -->

**Medium**: Find the area of the parallelogram with adjacent sides represented by **a** = {{a1}}**i** + {{a2}}**j** + {{a3}}**k** and **b** = {{b1}}**i** + {{b2}}**j** + {{b3}}**k**.
<!-- components: integers [-5, 5] -->

**Hard**: Find the area of the triangle with vertices A({{x1}}, {{y1}}, {{z1}}), B({{x2}}, {{y2}}, {{z2}}), and C({{x3}}, {{y3}}, {{z3}}).
<!-- coordinates: integers [-5, 5] -->

### 10.4 Vector Projection

**Medium**: Find the projection of vector **a** = {{a1}}**i** + {{a2}}**j** onto **b** = {{b1}}**i** + {{b2}}**j**.
<!-- components: integers [-8, 8] -->

**Hard**: Find the component of **a** = {{a1}}**i** + {{a2}}**j** + {{a3}}**k** along **b** = {{b1}}**i** + {{b2}}**j** + {{b3}}**k** and perpendicular to **b**.
<!-- components: integers [-5, 5] -->

---

## 11. Trigonometry

### 11.1 Trigonometric Ratios

**Easy**: In a right triangle, if sin θ = {{num}}/{{den}}, find cos θ and tan θ.
<!-- num < den, both positive integers, forms valid sin value -->

**Medium**: In a right triangle ABC with right angle at B, if AB = {{ab}} and BC = {{bc}}, find all six trigonometric ratios of angle A.
<!-- ab, bc: integers [3, 15], forms Pythagorean triple with hypotenuse -->

**Hard**: If tan A = {{tan_val}} and A is in the {{quadrant}} quadrant, find sin A and cos A.
<!-- tan_val: simple fraction, quadrant: "first", "second", "third", or "fourth" -->

### 11.2 Trigonometric Identities

**Easy**: Simplify: sin²θ + cos²θ · {{multiplier}}.
<!-- multiplier: integer [1, 5] or simple expression -->

**Medium**: Prove that (1 + tan²θ)(1 + cot²θ) = 1/(sin²θ · cos²θ) by simplifying the left side when θ = {{angle}}°.
<!-- angle: 30, 45, 60 for clean values -->

**Hard**: If sin θ + cos θ = {{sum_val}}, find the value of sin θ · cos θ and sin³θ + cos³θ.
<!-- sum_val: value that gives real solutions, like √2, 1.2, etc. -->

### 11.3 Angle Formulas

**Easy**: Find the exact value of sin({{angle1}}° + {{angle2}}°) using the sum formula.
<!-- angle1 + angle2 should give standard angle, e.g., 30+45=75 -->

**Medium**: If sin A = {{sin_a}} and cos B = {{cos_b}}, where A and B are acute angles, find sin(A + B) and cos(A - B).
<!-- sin_a, cos_b: standard values like 3/5, 4/5, 5/13, 12/13 -->

**Hard**: Express sin {{n}}θ in terms of sin θ using multiple angle formulas (for n = {{n}}).
<!-- n: 2 or 3 -->

### 11.4 Height and Distance

**Easy**: A tower casts a shadow of {{shadow}} m when the sun's elevation is {{angle}}°. Find the height of the tower.
<!-- shadow: integer [10, 50], angle: 30, 45, or 60 for clean answer -->

**Medium**: From the top of a {{height}} m high building, the angle of elevation of the top of a tower is {{elev}}° and the angle of depression of its base is {{depr}}°. Find the height of the tower and the distance between the building and tower.
<!-- height: integer [20, 50], angles: 30, 45, 60 -->

**Hard**: Two towers are {{distance}} m apart. From a point midway between them on the ground, the angles of elevation to the tops are {{angle1}}° and {{angle2}}°. Find the heights of both towers.
<!-- distance: integer [50, 200], angles: 30, 45, 60 -->

### 11.5 Inverse Trigonometric Functions

**Easy**: Find the principal value of sin⁻¹({{value}}).
<!-- value: -1, -√3/2, -√2/2, -1/2, 0, 1/2, √2/2, √3/2, 1 -->

**Medium**: Simplify: tan⁻¹({{a}}) + tan⁻¹({{b}}).
<!-- a, b chosen so ab < 1 or ab > 1 for different formulas -->

**Hard**: Prove that sin⁻¹({{a}}/{{c}}) + cos⁻¹({{b}}/{{c}}) = π/2 when {{a}}² + {{b}}² = {{c}}² (verify with specific Pythagorean triple values).
<!-- a, b, c: Pythagorean triple like 3, 4, 5 or 5, 12, 13 -->

---

## 12. Probability

### 12.1 Basic Probability

**Easy**: A bag contains {{red}} red balls, {{blue}} blue balls, and {{green}} green balls. If one ball is drawn at random, find the probability of drawing a {{color}} ball.
<!-- red, blue, green: integers [2, 10], color: "red", "blue", or "green" -->

**Medium**: Two dice are thrown simultaneously. Find the probability of getting a sum of {{target_sum}}.
<!-- target_sum: integer [2, 12] -->

**Hard**: A bag contains {{total}} balls numbered 1 to {{total}}. One ball is drawn at random. Find the probability that the number on the ball is: (a) divisible by {{divisor}}, (b) a prime number, (c) a perfect square.
<!-- total: integer [20, 50], divisor: 2, 3, 4, or 5 -->

### 12.2 Permutations

**Easy**: In how many ways can {{n}} different books be arranged on a shelf?
<!-- n: integer [4, 8] -->

**Medium**: How many {{r}}-digit numbers can be formed using the digits {{digit_list}} if repetition is {{allowed_status}}?
<!-- r: integer [2, 4], digit_list: comma-separated digits, allowed_status: "allowed" or "not allowed" -->

**Hard**: In how many ways can the letters of the word "{{word}}" be arranged such that {{condition}}?
<!-- word: suitable word with repeating letters, condition: specific constraint -->

### 12.3 Combinations

**Easy**: In how many ways can a committee of {{r}} people be formed from {{n}} people?
<!-- n > r, both integers, n: [6, 15], r: [2, 5] -->

**Medium**: From a group of {{men}} men and {{women}} women, a committee of {{total}} is to be formed with at least {{min_women}} women. In how many ways can this be done?
<!-- men, women: integers [4, 10], total: integer [3, 6], min_women: integer [1, total-1] -->

**Hard**: How many triangles can be formed using {{n}} points in a plane, of which {{collinear}} points are collinear?
<!-- n: integer [8, 15], collinear: integer [3, 5] -->

### 12.4 Conditional Probability

**Medium**: A box contains {{red}} red and {{black}} black balls. Two balls are drawn successively without replacement. Find the probability that: (a) both are red, (b) first is red and second is black, (c) one of each color.
<!-- red, black: integers [4, 10] -->

**Hard**: In a class, {{pass_prob}}% of students pass in Mathematics and {{both_prob}}% pass in both Mathematics and Science. If a student is selected who passed in Mathematics, find the probability that they also passed in Science.
<!-- pass_prob > both_prob, both probabilities: integers [40, 90] -->

### 12.5 Bayes' Theorem

**Hard**: A factory has {{n}} machines producing identical items. Machine {{machine_list}} produces {{percent_list}}% of items respectively. Defect rates for machines are {{defect_list}}% respectively. If a randomly selected item is defective, find the probability it came from Machine {{query_machine}}.
<!-- n: 2 or 3, percentages sum to 100, defect rates: small percentages -->

---

## 13. Complex Numbers

### 13.1 Basic Operations

**Easy**: Simplify: ({{a}} + {{b}}i) + ({{c}} + {{d}}i).
<!-- a, b, c, d: integers [-10, 10] -->

**Medium**: Find the product of ({{a}} + {{b}}i) and ({{c}} + {{d}}i).
<!-- a, b, c, d: integers [-8, 8] -->

**Hard**: Divide ({{a}} + {{b}}i) by ({{c}} + {{d}}i) and express in the form x + yi.
<!-- a, b, c, d: integers [-10, 10], c² + d² ≠ 0 -->

### 13.2 Modulus and Argument

**Easy**: Find the modulus of the complex number {{a}} + {{b}}i.
<!-- a, b: integers [-10, 10] -->

**Medium**: Find the modulus and argument of z = {{a}} + {{b}}i.
<!-- a, b chosen for standard angle arguments: 0°, 30°, 45°, 60°, 90°, etc. -->

**Hard**: If |z - ({{a}} + {{b}}i)| = {{r}}, describe the locus of z in the Argand plane and find its equation.
<!-- a, b: integers [-5, 5], r: positive integer [2, 8] -->

### 13.3 Polar and Exponential Form

**Medium**: Convert z = {{a}} + {{b}}i to polar form r(cos θ + i sin θ).
<!-- a, b chosen for standard angles -->

**Hard**: Using De Moivre's theorem, find ({{a}} + {{b}}i)^{{n}}.
<!-- a, b: simple values, n: integer [2, 6] -->

### 13.4 Powers of i

**Easy**: Simplify i^{{n}}.
<!-- n: integer [1, 100], cycles every 4 -->

**Medium**: Simplify: i^{{n1}} + i^{{n2}} + i^{{n3}} + i^{{n4}}.
<!-- n1, n2, n3, n4: integers chosen for interesting sums -->

---

## 14. Logarithms

### 14.1 Basic Logarithm Calculations

**Easy**: Evaluate log_{{base}}({{value}}).
<!-- base and value chosen so answer is integer: e.g., log_2(8) = 3 -->

**Medium**: Simplify: log_{{base}}({{a}}) + log_{{base}}({{b}}).
<!-- a, b, base: positive integers -->

**Hard**: Solve for x: log_{{base1}}(x) + log_{{base2}}(x) = {{value}}.
<!-- bases and value chosen for solvable equation -->

### 14.2 Logarithm Properties

**Easy**: Express log_{{base}}({{a}}^{{n}}) in terms of log_{{base}}({{a}}).
<!-- a, n, base: positive integers [2, 10] -->

**Medium**: Simplify: {{coeff1}}·log_{{base}}({{a}}) - {{coeff2}}·log_{{base}}({{b}}) + log_{{base}}({{c}}).
<!-- coefficients and values chosen for meaningful simplification -->

**Hard**: If log_{{base1}}({{a}}) = {{val1}} and log_{{base1}}({{b}}) = {{val2}}, find log_{{base2}}({{expression}}).
<!-- expression involving a and b -->

### 14.3 Change of Base

**Medium**: Convert log_{{base1}}({{value}}) to base {{base2}}.
<!-- bases: 2, 5, 10, e; value: positive integer -->

**Hard**: Prove that log_a(b) × log_b(c) × log_c(a) = 1 using specific values a = {{a}}, b = {{b}}, c = {{c}}.
<!-- a, b, c: positive integers, all different -->

### 14.4 Logarithmic Equations

**Easy**: Solve: log_{{base}}(x) = {{value}}.
<!-- base: integer [2, 10], value: integer [-2, 4] -->

**Medium**: Solve: log_{{base}}(x + {{const1}}) + log_{{base}}(x + {{const2}}) = {{value}}.
<!-- constants and value chosen for real positive solution -->

**Hard**: Solve: log_{{base1}}({{a}}^x) = log_{{base2}}({{b}}^(x+{{c}})).
<!-- values chosen for solvable equation -->

---

## 15. Sequences and Series

### 15.1 Arithmetic Progression (AP)

**Easy**: Find the {{n}}th term of the AP: {{first}}, {{second}}, {{third}}, ...
<!-- first, second, third in AP, n: integer [5, 20] -->

**Medium**: The {{m}}th term of an AP is {{tm}} and the {{n}}th term is {{tn}}. Find the first term and common difference.
<!-- m, n, tm, tn chosen for integer solutions -->

**Hard**: The sum of the first {{n1}} terms of an AP is {{s1}} and the sum of first {{n2}} terms is {{s2}}. Find the sum of first {{n3}} terms.
<!-- n1, n2, n3: different positive integers, s1, s2 consistent with an AP -->

### 15.2 Geometric Progression (GP)

**Easy**: Find the {{n}}th term of the GP: {{first}}, {{second}}, {{third}}, ...
<!-- first, second, third in GP, n: integer [5, 10] -->

**Medium**: The {{m}}th term of a GP is {{tm}} and the {{n}}th term is {{tn}}. Find the first term and common ratio.
<!-- m, n, tm, tn chosen for clean ratio -->

**Hard**: The sum of a GP is {{sum}}, the first term is {{first}}, and the common ratio is {{ratio}}. Find the number of terms.
<!-- values chosen for integer number of terms -->

### 15.3 Sum of Series

**Easy**: Find the sum of the first {{n}} terms of the AP: {{first}} + {{second}} + {{third}} + ...
<!-- first, second, third in AP, n: integer [10, 25] -->

**Medium**: Find the sum of the GP: {{first}} + {{second}} + {{third}} + ... to {{n}} terms.
<!-- first, second, third in GP, n: integer [5, 10] -->

**Hard**: Find the sum: {{a1}} + {{a2}} + {{a3}} + ... + {{an}} where the kth term is given by a_k = {{formula}}.
<!-- formula involving k, like k², k(k+1), etc. -->

### 15.4 Arithmetic-Geometric Progression (AGP)

**Hard**: Find the sum of {{n}} terms of the series: {{first}} + {{second}} + {{third}} + ... where each term is the product of corresponding terms of an AP with first term {{ap_first}} and common difference {{ap_diff}}, and a GP with first term {{gp_first}} and common ratio {{gp_ratio}}.
<!-- parameters chosen for manageable calculation -->
