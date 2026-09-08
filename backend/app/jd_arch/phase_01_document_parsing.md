# Phase 1: Document Parsing Architecture

## Overview
Phase 1 serves as the foundational ingestion layer for the matching architecture. It is responsible for reading raw files (Resumes and JDs) and transforming their text into structured, traceable formats.

Crucially, **Phase 1 does NOT perform semantic matching or deep canonicalization**. It simply answers: *"What text exists in this document, and what are its boundaries?"*

## Existing Components
This architecture respects and isolates from the existing functionality in the Career-Copilot repository:
- **Resume Parsing:** Uses the existing base parser (`app/services/parser.py`) which extracts sections like Experience, Education, and Skills deterministically.
- **JD Parsing:** Handled via a new isolated `HybridJDParser` located in `app/resume_jd/parsing/jd/`.

## Extracted Information
The structured parsers are designed to extract discrete units of information without flattening everything into a single keyword list. 

**For a JD, this includes:**
- Job Title
- Required Skills & Qualifications
- Preferred / Nice-to-have Skills
- Experience Requirements
- Education Requirements
- Domain Knowledge
- Tools / Technologies
- Responsibilities / Expected actions
- Context surrounding the requirements

## Traceability Requirement
A strict rule of Phase 1 is that raw data must never be discarded. 

For example, if the JD contains:
*"Design, develop, and implement scalable and efficient data pipelines using AWS services (e.g., S3, EC2, ECS, Aurora)."*

The parser extracts the skills but strictly maintains the context:
- **Raw Skill:** AWS, S3, EC2, ECS, Aurora
- **Context/Source Span:** "Design, develop, and implement scalable and efficient data pipelines using AWS services (e.g., S3, EC2, ECS, Aurora)."
- **Requirement Type:** REQUIRED

This traceability guarantees explainability in later phases.

## JD Structured Output
The source of truth for a parsed JD is the `CanonicalJD` JSON structure. 

- **JSON Output Location:** `backend/app/uploads/parsed_jds/`
- **File Naming Convention:** `{jd_id}_canonical.json` (where `jd_id` is a generated UUID).

### Example JSON Requirement Output
```json
{
  "requirement_id": "req_8e5ccb91",
  "requirement_type": "REQUIRED",
  "category": "SKILL",
  "raw_text": "AWS services (e.g., S3, EC2, ECS, Aurora)",
  "source_span": "Design, develop, and implement scalable and efficient data pipelines using AWS services (e.g., S3, EC2, ECS, Aurora).",
  "source_section": "Responsibilities",
  "confidence": 0.9,
  "provenance": "EXTRACTED",
  "weight": 1.5,
  "canonical_skills": ["Amazon Web Services"]
}
```

## What Phase 1 Does NOT Do
- It does **not** map disparate skills together (e.g., knowing that "S3" is part of "AWS").
- It does **not** score the candidate.
- It does **not** rewrite the resume.
- It does **not** replace the existing primary ATS parser workflow outside of this isolated architecture.
