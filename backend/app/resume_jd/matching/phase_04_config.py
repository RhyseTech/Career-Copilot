# Phase 4 Configuration & Thresholds

# INITIAL / UNCALIBRATED
# These are application-level starting thresholds, NOT scientifically validated probabilities.
# They require later calibration using benchmark/evaluation data.

class Phase4Config:
    # Lexical overlap threshold to consider strings practically identical (used if canonical mapping isn't perfect)
    LEXICAL_EXACT_THRESHOLD = 0.95

    # Semantic threshold for TRANSFERABLE (ontology-UNKNOWN path only).
    # UNCALIBRATED — requires empirical measurement against benchmark pairs using the deployed model.
    # For all-MiniLM-L6-v2, functionally-equivalent but different-tech pairs typically score 0.45-0.65.
    SEMANTIC_STRONG_THRESHOLD = 0.75

    # Semantic threshold for moderate relationship
    SEMANTIC_MODERATE_THRESHOLD = 0.55

    # Minimum token overlap for candidate generation (NOT used for lexical similarity score)
    CANDIDATE_MIN_LEXICAL = 0.15
    CANDIDATE_MIN_SEMANTIC = 0.30

    # TRANSFERABLE_ACTION_THRESHOLD: minimum action/context overlap (lexical on residuals after
    # stripping technology name) required to classify RELATED → TRANSFERABLE.
    # UNCALIBRATED — requires review once empirical pairs are collected.
    # Rationale: "GCP Dataflow pipeline development" vs "AWS Glue pipeline development"
    # residuals are "pipeline development" vs "pipeline development" → ~1.0 lexical.
    # "GCP Dataflow" vs "AWS Glue" residuals are empty → 0.0.
    TRANSFERABLE_ACTION_THRESHOLD = 0.30
