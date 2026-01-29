# 12th Grade Math Problem Templates

# PART 1: MATRICES

---

## 1.1 Introduction to Matrices

### **Easy:** Basic Matrix Identification
> Write the matrix with {{m}} rows and {{n}} columns where the element in row i and column j equals {{formula}}.

**Example:** Write the 2×3 matrix where element aᵢⱼ = i + j.

### **Medium:** Matrix from Real-World Data
> A store sells {{n}} products at {{m}} different locations. The sales data shows Location 1 sold {a₁₁}, {a₁₂}, ... units of each product. Location 2 sold {a₂₁}, {a₂₂}, ... units. Represent this data as a matrix and identify its dimensions.

### **Hard:** Matrix Construction with Conditions
> Construct a {{n}}×{{n}} matrix A where aᵢⱼ = {{formula_1}} when i < j, aᵢⱼ = {{formula_2}} when i > j, and aᵢⱼ = {{formula_3}} when i = j.

---

## 1.2 Types of Matrices

### **Easy:** Matrix Type Identification
> Identify the type of the following matrix: {{matrix}}. Choose from: square, diagonal, identity, zero, symmetric, skew-symmetric, upper triangular, lower triangular.

### **Medium:** Construct Specific Matrix Types
> Construct a {{n}}×{{n}} {{matrix_type}} matrix where the non-zero elements follow the pattern {{pattern}}.

**Example:** Construct a 3×3 upper triangular matrix where the non-zero elements equal i × j.

### **Hard:** Matrix Type Properties
> Given that A is a {{n}}×{{n}} {{matrix_type_1}} matrix with diagonal elements {d₁}, {d₂}, ..., {dₙ}, find a matrix B such that A + B is a {{matrix_type_2}} matrix.

---

## 1.3 Matrix Addition & Subtraction

### **Easy:** Basic Matrix Addition
> Add the matrices A = {{matrix_A}} and B = {{matrix_B}}.

**Example:** Add A = [2, 3; 1, 4] and B = [5, -1; 2, 3].

### **Medium:** Matrix Equation Solving
> Find matrix X if {{a}}A + {{b}}X = {{c}}B, where A = {{matrix_A}} and B = {{matrix_B}}.

**Example:** Find X if 2A + 3X = B, where A = [1, 2; 3, 4] and B = [11, 16; 21, 26].

### **Hard:** System of Matrix Equations
> Find matrices X and Y if X + Y = {{matrix_A}} and X - Y = {{matrix_B}}.

---

## 1.4 Scalar Multiplication

### **Easy:** Basic Scalar Multiplication
> Multiply the matrix A = {{matrix_A}} by the scalar k = {{k}}.

### **Medium:** Combined Scalar Operations
> Compute {{a}}A - {{b}}B + {{c}}C where A = {{matrix_A}}, B = {{matrix_B}}, and C = {{matrix_C}}.

### **Hard:** Finding Scalars
> Find the values of {{x}} and {{y}} such that {{x}}A + {{y}}B = C, where A = {{matrix_A}}, B = {{matrix_B}}, and C = {{matrix_C}}.

---

## 1.5 Matrix Multiplication

### **Easy:** Basic Matrix Multiplication
> Compute the product AB where A = {{matrix_A}} ({{m}}×{{n}}) and B = {{matrix_B}} ({{n}}×{{p}}).

**Example:** Compute AB where A = [1, 2; 3, 4] and B = [5, 6; 7, 8].

### **Medium:** Matrix Power
> Compute A^{{n}} where A = {{matrix_A}}.

**Example:** Compute A² where A = [1, 1; 1, 0].

### **Hard:** Matrix Multiplication Properties
> Given A = {{matrix_A}} and B = {{matrix_B}}, verify whether AB = BA. If not, compute both products and find AB - BA.

---

## 1.6 Transpose of a Matrix

### **Easy:** Basic Transpose
> Find the transpose of matrix A = {{matrix_A}}.

### **Medium:** Transpose Properties
> Given A = {{matrix_A}} and B = {{matrix_B}}, verify that (AB)ᵀ = BᵀAᵀ.

### **Hard:** Symmetric/Skew-Symmetric Decomposition
> Express the matrix A = {{matrix_A}} as the sum of a symmetric matrix and a skew-symmetric matrix.

---

## 1.7 Determinant of a Matrix

### **Easy:** 2×2 Determinant
> Calculate the determinant of the matrix A = [{{a}}, {{b}}; {{c}}, {{d}}].

**Example:** Find |A| where A = [3, 5; 2, 4].

