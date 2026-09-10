# Career-Copilot Project Memory

## Resume + JD Module: JD Parsing Foundation (Completed)
- **Status:** Completed
- **Architecture Source of Truth:** `docs/jd_architecture.md`
- **Canonical Data Contract:** `backend/app/resume_jd/models/canonical_jd.py` (CanonicalJD)
- **JSON Storage Location:** `backend/app/uploads/parsed_jds/{jd_id}_canonical.json`
- **Implementation Strategy:** Hybrid (Deterministic section boundaries + LLM semantic extraction + Strict validation against hallucination).

### Files Created
- `docs/jd_architecture.md`
- `backend/app/resume_jd/models/canonical_jd.py`
- `backend/app/resume_jd/parsing/jd/hybrid_parser.py`
- `backend/app/resume_jd/parsing/jd/llm_extractor.py`
- `backend/app/resume_jd/parsing/jd/sectionizer.py`
- `backend/app/resume_jd/storage/json_store.py`
- `backend/tests/resume_jd/parsing/test_jd_parser.py`

### Existing Files Reused
- `backend/app/services/llm_optimizer.py` (Wrapped strictly inside `llm_extractor.py` to decouple from existing ATS behavior).

## Architecture Strategy (9-Phase Pipeline)
- **Status:** Phase 2 (Canonicalization) Implemented.
- **Phases:** 
  1. Document Parsing (Implemented - HybridJDParser & ResumeParser)
  2. Canonicalization (Implemented - JDAdapter & ResumeAdapter)
  3. Requirements + Evidence (Implemented - Phase3Extractor)
  4. Matching (Implemented - Phase4Matcher)
  5. Scoring (NOT implemented yet)
  6. Gap Analysis (NOT implemented yet)
  7. Optimization (NOT implemented yet)
  8. Validation (NOT implemented yet)
  9. Re-scoring (NOT implemented yet)
- **Files Created:**
  - `backend/app/resume_jd/models/canonical_models.py`
  - `backend/app/resume_jd/adapters/resume_adapter.py`
  - `backend/app/resume_jd/adapters/jd_adapter.py`
  - `backend/tests/resume_jd/matching/test_phase_02_canonicalization.py`
  - `backend/app/resume_jd/models/phase_03_models.py`
  - `backend/app/resume_jd/pipelines/phase_03_extractor.py`
  - `backend/tests/resume_jd/phase_03/test_phase_03_requirements.py`
  - `backend/app/resume_jd/models/phase_04_models.py`
  - `backend/app/resume_jd/matching/phase_04_config.py`
  - `backend/app/resume_jd/matching/ontology.py`
  - `backend/app/resume_jd/pipelines/phase_04_matcher.py`
  - `backend/tests/resume_jd/phase_04/test_phase_04_matching.py`
  - `backend/test_phase4_e2e.py`
- **Files Modified:**
  - `backend/app/resume_jd/models/canonical_jd.py`
  - `backend/app/resume_jd/matching/normalizer.py`
  - `backend/app/resume_jd/matching/engine.py`
  - `backend/app/resume_jd/storage/json_store.py`
- **Implementation Details:** 
  - **Normalization Approach:** Strict, explicit mapping for aliases (e.g., "Amazon Web Services Glue" -> "AWS Glue", "k8s" -> "Kubernetes"). If an item doesn't map, its original value is preserved.
  - **Adapter Approach:** Adapters wrap the raw Parsers (Phase 1). They convert chunks and raw arrays into `CanonicalItem`s, packaging them into `CanonicalResume` and `CanonicalJD`. `MatchEngine` was updated to consume these.
  - **Phase 3 Source Grounding:** Strict deterministic validation; LLM provides `source_text` which is verified and converted into `source_span` offsets. Hallucinations are actively rejected.
  - **Phase 3 Atomization:** Parent requirement capabilities are preserved distinctly from child `atoms` (technologies, skills), allowing downstream phases to connect exact canonical dependencies.
  - [x] Phase 5: Scoring (0-100 deterministic) pipeline processing Candidate Generation (cheap/conservative) -> Lexical Analysis -> Semantic Analysis -> Ontology -> Qualifier Validation. Produces `MatchEdge[]` with specific categories (EXACT, RELATED, PARTIAL, TRANSFERABLE, GAP).
  - **Phase 4 GAP Logic:** Resolves GAPs only at the REQUIREMENT level, rather than at the individual edge level, ensuring that if ANY valid evidence satisfies a requirement, it is NOT classified as a GAP.
  - **Timestamping:** All Phase 3 artifacts are generated with an Asia/Kolkata ISO-8601 timestamp and naming prefix indicating chronological sort order via `JSONStore`.
  - **Tests Executed:** E2E Phase 3 execution, deterministic source grounding acceptance/rejection tests, hallucination rejection, and canonical object linking tests. Phase 4 matching scenarios tests completed including logic assertions on match fall-through decisions (14/14 tests passing).
  - **Confirmation:** Phases 6-9 are absolutely NOT implemented.
### 5. Phase 5 (Deterministic JD Match Scoring) [COMPLETED]
- **Files Added:** `backend/app/jd_arch/phase_05_scoring.md`, `backend/app/resume_jd/scoring/phase_05_config.py`, `backend/app/resume_jd/scoring/phase_05_scorer.py`, `backend/app/resume_jd/models/phase_05_models.py`, `backend/tests/resume_jd/phase_05/test_phase_05_scoring.py`, `backend/test_phase5_e2e.py`.
- **Implementation Details:** 
  - Implemented the deterministc Phase 5 Scoring pipeline utilizing purely Phase 4 `MatchEdge` outputs.
  - Calculated required vs preferred scaling logic mapped cleanly by importance signals.
  - Centralized configurable scoring parameters (Exact=1.0, Transferable=0.35, Required=1.0) decoupled from core logic.
  - Mitigated "duplicate counting" by strictly iterating atom fulfillment.
  - Integrated `ConstraintGate` mechanisms for strict qualifiers to safely zero metrics if conditions aren't met.
  - Implemented stable, deterministic `edge_id` generation using SHA-256 for comprehensive audit explainability.
- **Tests Executed:** E2E Phase 5 execution, hard constraints degradation, and atom deduplication tests. 5/5 Phase 5 tests passed; 54/54 overall backend tests passed.
- **Confirmation:** Phases 6-9 are absolutely NOT implemented.

## Next Session Focus
- **Next Step:** Phase 6 (API Payload + Frontend Component definition).
