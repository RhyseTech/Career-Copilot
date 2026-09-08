    
    
    # Research Map

The architecture of the Resume ↔ JD Match & Optimization pipeline is fundamentally research-driven. We do not invent custom semantic matching paradigms where academic literature has already solved the problem.

Below is the mapping of established research papers to our architectural phases.

---

### 1. Large-Scale Occupational Skills Normalization for Online Recruitment
- **Authors:** Javed et al.
- **Year:** 2017
- **Relevant Concept:** Skill Normalization using a large-scale taxonomy.
- **Informs Phase:** Phase 2 (Canonicalization).
- **Takeaways:** We should build our canonical dictionary based on the finding that alias resolution and acronym expansion drastically improve matching recall. Normalization should be performed as an isolated step before any deep semantic matching occurs.
- **Do NOT blindly implement:** We must not construct their entire multi-million node graph; a subset specific to our domain is sufficient for our Canonicalization layer.

### 2. SKILL: A System for Skill Identification and Normalization
- **Authors:** Zhao et al.
- **Year:** 2015
- **Relevant Concept:** Extracting raw skill terms from unstructured text and normalizing them.
- **Informs Phase:** Phase 1 (Document Parsing) & Phase 2 (Canonicalization).
- **Takeaways:** Validates our Hybrid parsing approach where deterministic chunking precedes extraction. Proves that preserving the raw string context is vital for mapping accuracy.
- **Do NOT blindly implement:** Do not utilize their specific proprietary named-entity recognition (NER) models; our existing LLM wrapper/extraction handles this natively and effectively.

### 3. Implicit Skills Extraction Using Document Embedding and Its Use in Job Recommendation
- **Authors:** Gugnani & Misra
- **Year:** 2020
- **Relevant Concept:** Deducing skills that are implied but not explicitly stated.
- **Informs Phase:** Phase 1 (Document Parsing) & Phase 4 (Matching).
- **Takeaways:** Differentiates between *EXTRACTED* provenance and *INFERRED* provenance. We must clearly label when an entity is explicitly extracted vs implicitly inferred.
- **Do NOT blindly implement:** Do not infer skills directly into the raw source documents. Any inferred skills belong strictly in the matching logic as relationships (e.g., Transferable), not as hallucinated resume evidence.

### 4. Explainable Resume/JD Matching Pipeline Design
- **Authors:** Khelkhal & Lanasri
- **Year:** 2025
- **Relevant Concept:** Architecting pipelines that yield deterministic, explainable scores instead of black-box metrics.
- **Informs Phase:** Phase 4 (Matching) & Phase 5 (Scoring).
- **Takeaways:** The primary directive that scoring must be a formula built on categorical labels (EXACT, RELATED, GAP) rather than an LLM emitting an opaque 0-100 number.
- **Do NOT blindly implement:** Do not couple scoring logic to the document parsers; parsing, matching, and scoring must remain perfectly isolated phases.

### 5. Ontology-based Semantic Normalization
- **Authors:** Anghel et al.
- **Year:** 2026
- **Relevant Concept:** Using hierarchical graphs to represent semantic equivalency and relationship distance.
- **Informs Phase:** Phase 4 (Matching).
- **Takeaways:** We will eventually use ontology distance to calculate "RELATED" or "TRANSFERABLE" match labels.
- **Do NOT blindly implement:** Do not push ontological traversal into Phase 2 (Canonicalization). Phase 2 is strictly for normalization mapping (1-to-1), while Phase 4 is for semantic proximity (graph traversal).
