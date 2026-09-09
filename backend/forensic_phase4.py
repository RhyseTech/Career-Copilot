from app.resume_jd.pipelines.phase_04_matcher import Phase4Matcher
from app.resume_jd.models.phase_03_models import JDRequirement, ResumeEvidence, JDRequirementAtom

matcher = Phase4Matcher()

def req(id, text, cat="EXPERIENCE", atoms=None):
    return JDRequirement(requirement_id=id, parent_capability=text, raw_value=text,
                         requirement_text=text, category=cat, requirement_type="REQUIRED",
                         source_document_id="d1", source_section="s1", atoms=atoms or [])

def ev(id, text, cat="EXPERIENCE"):
    return ResumeEvidence(evidence_id=id, raw_value=text, evidence_text=text,
                          category=cat, source_document_id="d2", source_section="s2")

# === Forensic Test: 5+ years Python vs 2 years Python (root-level, no atoms) ===
print("=== FORENSIC: 5+ years Python vs 2 years Python (simple, no atoms) ===")
e = matcher.match([req("R1", "5+ years Python")], [ev("E1", "2 years Python")])
print(f"match_type={e[0].match_type}")
print(f"qualifier={e[0].qualifier_results}")
print(f"reason={e[0].decision_reason}")

print()

# === Forensic Test: 5+ years Python vs 5 years Python (should be EXACT not TRANSFERABLE) ===
print("=== FORENSIC: 5+ years Python vs 5 years Python (simple, no atoms) ===")
e = matcher.match([req("R1", "5+ years Python")], [ev("E1", "5 years Python")])
print(f"match_type={e[0].match_type}")
print(f"qualifier={e[0].qualifier_results}")
print(f"canonical_overlap (req raw_value == ev raw_value): {'5+ years python' == '5 years python'}")

print()

# === Forensic Test: GAP at requirement level ===
print("=== FORENSIC: GAP - Two evidence items, one RELATED, one insufficient ===")
req_k8s = req("R1", "Kubernetes")
ev_docker = ev("E1", "Docker")   # related technology but not in ontology
ev_react = ev("E2", "React")     # completely unrelated
e = matcher.match([req_k8s], [ev_docker, ev_react])
print(f"num_edges={len(e)}")
for edge in e:
    print(f"  match_type={edge.match_type}, evidence_ids={edge.evidence_ids}, reason={edge.decision_reason[:80]}")

print()

# === Forensic Test: One evidence -> multiple requirements (many-to-many) ===
print("=== FORENSIC: One evidence -> multiple requirements (no mutation check) ===")
req1 = req("R1", "Python")
req2 = req("R2", "Python")
evidence_item = ev("E1", "Python")
original_ev_id = evidence_item.evidence_id
e = matcher.match([req1, req2], [evidence_item])
print(f"num_edges={len(e)}")
for edge in e:
    print(f"  req={edge.requirement_id}, match_type={edge.match_type}")
print(f"evidence_id after matching (not mutated): {evidence_item.evidence_id} == {original_ev_id}: {evidence_item.evidence_id == original_ev_id}")

print()

# === TRANSFERABLE: No monkeypatching, real semantic ===
print("=== FORENSIC: GCP Dataflow pipeline development vs AWS Glue pipeline development (real semantic) ===")
e = matcher.match([req("R1", "GCP Dataflow pipeline development")], [ev("E1", "AWS Glue pipeline development")])
print(f"match_type={e[0].match_type}")
print(f"semantic_score={e[0].semantic_features}")
print(f"ontology={e[0].ontology_features}")
print(f"reason={e[0].decision_reason}")