### **Medium:** 3×3 Determinant
> Calculate the determinant of the matrix A = {{3x3_matrix}} using cofactor expansion along {row/column}.

**Example:** Find |A| where A = [2, 1, 3; 4, -1, 2; 1, 5, -2].

### **Hard:** Determinant with Variables
> For what value(s) of {{x}} is the matrix A = {{matrix_with_x}} singular?

**Example:** Find x such that |[x, 2, 1; 3, x, 2; 1, 2, x]| = 0.

---

## 1.8 Inverse of a Matrix

### **Easy:** 2×2 Matrix Inverse
> Find the inverse of A = [{{a}}, {{b}}; {{c}}, {{d}}], if it exists.

**Example:** Find A⁻¹ where A = [4, 7; 2, 6].

### **Medium:** Inverse Verification
> Given A = {{matrix_A}}, find A⁻¹ and verify that AA⁻¹ = I.

### **Hard:** Inverse Using Row Reduction
> Use elementary row operations to find the inverse of A = {{3x3_matrix}}.

---

## 1.9 Adjoint of a Matrix

### **Easy:** Cofactor Calculation
> Find the cofactor of element a_{{ij}} in the matrix A = {{matrix_A}}.

**Example:** Find C₂₃ for A = [1, 2, 3; 4, 5, 6; 7, 8, 9].

### **Medium:** Adjoint Matrix
> Find the adjoint of the matrix A = {{3x3_matrix}}.

### **Hard:** Inverse via Adjoint
> Use the formula A⁻¹ = (1/|A|)·adj(A) to find the inverse of A = {{3x3_matrix}}.

---

## 1.10 Solving Systems Using Matrices

### **Easy:** 2×2 System
> Solve the system using matrices:
> {a₁}x + {b₁}y = {c₁}
> {a₂}x + {b₂}y = {c₂}

**Example:** Solve: 2x + 3y = 7, 4x - y = 5.

### **Medium:** 3×3 System (Cramer's Rule)
> Use Cramer's Rule to solve:
> {a₁}x + {b₁}y + {c₁}z = {d₁}
> {a₂}x + {b₂}y + {c₂}z = {d₂}
> {a₃}x + {b₃}y + {c₃}z = {d₃}

### **Hard:** Augmented Matrix & Row Reduction
> Solve the following system using the augmented matrix and Gauss-Jordan elimination:
> {{system_of_equations}}

---

## 1.11 Eigenvalues and Eigenvectors

### **Easy:** Verify Eigenvalue/Eigenvector
> Verify that λ = {{lambda}} is an eigenvalue of A = {{matrix_A}} with eigenvector v = {{vector_v}}.

**Example:** Verify λ = 5 is an eigenvalue of A = [4, 1; 2, 3] with eigenvector v = [1, 1]ᵀ.

### **Medium:** Find Eigenvalues
> Find the eigenvalues of the matrix A = {{2x2_matrix}}.

**Example:** Find eigenvalues of A = [3, 1; 0, 2].

### **Hard:** Complete Eigen Analysis
> Find all eigenvalues and corresponding eigenvectors of A = {{matrix_A}}. Determine if A is diagonalizable.

---

## 1.12 Rank and Trace

### **Easy:** Trace Calculation
> Find the trace of the matrix A = {n×n_matrix}.

**Example:** Find tr(A) where A = [2, 1, 3; 4, 5, 6; 7, 8, 9].

### **Medium:** Rank Determination
> Find the rank of the matrix A = {{matrix_A}} using row reduction.

### **Hard:** Rank-Nullity Application
> Given the matrix A = {m×n_matrix}, find the rank of A and the dimension of its null space.

---

# PART 2: VECTOR ALGEBRA

---

## 2.1 Vector Basics & Magnitude

### **Easy:** Vector Magnitude
> Find the magnitude of vector **v** = ⟨{{a}}, {{b}}, {{c}}⟩.

**Example:** Find |**v**| where **v** = ⟨3, 4, 0⟩.

### **Medium:** Vector Between Points
> Find the vector from point P({x₁}, {y₁}, {z₁}) to point Q({x₂}, {y₂}, {z₂}) and calculate its magnitude.

### **Hard:** Normalized Components
> A vector has magnitude {{m}} and makes angles {α}, {β}, {γ} with the positive x, y, z axes respectively. Find the vector's components.

---

## 2.2 Types of Vectors

### **Easy:** Unit Vector
> Find the unit vector in the direction of **v** = ⟨{{a}}, {{b}}, {{c}}⟩.

**Example:** Find the unit vector in the direction of **v** = ⟨1, 2, 2⟩.

