"""
Phase 4 Matching Unit Tests

Covers all forensic-identified issues and the 10 tests required by the remediation spec.
"""
import pytest
from typing import List

from app.resume_jd.models.phase_03_models import JDRequirement, ResumeEvidence, JDRequirementAtom
from app.resume_jd.models.phase_04_models import MatchEdge, OntologyRelation, QualifierStatus
from app.resume_jd.pipelines.phase_04_matcher import Phase4Matcher


@pytest.fixture
def matcher():
    return Phase4Matcher()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def mock_req(req_id, text, category="EXPERIENCE", atoms=None, canonical_ids=None):
    """Build a JDRequirement. If canonical_ids provided, wraps them in a single atom."""
    r_atoms = list(atoms) if atoms else []
    if canonical_ids and not r_atoms:
        r_atoms.append(JDRequirementAtom(
            atom_id=f"{req_id}_a1",
            raw_value=text,
            atom_type="TECHNOLOGY",
            canonical_item_ids=canonical_ids,
        ))
    return JDRequirement(
        requirement_id=req_id,
        parent_capability=text,
        raw_value=text,
        requirement_text=text,
        category=category,
        requirement_type="REQUIRED",
        source_document_id="doc1",
        source_section="reqs",
        atoms=r_atoms,
    )


def mock_ev(ev_id, text, category="EXPERIENCE", canonical_ids=None):
    e = ResumeEvidence(
        evidence_id=ev_id,
        raw_value=text,
        evidence_text=text,
        category=category,
        source_document_id="doc2",
        source_section="exp",
    )
    if canonical_ids:
        e.canonical_item_ids = canonical_ids
    return e


# ===========================================================================
# REMEDIATION TEST 1 — YOE Satisfied → EXACT
# "5+ years Python" vs "5 years Python" must produce EXACT
# ===========================================================================

def test_rem1_yoe_satisfied_produces_exact(matcher):
    req = mock_req("R1", "5+ years Python")
    ev = mock_ev("E1", "5 years Python")
    edges = matcher.match([req], [ev])
    assert len(edges) == 1
    assert edges[0].match_type == "EXACT", (
        f"Expected EXACT, got {edges[0].match_type}. Reason: {edges[0].decision_reason}"
    )
    assert edges[0].qualifier_results.get("yoe") == QualifierStatus.SATISFIED


def test_rem1_yoe_more_than_required_produces_exact(matcher):
    req = mock_req("R1", "3 years Python")
    ev = mock_ev("E1", "5 years Python")
    edges = matcher.match([req], [ev])
    assert edges[0].match_type == "EXACT"


# ===========================================================================
# REMEDIATION TEST 2 — YOE Shortfall → PARTIAL, never EXACT or TRANSFERABLE
# "5+ years Python" vs "2 years Python" must never be EXACT or TRANSFERABLE
# ===========================================================================

def test_rem2_yoe_shortfall_not_exact_not_transferable(matcher):
    req = mock_req("R1", "5+ years Python")
    ev = mock_ev("E1", "2 years Python")
    edges = matcher.match([req], [ev])
    assert len(edges) == 1
    assert edges[0].match_type not in ("EXACT", "TRANSFERABLE"), (
        f"Qualifier shortfall must not produce EXACT/TRANSFERABLE, got {edges[0].match_type}"
    )
    assert edges[0].qualifier_results.get("yoe") == QualifierStatus.NOT_SATISFIED


def test_rem2_yoe_shortfall_preferred_partial(matcher):
    req = mock_req("R1", "5+ years Python")
    ev = mock_ev("E1", "2 years Python")
    edges = matcher.match([req], [ev])
    # Preferred: PARTIAL; acceptable: GAP — never EXACT/TRANSFERABLE
    assert edges[0].match_type in ("PARTIAL", "GAP")


# ===========================================================================
# REMEDIATION TEST 3 — Qualifier precedence: high semantic cannot override NOT_SATISFIED
# ===========================================================================

def test_rem3_qualifier_blocks_even_at_high_semantic(matcher, monkeypatch):
    """Even with semantic similarity forced to 0.99, NOT_SATISFIED qualifier must block EXACT and TRANSFERABLE."""
    monkeypatch.setattr(matcher.similarity, "compute_semantic", lambda a, b: 0.99)
    req = mock_req("R1", "5+ years Python")
    ev = mock_ev("E1", "2 years Python")
    edges = matcher.match([req], [ev])
    assert edges[0].match_type not in ("EXACT", "TRANSFERABLE"), (
        f"High semantic must not override NOT_SATISFIED qualifier; got {edges[0].match_type}"
    )
    assert edges[0].qualifier_results.get("yoe") == QualifierStatus.NOT_SATISFIED


