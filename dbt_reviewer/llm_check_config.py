LLM_CHECKS = [
    "wrong or ambiguous aggregation grain",
    "joins that may cause row duplication (fan-out)",
    "missing GROUP BY given the selected columns",
    "business logic that contradicts the model type",
    "column naming that is misleading or unclear",
]

LLM_SKIP_CHECKS = [
    "SELECT * (already checked by static analysis)",
    "hardcoded schema references (already checked by static analysis)",
    "number of joins (already checked by static analysis)",
    "hardcoded dates (already checked by static analysis)",
]
