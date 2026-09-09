from app.resume_jd.pipelines.phase_04_matcher import Phase4Matcher

matcher = Phase4Matcher()

req_text = "GCP Dataflow pipeline development"
ev_text = "AWS Glue pipeline development"

# Check concept extraction
req_concept = matcher._extract_concept(req_text)
ev_concept = matcher._extract_concept(ev_text)
print(f"req_concept: {repr(req_concept)}")
print(f"ev_concept: {repr(ev_concept)}")

# Check residuals
req_residual = req_text.lower().replace(req_concept.lower(), "").strip()
ev_residual = ev_text.lower().replace(ev_concept.lower(), "").strip()
print(f"req_residual: {repr(req_residual)}")
print(f"ev_residual: {repr(ev_residual)}")

# Check action overlap
ao = matcher._compute_action_overlap(req_text, ev_text)
print(f"action_overlap: {ao}")

# Check ontology
from app.resume_jd.models.phase_04_models import OntologyRelation
rel = matcher.ontology.get_relation(req_text, ev_text)
print(f"relation (full text): {rel}")
rel2 = matcher.ontology.get_relation("gcp dataflow", "aws glue")
print(f"relation (concept only): {rel2}")

# Full match
from app.resume_jd.models.phase_03_models import JDRequirement, ResumeEvidence
req = JDRequirement(requirement_id="R1", parent_capability=req_text, raw_value=req_text, requirement_text=req_text, category="EXPERIENCE", requirement_type="REQUIRED", source_document_id="d1", source_section="s1", atoms=[])
ev = ResumeEvidence(evidence_id="E1", raw_value=ev_text, evidence_text=ev_text, category="EXPERIENCE", source_document_id="d2", source_section="s2")
edges = matcher.match([req], [ev])
print(f"\nFull match result: match_type={edges[0].match_type}")
print(f"Reason: {edges[0].decision_reason}")
print(f"Ontology: {edges[0].ontology_features}")
