# Phase 4: Matching Architecture

## Phase 4 Objective
Phase 4 answers ONLY:
"How does Resume Evidence relate to a JD Requirement?"

**Input:** `JDRequirements[]` + `ResumeEvidence[]`
**Output:** `MatchEdge[]`

Supported match types: EXACT, RELATED, PARTIAL, TRANSFERABLE, GAP.
Phase 4 MUST NOT calculate the final Resume ↔ JD score. That is Phase 5.

## Core Pipeline
1. Candidate Generation
2. Lexical Analysis
3. Semantic Analysis
4. Ontology Analysis
5. Qualifier Validation
6. Deterministic Match Decision
-> Explainable `MatchEdge[]`

## 1. Candidate Generation
Do NOT compare every requirement against every evidence item blindly if deterministic filtering can reduce candidates.
Use conservative candidate generation based on available:
- canonical IDs
- canonical concepts
- raw values
- categories
- lexical signals
- ontology relationships

Candidate generation must NOT itself declare a final match.
Do NOT use semantic similarity as the only candidate-generation mechanism.

## 2. Lexical Matching
Implement deterministic lexical signals.
Possible signals include: exact normalized string match, token overlap, n-gram overlap, controlled string similarity.
All thresholds must be explicit and centralized/configurable.
Do NOT let lexical similarity alone automatically produce EXACT unless the architecture explicitly permits it.

## 3. Semantic Matching
Use sentence/skill/context-level semantic similarity where required by the frozen architecture.
Also preserve contextual matching where available.
Calculate separate semantic signals for:
- concept/skill
- action/responsibility
- context

Semantic similarity is a FEATURE used by the decision engine. It is NOT the final match score.

## 4. Ontology / Taxonomy
Create the smallest architecture-compliant abstraction required so ontology matching can be integrated conservatively.
Ontology relationships should distinguish concepts such as: equivalent, related, broader, narrower, disjoint.
Related ontology concepts do NOT automatically mean EXACT.

## 5. Qualifier Validation
Before final classification, explicitly evaluate hard requirement qualifiers where available.
Examples: years of experience, education, certification, seniority/level, explicit technology, other structured constraints.
A high semantic similarity must NOT override an explicit contradiction (e.g. 5+ years vs 2 years).
The qualifier result must be visible in the MatchEdge/explanation.

## 6. EXACT
EXACT should require strong evidence.
Conceptually:
- same canonical concept / defensible equivalent identity
- compatible category
- relevant contextual evidence
- hard qualifiers satisfied
- no explicit contradiction
Do NOT use semantic similarity alone to declare EXACT.

## 7. RELATED
RELATED means the evidence is a genuinely related competency but is not the same canonical competency.
Require defensible semantic and/or ontology evidence.
Do NOT use generic domain similarity as sufficient evidence.

## 8. PARTIAL
PARTIAL primarily represents incomplete fulfillment.
Examples: Compound requirement where only some atoms are found, or qualifiers partially met (if rules support).
The system must preserve which atoms/qualifiers were satisfied and which were not.

## 9. TRANSFERABLE
TRANSFERABLE is when the requested technology/competency itself is not demonstrated BUT the resume contains evidence of substantially similar work/responsibility patterns and the relationship is defensible from action/context/domain evidence.

## 10. GAP
GAP means no sufficient reliable evidence was found after evaluating relevant candidates.
Evaluate the available evidence collectively. A GAP should explain why sufficient evidence was not found.

## 11. Multiple Evidence
Support One Requirement → multiple Evidence objects. The combined evidence may support a stronger relationship than any individual evidence object. Preserve all contributing evidence IDs.

## 12. Multiple Requirements
Support One Evidence → multiple Requirements. Do not duplicate or mutate the evidence object. Create separate MatchEdge relationships.

## 13. MatchEdge Model
It should contain:
- requirement_id
- requirement_atom_ids where applicable
- evidence_ids
- match_type
- lexical features
- semantic features
- ontology features
- qualifier results
- decision reasons
- provenance/explanation
- confidence where defined by architecture

Do NOT add final_score, JD_score, optimization recommendations, etc.

## 14. Explainability
Every non-GAP match should be explainable. GAP should also explain why. Do NOT use vague explanations.

## 15. LLM Boundary
LLM must NOT be the authoritative match decision engine. Output must be deterministic based on features.

## 16. Thresholds
Create a centralized configuration/constants structure. Document every threshold. Clearly label them as initial/application-level thresholds where appropriate.

## 17. Phase Boundary
Ends at MatchEdge[]. Does not score, rank, prioritize, or optimize.
