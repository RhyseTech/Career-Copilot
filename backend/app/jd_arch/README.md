# Resume + JD Match & Optimization Architecture

This directory (`backend/app/jd_arch/`) serves as the central documentation and architectural source of truth for the complete 9-phase Resume ↔ JD Match & Optimization pipeline in Career-Copilot.

## Purpose

The `jd_arch` module establishes the architectural boundaries, contracts, and research-driven foundation for advanced candidate-to-job matching, scoring, and resume optimization. By mapping raw text to canonical representations, extracting requirements and evidence, and applying explainable matching logic, this pipeline aims to offer deterministic, non-hallucinated feedback and targeted resume optimization.

## Overall Pipeline

The pipeline is structured into 9 isolated, sequential phases:

1. **DOCUMENT PARSING:** Extract text and structured metadata/requirements from raw Resume and JD.
2. **CANONICALIZATION:** Convert raw representations into a shared, normalized schema with provenance.
3. **REQUIREMENTS + EVIDENCE:** Define required JD skills vs extracted Resume evidence.
4. **MATCHING:** Determine the strength of relationship (e.g., EXACT, RELATED, TRANSFERABLE) between requirements and evidence.
5. **SCORING:** Generate an explainable, deterministic 0–100 score.
6. **GAP ANALYSIS:** Identify the highest-impact missing requirements.
7. **OPTIMIZATION:** Suggest truthful resume adjustments.
8. **VALIDATION:** Prevent hallucination and verify constraints.
9. **RE-SCORING:** Confirm optimization impact.

## Relationship to Existing Career-Copilot Code

This architecture **must not** disrupt or redesign the existing, functioning ATS flow or simple document parsers. 
- It reuses existing robust parsing implementations where applicable.
- It completely isolates advanced matching logic into its own self-contained workflow.
- It defines and stores its state using independent JSON representations (`{jd_id}_canonical.json`).

## Ownership

**What this module OWNS:**
- The end-to-end architecture definitions for matching and optimization.
- The canonical data contracts (e.g., `CanonicalJD`, normalized Resume models).
- Deterministic extraction rules, normalizers, similarity classifiers, and scoring logic.

**What this module must NOT own:**
- Baseline PDF/DOCX text extraction libraries (downstream utilities).
- UI state or presentation layers.
- The primary ATS schema (unless explicitly adopted for shared use cases).
- Opaque LLM-only scoring flows (all scoring must remain deterministic and verifiable).

## Current Implementation Status

- **Phase 1 (Document Parsing):** Partially implemented. JD Hybrid parsing exists and stores canonical JSON.
- **Phase 2 (Canonicalization):** Architectural definition established; partial canonicalization model (`Requirement.canonical_skills`) implemented.
- **Phases 3–9:** Architecture boundries defined. Implementation pending.
