# Phase 2: Canonicalization Architecture

## Purpose
Canonicalization creates a shared representation schema that allows Resume and JD information to be compared consistently. It normalizes equivalent representations of the same concept into a shared canonical representation, while preserving semantic distinctions between different concepts.

## Why Canonicalization is Required
Job descriptions and Resumes are written by different people using different acronyms, spellings, and terminologies. A matching engine cannot deterministically compare "Amazon Web Services Glue" on a resume to "AWS Glue" on a JD without a shared dictionary. 

## Canonical Flow Conceptually
We use an adapter pattern to convert extracted document structures into their canonical forms:

**Resume Flow:**
`Existing Resume Parser` → `Resume Adapter` → `Canonical Resume`

**JD Flow:**
`Existing JD Parser` → `JD Adapter` → `Canonical JD`

## Raw vs Normalized Values
The core principle of Canonicalization is:
`RAW VALUE` → `NORMALIZED VALUE` + `PROVENANCE` + `SOURCE LOCATION` + `CATEGORY`

- **Raw Value:** Exactly what was extracted (e.g., "Amazon Web Services").
- **Normalized Value:** The mapped canonical string (e.g., "AWS").

**CRITICAL RULE:** Raw source information must never be destroyed during normalization.

## Attributes of a Canonical Entity
Every canonicalized item must preserve:
- **Stable ID:** UUID linking the Canonical entity to downstream Match tracking.
- **Raw Value:** The unedited text.
- **Normalized Value:** The mapped canonical skills.
- **Category:** e.g., SKILL, EXPERIENCE, EDUCATION.
- **Provenance:** EXPLICIT vs INFERRED.
- **Source Location:** The section or exact sentence where it was found.
- **Source Text / Span:** Exact matching substring where available.
- **Confidence:** Normalization confidence, where applicable.
- **Normalization Method:** How the normalized value was produced.
- **Normalization Status:** Status of the normalization action.
- **Verification Status:** Confidence in tracing back to the source.
- **Source Occurrences / References:** Required where deduplication applies.

Where information is unavailable, preserve null/unknown semantics rather than inventing data.

Requirement and Evidence are downstream concepts owned by Phase 3. Phase 2 only produces the normalized/common representation that Phase 3 will use to construct JD Requirements and Resume Evidence.

## Source Traceability
Every canonicalized item should preserve enough information to answer:
"Where exactly did this canonical value come from?"

Document support for the following where available:
- `source_document_id`
- `source_section`
- `source_field`
- `source_text`
- `source_span` / `line_range`
- `raw_value`

**Example:**
Canonical: AWS Glue
Raw: Amazon Web Services Glue
Source: JD document
Section: Responsibilities
Source Text: "Design, develop, and implement scalable data pipelines using Amazon Web Services Glue..."

The normalized value must remain traceable to the original representation. If exact source spans are unavailable from the existing parser, this is documented as a limitation rather than inventing spans.

## Deduplication
Canonicalization may encounter the same concept multiple times in a Resume or JD.

**Example:**
Skills: Python
Experience: Built ETL pipelines using Python
Project: Python ETL pipeline

These may normalize to the same canonical concept: Python
BUT deduplication must NOT destroy source evidence or occurrences. The canonical representation should preserve all relevant source occurrences/references.

**Conceptually:**
Python
 ├── occurrence → Skills
 ├── occurrence → Experience
 └── occurrence → Project

**Rule:** Deduplication removes redundant canonical entities while preserving all source locations and occurrences required for downstream traceability. Do NOT deduplicate by simply deleting repeated source records. Do NOT allow deduplication to remove evidence that Phase 3 may need.

## Explicit vs Implicit
The architecture must clearly distinguish:
- **EXPLICIT:** The concept is directly represented in the source text.
- **INFERRED:** The system derived the concept from contextual information.

Phase 2 must be conservative. It must NOT automatically infer additional skills simply because they are commonly associated with another skill.

**Example:**
Resume text: "Built ETL pipelines using Python."
Python → EXPLICIT

Do NOT automatically create INFERRED records (e.g., Object-Oriented Programming, Machine Learning, Pandas, SQL) unless those concepts are actually supported by the source and the relevant architecture explicitly permits such inference. For Phase 2, preservation of explicit source information is more important than expanding the skill set. Keep the distinction traceable so downstream phases can decide how inferred information should be treated.

## Verification
Verification is a first-class part of canonicalization. The architecture defines that canonicalized values should be verifiable against their original source.

**Verification Status:**
- **VERIFIED:** The normalized value can be confidently traced back to the source representation.
- **UNVERIFIED:** Normalization/extraction exists but has not been sufficiently verified.
- **AMBIGUOUS:** Multiple interpretations are possible and the system must not silently choose an aggressive normalization.

