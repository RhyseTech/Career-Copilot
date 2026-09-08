# JD Parsing Architecture

## The Idea
The JD parsing step is responsible for ingesting a raw Job Description (text or document) and extracting its core components deterministically. Rather than extracting a flat list of text, it breaks down the JD into discrete, structured **Requirements**.

We will parse the following attributes from the JD:
- Job Title
- Required Skills & Qualifications
- Preferred/Nice-to-have Skills
- Experience Requirements (e.g., "4 years")
- Education Requirements
- Domain Knowledge
- Tools / Technologies

Each requirement will have an assigned **weight** and a **required vs preferred** flag. This ensures that the downstream matching engine can score candidates deterministically rather than relying on black-box LLM decisions.

## Code Location
The logic for JD Parsing will be centralized in:
- `backend/app/jd_arch/jd_parser.py` (The main parsing logic)
- `backend/app/jd_arch/models.py` (The Pydantic schemas defining the `CanonicalJD` and `Requirement` structure)

## JSON Output Location
When a JD is successfully parsed, the structured output will be stored as a JSON file to ensure traceability and reproducibility.
- **Output Directory:** `backend/app/uploads/parsed_jds/`
- **Output Format:** JSON
- **Naming Convention:** `{jd_id}_canonical.json` (where `jd_id` is a generated UUID corresponding to the uploaded JD).

This JSON file can be inspected at any time to verify exactly what the engine extracted before any matching occurs.
