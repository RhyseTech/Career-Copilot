# Phase 3: Requirements & Evidence Architecture

## 1. Purpose
Phase 3 converts the canonical JD and canonical Resume produced by Phase 2 into two independent, structured, typed and traceable outputs:
1. JD Requirements
2. Resume Evidence

Phase 3 does NOT compare them.

The output of Phase 3 becomes the input to Phase 4 Matching.

## 2. Phase Boundary
Clearly establish:
- **Phase 2:** "What is the normalized representation?"
- **Phase 3:** "What does the JD require?" & "What evidence exists in the Resume?"
- **Phase 4:** "How does the Resume evidence relate to the JD requirement?"
- **Phase 5:** "What numerical score should the matches produce?"

## 3. Architecture Overview
```text
                PHASE 2
        Canonical Resume + JD
                  │
        ┌─────────┴─────────┐
        ↓                   ↓
   JD PROCESSING       RESUME PROCESSING
        ↓                   ↓
Requirement Detection   Evidence Detection
        ↓                   ↓
Requirement             Evidence
Atomization             Atomization
        ↓                   ↓
Context Extraction     Context Extraction
        ↓                   ↓
Requirement Metadata   Evidence Metadata
        ↓                   ↓
 JD Requirements       Resume Evidence
        │                   │
        └─────────┬─────────┘
                  ↓
               PHASE 4
               MATCHING
```

## 4. JD Requirement Detection
Phase 3 must identify meaningful employer requirements from the canonical JD. Requirements may include:
- TECHNOLOGY
- SKILL
- EXPERIENCE
- EDUCATION
- CERTIFICATION
- RESPONSIBILITY
- DOMAIN
- SOFT_SKILL

Do NOT flatten all requirements into skills.

**Examples:**
- Python → TECHNOLOGY/SKILL
- 4 years Data Engineering → EXPERIENCE
- Bachelor's degree → EDUCATION
- AWS certification → CERTIFICATION
- Build scalable pipelines → RESPONSIBILITY/CAPABILITY
- Cisco telemetry → DOMAIN CONTEXT

Domain/business context must remain distinguishable from an actual candidate requirement.

## 5. Requirement Atomization
This is a CORE Phase 3 responsibility. Compound JD statements should be decomposed into meaningful independently representable concepts while preserving the parent requirement and context.

**Example:**
"Design, develop, and implement scalable and efficient data pipelines using AWS services such as S3, EC2, ECS and Aurora."

Do NOT produce only: AWS, S3, EC2, ECS, Aurora.
Instead preserve:
- **Parent capability:** Data Pipeline Development
- **Actions:** design, develop, implement
- **Technologies:** AWS, S3, EC2, ECS, Aurora
- **Context:** scalable and efficient data pipelines
- **Requirement type:** REQUIRED

The architecture must preserve the relationship between these pieces. Do not perform matching during atomization.

## 6. JD Requirement Context
Every requirement should preserve, where available:
- `requirement_id`
- `raw value`
- `canonical concept`
- `requirement text`
- `surrounding context`
- `expected action/capability`
- `category`
- `required/preferred status`
- `original lexical signal`
- `importance signals`
- `source document`
- `source section`
- `source field`
- `source sentence/span`
- `provenance`
- `confidence`

The original requirement sentence must never be discarded.

## 7. Required vs Preferred
Phase 3 must distinguish:
- REQUIRED
- PREFERRED

Preserve the original lexical signal where available.
**Examples:** "must have", "required", "mandatory", "preferred", "nice to have", "bonus".

Conceptually:
- `requirement_type`: REQUIRED
- `requirement_signal`: "must have"

Do not discard the original wording.

## 8. Importance Signals
Phase 3 may capture qualitative importance signals.
**Examples:** REQUIRED, CORE_RESPONSIBILITY, EMPHASIZED, REPEATED, PREFERRED.

But Phase 3 MUST NOT calculate final numerical weights.
**Explicit boundary:**
- Phase 3 captures importance signals.
- Phase 5 calculates scoring weights.
Do not produce values such as `weight = 0.18` in Phase 3.

## 9. Resume Evidence Detection
Phase 3 must identify evidence from the Resume that supports actual candidate capabilities. Do NOT simply extract a flat skill list.

Evidence should preserve:
- `evidence_id`
- `canonical concept`
- `raw value`
- `evidence text`
- `surrounding context`
- `action`
- `category`
- `evidence type`
- `provenance`
- `source document`
- `source section`
- `source field`
- `source sentence/span`
- `confidence`

**Example:**
Resume: "Built scalable ETL pipelines using AWS Glue and Python processing 2TB of daily data."
Evidence should preserve concepts such as `AWS Glue`, `Python`, `ETL` and context such as:
- **Action:** Built
- **Context:** scalable ETL pipelines
- **Scale:** 2TB daily
- **Source:** Experience → relevant bullet

Do not turn this into only: AWS Glue, Python, ETL. The actual candidate action/context must remain available.

