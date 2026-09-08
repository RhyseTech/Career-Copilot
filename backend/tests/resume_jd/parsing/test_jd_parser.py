import pytest
from unittest.mock import patch, MagicMock
from app.resume_jd.parsing.jd.hybrid_parser import HybridJDParser
from app.resume_jd.parsing.jd.sectionizer import Sectionizer
from app.resume_jd.models.canonical_jd import CanonicalJD

@pytest.fixture
def parser():
    return HybridJDParser()

def test_sectionizer():
    raw_text = """
    Job Summary
    We are looking for a Data Engineer.
    
    Responsibilities
    - Build data pipelines in AWS.
    
    Required Qualifications
    - Python experience
    """
    sectionizer = Sectionizer()
    sections = sectionizer.extract_sections(raw_text)
    
    assert "Job Summary" in sections
    assert "Responsibilities" in sections
    assert "Required Qualifications" in sections
    assert "Build data pipelines" in sections["Responsibilities"]

@patch("app.resume_jd.parsing.jd.llm_extractor.LLMExtractor.extract_requirements")
def test_hybrid_parser_valid_extraction(mock_extract, parser):
    raw_text = "Responsibilities\nWe need someone with AWS Glue and Python."
    
    # Mock LLM returning perfect extractions with exact source_span matches
    mock_extract.return_value = [
        {
            "category": "SKILL",
            "requirement_type": "REQUIRED",
            "raw_text": "AWS Glue",
            "source_span": "AWS Glue"
        },
        {
            "category": "SKILL",
            "requirement_type": "REQUIRED",
            "raw_text": "Python",
            "source_span": "Python"
        }
    ]
    
    jd = parser.parse(raw_text, "Data Engineer")
    
    assert isinstance(jd, CanonicalJD)
    assert len(jd.requirements) == 2
    assert jd.requirements[0].raw_text == "AWS Glue"
    assert jd.requirements[0].source_span == "AWS Glue"

@patch("app.resume_jd.parsing.jd.llm_extractor.LLMExtractor.extract_requirements")
def test_hybrid_parser_anti_hallucination(mock_extract, parser):
    raw_text = "Responsibilities\nWe need someone with AWS Glue and Python."
    
    # Mock LLM hallucinating a skill that isn't in the text
    mock_extract.return_value = [
        {
            "category": "SKILL",
            "requirement_type": "REQUIRED",
            "raw_text": "AWS Glue",
            "source_span": "AWS Glue"
        },
        {
            "category": "SKILL",
            "requirement_type": "REQUIRED",
            "raw_text": "Apache Spark", # LLM inferred this
            "source_span": "Apache Spark" # Hallucinated span
        }
    ]
    
    jd = parser.parse(raw_text, "Data Engineer")
    
    # Validation logic should reject "Apache Spark" because the string isn't in raw_text
    assert len(jd.requirements) == 1
    assert jd.requirements[0].raw_text == "AWS Glue"