### **Medium:** Parallel Vectors Check
> Determine whether vectors **u** = ⟨{a₁}, {b₁}, {c₁}⟩ and **v** = ⟨{a₂}, {b₂}, {c₂}⟩ are parallel, anti-parallel, or neither.

### **Hard:** Collinearity of Points
> Determine if the points A({x₁}, {y₁}, {z₁}), B({x₂}, {y₂}, {z₂}), and C({x₃}, {y₃}, {z₃}) are collinear.

---

## 2.3 Vector Addition

### **Easy:** Basic Vector Addition
> Add vectors **u** = ⟨{a₁}, {b₁}⟩ and **v** = ⟨{a₂}, {b₂}⟩.

### **Medium:** Triangle Law Application
> Using the triangle law, find **a** + **b** where |**a**| = {m₁}, |**b**| = {m₂}, and the angle between them is {θ}°.

### **Hard:** Parallelogram Law with Diagonals
> Two adjacent sides of a parallelogram are represented by vectors **a** = ⟨{a₁}, {a₂}, {a₃}⟩ and **b** = ⟨{b₁}, {b₂}, {b₃}⟩. Find the vectors representing both diagonals and their magnitudes.

---

## 2.4 Dot Product

### **Easy:** Basic Dot Product
> Calculate **u** · **v** where **u** = ⟨{a₁}, {b₁}, {c₁}⟩ and **v** = ⟨{a₂}, {b₂}, {c₂}⟩.

**Example:** Find **u** · **v** where **u** = ⟨2, 3, 1⟩ and **v** = ⟨1, -2, 4⟩.

### **Medium:** Angle Between Vectors
> Find the angle between vectors **u** = ⟨{a₁}, {b₁}, {c₁}⟩ and **v** = ⟨{a₂}, {b₂}, {c₂}⟩.

**Example:** Find the angle between **u** = ⟨1, 0, 1⟩ and **v** = ⟨0, 1, 1⟩.

### **Hard:** Orthogonality Condition
> For what value of {{k}} are vectors **u** = ⟨{a₁}, {b₁}, k⟩ and **v** = ⟨{a₂}, {b₂}, {c₂}⟩ orthogonal?

---

## 2.5 Cross Product

### **Easy:** Basic Cross Product
> Calculate **u** × **v** where **u** = ⟨{a₁}, {b₁}, {c₁}⟩ and **v** = ⟨{a₂}, {b₂}, {c₂}⟩.

**Example:** Find **u** × **v** where **u** = ⟨1, 2, 3⟩ and **v** = ⟨4, 5, 6⟩.

### **Medium:** Area of Parallelogram
> Find the area of the parallelogram with adjacent sides **a** = ⟨{a₁}, {a₂}, {a₃}⟩ and **b** = ⟨{b₁}, {b₂}, {b₃}⟩.

### **Hard:** Triangle Area from Vertices
> Find the area of the triangle with vertices A({x₁}, {y₁}, {z₁}), B({x₂}, {y₂}, {z₂}), and C({x₃}, {y₃}, {z₃}).

---

## 2.6 Vector Projection

### **Easy:** Scalar Projection
> Find the scalar projection of **a** = ⟨{a₁}, {a₂}⟩ onto **b** = ⟨{b₁}, {b₂}⟩.

### **Medium:** Vector Projection
> Find the vector projection of **a** = ⟨{a₁}, {a₂}, {a₃}⟩ onto **b** = ⟨{b₁}, {b₂}, {b₃}⟩.

**Example:** Project **a** = ⟨3, 4, 0⟩ onto **b** = ⟨1, 0, 0⟩.

### **Hard:** Orthogonal Decomposition
> Decompose vector **v** = ⟨{{a}}, {{b}}, {{c}}⟩ into components parallel and perpendicular to **u** = ⟨{{d}}, {{e}}, {{f}}⟩.

---

# PART 3: CALCULUS — LIMITS

---

## 3.1 Limits from Definition

### **Easy:** Direct Substitution
> Evaluate lim(x→{{a}}) ({{polynomial}}).

**Example:** Evaluate lim(x→2) (x² + 3x - 1).

### **Medium:** Limit with Factoring
> Evaluate lim(x→{{a}}) [(x² - {a²})/(x - {{a}})].

**Example:** Evaluate lim(x→3) [(x² - 9)/(x - 3)].

### **Hard:** Piecewise Function Limit
> Given f(x) = { {expr₁}, if x < {{a}}; {expr₂}, if x ≥ {{a}} }, find lim(x→{{a}}) f(x) if it exists.

---

## 3.2 One-Sided Limits

