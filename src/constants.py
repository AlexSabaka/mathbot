"""Constants and available options for the math problem generator."""

# Available grades
GRADES = ["elementary", "middle", "high", "college", "university"]

# Available math topics
MATH_TOPICS = [
    "arithmetic",
    "percentages",
    "fractions",
    "ratios",
    "algebra",
    "geometry",
    "measurement",
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
    "area_perimeter_chain"
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
    "arithmetic": ["elementary", "middle", "high", "college", "university"],
    "percentages": ["middle", "high", "college", "university"],
    "fractions": ["elementary", "middle", "high", "college", "university"],
    "ratios": ["elementary", "middle", "high", "college", "university"],
    "algebra": ["middle", "high", "college", "university"],
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
    "area_perimeter_chain": ["geometry", "algebra", "powers_logs"]  # roots, squares
}

# Topics that require specific problem types (these need special handling)
ADVANCED_TOPICS = ["quadratics", "derivatives", "powers_logs"]
