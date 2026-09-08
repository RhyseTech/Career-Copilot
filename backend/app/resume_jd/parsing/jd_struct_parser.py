import re
import uuid
from typing import List, Dict, Any
from app.services.skill_extractor import SkillExtractor
from app.resume_jd.matching.normalizer import SkillNormalizer

class JDStructParser:
    def __init__(self):
        self.skill_extractor = SkillExtractor()
        self.normalizer = SkillNormalizer()

    def parse(self, jd_text: str) -> List[Dict[str, Any]]:
        """
        Splits JD into lines/bullets and extracts structured fields per line.
        Returns List of requirement objects.
        """
        requirements = []
        # Split by newlines or bullet points
        lines = re.split(r'\n|•|- ', jd_text)
        
        for line in lines:
            text = line.strip()
            # Ignore very short lines or common headers
            if len(text) < 10 or text.lower() in ["requirements", "qualifications", "what you'll do"]:
                continue
                
            raw_skills = self.skill_extractor.extract_skills(text)
            canonical_skills = self.normalizer.normalize_list(raw_skills)
            
            # Simple heuristic for required vs preferred
            is_preferred = bool(re.search(r'\b(preferred|plus|nice to have|optional)\b', text.lower()))
            
            # Simple heuristic for type
            req_type = "technical_skill" if len(canonical_skills) > 0 else "general_requirement"
            if re.search(r'\b(degree|bachelor|master|phd|diploma)\b', text.lower()):
                req_type = "education"
                
            requirements.append({
                "requirement_id": f"req_{uuid.uuid4().hex[:8]}",
                "text": text,
                "type": req_type,
                "required": not is_preferred,
                "canonical_skills": canonical_skills
            })
            
        return requirements
