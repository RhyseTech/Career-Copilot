import pytest
import os
from app.resume_jd.matching.normalizer import SkillNormalizer
from app.resume_jd.adapters.resume_adapter import ResumeAdapter
from app.resume_jd.adapters.jd_adapter import JDAdapter
from app.resume_jd.models.canonical_models import CanonicalResume
from app.resume_jd.models.canonical_jd import CanonicalJD

def test_alias_normalization():
    normalizer = SkillNormalizer()
    assert normalizer.normalize("Amazon Web Services") == "AWS"
    assert normalizer.normalize("aws") == "AWS"

def test_multi_word_normalization():
    normalizer = SkillNormalizer()
    assert normalizer.normalize("Amazon Web Services Glue") == "AWS Glue"
    assert normalizer.normalize("aws glue") == "AWS Glue"

def test_acronym_normalization():
    normalizer = SkillNormalizer()
    assert normalizer.normalize("k8s") == "Kubernetes"
    assert normalizer.normalize("gcp") == "GCP"

def test_no_aggressive_normalization():
    normalizer = SkillNormalizer()
    # AWS Glue must NOT become Spark
    assert normalizer.normalize("AWS Glue") != "Spark"
    # Unknown value remains unchanged (just title cased as per our conservative heuristic)
    assert normalizer.normalize("Unknown Tech Stack 123") == "Unknown Tech Stack 123"

def test_resume_adapter_produces_canonical():
    adapter = ResumeAdapter()
    resume_path = os.path.join(os.path.dirname(__file__), "../../../../data/resume/resume.pdf")
    if os.path.exists(resume_path):
        canonical = adapter.process_file(resume_path, "resume.pdf")
        assert isinstance(canonical, CanonicalResume)
        assert len(canonical.items) > 0
        
        # Test preservation properties
        item = canonical.items[0]
        assert hasattr(item, "raw_value")
        assert hasattr(item, "normalized_value")
        assert hasattr(item, "provenance")
        assert hasattr(item, "category")
        assert item.provenance == "EXTRACTED"
        assert item.id.startswith("res_")

from app.resume_jd.models.canonical_jd import Requirement

def test_jd_adapter_produces_canonical():
    adapter = JDAdapter()
    
    # Mock the Phase 1 parser output to avoid LLM dependency during unit test
    mock_req1 = Requirement(
        requirement_id="req_1",
        requirement_type="REQUIRED",
        category="SKILL",
        raw_text="Python",
        source_span="Python",
        source_section="Requirements",
        confidence=0.9,
        provenance="EXTRACTED",
        weight=1.5
    )
    mock_req2 = Requirement(
        requirement_id="req_2",
        requirement_type="REQUIRED",
        category="SKILL",
        raw_text="Amazon Web Services Glue",
        source_span="Amazon Web Services Glue",
        source_section="Requirements",
        confidence=0.9,
        provenance="EXTRACTED",
        weight=1.5
    )
    
    mock_jd = CanonicalJD(
        jd_id="jd_123",
        content_hash="hash",
        job_title="Data Engineer",
        raw_text="Required Skills: Python and Amazon Web Services Glue.",
        requirements=[mock_req1, mock_req2]
    )
    
    # Monkey-patch the parser
    adapter.parser.parse = lambda text, title=None: mock_jd
    
    canonical = adapter.adapt("Required Skills: Python and Amazon Web Services Glue.", "Data Engineer")
    
    assert isinstance(canonical, CanonicalJD)
    assert len(canonical.items) > 0
    
    # Check that AWS Glue was properly extracted and normalized from "Amazon Web Services Glue"
    normalized_skills = [i.normalized_value for i in canonical.items]
    assert "Python" in normalized_skills
    assert "AWS Glue" in normalized_skills
    
    item = canonical.items[0]
    assert hasattr(item, "raw_value")
    assert hasattr(item, "normalized_value")
    assert item.provenance == "EXTRACTED"
    assert item.id.startswith("jd_")