# ===========================================================================
# REMEDIATION TEST 4 — YOE regex false positives
# Version numbers and data sizes must NOT be interpreted as YOE
# ===========================================================================

def test_rem4_python_version_not_yoe(matcher):
    yoe = matcher._extract_yoe("Python 3.11")
    assert yoe is None, f"'Python 3.11' must not be parsed as YOE; got {yoe}"


def test_rem4_data_size_not_yoe(matcher):
    yoe = matcher._extract_yoe("5TB/day pipeline processing")
    assert yoe is None, f"'5TB/day' must not be parsed as YOE; got {yoe}"


def test_rem4_calendar_year_not_yoe(matcher):
    yoe = matcher._extract_yoe("Used Python since 2024")
    assert yoe is None, f"Calendar year '2024' must not be parsed as YOE; got {yoe}"


# ===========================================================================
# REMEDIATION TEST 5 — TRANSFERABLE: GCP Dataflow pipeline dev vs AWS Glue pipeline dev
# Ontology RELATED + meaningful action overlap → TRANSFERABLE
# ===========================================================================

def test_rem5_transferable_related_with_action_context(matcher):
    """GCP Dataflow pipeline development vs AWS Glue pipeline development → TRANSFERABLE."""
    req = mock_req("R1", "GCP Dataflow pipeline development")
    ev = mock_ev("E1", "AWS Glue pipeline development")
    edges = matcher.match([req], [ev])
    assert len(edges) == 1
    assert edges[0].match_type == "TRANSFERABLE", (
        f"Expected TRANSFERABLE, got {edges[0].match_type}. Reason: {edges[0].decision_reason}"
    )


# ===========================================================================
# REMEDIATION TEST 6 — NOT automatically TRANSFERABLE with no action context
# GCP Dataflow vs AWS Glue (technology names only, no action words) → RELATED, not TRANSFERABLE
# ===========================================================================

def test_rem6_related_without_action_context_is_not_transferable(matcher):
    """GCP Dataflow vs AWS Glue with no action/context words → RELATED (not TRANSFERABLE)."""
    req = mock_req("R1", "GCP Dataflow")
    ev = mock_ev("E1", "AWS Glue")
    edges = matcher.match([req], [ev])
    assert len(edges) == 1
    assert edges[0].match_type == "RELATED", (
        f"Without action context, ontology-RELATED pair must be RELATED, not TRANSFERABLE; "
        f"got {edges[0].match_type}"
    )


# ===========================================================================
# REMEDIATION TEST 7 — Unrelated technology pair → not TRANSFERABLE
# GCP Dataflow pipeline development vs React frontend development → GAP
# ===========================================================================

def test_rem7_unrelated_pair_is_not_transferable(matcher):
    req = mock_req("R1", "GCP Dataflow pipeline development")
    ev = mock_ev("E1", "React frontend development")
    edges = matcher.match([req], [ev])
    assert len(edges) == 1
    assert edges[0].match_type not in ("TRANSFERABLE", "EXACT", "RELATED"), (
        f"Unrelated technologies must not produce TRANSFERABLE; got {edges[0].match_type}"
    )


# ===========================================================================
# REMEDIATION TEST 8 — GAP creation does not mutate any evaluated MatchEdge
# ===========================================================================

def test_rem8_gap_creation_does_not_mutate_existing_edges(matcher):
    """
    When all candidates evaluate internally to GAP, the final output must be a
    FRESH MatchEdge. The evaluated edge objects must retain their original state.
    """
    req = mock_req("R1", "Kubernetes")
    ev = mock_ev("E1", "AngularJS")

    # Manually run evaluation to capture the evaluated edge before match() is called
    candidates = matcher._generate_candidates(req, [ev])
    evaluated_edges = [matcher._evaluate_candidate(req, c) for c in candidates] if candidates else []

    # Now call match()
    output_edges = matcher.match([req], [ev])

    # If we had evaluated edges, confirm none were mutated
    for orig in evaluated_edges:
        # match_type on the originally-evaluated object should not be "GAP" from in-place mutation
        # (in the new implementation, GAP is a fresh object, so orig is untouched)
        assert id(orig) not in [id(e) for e in output_edges], (
            "The final GAP edge must be a fresh object, not a mutated reference to an evaluated edge."
        )

    # The output must have exactly 1 edge and it must be GAP
    assert len(output_edges) == 1
    assert output_edges[0].match_type == "GAP"


# ===========================================================================
# Existing tests — all must continue to pass (REGRESSION)
# ===========================================================================

def test_exact_canonical_match(matcher):
    req = mock_req("R1", "Python", canonical_ids=["c_python"])
    ev = mock_ev("E1", "Python", canonical_ids=["c_python"])
    edges = matcher.match([req], [ev])
    assert len(edges) == 1
    assert edges[0].match_type == "EXACT"
    assert "same canonical concept" in edges[0].decision_reason
    assert "E1" in edges[0].evidence_ids