### **Easy:** Basic One-Sided
> Evaluate lim(x→{{a}}⁺) {{function}} and lim(x→{{a}}⁻) {{function}}.

### **Medium:** One-Sided for Piecewise
> For f(x) = { {expr₁}, x < {{a}}; {expr₂}, x ≥ {{a}} }, find lim(x→{{a}}⁻) f(x) and lim(x→{{a}}⁺) f(x).

### **Hard:** Continuity Analysis
> Determine values of {{k}} for which lim(x→{{a}}) f(x) exists, where f(x) = { {expr₁}, x < {{a}}; {{k}}x + {{b}}, x ≥ {{a}} }.

---

## 3.3 Limits by Rationalization

### **Easy:** Basic Rationalization
> Evaluate lim(x→{{a}}) [(√x - √{{a}})/(x - {{a}})].

**Example:** Evaluate lim(x→4) [(√x - 2)/(x - 4)].

### **Medium:** Complex Rationalization
> Evaluate lim(x→{{a}}) [(√(x + {{b}}) - √({{a}} + {{b}}))/(x - {{a}})].

### **Hard:** Double Radical
> Evaluate lim(x→0) [(√({{a}} + x) - √({{a}} - x))/x].

---

## 3.4 Limits at Infinity

### **Easy:** Polynomial Ratio
> Evaluate lim(x→∞) [({{a}}x² + {{b}}x + {{c}})/({{d}}x² + {{e}}x + {{f}})].

**Example:** Evaluate lim(x→∞) [(3x² + 2x)/(5x² - 1)].

### **Medium:** Different Degree Polynomials
> Evaluate lim(x→∞) [({{a}}x³ + {{b}})/({{c}}x² + {{d}})].

### **Hard:** Radical at Infinity
> Evaluate lim(x→∞) [√({{a}}x² + {{b}}x) - {{c}}x].

---

## 3.5 Asymptotes

### **Easy:** Vertical Asymptote
> Find all vertical asymptotes of f(x) = {{rational_function}}.

**Example:** Find vertical asymptotes of f(x) = (x + 2)/(x² - 4).

