# JD Parsing Architecture

## 1. Purpose
The new JD parser exists to provide a robust, deterministic, and explainable foundation for the isolated Resume + JD intelligence module. Traditional parsing either relies entirely on brittle regex (missing semantic context) or entirely on an LLM "black box" (causing hallucinations and untraceable scoring decisions). This architecture introduces a **Hybrid** approach: using deterministic logic for boundaries and metadata, while using an LLM strictly as an extraction assistant. The final output is a single, traceable source of truth called the `CanonicalJD`.

## 2. Existing Flow
Currently in Career-Copilot, JD parsing happens in two disconnected paths:
- `backend/app/services/jd_parser.py`: Uses `SkillExtractor` (regex/string matching) and simple regex to extract flat lists of "required_skills" and "required_experience_years".
- `backend/app/services/jd_analyzer.py`: Sends the entire JD to an LLM (`LLMOptimizer`) with a system prompt to return a flat JSON structure (`role`, `required_skills`, `preferred_skills`).

**Current Consumers:** The existing ATS system uses these to power basic matching and keyword displays. 
**Limitations:** Neither flow maps extracted skills back to the source text (provenance), making explainability impossible. The LLM can also hallucinate skills.

## 3. New Flow
```
JD
 ↓
Text extraction (DocumentParser)
 ↓
Deterministic extraction (Sectionizer)
 ↓
LLM extraction when required (LLMExtractor)
 ↓
Validation (Anti-hallucination verification)
 ↓
Normalization (Mapping to Canonical forms)
 ↓
CanonicalJD (Pydantic Model)
 ↓
Canonical JSON storage (JSON Store)
```

## 4. Architecture Diagram
```
                    EXISTING CAREER-COPILOT
                           │
                    Existing JD Parser
                    Existing JD Analyzer
                           │
                           ▼
                 ┌─────────────────────┐
                 │  HYBRID JD PARSER   │
                 │                     │
                 │ Deterministic       │
                 │        +            │
                 │ LLM when needed     │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Validation +        │
                 │ Normalization       │
                 └──────────┬──────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │ CanonicalJD │
                     └──────┬──────┘
                            │
                            ▼
                   canonical JD JSON
                  SINGLE SOURCE OF TRUTH
```

## 5. File/Folder Map
All new logic is strictly isolated to avoid breaking existing ATS flows:

```text
backend/app/resume_jd/
├── models/
│   └── canonical_jd.py       # Pydantic schemas representing the Source of Truth.
├── parsing/
│   └── jd/
│       ├── hybrid_parser.py  # Orchestrates deterministic + LLM + validation.
│       ├── sectionizer.py    # Deterministically splits JD into sections.
│       └── llm_extractor.py  # Isolated LLM boundary with strict JSON output contract.
└── storage/
    └── json_store.py         # Persists CanonicalJD to backend/app/uploads/parsed_jds/
```

- **`hybrid_parser.py`**: The main entry point. Takes raw text, uses `sectionizer` to chunk it, passes complex chunks to `llm_extractor`, validates the LLM output against the raw text, and returns a `CanonicalJD`.
- **`sectionizer.py`**: Uses heuristics to find headings like "Responsibilities", "Qualifications", etc.
- **`llm_extractor.py`**: Wraps the existing `LLMOptimizer` but enforces a strict JSON schema for extracting `requirements`.

## 6. CanonicalJD Schema
```json
{
  "jd_id": "string (UUID)",
  "content_hash": "string (SHA256)",
  "job_title": "string",
  "raw_text": "string",
  "requirements": [
    {
      "requirement_id": "string",
      "requirement_type": "REQUIRED | PREFERRED",
      "category": "SKILL | EXPERIENCE | EDUCATION | CERTIFICATION | GENERAL",
      "raw_text": "string (The extracted phrase)",
      "source_span": "string (Exact matching text from the JD)",
      "source_section": "string",
      "confidence": "float",
      "provenance": "EXTRACTED | INFERRED"
    }
  ]
}
```

## 7. LLM Boundary
- **When called:** Only when parsing sections like "Responsibilities" or "Requirements" where skills are buried in natural language.
- **Input Contract:** Raw text of a specific section.
- **Output Contract:** A JSON list of objects matching the `Requirement` schema.
- **Validation (Hallucination Protection):** A post-processing step ensures that the `source_span` returned by the LLM exists exactly as a substring in the provided section text. If it doesn't, the extraction is rejected.
- **Provider Abstraction:** Uses the existing `app.services.llm_optimizer.LLMOptimizer` to support Groq/Gemini transparently.

## 8. Deterministic vs LLM Responsibilities
| Responsibility | Deterministic | LLM |
|---|---|---|
| Section detection | Yes | No |
| Obvious metadata | Yes | No |
| Contextual skill extraction | Partial | Yes |
| Required vs preferred | Partial | Yes |
| Experience interpretation | Partial | Yes |
| Validation & Traceability | Yes | NEVER |
| Final match score | Yes/Downstream | NEVER |
| Resume rewriting | No | NEVER |

## 9. Provenance and Traceability
Every requirement in `CanonicalJD` has a `source_span` and `source_section`. When presenting results or explaining a match score, the UI can highlight the exact sentence in the original JD that demanded that skill.

## 10. JSON Source of Truth
- **Authoritative Representation:** `CanonicalJD` JSON.
- **Location:** `backend/app/uploads/parsed_jds/{jd_id}_canonical.json`.
- **Writers:** Written exactly once by `json_store.py` upon successful parsing.
- **Readers:** Downstream systems (Matching, Gap Analysis, Optimization).
- **Temporary Representations:** LLM output dictionaries, `DocumentParser` strings. These are discarded.

## 11. Error Handling
- **Malformed LLM Output:** If the LLM fails to return valid JSON, the parser falls back to deterministic extraction for that section.
- **Mapping Failures:** If an LLM extracts a skill but the `source_span` is not found in the original text (hallucination), that specific requirement is silently dropped from the final `CanonicalJD`.

## 12. Testing Strategy
- Unit tests located in `backend/tests/resume_jd/parsing/test_jd_parser.py`.
- The `LLMExtractor` class is patched/mocked to return predefined JSON during unit tests, ensuring no live API calls are made and tests run instantly.
- Tests verify that deterministic heuristics work and that hallucinated LLM responses are properly rejected by the validation layer.

## 13. Future Integration
This CanonicalJD will eventually feed into:
`JD Requirements -> Weighting -> Resume Evidence -> Matching -> Explainable Score -> Gap Analysis -> Optimization`.
These stages are completely isolated from parsing and only consume the JSON output.
