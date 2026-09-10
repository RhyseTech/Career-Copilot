import unittest
from unittest.mock import patch, MagicMock
from app.resume_jd.pipelines.phase_03_extractor import Phase3Extractor
from app.resume_jd.models.canonical_models import CanonicalResume
import json

class TestPhase3Validation(unittest.TestCase):
    @patch.object(Phase3Extractor, '_call_llm')
    def test_exhaustive_evidence_extraction(self, mock_call_llm):
        raw_resume_text = """
SUMMARY:
Data Engineer with experience in Python and SQL.

SKILLS:
Python
SQL
Spark
Databricks
AWS
FastAPI

EXPERIENCE:
Built ETL pipelines using Python and Spark.
Designed data pipelines using Databricks.
Developed REST APIs using FastAPI.
Implemented CI/CD using GitHub Actions.

CERTIFICATIONS:
AWS Certified Data Engineer Associate
"""
        mock_response = {
            "evidence": [
                {
                    "raw_value": "Python",
                    "evidence_text": "Data Engineer with experience in Python and SQL.",
                    "category": "SKILL",
                    "source_section": "SUMMARY",
                    "source_text": "Data Engineer with experience in Python and SQL."
                },
                {
                    "raw_value": "SQL",
                    "evidence_text": "Data Engineer with experience in Python and SQL.",
                    "category": "SKILL",
                    "source_section": "SUMMARY",
                    "source_text": "Data Engineer with experience in Python and SQL."
                },
                {
                    "raw_value": "Python",
                    "evidence_text": "Python",
                    "category": "SKILL",
                    "source_section": "SKILLS",
                    "source_text": "Python"
                },
                {
                    "raw_value": "SQL",
                    "evidence_text": "SQL",
                    "category": "SKILL",
                    "source_section": "SKILLS",
                    "source_text": "SQL"
                },
                {
                    "raw_value": "Spark",
                    "evidence_text": "Spark",
                    "category": "SKILL",
                    "source_section": "SKILLS",
                    "source_text": "Spark"
                },
                {
                    "raw_value": "Databricks",
                    "evidence_text": "Databricks",
                    "category": "SKILL",
                    "source_section": "SKILLS",
                    "source_text": "Databricks"
                },
                {
                    "raw_value": "AWS",
                    "evidence_text": "AWS",
                    "category": "SKILL",
                    "source_section": "SKILLS",
                    "source_text": "AWS"
                },
                {
                    "raw_value": "FastAPI",
                    "evidence_text": "FastAPI",
                    "category": "SKILL",
                    "source_section": "SKILLS",
                    "source_text": "FastAPI"
                },
                {
                    "raw_value": "Python",
                    "evidence_text": "Built ETL pipelines using Python and Spark.",
                    "action": "Built",
                    "surrounding_context": "ETL pipelines",
                    "category": "TECHNOLOGY",
                    "source_section": "EXPERIENCE",
                    "source_text": "Built ETL pipelines using Python and Spark."
                },
                {
                    "raw_value": "Spark",
                    "evidence_text": "Built ETL pipelines using Python and Spark.",
                    "action": "Built",
                    "surrounding_context": "ETL pipelines",
                    "category": "TECHNOLOGY",
                    "source_section": "EXPERIENCE",
                    "source_text": "Built ETL pipelines using Python and Spark."
                },
                {
                    "raw_value": "ETL pipelines",
                    "evidence_text": "Built ETL pipelines using Python and Spark.",
                    "action": "Built",
                    "category": "EXPERIENCE",
                    "source_section": "EXPERIENCE",
                    "source_text": "Built ETL pipelines using Python and Spark."
                },
                {
                    "raw_value": "Databricks",
                    "evidence_text": "Designed data pipelines using Databricks.",
                    "action": "Designed",
                    "surrounding_context": "data pipelines",
                    "category": "TECHNOLOGY",
                    "source_section": "EXPERIENCE",
                    "source_text": "Designed data pipelines using Databricks."
                },
                {
                    "raw_value": "FastAPI",
                    "evidence_text": "Developed REST APIs using FastAPI.",
                    "action": "Developed",
                    "surrounding_context": "REST APIs",
                    "category": "TECHNOLOGY",
                    "source_section": "EXPERIENCE",
                    "source_text": "Developed REST APIs using FastAPI."
                },
                {
                    "raw_value": "API development",
                    "evidence_text": "Developed REST APIs using FastAPI.",
                    "action": "Developed",
                    "category": "EXPERIENCE",
                    "source_section": "EXPERIENCE",
                    "source_text": "Developed REST APIs using FastAPI."
                },
                {
                    "raw_value": "CI/CD",
                    "evidence_text": "Implemented CI/CD using GitHub Actions.",
                    "action": "Implemented",
                    "category": "EXPERIENCE",
                    "source_section": "EXPERIENCE",
                    "source_text": "Implemented CI/CD using GitHub Actions."
                },
                {
                    "raw_value": "GitHub Actions",
                    "evidence_text": "Implemented CI/CD using GitHub Actions.",
                    "action": "Implemented",
                    "category": "TECHNOLOGY",
                    "source_section": "EXPERIENCE",
                    "source_text": "Implemented CI/CD using GitHub Actions."
                },
                {
                    "raw_value": "AWS Certified Data Engineer Associate",
                    "evidence_text": "AWS Certified Data Engineer Associate",
                    "category": "CERTIFICATION",
                    "source_section": "CERTIFICATIONS",
                    "source_text": "AWS Certified Data Engineer Associate"
                },
                {
                    "raw_value": "Hallucinated Skill",
                    "evidence_text": "Some made up text",
                    "category": "SKILL",
                    "source_section": "EXPERIENCE",
                    "source_text": "I used Kubernetes." # Not in raw_text
                }
            ]
        }
        
        mock_call_llm.return_value = mock_response
        
        extractor = Phase3Extractor()
        canonical = CanonicalResume(resume_id="test_res_1", file_name="test.pdf", items=[])
        
        evidence_list = extractor.process_resume(canonical, raw_resume_text)
        
        # Verify hallucinated text is rejected
        extracted_raw_values = [e.raw_value for e in evidence_list]
        self.assertNotIn("Hallucinated Skill", extracted_raw_values)
        
        # Verify legitimate evidence is retained
        self.assertIn("Python", extracted_raw_values)
        self.assertIn("SQL", extracted_raw_values)
        self.assertIn("Spark", extracted_raw_values)
        self.assertIn("Databricks", extracted_raw_values)
        self.assertIn("AWS", extracted_raw_values)
        self.assertIn("FastAPI", extracted_raw_values)
        self.assertIn("ETL pipelines", extracted_raw_values)
        self.assertIn("CI/CD", extracted_raw_values)
        self.assertIn("AWS Certified Data Engineer Associate", extracted_raw_values)
        self.assertIn("GitHub Actions", extracted_raw_values)
        
        # Verify duplicate concepts are preserved if from distinct sources
        python_evs = [e for e in evidence_list if e.raw_value == "Python"]
        self.assertEqual(len(python_evs), 3)
        self.assertTrue(any(e.source_section == "SUMMARY" for e in python_evs))
        self.assertTrue(any(e.source_section == "SKILLS" for e in python_evs))
        self.assertTrue(any(e.source_section == "EXPERIENCE" for e in python_evs))
        
        # Verify proper category tagging
        aws_cert = next(e for e in evidence_list if "AWS Certified Data Engineer Associate" in e.raw_value)
        self.assertEqual(aws_cert.category, "CERTIFICATION")
        self.assertEqual(aws_cert.source_section, "CERTIFICATIONS")

if __name__ == '__main__':
    unittest.main()
