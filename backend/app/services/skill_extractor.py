from typing import List, Dict
from rapidfuzz import process, fuzz
import warnings

class SkillExtractor:
    def __init__(self):
        warnings.warn("SkillExtractor is deprecated and causes severe capability loss. Use structured_data instead.", DeprecationWarning, stacklevel=2)
        # A simplified canonical skill dictionary for MVP
        self.canonical_skills = [
            "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Ruby", "Go", "Rust",
            "SQL", "NoSQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
            "React", "Angular", "Vue", "Next.js", "Node.js", "Express",
            "FastAPI", "Django", "Flask", "Spring Boot",
            "Machine Learning", "Data Analysis", "Data Engineering", "ETL", "PySpark", "Databricks", "Power BI",
            "Agile", "Scrum", "Git", "CI/CD"
        ]
        self.lower_canonical = {s.lower(): s for s in self.canonical_skills}

    def extract_skills(self, text: str) -> List[str]:
        """
        Extracts skills using exact match and fuzzy matching.
        """
        extracted = set()
        words = set(text.lower().replace(',', ' ').replace(';', ' ').replace('\n', ' ').split())
        
        # Exact match
        for word in words:
            if word in self.lower_canonical:
                extracted.add(self.lower_canonical[word])
                
        # Basic Fuzzy match against the entire text chunk instead of single words
        # This prevents "data" from matching "data analysis" with 100% score.
        text_lower = text.lower()
        for skill in self.canonical_skills:
            if skill not in extracted:
                # We use token_set_ratio against the whole text
                score = fuzz.token_set_ratio(skill.lower(), text_lower)
                if score >= 85:
                    extracted.add(skill)
                    
        return list(extracted)
