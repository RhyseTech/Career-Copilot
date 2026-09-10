import pytest
from app.resume_jd.models.phase_03_models import JDRequirement, ResumeEvidence, JDRequirementAtom
from app.resume_jd.models.phase_04_models import MatchEdge, QualifierStatus
from app.resume_jd.scoring.phase_05_config import Phase5Config
from app.resume_jd.scoring.phase_05_scorer import Phase5Scorer

@pytest.fixture
def scorer():
    return Phase5Scorer()

def test_explainability_and_traceability(scorer):
    req = JDRequirement(
        requirement_id="req1",
        parent_capability="Backend Dev",
        raw_value="Python",
        requirement_text="Must know Python",
        category="SKILL",
        requirement_type="REQUIRED",
        importance_signals=["MEDIUM"],
        source_document_id="doc1",
        source_section="skills",
        atoms=[JDRequirementAtom(atom_id="atom1", raw_value="Python", atom_type="TECHNOLOGY")]
    )
    edge = MatchEdge(
        requirement_id="req1",
        match_type="EXACT",
        satisfied_atoms=["atom1"],
        evidence_ids=["ev1", "ev2"],
        decision_reason="Exact match on Python"
    )
    score = scorer.score([req], [], [edge])
    
    rs = score.requirement_scores[0]
    # Traceability
    assert "atom1" in rs.contributing_atom_ids
    assert "ev1" in rs.contributing_evidence_ids
    assert "ev2" in rs.contributing_evidence_ids
    assert edge.edge_id in rs.contributing_match_edge_ids
    assert score.scoring_config_version == Phase5Config.VERSION
    
    # Explainability
    assert "Weight: 1.00, Coverage: 1.00" in rs.deterministic_explanation
    assert "'Python' requirement atom received EXACT coverage" in rs.deterministic_explanation
    assert "ev1, ev2" in rs.deterministic_explanation
    assert edge.edge_id in rs.deterministic_explanation

def test_hard_constraint_failure_gates_score(scorer):
    req = JDRequirement(
        requirement_id="req1",
        parent_capability="Clearance",
        raw_value="Top Secret",
        requirement_text="Must have TS",
        category="SKILL",
        requirement_type="REQUIRED",
        importance_signals=["HARD_CONSTRAINT"],
        source_document_id="doc1",
        source_section="skills",
        atoms=[JDRequirementAtom(atom_id="atom1", raw_value="Top Secret", atom_type="CERTIFICATION")]
    )
    
    req_unrelated = JDRequirement(
        requirement_id="req2",
        parent_capability="Backend",
        raw_value="Python",
        requirement_text="Python",
        category="SKILL",
        requirement_type="REQUIRED",
        source_document_id="doc1",
        source_section="skills",
        atoms=[JDRequirementAtom(atom_id="atom2", raw_value="Python", atom_type="TECHNOLOGY")]
    )
    
    edge_ts = MatchEdge(
        requirement_id="req1", match_type="GAP", satisfied_atoms=[],
        decision_reason="No clearance"
    )
    edge_py = MatchEdge(
        requirement_id="req2", match_type="EXACT", satisfied_atoms=["atom2"],
        decision_reason="Has Python"
    )
    
    score = scorer.score([req, req_unrelated], [], [edge_ts, edge_py])
    
    # Even though Python is EXACT (Base score should be 50%), the constraint gate zeros the final score.
    assert score.base_score == 50.0
    assert score.constraint_gate == 0.0
    assert score.final_score == 0.0
    assert "req1" in score.hard_constraints_failed

def test_transferable_contribution_reason(scorer):
    req = JDRequirement(
        requirement_id="req1",
        parent_capability="Cloud",
        raw_value="GCP Dataflow",
        requirement_text="GCP Dataflow",
        category="SKILL",
        requirement_type="REQUIRED",
        source_document_id="doc1",
        source_section="skills",
        atoms=[JDRequirementAtom(atom_id="atom1", raw_value="GCP Dataflow", atom_type="TECHNOLOGY")]
    )
    edge = MatchEdge(
        requirement_id="req1", match_type="TRANSFERABLE", satisfied_atoms=["atom1"],
        evidence_ids=["ev1"], decision_reason="AWS Glue pipeline evidence supports similar responsibility"
    )
    score = scorer.score([req], [], [edge])
    rs = score.requirement_scores[0]
    assert rs.coverage == 0.35 # TRANSFERABLE contribution
    assert "AWS Glue pipeline evidence supports similar responsibility" in rs.deterministic_explanation

