from typing import List, Dict
from rapidfuzz import process, fuzz

class SkillExtractor:
    def __init__(self):
        # A simplified canonical skill dictionary for MVP
        self.canonical_skills = [
            "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Ruby", "Go", "Rust",
            "SQL", "NoSQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
            "React", "Angular", "Vue", "Next.js", "Node.js", "Express",
            "FastAPI", "Django", "Flask", "Spring Boot",
            "Machine Learning", "Data Analysis", "ETL", "PySpark", "Databricks", "Power BI",
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
                
        # Basic Fuzzy match for phrases or misspellings (using token_set_ratio > 85 as per research)
        # For a full production system, we'd chunk the text better.
        for skill in self.canonical_skills:
            if skill not in extracted:
                match = process.extractOne(
                    skill.lower(), 
                    words, 
                    scorer=fuzz.token_set_ratio, 
                    score_cutoff=85
                )
                if match:
                    extracted.add(skill)
                    
        return list(extracted)
