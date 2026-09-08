from typing import List

class SkillNormalizer:
    def __init__(self):
        # Base mappings
        self.aliases = {
            "amazon web services": "AWS",
            "aws": "AWS",
            "amazon web services glue": "AWS Glue",
            "aws glue": "AWS Glue",
            "k8s": "Kubernetes",
            "kubernetes": "Kubernetes",
            "gcp": "GCP",
            "google cloud platform": "GCP",
            "ml": "Machine Learning",
            "js": "JavaScript",
            "ts": "TypeScript",
            "node": "Node.js",
            "reactjs": "React",
            "react.js": "React",
            "vuejs": "Vue",
            "postgresql": "PostgreSQL",
            "postgres": "PostgreSQL",
            "cpp": "C++",
            "c++": "C++",
            "nlp": "Natural Language Processing",
            "cv": "Computer Vision",
            "artificial intelligence": "AI"
        }
        
        # We also maintain a canonical list
        self.canonical_skills = set(self.aliases.values()).union({
            "Python", "Java", "Ruby", "Go", "Rust", "SQL", "NoSQL",
            "MySQL", "MongoDB", "Redis", "Azure", "Docker", "Terraform",
            "Angular", "Next.js", "Express", "FastAPI", "Django", "Flask",
            "Spring Boot", "Data Analysis", "Data Engineering", "ETL", "PySpark", "Databricks",
            "Power BI", "Agile", "Scrum", "Git", "CI/CD", "Linux", "Ubuntu", "CentOS"
        })
        
        self.lower_canonical = {s.lower(): s for s in self.canonical_skills}

    def normalize(self, raw_skill: str) -> str:
        """
        Maps a raw string to its canonical form if possible.
        """
        clean = str(raw_skill).strip().lower()
        
        if clean in self.aliases:
            return self.aliases[clean]
            
        if clean in self.lower_canonical:
            return self.lower_canonical[clean]
            
        # If no mapping found, Title Case it and treat as valid canonical
        # (This is conservative: we don't drop unknown skills)
        return str(raw_skill).strip().title()

    def normalize_list(self, skills: List[str]) -> List[str]:
        """
        Normalizes a list of skills and removes duplicates.
        """
        normalized_set = {self.normalize(s) for s in skills if str(s).strip()}
        return list(normalized_set)
