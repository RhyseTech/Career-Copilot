import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(__file__))

from app.services.skill_extractor import SkillExtractor
from app.services.experience_parser import ExperienceParser
from app.services.scoring_engine import ScoringEngine
from app.services.jd_parser import JDParser
from app.services.jd_scoring_engine import JDScoringEngine

def test_system():
    print("--- Testing Skill Extractor ---")
    skill_extractor = SkillExtractor()
    skills = skill_extractor.extract_skills("I am experienced in Python, Sql, and PySprk.")
    print(f"Extracted Skills: {skills}")
    assert "Python" in skills
    assert "SQL" in skills
    assert "PySpark" in skills # Fuzzy match check
    
    print("\n--- Testing Experience Parser ---")
    exp_parser = ExperienceParser()
    exp = exp_parser.parse_experience("Data Engineer\nJan 2018 - Present")
    print(f"Experience: {exp}")
    assert exp["total_years"] >= 6
    
    print("\n--- Testing Scoring Engine (Resume Only) ---")
    scoring_engine = ScoringEngine()
    parsed_data = {
        "raw_text": "Experienced Python developer " * 100, # Mocking 300 words
        "sections": {
            "summary": "Experienced Python developer.",
            "experience": "Jan 2018 - Present. Increased sales by 50%.",
            "skills": "Python, SQL",
            "education": "BSc Computer Science"
        }
    }
    score = scoring_engine.calculate_resume_score(parsed_data, skills, exp)
    print(f"Resume Score: {score}")
    assert score["overall_score"] > 50
    
    print("\n--- Testing JD Match ---")
    jd_parser = JDParser()
    jd_data = jd_parser.parse_jd("We need a Python developer with SQL skills. 5+ years experience required. Preferred: Docker.")
    print(f"JD Data: {jd_data}")
    
    jd_scorer = JDScoringEngine()
    match_score = jd_scorer.calculate_match_score(
        {"parsed_data": parsed_data, "skills": skills, "experience": exp},
        jd_data
    )
    print(f"Match Score: {match_score}")
    assert match_score["overall_match_score"] > 50
    
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    test_system()
