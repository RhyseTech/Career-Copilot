from typing import Dict

class Phase5Config:
    # Versioning for tracking changes to scoring config over time
    VERSION = "1.0.0"

    # Requirement Type Factors
    REQUIREMENT_TYPE_FACTORS: Dict[str, float] = {
        "REQUIRED": 1.0,
        "PREFERRED": 0.35
    }

    # Importance Signals Multipliers
    # High: "must-have", "core", etc.
    IMPORTANCE_FACTORS: Dict[str, float] = {
        "HIGH": 1.5,
        "MEDIUM": 1.0,
        "LOW": 0.6
    }
    DEFAULT_IMPORTANCE = "MEDIUM"

    # Match Type Coefficients
    MATCH_CONTRIBUTIONS: Dict[str, float] = {
        "EXACT": 1.00,
        "RELATED": 0.75,
        "PARTIAL": 0.50,
        "TRANSFERABLE": 0.35,
        "GAP": 0.00
    }

    # Constraint Gate multipliers
    # If a hard constraint requirement is completely missing (GAP), this gate is applied.
    # E.g., 0.0 means immediate zeroing of the total score.
    HARD_CONSTRAINT_GATE_MULTIPLIER = 0.0
