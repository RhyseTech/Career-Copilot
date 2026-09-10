# Phase 5 Integration Forensic Analysis

This document outlines the forensic assessment of the legacy scoring/matching infrastructure versus the newly implemented Phase 3–5 pipeline. No codebase modifications were made during the compilation of this assessment.

## 1. Current Execution Flow
The current flow in the UI uses the hybrid endpoint `POST /resume-jd/match-types`:
1. Receives Resume File and JD Text.
2. Invokes the legacy `MatchEngine` to generate canonical forms and calculate similarity thresholds per requirement.
3. Simultaneously attempts to run the new `Phase3Extractor` → `Phase4Matcher` → `Phase5Scorer` pipeline.
4. Returns a hybrid payload containing both the legacy `MatchEngine` requirement results and the `phase5_score`.
5. **The Frontend computes its own score**: The 45% score visible in the UI is actually calculated inside `page.tsx` via `const matchScore = totalReqs > 0 ? Math.round((satisfiedReqs / totalReqs) * 100) : 0;` using the legacy match results.

## 2. Legacy Execution Flow (ATS route)
1. `POST /ats/match` is invoked.
2. Calls `ResumeParser`, `SkillExtractor`, and `ExperienceParser`.
3. Calls `JDParser`.
4. Executes `JDScoringEngine.calculate_match_score()`, a hardcoded weighted formula (`55% Skills, 25% Experience, 15% Semantic, 5% Base Penalty`).

## 3. Phase 3–5 Execution Flow
1. **Phase 3 (`Phase3Extractor`)**: Uses LLM to extract granular `JDRequirements` (with ontology-derived atoms) and `ResumeEvidence` spans natively grounded in the source text.
2. **Phase 4 (`Phase4Matcher`)**: Deterministically generates evidence-candidate intersection tokens, evaluating exact/partial matches into immutable `MatchEdges`.
3. **Phase 5 (`Phase5Scorer`)**: Produces a purely deterministic, mathematically traceable requirement-coverage score based on Phase 4 edges, strictly prohibiting prompt-tuning drift.

## 4. Current Endpoint Inventory
| Endpoint | Description | Status Assessment |
| --- | --- | --- |
| `POST /ats/analyze` | Resume basic parse | KEEP (Base capabilities) |
| `POST /ats/match` | Legacy scoring engine (55/25/15) | DEPRECATE |
| `POST /ats/diagnose` | LLM suggestions | KEEP (External module) |
| `POST /resume-jd/match-types`| Hybrid wrapper for MatchEngine & Phase 3-5 | WRAP/REPLACE |

## 5. Current Frontend Data Flow
- **Data Source**: Reaches `/resume-jd/match-types`.
- **Top Score (45%)**: Calculated dynamically in React UI via `(satisfiedReqs / totalReqs) * 100`.
- **Three Skill Sections**: Sourced from legacy `MatchEngine` output elements via mapping requirement label classes (`Exact`, `Related`, etc.).
- **Dashboard**: Phase 5 component is conditionally bolted onto the bottom if the score exists.

## 6. Old Scoring Implementation Assessment
- **File**: `app/services/jd_scoring_engine.py` & `app/resume_jd/matching/engine.py`
- **Assessment**: The old systems rely heavily on heuristic percentage boundaries and semantic similarity thresholding inside the backend logic. Furthermore, the frontend is bypassing backend scoring authority by calculating an arbitrary ratio itself.
- **Verdict**: **REPLACE / DEPRECATE**. Must not compete with Phase 5.

## 7. New Scoring Implementation Assessment
- **File**: `app/resume_jd/scoring/phase_05_scorer.py`
- **Assessment**: Mathematically sound, directly tracks to MatchEdges, immune to parsing hallucinations due to strict safe-containment evaluation.
- **Verdict**: **KEEP / PROMOTE**. This is the sole authoritative scoring engine.

## 8. Three Skill Sections Assessment
- **Sections**: "Extracted JD Skills", "Matched Skills", "Unmatched Skills"
- **Assessment**: Highly valuable UI components, but currently drawing data from the legacy `MatchEngine` response instead of Phase 3 `JDRequirements` and Phase 4 `MatchEdges`.
- **Verdict**: **KEEP UI, REPLACE DATA**. Remap frontend mappings to use Phase 3/4 taxonomy.

## 9. Exact Source of the Old 45% Score
**Frontend Calculation**: `frontend/src/app/resume-jd/page.tsx` line 152:
```javascript
const satisfiedReqs = results.filter(r => ["Exact", "Related", "Partial", "Transferable"].includes(r.match.label)).length;
const matchScore = totalReqs > 0 ? Math.round((satisfiedReqs / totalReqs) * 100) : 0;
```

## 10. Exact Source of the New Phase 5 Score
**Backend Calculation**: `app/resume_jd/scoring/phase_05_scorer.py` yielding the `final_score` field in the `Phase5Score` schema.

## 11. Files to Keep
- `app/resume_jd/pipelines/phase_03_extractor.py`
- `app/resume_jd/pipelines/phase_04_matcher.py`
- `app/resume_jd/scoring/phase_05_scorer.py`
- `app/resume_jd/models/phase_0*` (Schemas)
- `frontend/src/app/resume-jd/page.tsx` (UI Structure)

## 12. Files to Deprecate
- `app/services/jd_scoring_engine.py`
- `app/resume_jd/matching/engine.py`
- `app/resume_jd/matching/similarity.py`
- `app/resume_jd/matching/classifier.py`

## 13. Files That Should Not Be Touched
- All core logic files for Phase 3, Phase 4, and Phase 5 (`phase_03_extractor.py`, `phase_04_matcher.py`, `phase_05_scorer.py`, and `phase_05_config.py`).
- Existing parsing prompt structures (unless fundamentally required to satisfy strict API schema, but Phase 3 is frozen).

## 14. Recommended API Structure
The new API layer will strictly isolate phases while providing an orchestrator:
- `POST /api/v1/resume/parse` (Phase 1)
- `POST /api/v1/jd/parse` (Phase 1)
- `POST /api/v1/resume/canonicalize` (Phase 2)
- `POST /api/v1/jd/canonicalize` (Phase 2)
- `POST /api/v1/analysis/requirements-evidence` (Phase 3)
- `POST /api/v1/analysis/matches` (Phase 4)
- `POST /api/v1/analysis/score` (Phase 5)
- `POST /api/v1/analysis/run` (Orchestrator)

## 15. Inconsistencies Discovered
1. **Frontend Score Usurpation**: The frontend calculates a high-level percentage score based on ratio division, entirely bypassing any backend weighted scoring system (legacy or new).
2. **Dual-Pipeline Execution**: `POST /resume-jd/match-types` currently executes the legacy MatchEngine and the new Phase 3-5 pipeline entirely in parallel, creating severe performance overlap and duplicative storage logic.
