"""Constants and available options for the math problem generator."""

# Available grades
GRADES = ["elementary", "middle", "high", "college", "university"]

# Available math topics
MATH_TOPICS = [
    "numbers",
    "arithmetic",
    "percentages",
    "fractions",
    "decimals",
    "ratios",
    "algebra",
    "geometry",
    "measurement",
    "statistics",
    "quadratics",
    "derivatives",
    "powers_logs"
]

# Available problem families
PROBLEM_FAMILIES = [
    "sequential_purchase",
    "rate_time",
    "compound_growth",
    "multi_person_sharing",
    "area_perimeter_chain",
    "calendar",
    "addition",
    "subtraction",
    "subtraction_facts",
    "counting",
    "skip_counting",
    "comparing",
    "patterns",
    "length",
    "weight",
    "time",
    "metric",
    "area",
    "shapes2d",
    "shapes3d",
    "multiplication",
    "division",
    "fractions",
    "properties",
    "factors_multiples",
    "divisibility",
    "fraction_operations",
    "decimal_operations",
    "angles",
    "triangles",
    "quadrilaterals",
    "symmetry",
    "numbers_standard",
    "powers_of_10",
    "expressions_intro",
    "expressions_terms",
    "coordinate_plane",
    "statistics_mean",
    "statistics_median",
    "statistics_mode",
    "polygons",
    "triangle_area",
    "square_area",
    "rectangle_area",
    "parallelogram_area",
    "rhombus_area",
    "trapezium_area",
    "volume",
    "fractions_mixed",
    "fractions_mult_whole"
]

# Grade to max complexity mapping
GRADE_MAX_COMPLEXITY = {
    "elementary": 2,
    "middle": 3,
    "high": 3,
    "college": 3,
    "university": 3
}

# Math topic grade compatibility
TOPIC_GRADE_COMPATIBILITY = {
    "numbers": ["elementary"],
    "arithmetic": ["elementary", "middle", "high", "college", "university"],
    "percentages": ["middle", "high", "college", "university"],
    "fractions": ["elementary", "middle", "high", "college", "university"],
    "decimals": ["elementary", "middle", "high", "college", "university"],
    "statistics": ["elementary", "middle", "high", "college", "university"],
    "ratios": ["elementary", "middle", "high", "college", "university"],
    "algebra": ["elementary", "middle", "high", "college", "university"],
    "geometry": ["elementary", "middle", "high", "college", "university"],
    "measurement": ["elementary", "middle", "high", "college", "university"],
    "quadratics": ["high", "college", "university"],
    "derivatives": ["high", "college", "university"],
    "powers_logs": ["high", "college", "university"]
}

# Complexity to steps range mapping
COMPLEXITY_STEPS_RANGE = {
    1: (1, 3),
    2: (3, 5),
    3: (5, 8)
}

# Family to supported topics mapping
# Defines which math topics each problem family can meaningfully incorporate
FAMILY_TOPIC_SUPPORT = {
    "sequential_purchase": ["arithmetic", "percentages", "fractions", "algebra"],
    "rate_time": ["arithmetic", "fractions", "algebra", "derivatives"],  # derivatives = rates of change
    "compound_growth": ["percentages", "algebra", "powers_logs"],  # exponential growth, logs
    "multi_person_sharing": ["arithmetic", "ratios", "percentages", "fractions", "algebra"],
    "area_perimeter_chain": ["geometry", "algebra", "powers_logs"],  # roots, squares
    "calendar": ["measurement"],  # calendar and time problems
    "addition": ["arithmetic"],
    "subtraction": ["arithmetic"],
    "subtraction_facts": ["arithmetic"],
    "counting": ["numbers"],
    "skip_counting": ["numbers"],
    "comparing": ["numbers"],
    "patterns": ["numbers"],
    "length": ["measurement"],
    "weight": ["measurement"],
    "time": ["measurement"],
    "metric": ["measurement"],
    "area": ["measurement", "geometry"],
    "shapes2d": ["geometry"],
    "shapes3d": ["geometry"],
    "multiplication": ["arithmetic"],
    "division": ["arithmetic"],
    "fractions": ["fractions"],
    "properties": ["arithmetic"],  # properties of addition and multiplication
    "factors_multiples": ["arithmetic"],  # factors, multiples, GCF, LCM
    "divisibility": ["arithmetic"],  # divisibility rules and tests
    "fraction_operations": ["fractions"],  # add, subtract, multiply, divide fractions
    "decimal_operations": ["arithmetic"],  # decimal operations
    "angles": ["geometry"],  # angle measurement and relationships
    "triangles": ["geometry"],  # triangle classification and properties
    "quadrilaterals": ["geometry"],  # quadrilateral identification and properties
    "symmetry": ["geometry"],  # lines of symmetry, rotational, point, reflexive
    "numbers_standard": ["arithmetic", "numbers"],  # writing numbers in standard form
    "powers_of_10": ["algebra"],  # powers of 10 and scientific notation
    "expressions_intro": ["algebra"],  # introduction to algebraic expressions
    "expressions_terms": ["algebra"],  # variables, coefficients, terms, and constants
    "decimals_mult_whole": ["decimals"],  # multiply decimals by whole numbers
    "decimals_mult_power10": ["decimals"],  # multiply decimals by powers of 10
    "decimals_div_power10": ["decimals"],  # divide decimals by powers of 10
    "decimals_fractions": ["decimals"],  # convert between decimals and fractions
    "coordinate_plane": ["geometry"],  # coordinate plane and graphing
    "statistics_mean": ["statistics"],  # calculating mean/average
    "statistics_median": ["statistics"],  # calculating median
    "statistics_mode": ["statistics"],  # calculating mode
    "polygons": ["geometry"],  # types of polygons
    "triangle_area": ["geometry"],  # triangle area and perimeter
    "square_area": ["geometry"],  # square area and perimeter
    "rectangle_area": ["geometry"],  # rectangle area and perimeter
    "parallelogram_area": ["geometry"],  # parallelogram area
    "rhombus_area": ["geometry"],  # rhombus area
    "trapezium_area": ["geometry"],  # trapezium/trapezoid area
    "volume": ["geometry"],  # volume of 3D shapes
    "fractions_mixed": ["fractions"],  # mixed fractions conversion
    "fractions_mult_whole": ["fractions"]  # multiply fractions by whole numbers
}

# Topics that require specific problem types (these need special handling)
ADVANCED_TOPICS = ["quadratics", "derivatives", "powers_logs"]