### **Medium:** Horizontal Asymptote
> Find the horizontal asymptote of f(x) = ({{a}}x^{{n}} + ...)/(({{b}}x^{{m}} + ...).

### **Hard:** Oblique Asymptote
> Find all asymptotes (vertical, horizontal, and oblique) of f(x) = (x² + {{a}}x + {{b}})/(x + {{c}}).

---

## 3.6 Continuity

### **Easy:** Continuity at a Point
> Is f(x) = {{function}} continuous at x = {{a}}? Justify your answer.

**Example:** Is f(x) = (x² - 4)/(x - 2) continuous at x = 2?

### **Medium:** Making a Function Continuous
> Find the value of k that makes f(x) continuous at x = {{a}}, where f(x) = { {expr₁}, x ≠ {{a}}; k, x = {{a}} }.

**Example:** Find k so f(x) = { (x² - 9)/(x - 3), x ≠ 3; k, x = 3 } is continuous at x = 3.

### **Hard:** Intermediate Value Theorem
> Use the Intermediate Value Theorem to show that f(x) = {{polynomial}} has a root in the interval [{{a}}, {{b}}].

**Example:** Show that x³ - 2x - 5 = 0 has a solution in [2, 3].

---

# PART 4: CALCULUS — DERIVATIVES

---

## 4.1 Introduction to Derivatives

### **Easy:** Derivative from Definition
> Use the limit definition to find f'({{a}}) where f(x) = {{simple_function}}.

**Example:** Use the definition to find f'(2) where f(x) = x².

### **Medium:** Average vs Instantaneous Rate
> For f(x) = {{function}}, find the average rate of change on [{{a}}, {{b}}] and the instantaneous rate of change at x = {{c}}.

### **Hard:** Differentiability Analysis
> Determine whether f(x) = |x - {{a}}| is differentiable at x = {{a}}. Explain using the limit definition.

---

## 4.2 Power Rule

### **Easy:** Basic Power Rule
> Find the derivative of f(x) = {{a}}x^{{n}}.

**Example:** Find d/dx [5x⁴].

### **Medium:** Polynomial Derivative
> Find f'(x) where f(x) = {{a}}x^{{n}} + {{b}}x^{{m}} + {{c}}x^{{p}} + {{d}}.

**Example:** Find the derivative of f(x) = 3x⁵ - 2x³ + 7x - 4.

### **Hard:** Rational Exponents
> Find the derivative of f(x) = {{a}}x^{p/q} + {{b}}x^{-r/s}.

**Example:** Find d/dx [4x^(3/2) - 2x^(-1/2)].

---

## 4.3 Product Rule

### **Easy:** Basic Product Rule
> Find the derivative of f(x) = ({{a}}x + {{b}})({{c}}x² + {{d}}).

**Example:** Find d/dx [(2x + 1)(x² - 3)].

### **Medium:** Product with Transcendental
> Find the derivative of f(x) = {{polynomial}} · {{transcendental_function}}.

**Example:** Find d/dx [x² sin(x)].

### **Hard:** Triple Product
> Find the derivative of f(x) = ({expr₁})({expr₂})({expr₃}).

**Example:** Find d/dx [x · eˣ · ln(x)].

---

## 4.4 Quotient Rule

### **Easy:** Basic Quotient Rule
> Find the derivative of f(x) = ({{a}}x + {{b}})/({{c}}x + {{d}}).

**Example:** Find d/dx [(3x + 2)/(x - 1)].

### **Medium:** Polynomial Quotient
> Find the derivative of f(x) = (x² + {{a}}x + {{b}})/(x² + {{c}}x + {{d}}).

### **Hard:** Quotient with Transcendentals
> Find the derivative of f(x) = {{trig_function}}/{{exponential_function}}.

**Example:** Find d/dx [sin(x)/(eˣ + 1)].

---

## 4.5 Chain Rule

### **Easy:** Basic Chain Rule
> Find the derivative of f(x) = ({{a}}x + {{b}})^{{n}}.

**Example:** Find d/dx [(3x + 2)⁵].

### **Medium:** Nested Function
> Find the derivative of f(x) = {{outer_function}}({{inner_function}}).

**Example:** Find d/dx [sin(x²)].

### **Hard:** Multiple Chain Rule
> Find the derivative of f(x) = {{outer}}({{middle}}({{inner}})).

**Example:** Find d/dx [ln(cos(eˣ))].

---

## 4.6 Derivatives of Trigonometric Functions

### **Easy:** Basic Trig Derivative
> Find the derivative of f(x) = {{a}}sin({{b}}x) + {{c}}cos({{d}}x).

**Example:** Find d/dx [3sin(2x) - cos(x)].

### **Medium:** Trig with Chain Rule
> Find the derivative of f(x) = tan({{polynomial}}).

**Example:** Find d/dx [tan(x² + 1)].

### **Hard:** Composite Trig Functions
> Find the derivative of f(x) = sec²({{a}}x) · tan³({{b}}x).

---

## 4.7 Derivatives of Exponential & Logarithmic Functions

### **Easy:** Basic Exponential
> Find the derivative of f(x) = {{a}}e^({{b}}x).

**Example:** Find d/dx [5e^(3x)].

### **Medium:** General Exponential/Logarithm
> Find the derivative of f(x) = {{a}}^{g(x)} or f(x) = log_{{a}}({g(x)}).

**Example:** Find d/dx [2^(x²)] and d/dx [log₃(x² + 1)].

### **Hard:** Logarithmic Differentiation Required
> Use logarithmic differentiation to find dy/dx where y = x^{{x}} or y = ({{function}})^{{function}}.

**Example:** Find dy/dx where y = x^(sin x).

---

## 4.8 Derivatives of Inverse Trig Functions

### **Easy:** Basic Inverse Trig
> Find the derivative of f(x) = arcsin({{a}}x) or arctan({{b}}x).

**Example:** Find d/dx [arctan(3x)].

### **Medium:** Inverse Trig with Chain Rule
> Find the derivative of f(x) = arcsin({{polynomial}}).

**Example:** Find d/dx [arccos(x²)].

### **Hard:** Complex Inverse Trig
> Find the derivative of f(x) = arctan({{rational_function}}).

**Example:** Find d/dx [arctan((1-x)/(1+x))].

---

## 4.9 Implicit Differentiation

### **Easy:** Basic Implicit
> Find dy/dx if x² + y² = {r²}.

**Example:** Find dy/dx if x² + y² = 25.

### **Medium:** Polynomial Implicit
> Find dy/dx if x³ + y³ = {{a}}xy.

**Example:** Find dy/dx if x³ + y³ = 6xy.

### **Hard:** Transcendental Implicit
> Find dy/dx if sin(xy) + eʸ = x.

---

## 4.10 Higher Order Derivatives

### **Easy:** Second Derivative
> Find f''(x) where f(x) = {{polynomial}}.

**Example:** Find f''(x) where f(x) = x⁴ - 3x² + 2x.

### **Medium:** nth Derivative
> Find the {{n}}th derivative of f(x) = e^({{a}}x) or f(x) = sin({{b}}x).

**Example:** Find the 4th derivative of f(x) = sin(2x).

### **Hard:** Parametric Second Derivative
> If x = {f(t)} and y = {g(t)}, find d²y/dx².

**Example:** Find d²y/dx² if x = t² and y = t³.

---

## 4.11 L'Hôpital's Rule

### **Easy:** Basic 0/0 Form
> Use L'Hôpital's Rule to evaluate lim(x→{{a}}) [{f(x)}/{g(x)}].

**Example:** Evaluate lim(x→0) [sin(x)/x].

### **Medium:** ∞/∞ Form
> Use L'Hôpital's Rule to evaluate lim(x→∞) [ln(x)/x^{{n}}].

**Example:** Evaluate lim(x→∞) [ln(x)/√x].

### **Hard:** Indeterminate Powers (0⁰, 1^∞, ∞⁰)
> Evaluate lim(x→{{a}}) [{f(x)}^{g(x)}] where the form is indeterminate.

**Example:** Evaluate lim(x→0⁺) [x^x].

---

## 4.12 First Derivative Test (Extrema)

### **Easy:** Critical Points
> Find all critical points of f(x) = {{polynomial}}.

**Example:** Find critical points of f(x) = x³ - 3x + 2.

### **Medium:** Local Extrema Classification
> Find and classify all local extrema of f(x) = {{function}} using the first derivative test.

**Example:** Find local max/min of f(x) = x⁴ - 4x³.

### **Hard:** Optimization Problem
> A {{geometric_shape}} has {{constraint}}. Find the dimensions that maximize/minimize {{quantity}}.

**Example:** A rectangle has perimeter 24 cm. Find dimensions that maximize area.

---

## 4.13 Second Derivative Test & Concavity

### **Easy:** Concavity Intervals
> Determine intervals where f(x) = {{polynomial}} is concave up and concave down.

**Example:** Find concavity intervals for f(x) = x³ - 6x².

### **Medium:** Inflection Points
> Find all inflection points of f(x) = {{function}}.

**Example:** Find inflection points of f(x) = x⁴ - 6x² + 8x.

### **Hard:** Complete Curve Sketch
> For f(x) = {{rational_or_transcendental}}, find: domain, intercepts, asymptotes, critical points, inflection points, and sketch the curve.

---

## 4.14 Mean Value Theorem

### **Easy:** MVT Application
> Verify the Mean Value Theorem for f(x) = {{polynomial}} on [{{a}}, {{b}}] and find all values c.

**Example:** Verify MVT for f(x) = x² on [0, 2] and find c.

### **Medium:** MVT Problem Solving
> A car travels {{d}} miles in {{t}} hours. Prove that at some point, the car's speed was exactly {d/t} mph.

### **Hard:** MVT with Bounds
> Given f(x) = {{function}} on [{{a}}, {{b}}] with f'(x) bounded by {{m}} ≤ f'(x) ≤ {{M}}, find bounds for f({{b}}) - f({{a}}).

---

## 4.15 Linear Approximation

### **Easy:** Basic Linearization
> Find the linear approximation of f(x) = {{function}} at a = {{a}}.

**Example:** Find linearization of f(x) = √x at a = 4.

### **Medium:** Approximation Calculation
> Use linear approximation to estimate {f(value)} where f(x) = {{function}}.

**Example:** Use linearization to estimate √4.1.

### **Hard:** Error Estimation
> Estimate {f(value)} using linear approximation and bound the error using the second derivative.

---

# PART 5: CALCULUS — INTEGRATION

---

## 5.1 Antiderivatives

### **Easy:** Basic Antiderivative
> Find ∫ {{a}}x^{{n}} dx.

**Example:** Find ∫ 4x³ dx.

### **Medium:** Sum of Powers
> Find ∫ ({{a}}x^{{n}} + {{b}}x^{{m}} + {{c}}x^{{p}}) dx.

**Example:** Find ∫ (3x² - 2x + 5) dx.

### **Hard:** Antiderivative with Initial Condition
> Find f(x) given f'(x) = {{expression}} and f({{a}}) = {{b}}.

**Example:** Find f(x) if f'(x) = 6x² - 4x + 1 and f(0) = 3.

---

## 5.2 Power Rule for Integration

### **Easy:** Positive Integer Powers
> Find ∫ {{a}}x^{{n}} dx where n is a positive integer.

### **Medium:** Fractional & Negative Powers
> Find ∫ ({{a}}/x^{{n}} + {{b}}√x) dx.

**Example:** Find ∫ (3/x² + 2√x) dx.

### **Hard:** Mixed Radicals
> Find ∫ (x^{p/q} - {{a}}x^{r/s} + {{b}}/x^{m/n}) dx.

---

## 5.3 Integration by Substitution

### **Easy:** Basic u-Substitution
> Find ∫ {f'(g(x))} · {g'(x)} dx.

**Example:** Find ∫ 2x(x² + 1)⁵ dx.

### **Medium:** Trig Substitution
> Find ∫ sin^{{n}}(x) cos(x) dx or ∫ {{trig_function}} dx.

**Example:** Find ∫ sin³(x) cos(x) dx.

### **Hard:** Complex Substitution
> Find ∫ {{complex_integrand}} dx requiring creative substitution.

**Example:** Find ∫ x/√(1 - x⁴) dx.

---

## 5.4 Integration by Parts

### **Easy:** Basic Integration by Parts
> Find ∫ x · e^({{a}}x) dx.

**Example:** Find ∫ x · e^(2x) dx.

### **Medium:** Multiple Applications
> Find ∫ x² · e^({{a}}x) dx or ∫ x² · sin({{b}}x) dx.

**Example:** Find ∫ x² sin(x) dx.

### **Hard:** Cyclic Integration by Parts
> Find ∫ e^({{a}}x) · sin({{b}}x) dx.

**Example:** Find ∫ eˣ sin(x) dx.

---

## 5.5 Definite Integrals

### **Easy:** Basic Definite Integral
> Evaluate ∫ from {{a}} to {{b}} of {{polynomial}} dx.

**Example:** Evaluate ∫₀² (3x² - 2x + 1) dx.

### **Medium:** Definite Integral with Substitution
> Evaluate ∫ from {{a}} to {{b}} of {{integrand}} dx using substitution.

**Example:** Evaluate ∫₀¹ x√(1 + x²) dx.

### **Hard:** Piecewise Definite Integral
> Evaluate ∫ from {{a}} to {{b}} of |{f(x)}| dx.

**Example:** Evaluate ∫₋₁² |x² - 1| dx.

---

## 5.6 Properties of Definite Integrals

### **Easy:** Basic Properties
> If ∫₀³ f(x)dx = {{a}} and ∫₃⁵ f(x)dx = {{b}}, find ∫₀⁵ f(x)dx.

### **Medium:** Symmetry Properties
> Evaluate ∫ from -{{a}} to {{a}} of {{odd_or_even_function}} dx using symmetry.

**Example:** Evaluate ∫₋₂² (x³ + x² - 2x + 3) dx.

### **Hard:** Comparison Properties
> Without calculating, determine which is larger: ∫₀¹ {f(x)} dx or ∫₀¹ {g(x)} dx.

---

## 5.7 Area Under Curve

### **Easy:** Area Below x-axis Awareness
> Find the area bounded by y = {{polynomial}}, the x-axis, x = {{a}}, and x = {{b}}.

**Example:** Find the area bounded by y = x² - 4, the x-axis, x = 0, and x = 3.

### **Medium:** Area Between Two Curves
> Find the area of the region bounded by y = {f(x)} and y = {g(x)}.

**Example:** Find the area between y = x² and y = x + 2.

### **Hard:** Area with Multiple Intersections
> Find the total area enclosed by y = {f(x)} and y = {g(x)} over [{{a}}, {{b}}].

---

## 5.8 Riemann Sums & Trapezoidal Rule

### **Easy:** Left/Right Riemann Sum
> Approximate ∫ from {{a}} to {{b}} of {f(x)} dx using a {left/right} Riemann sum with n = {{n}} subintervals.

**Example:** Approximate ∫₀⁴ x² dx using right Riemann sum with n = 4.

### **Medium:** Trapezoidal Rule
> Use the Trapezoidal Rule with n = {{n}} subintervals to approximate ∫ from {{a}} to {{b}} of {f(x)} dx.

**Example:** Use Trapezoidal Rule with n = 4 to approximate ∫₁³ 1/x dx.

### **Hard:** Error Bound Analysis
> Estimate ∫ from {{a}} to {{b}} of {f(x)} dx using the Trapezoidal Rule with n = {{n}}, and find the error bound.

---

## 5.9 Fundamental Theorem of Calculus

### **Easy:** FTC Part 1
> Find d/dx [∫ from {{a}} to x of {f(t)} dt].

**Example:** Find d/dx [∫₀ˣ sin(t²) dt].

### **Medium:** FTC with Variable Limits
> Find d/dx [∫ from {g(x)} to {h(x)} of {f(t)} dt].

**Example:** Find d/dx [∫₁^(x²) √(1 + t³) dt].

### **Hard:** FTC Application
> Find the value of ∫ from {{a}} to {{b}} of f'(x) · {g(f(x))} dx given f({{a}}) = {{c}} and f({{b}}) = {{d}}.

---

## 5.10 Improper Integrals

### **Easy:** Infinite Upper Limit
> Evaluate ∫ from {{a}} to ∞ of {f(x)} dx, or show it diverges.

**Example:** Evaluate ∫₁^∞ 1/x² dx.

### **Medium:** Infinite Lower Limit or Both
> Evaluate ∫ from -∞ to ∞ of {f(x)} dx.

**Example:** Evaluate ∫₋∞^∞ e^(-x²) dx (state result).

### **Hard:** Discontinuous Integrand
> Evaluate ∫ from {{a}} to {{b}} of {f(x)} dx where f has a discontinuity in [{{a}}, {{b}}].

**Example:** Evaluate ∫₀³ 1/(x-1)^(2/3) dx.

---

# PART 6: DIFFERENTIAL EQUATIONS

---

## 6.1 First-Order ODEs

### **Easy:** Separable Equations
> Solve the differential equation dy/dx = {f(x)} · {g(y)}.

**Example:** Solve dy/dx = xy.

### **Medium:** First-Order Linear
> Solve dy/dx + {P(x)}y = {Q(x)}.

**Example:** Solve dy/dx + 2y = e^(-x).

### **Hard:** Exact Equations
> Solve {M(x,y)}dx + {N(x,y)}dy = 0 by checking exactness.

**Example:** Solve (2xy + 3)dx + (x² - 1)dy = 0.

---

## 6.2 Second-Order Linear ODEs (Homogeneous)

### **Easy:** Constant Coefficients - Distinct Real Roots
> Solve y'' + {{a}}y' + {{b}}y = 0.

**Example:** Solve y'' - 5y' + 6y = 0.

### **Medium:** Repeated Roots
> Solve y'' + {{a}}y' + {{b}}y = 0 where the characteristic equation has a repeated root.

**Example:** Solve y'' - 4y' + 4y = 0.

### **Hard:** Complex Roots
> Solve y'' + {{a}}y' + {{b}}y = 0 where the characteristic equation has complex roots.

**Example:** Solve y'' + 2y' + 5y = 0.

---

## 6.3 Second-Order Linear ODEs (Non-Homogeneous)

### **Easy:** Method of Undetermined Coefficients (Polynomial)
> Find a particular solution to y'' + {{a}}y' + {{b}}y = {{polynomial}}.

**Example:** Find yₚ for y'' - 3y' + 2y = 4x.

### **Medium:** Undetermined Coefficients (Exponential/Trig)
> Find the general solution to y'' + {{a}}y' + {{b}}y = {{exponential}} or {{trig_function}}.

**Example:** Solve y'' + y = sin(x).

### **Hard:** Variation of Parameters
> Use variation of parameters to solve y'' + {{a}}y' + {{b}}y = {f(x)}.

**Example:** Solve y'' + y = tan(x).

---

## 6.4 Applications of Differential Equations

### **Easy:** Exponential Growth/Decay
> A population/substance follows dP/dt = {{k}}P with P(0) = {P₀}. Find P(t) and P({t₁}).

**Example:** A population grows at rate dP/dt = 0.05P with P(0) = 100. Find P(10).

### **Medium:** Newton's Law of Cooling
> An object at temperature {T₀} is placed in a room at temperature {Tₐ}. After {t₁} minutes, it reaches {T₁}. Find T(t) and the time to reach {T₂}.

### **Hard:** Mixing Problems
> A tank contains {V₀} L of brine with {a₀} kg of salt. Brine with {cᵢₙ} kg/L flows in at {rᵢₙ} L/min, and mixture flows out at {rₒᵤₜ} L/min. Find the amount of salt at time t.

---

## 6.5 Partial Differential Equations (Introduction)

### **Easy:** Verify PDE Solution
> Verify that u(x,t) = {{function}} is a solution to the PDE {{equation}}.

**Example:** Verify u(x,t) = sin(x - ct) satisfies the wave equation uₜₜ = c²uₓₓ.

### **Medium:** Separation of Variables Setup
> Use separation of variables to convert the PDE {{equation}} into ordinary differential equations.

**Example:** Use separation of variables on uₜ = k·uₓₓ by letting u(x,t) = X(x)T(t).

### **Hard:** Heat Equation Solution
> Solve the heat equation uₜ = {{k}}uₓₓ on 0 < x < {{L}} with boundary conditions u(0,t) = u({{L}},t) = 0 and initial condition u(x,0) = {f(x)}.
