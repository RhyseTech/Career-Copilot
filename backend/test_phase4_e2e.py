import json
import os
import pytest
from app.resume_jd.pipelines.phase_04_matcher import Phase4Matcher
from app.resume_jd.models.phase_03_models import JDRequirement, ResumeEvidence

def get_latest_file(directory: str, prefix: str) -> str:
    if not os.path.exists(directory):
        return None
    files = [f for f in os.listdir(directory) if f.startswith(prefix) and f.endswith('.json')]
    if not files:
        return None
    files.sort(reverse=True)
    return os.path.join(directory, files[0])

def test_phase4_e2e_with_real_artifacts():
    # Attempt to load actual Phase 3 artifacts
    jd_dir = "data/parsed_jds"
    resume_dir = "data/parsed_resumes"
    
    jd_file = get_latest_file(jd_dir, "reqs_canonical_jd_")
    resume_file = get_latest_file(resume_dir, "ev_canonical_resume_")
    
    if not jd_file or not resume_file:
        pytest.skip("Phase 3 artifacts not found, skipping Phase 4 E2E.")
        return
        
    with open(jd_file, 'r', encoding='utf-8') as f:
        jd_data = json.load(f)
        
    with open(resume_file, 'r', encoding='utf-8') as f:
        resume_data = json.load(f)
        
    requirements = [JDRequirement(**req) for req in jd_data.get('requirements', [])]
    evidence_items = [ResumeEvidence(**ev) for ev in resume_data.get('evidence', [])]
    
    if not requirements or not evidence_items:
        pytest.skip("Phase 3 artifacts are empty, skipping Phase 4 E2E.")
        return
        
    matcher = Phase4Matcher()
    edges = matcher.match(requirements, evidence_items)
    
    # Assert we produced some edges
    assert len(edges) > 0
    
    # Assert all requirements are covered (either by a match or a GAP)
    req_ids_in_edges = {edge.requirement_id for edge in edges}
    for req in requirements:
        assert req.requirement_id in req_ids_in_edges
        
    # Print some stats if run with -s
    exact_count = sum(1 for e in edges if e.match_type == "EXACT")
    related_count = sum(1 for e in edges if e.match_type == "RELATED")
    partial_count = sum(1 for e in edges if e.match_type == "PARTIAL")
    transfer_count = sum(1 for e in edges if e.match_type == "TRANSFERABLE")
    gap_count = sum(1 for e in edges if e.match_type == "GAP")
    
    print(f"\nPhase 4 E2E Results:")
    print(f"Total Requirements: {len(requirements)}")
    print(f"Total Evidence: {len(evidence_items)}")
    print(f"EXACT: {exact_count}")
    print(f"RELATED: {related_count}")
    print(f"PARTIAL: {partial_count}")
    print(f"TRANSFERABLE: {transfer_count}")
    print(f"GAP: {gap_count}")

if __name__ == "__main__":
    test_phase4_e2e_with_real_artifacts()
