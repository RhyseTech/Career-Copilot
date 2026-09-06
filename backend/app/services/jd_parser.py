from .skill_extractor import SkillExtractor
from .experience_parser import ExperienceParser
from typing import Dict

class JDParser:
    def __init__(self):
        self.skill_extractor = SkillExtractor()
        self.exp_parser = ExperienceParser()

    def parse_jd(self, jd_text: str) -> Dict:
        """
        Extracts required skills and experience from Job Description.
        """
        # For MVP, we use the same skill extractor and experience parser
        # In a real system, we'd look specifically for "Required:" vs "Preferred:"
        
        extracted_skills = self.skill_extractor.extract_skills(jd_text)
        
        # JD experience often says "3-5 years" or "5+ years"
        # We can reuse the experience parser's date logic or use a simpler regex
        import re
        exp_match = re.search(r'(\d+)(?:\s*-\s*\d+)?\s*(?:\+|years?)', jd_text, re.IGNORECASE)
        required_years = int(exp_match.group(1)) if exp_match else 0
        
        return {
            "required_skills": extracted_skills,
            "required_experience_years": required_years,
            "raw_text": jd_text
        }