## 10. Evidence Context
Context is required to differentiate basic keyword presence from actual application.
Compare "Python" versus "Built production ETL pipelines using Python."
The second contains technology, action, responsibility, context, and potentially scale/impact. Phase 3 must preserve this information for Phase 4. Do NOT score evidence strength in Phase 3.

## 11. Explicit vs Inferred
Preserve EXPLICIT vs INFERRED.
- **Explicit:** The concept is directly supported by resume text.
- **Inferred:** The concept was derived from contextual information.

Phase 3 must NOT automatically invent missing skills.
**Example:** "Built ETL pipelines using Python."
- Python: EXPLICIT.
Do NOT automatically create SQL, Pandas, Machine Learning, or Object-Oriented Programming unless explicitly supported by the source or an explicitly defined inference mechanism approved later. Keep inferred evidence separate from explicit evidence.

## 12. Requirement vs Domain Context
Explicitly distinguish REQUIREMENT from DOMAIN/BUSINESS CONTEXT.
**Example:** "Build data pipelines for Cisco telemetry data."
- **Requirement:** Data Pipeline Development
- **Domain Context:** Cisco telemetry
Do NOT automatically create "Cisco telemetry" as a candidate skill requirement unless the JD explicitly makes it a requirement.

## 13. Traceability
Every Requirement and Evidence object must remain traceable to Phase 2 canonical data and the original source.
Preserve where available:
- `source_document_id`
- `source_section`
- `source_field`
- `source_text`
- `source_span` / `line_range`
- `raw_value`
- `canonical item ID`

The architecture must support answering "Why does this Requirement/Evidence exist?" and "Where exactly did it come from?". If exact spans are unavailable from the existing parser, preserve the available source information and explicitly document the limitation. Never fabricate source spans.

## 14. Phase 2 → Phase 3 Contract
Phase 3 consumes `CanonicalJD` and `CanonicalResume` from Phase 2.
Do not duplicate Phase 2 normalization logic. Do not introduce a competing canonical schema. Phase 2 owns normalization. Phase 3 owns requirement/evidence construction.

## 15. Phase 3 Output
Phase 3 produces:
- `CanonicalJD` → `JDRequirements[]`
- `CanonicalResume` → `ResumeEvidence[]`

The two collections remain independent. There is NO Requirement ↔ Evidence match in Phase 3.

## 16. LLM vs Deterministic Boundary
Phase 3 may use deterministic and/or LLM-assisted extraction where appropriate, but the output must be schema validated, traceable, source grounded, conservative, and reproducible/auditable.

**Every LLM-extracted Requirement or Evidence object must be grounded in and traceable to the source text; schema-valid but source-unsupported output must be rejected rather than accepted.**

The LLM must not calculate matching or scoring. The architecture must not depend on an opaque LLM-generated match score.

## 17. What Phase 3 Must NOT Do
Explicitly prohibit:
- Resume ↔ JD matching
- semantic similarity
- EXACT classification
- RELATED classification
- PARTIAL classification
- TRANSFERABLE classification
- GAP classification
- scoring
- numerical requirement weights
- ontology traversal
- related-skill expansion
- replacing one technology with another
- inventing missing resume skills
- optimization
- target resume generation
- learning recommendations
- interview recommendations

Those belong to later phases.

## 18. Research Alignment
Phase 3 consensus builds upon established research themes:
- section-aware extraction
- typed requirements
- requirement atomization
- sentence/span-level extraction
- contextual skill representation
- required vs preferred classification
- explicit vs inferred evidence
- provenance
- separation of extraction from matching
- avoidance of hallucinated skills
- typed rather than flat keyword structures

**Primary references:**
- Khelkhal & Lanasri (2025)
- Decorte et al. (2025)
- Gnehm et al. (2022)
- Menezes et al. (2026)
- Gugnani & Misra (2020)
- Tayade et al. (2026)
- Khaouja et al. (2021)
- Akkasi (2024)
- Schedlbauer et al. (2021)
- Wild et al. (2021)

## 19. Upload/Artifact Timestamp Convention
We need Resume and JD uploads/artifacts to be easily identifiable by creation time.
Use `YYYYMMDD_HHMMSS` format mapped to `Asia/Kolkata` timezone (e.g., `20260909_120122`).
Timestamps should be stored as metadata in the canonical artifact:
```json
created_at: "2026-09-09T12:01:22+05:30"
```
Where filenames are generated by the system, use a sortable naming pattern: `{document_type}_{YYYYMMDD_HHMMSS}_{document_id}.json` (e.g., `jd_20260909_120122_7f3a....json`, `resume_20260909_120122_a91b....json`).

**IMPORTANT:** The timestamp is for artifact/version identification and human visibility. The stable document ID must remain the primary identity. Do not use timestamps as the sole identity.

## 20. Open Design Questions
- Exact requirement atomization strategy
- How compound requirements should be represented
- Evidence strength representation
- Deterministic vs LLM extraction boundary
- Treatment of inferred evidence
- Responsibility/capability representation
- Domain context representation
- Relationship between parent requirements and child atoms
- How multiple evidence occurrences should be represented

## 21. References
See `research.md` for extended mappings of the above publications against architectural decisions.
