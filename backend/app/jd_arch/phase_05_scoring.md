# Phase 5: Deterministic JD Match Scoring

## Goal
Phase 5 consumes the `MatchEdge[]` output from Phase 4 and deterministically computes an explainable 0–100 match score for a given Resume against a specific JD. 

## Architectural Principles
1. **Determinism**: The score must be strictly reproducible. Same `MatchEdge[]` + same config = same score.
2. **Explainability**: Every point awarded or deducted must be traceable to explicit config values and specific evidence atoms. No LLM magic.
3. **No Training/Optimization**: This is not an ML model. There are no learned weights. Optimization and gap generation are deferred to later phases.
4. **Hard Constraints**: Critical requirements (e.g., clearance, explicit mandatory years of experience) act as gates. A hard failure can cap or zero the final score regardless of semantic overlap.

## Scoring Model

### Requirement Weights
Each `JDRequirement` is assigned a base weight derived from its type and importance:

```
weight_r = requirement_type_factor × importance_factor
```

Where factors are read from `Phase5Config`:
- **Requirement Type**: `REQUIRED` = 1.0, `PREFERRED` = 0.35
- **Importance Signal**: `HIGH` = 1.5, `MEDIUM` = 1.0, `LOW` = 0.6 (Default to MEDIUM if none specified).

### Atom and Requirement Coverage
For a compound requirement (multiple atoms), each atom contributes equally to the requirement's potential.
The contribution of each atom is based on the *best* `MatchEdge` for that atom.

- `EXACT` = 1.00
- `RELATED` = 0.75
- `PARTIAL` = 0.50
- `TRANSFERABLE` = 0.35
- `GAP` = 0.00

`coverage_r` (0.0 to 1.0) is the sum of the best match contributions for all atoms in requirement `r`, divided by the number of atoms.

### Deduplication and Double-Counting
1. **Duplicate Evidence**: If a resume mentions "Python" 5 times, it only satisfies the Python atom once (max score = 1.0).
2. **Evidence Overloading**: One evidence item (e.g., "Built data pipelines in Python and Spark") can satisfy multiple distinct requirements (e.g., a "Python" requirement and a "Data Pipelines" requirement). However, it cannot satisfy the *same* requirement multiple times to artificially inflate the score above 1.0.

### Base Score Calculation
The base score is a weighted average of all requirement coverages, scaled to 100:

```
Score_base = 100 × [ Σ(weight_r × coverage_r) / Σ(weight_r) ]
```

### Qualifier Gating
Qualifiers (e.g., Years of Experience) are evaluated separately.
If an EXACT match fails a hard qualifier (e.g., "5+ years Python" but evidence shows "2 years Python"), the edge degrades to `PARTIAL` (if partially satisfied) or `GAP` (if completely failed) before the `coverage_r` calculation.

If a top-level requirement is marked as a **Hard Constraint** and fails completely, a `ConstraintGate` is applied.
```
FinalScore = Score_base × ConstraintGate
```
*Note: ConstraintGate is configurable (e.g., 0.0 for immediate failure, or 1.0 if not enforced).*

## Data Models
- **`Phase5Score`**: The root object containing `final_score`, `base_score`, and breakdowns.
- **`RequirementScore`**: Per-requirement breakdown of weight, coverage, contributing edges, and human-readable explanation.
- **`AtomScore`**: Per-atom resolution tracking the single best evidence ID and match contribution used.