The original raw value must always remain available for verification. Verification does NOT imply that the candidate satisfies a JD requirement. That belongs to later phases.

## Normalization Method
Records HOW the normalized value was produced.

**At minimum document:**
- **EXACT:** Exact string match.
- **ALIAS_DICTIONARY:** Deterministic mapping via predefined aliases.
- **NO_CHANGE:** The value was not changed.

Phase 2 does NOT introduce embeddings or fuzzy semantic matching. The method must be traceable and auditable.

**Examples:**
- "k8s" → "Kubernetes" → normalization_method: ALIAS_DICTIONARY
- "Python" → "Python" → normalization_method: NO_CHANGE
- "Amazon Web Services Glue" → "AWS Glue" → normalization_method: ALIAS_DICTIONARY

## Normalization Status
Tracks the outcome of the normalization attempt:
- **NORMALIZED:** A reliable normalization rule mapped the raw value to a canonical representation.
- **UNCHANGED:** The value was already canonical or no normalization was necessary.
- **AMBIGUOUS:** The system cannot safely determine a canonical representation.

For AMBIGUOUS values: preserve the raw value, do not guess, and do not create semantic relationships.

## Confidence
Normalization confidence, where applicable. The architecture should allow deterministic high-confidence mappings such as ("k8s" → "Kubernetes") while avoiding claims that confidence values are universally calibrated probabilities unless the implementation actually provides one.

## Conservative Normalization
Canonicalization means: *"Same concept → Same normalized representation."*
It does **NOT** mean: *"Related concept → Same normalized representation."*

**Valid Canonicalization:**
- "Amazon Web Services" → "AWS"
- "k8s" → "Kubernetes"

**Invalid Canonicalization (Anti-Patterns):**
- "AWS Glue" ≠ "Spark"
- "AWS Glue" ≠ "Dataflow"

If an entity represents a specialized tool, it should remain specific. 

## Important Phase Boundary
**Phase 2 answers:**
"Do these representations refer to the same concept, and what is the traceable canonical representation?"

**Phase 2 does NOT answer:**
- "Does the candidate satisfy this JD requirement?" (That is Phase 4).
- "What score should the candidate receive?" (That is Phase 5).
- "What skills should the candidate learn?" (That belongs to later optimization/gap-analysis work).

## Normalization vs Ontology vs Matching
- **Normalization (Phase 2):** Determines whether different representations refer to the same concept and maps them to the same canonical representation.
- **Ontology / Relationships (later phase):** May determine semantic relationships between different concepts.
- **Matching (Phase 4):** Determines how the candidate's evidence relates to a JD requirement and classifies it as EXACT / RELATED / PARTIAL / TRANSFERABLE / GAP.

**Valid Canonicalization (Phase 2):**
- "AWS Glue" → "AWS Glue"
- "Amazon Web Services Glue" → "AWS Glue"

**Do NOT Normalize (belongs to later phases):**
- "AWS Glue" → "Spark"
- "AWS Glue" → "Dataflow"
- "AWS Glue" → "Data Engineering"

Phase 2 must not create RELATED or TRANSFERABLE relationships. It must not determine whether a resume skill satisfies a JD requirement. Those decisions belong to later phases.

## Expected Inputs & Outputs
- **Expected Inputs:** Extracted chunks from Phase 1 (`JDStructParser` output or `HybridJDParser` text chunks; `ResumeStructParser` outputs).
- **Expected Outputs:** Fully hydrated `CanonicalJD` and canonical Resume JSON payloads stored in deterministic locations.

## Validation Principles
- Does the raw text exist in the source document?
- Does the canonicalization destroy the semantic uniqueness of a skill? (If yes, it's too aggressive).

## Research Alignment
Phase 2 relies heavily on established research regarding Skill Identification and Normalization (e.g., Javed et al., Zhao et al.).

**Research-supported Phase 2 capabilities:**
- Raw + normalized values
- Alias/synonym normalization
- Conservative normalization
- Source traceability
- Verification
- Normalization method
- Source-aware deduplication
- Explicit vs implicit provenance
- Category/type
- Confidence

**The following concepts are kept OUTSIDE Phase 2:**
- Ontology relationships
- RELATED classification
- TRANSFERABLE classification
- Resume ↔ JD matching
- Scoring
- Optimization

Those belong to later phases.

## Open Design Questions to Resolve Before Implementation
- Do we maintain a static dictionary mapping for aliases, or use a local lightweight embedding to resolve string similarity for normalizations?
- How do we canonically represent complex entities like "4 years of experience"? (Should experience duration be a sub-property of a canonical skill?).
- Do we adopt the existing `Requirement` model fully for Resume evidence, or does Evidence need a distinct but compatible Pydantic model?
