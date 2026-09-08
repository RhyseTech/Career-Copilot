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
  3. Requirements + Evidence (NOT implemented yet)
  4. Matching (NOT implemented yet)
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
- **Files Modified:**
  - `backend/app/resume_jd/models/canonical_jd.py`
  - `backend/app/resume_jd/matching/normalizer.py`
  - `backend/app/resume_jd/matching/engine.py`
- **Implementation Details:** 
  - **Normalization Approach:** Strict, explicit mapping for aliases (e.g., "Amazon Web Services Glue" -> "AWS Glue", "k8s" -> "Kubernetes"). If an item doesn't map, its original value is preserved.
  - **Adapter Approach:** Adapters wrap the raw Parsers (Phase 1). They convert chunks and raw arrays into `CanonicalItem`s, packaging them into `CanonicalResume` and `CanonicalJD`. `MatchEngine` was updated to consume these.
  - **Tests Executed:** Alias normalization, Multi-word normalization, Acronym normalization, No aggressive normalization, and both adapter conversions. (6/6 tests passed).
  - **E2E Result:** The full `MatchEngine.process()` flow executed successfully without crashing, using the adapters internally. (Result: `{"requirements": []}` due to empty local LLM extraction block out-of-scope for Phase 2).
  - **Known Limitations:** `SkillExtractor` (Phase 1) doesn't natively identify multi-word aliases unless specifically added; so `JDAdapter` performs a fallback normalization on the entire chunk to gracefully handle it.
  - **Confirmation:** Phases 3-9 are absolutely NOT implemented.
- **Next Step:** Phase 3 (Requirements + Evidence) implementation.