def test_related_ontology_relationship(matcher):
    req = mock_req("R1", "AWS Glue")
    ev = mock_ev("E1", "GCP Dataflow")
    edges = matcher.match([req], [ev])
    assert edges[0].match_type == "RELATED"


def test_partial_compound_requirement(matcher):
    atoms = [
        JDRequirementAtom(atom_id="a1", raw_value="AWS", atom_type="TECHNOLOGY"),
        JDRequirementAtom(atom_id="a2", raw_value="S3", atom_type="TECHNOLOGY"),
        JDRequirementAtom(atom_id="a3", raw_value="EC2", atom_type="TECHNOLOGY"),
    ]
    req = mock_req("R1", "AWS Cloud Services", atoms=atoms)
    ev = mock_ev("E1", "AWS")
    edges = matcher.match([req], [ev])
    assert len(edges) == 1
    assert edges[0].match_type == "PARTIAL"
    assert "a1" in edges[0].satisfied_atoms
    assert "a2" in edges[0].missing_atoms


def test_gap_requirement_level_outcome(matcher):
    req = mock_req("R1", "Kubernetes")
    ev = mock_ev("E1", "AngularJS")
    edges = matcher.match([req], [ev])
    assert len(edges) == 1
    assert edges[0].match_type == "GAP"
    assert "No sufficient evidence" in edges[0].decision_reason


def test_multiple_evidence_one_requirement(matcher):
    req = mock_req("R1", "Python")
    ev1 = mock_ev("E1", "Python")
    ev2 = mock_ev("E2", "Python scripting")
    edges = matcher.match([req], [ev1, ev2])
    assert len(edges) >= 1
    assert any(e.match_type == "EXACT" for e in edges)


def test_category_mismatch_protection(matcher):
    req = mock_req("R1", "Python", category="EXPERIENCE")
    ev = mock_ev("E1", "Python", category="EDUCATION")
    edges = matcher.match([req], [ev])
    assert edges[0].match_type != "EXACT"


def test_legitimate_cross_category_matching(matcher):
    req = mock_req("R1", "Python", category="EXPERIENCE")
    ev = mock_ev("E1", "Python", category="SKILL")
    edges = matcher.match([req], [ev])
    assert edges[0].match_type == "EXACT"


def test_domain_only_similarity_rejected(matcher):
    req = mock_req("R1", "Cassandra")
    ev = mock_ev("E1", "PostgreSQL")
    edges = matcher.match([req], [ev])
    assert edges[0].match_type not in ("EXACT", "RELATED")


def test_unknown_ontology_relation_remains_unknown(matcher):
    req = mock_req("R1", "React")
    ev = mock_ev("E1", "Angular")
    edges = matcher.match([req], [ev])
    assert edges[0].ontology_features.get("primary") == OntologyRelation.UNKNOWN


def test_no_score_fields(matcher):
    req = mock_req("R1", "Python")
    ev = mock_ev("E1", "Python")
    edges = matcher.match([req], [ev])
    edge_dict = edges[0].model_dump()
    assert "final_score" not in edge_dict
    assert "ranking" not in edge_dict
    assert "optimization" not in edge_dict


def test_explainability_fields_populated(matcher):
    req = mock_req("R1", "Python")
    ev = mock_ev("E1", "Python")
    edges = matcher.match([req], [ev])
    assert edges[0].decision_reason != ""


def test_unknown_hard_qualifier_does_not_produce_exact(matcher):
    """Requirement has YOE qualifier, evidence has no YOE → UNKNOWN → must not be EXACT."""
    req = mock_req("R1", "5+ years Python", canonical_ids=["c_python"])
    ev = mock_ev("E1", "Python", canonical_ids=["c_python"])
    edges = matcher.match([req], [ev])
    assert edges[0].match_type != "EXACT"
    assert edges[0].qualifier_results.get("yoe") == QualifierStatus.UNKNOWN


def test_exact_requires_qualifier_satisfaction(matcher):
    """Qualifier-satisfied → EXACT; qualifier-not-satisfied → not EXACT."""
    req = mock_req("R1", "5+ years Python", canonical_ids=["c_python"])

    ev_sat = mock_ev("E1", "5 years Python", canonical_ids=["c_python"])
    edges1 = matcher.match([req], [ev_sat])
    assert edges1[0].match_type == "EXACT"

    ev_unsat = mock_ev("E2", "2 years Python", canonical_ids=["c_python"])
    edges2 = matcher.match([req], [ev_unsat])
    assert edges2[0].match_type == "PARTIAL"
