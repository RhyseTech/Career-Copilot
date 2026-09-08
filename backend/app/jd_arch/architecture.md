# Complete 9-Phase Match & Optimization Architecture

This document defines the 9 sequential phases of the Resume ↔ JD Match & Optimization pipeline. Each phase possesses a strict boundary and single responsibility.

---

## Phase 1: Document Parsing
- **Question Answered:** "What does the document contain?"
- **Purpose:** Ingest raw documents (PDF, DOCX, text) and extract their structured content, splitting them into granular requirements or evidence bullets without losing original context.
- **Input:** Raw JD text and Candidate Resume document.
- **Output:** Parsed JSON definitions (e.g., `CanonicalJD`, extracted Resume items) containing `raw_text`, categories, requirement type, and source provenance.
- **Responsibility:** Deterministic chunking, initial semantic extraction (with strict hallucination boundaries), and storing the definitive source of truth JSON.
- **Downstream Consumer:** Phase 2 (Canonicalization).
- **Current Status:** JD Parsing foundation implemented via hybrid architecture. Resume Parsing leverages existing base parser.

## Phase 2: Canonicalization
- **Question Answered:** "What is the normalized/common representation?"
- **Purpose:** Transform raw extracted text into shared, normalized canonical concepts while retaining all original source information. "AWS Glue" becomes canonical "AWS Glue" for both Resume and JD.
- **Input:** Parsed JD and parsed Resume data.
- **Output:** Fully canonicalized structures mapping `raw_text` to `canonical_skills`.
- **Responsibility:** Guaranteeing that the identical concepts from two different sources evaluate to the exact same text string. Preserving provenance. Conservative mapping avoiding ontology generation.
- **Downstream Consumer:** Phase 3 (Requirements + Evidence).
- **Current Status:** Architectural boundary defined; `canonical_skills` modeled in `CanonicalJD`. Needs complete normalizer adapter build-out.

## Phase 3: Requirements + Evidence
- **Question Answered:** "What does the JD require and what evidence exists in the resume?"
- **Purpose:** To isolate the specific constraints of the JD and the available proof within the Resume, staging them for comparison.
- **Input:** Canonical JD JSON and Canonical Resume JSON.
- **Output:** A unified pairing structure representing Required entities vs Available entities.
- **Responsibility:** Aligning categories and weighing the importance of specific demands (Required vs Preferred). 
- **Downstream Consumer:** Phase 4 (Matching).
- **Current Status:** Architectural definition only.

## Phase 4: Matching
- **Question Answered:** "How well does the evidence satisfy each requirement?"
- **Purpose:** Determine semantic relationships and assign categorical labels such as EXACT, RELATED, PARTIAL, TRANSFERABLE, or GAP.
- **Input:** Paired requirements and evidence.
- **Output:** Match labels and justification mappings for each requirement.
- **Responsibility:** Executing semantic similarity rules, ontological relation lookups, and deterministic boundary checking.
- **Downstream Consumer:** Phase 5 (Scoring).
- **Current Status:** Architectural definition only.

## Phase 5: Scoring
- **Question Answered:** "What deterministic score should those matches produce?"
- **Purpose:** Roll up individual match labels and weights into a unified, explainable 0–100 percentage.
- **Input:** Match results.
- **Output:** Final numeric score and an accompanying human-readable explanation trace.
- **Responsibility:** Applying mathematical weighting strategies. No LLM "gut feeling" scores allowed here.
- **Downstream Consumer:** Phase 6 (Gap Analysis) and UI rendering.
- **Current Status:** Architectural definition only.

## Phase 6: Gap Analysis
- **Question Answered:** "What are the highest-impact missing requirements?"
- **Purpose:** Highlight areas where the candidate falls short, specifically ranking them by importance (e.g., missing a required skill vs. a preferred skill).
- **Input:** Match results (GAP items) and requirement weights.
- **Output:** Prioritized list of actionable gaps.
- **Responsibility:** Filtering out noise and calculating which additions would yield the highest optimization return.
- **Downstream Consumer:** Phase 7 (Optimization).
- **Current Status:** Architectural definition only.

## Phase 7: Optimization
- **Question Answered:** "How can the resume be optimized without inventing experience?"
- **Purpose:** Provide targeted rewrite suggestions for the resume text to bridge identified gaps utilizing valid, existing experience as anchors.
- **Input:** Gap list and original Resume text blocks.
- **Output:** Modified resume bullet points or summaries.
- **Responsibility:** Drafting improvements. Must not invent or hallucinate capabilities the user does not possess.
- **Downstream Consumer:** Phase 8 (Validation).
- **Current Status:** Architectural definition only.

## Phase 8: Validation
- **Question Answered:** "Is the optimized resume truthful and compliant?"
- **Purpose:** Audit the generated optimization against the original resume to enforce anti-hallucination rules.
- **Input:** Original Resume JSON and Optimized Resume Output.
- **Output:** Approved optimized resume or rejection flag.
- **Responsibility:** Serving as the truth-checking guardrail.
- **Downstream Consumer:** Phase 9 (Re-scoring).
- **Current Status:** Architectural definition only.

## Phase 9: Re-scoring
- **Question Answered:** "Did the validated optimization actually improve the score?"
- **Purpose:** Pass the validated, optimized resume back through Phase 1-5 to calculate the delta improvement.
- **Input:** Validated Optimized Resume and Original JD.
- **Output:** A Before/After score comparison.
- **Responsibility:** Closing the loop and providing definitive metric proof of the optimization's value.
- **Downstream Consumer:** End user presentation.
- **Current Status:** Architectural definition only.