def test_qualifier_degradation_reason(scorer):
    req = JDRequirement(
        requirement_id="req1",
        parent_capability="Backend Dev",
        raw_value="5+ years Python",
        requirement_text="5+ years Python",
        category="SKILL",
        requirement_type="REQUIRED",
        source_document_id="doc1",
        source_section="skills",
        atoms=[JDRequirementAtom(atom_id="atom1", raw_value="Python", atom_type="TECHNOLOGY")]
    )
    edge = MatchEdge(
        requirement_id="req1", match_type="PARTIAL", satisfied_atoms=["atom1"],
        qualifier_results={"YOE": QualifierStatus.NOT_SATISFIED},
        decision_reason="YOE failed"
    )
    score = scorer.score([req], [], [edge])
    rs = score.requirement_scores[0]
    assert "Qualifier YOE was NOT_SATISFIED" in rs.deterministic_explanation
    assert rs.coverage == 0.50

def test_weighting_multipliers(scorer):
    req_pref_low = JDRequirement(
        requirement_id="r1", parent_capability="A", raw_value="A", requirement_text="A", category="SKILL",
        requirement_type="PREFERRED", importance_signals=["LOW"], source_document_id="d1", source_section="s"
    )
    req_req_high = JDRequirement(
        requirement_id="r2", parent_capability="B", raw_value="B", requirement_text="B", category="SKILL",
        requirement_type="REQUIRED", importance_signals=["HIGH"], source_document_id="d1", source_section="s"
    )
    score = scorer.score([req_pref_low, req_req_high], [], [])
    
    w1 = score.requirement_scores[0].weight
    w2 = score.requirement_scores[1].weight
    assert w1 == 0.35 * 0.6 # 0.21
    assert w2 == 1.0 * 1.5 # 1.50

def test_zero_weight_protection(scorer):
    # Pass empty requirements
    score = scorer.score([], [], [])
    assert score.base_score == 0.0
    assert score.final_score == 0.0

def test_evidence_deduplication(scorer):
    req = JDRequirement(
        requirement_id="r1", parent_capability="A", raw_value="Python", requirement_text="Python", category="SKILL",
        requirement_type="REQUIRED", source_document_id="d1", source_section="s",
        atoms=[JDRequirementAtom(atom_id="a1", raw_value="Python", atom_type="TECHNOLOGY")]
    )
    # Duplicate MatchEdges
    e1 = MatchEdge(requirement_id="r1", match_type="EXACT", satisfied_atoms=["a1"], evidence_ids=["ev1"], decision_reason="R1")
    e2 = MatchEdge(requirement_id="r1", match_type="EXACT", satisfied_atoms=["a1"], evidence_ids=["ev2"], decision_reason="R2")
    
    score = scorer.score([req], [], [e1, e2])
    # The coverage should be exactly 1.0, not artificially inflated
    assert score.requirement_scores[0].coverage == 1.0
    assert score.base_score == 100.0

def test_compound_requirements_partial(scorer):
    req = JDRequirement(
        requirement_id="r1", parent_capability="A", raw_value="Python and Spark", requirement_text="Python and Spark", category="SKILL",
        requirement_type="REQUIRED", source_document_id="d1", source_section="s",
        atoms=[
            JDRequirementAtom(atom_id="a1", raw_value="Python", atom_type="TECHNOLOGY"),
            JDRequirementAtom(atom_id="a2", raw_value="Spark", atom_type="TECHNOLOGY")
        ]
    )
    # Python is EXACT, Spark is GAP
    e1 = MatchEdge(requirement_id="r1", match_type="EXACT", satisfied_atoms=["a1"], decision_reason="R1")
    e2 = MatchEdge(requirement_id="r1", match_type="GAP", satisfied_atoms=["a2"], decision_reason="R2")
    
    score = scorer.score([req], [], [e1, e2])
    # 2 atoms, 1 EXACT (1.0), 1 GAP (0.0). Coverage = 0.5
    assert score.requirement_scores[0].coverage == 0.5
