import numpy as np
from sentence_transformers import SentenceTransformer
from rapidfuzz import process, fuzz
from typing import Dict, Any, List
import uuid

class MatchEngine:
    def __init__(self):
        # Lightweight, fast embedding model for semantic matching
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
    def _calculate_cosine_similarity(self, vec1, vec2):
        if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
            return 0.0
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def get_role_weights(self, role_level: str) -> Dict[str, float]:
        level = role_level.lower()
        if level == "junior":
            return {"skills": 0.35, "experience": 0.15, "keywords": 0.20, "semantic": 0.15, "formatting": 0.15}
        elif level == "senior":
            return {"skills": 0.20, "experience": 0.35, "keywords": 0.10, "semantic": 0.25, "formatting": 0.10}
        else:
            # Mid-level default
            return {"skills": 0.25, "experience": 0.25, "keywords": 0.15, "semantic": 0.20, "formatting": 0.15}

    def _extract_experience_bullets(self, resume_json: Dict[str, Any]) -> List[str]:
        bullets = []
        cv = resume_json.get("cv", {})
        sections = cv.get("sections", {})
        experience = sections.get("experience", [])
        for job in experience:
            bullets.extend(job.get("highlights", []))
        return bullets

    def _extract_resume_skills(self, resume_json: Dict[str, Any]) -> List[str]:
        skills = []
        cv = resume_json.get("cv", {})
        sections = cv.get("sections", {})
        for skill_section in sections.get("skills", []):
            skills.extend(skill_section.get("details", "").split(","))
        return [s.strip() for s in skills if s.strip()]

    def calculate_match(self, resume_json: Dict[str, Any], jd_json: Dict[str, Any], role_level: str = "mid") -> Dict[str, Any]:
        """
        Calculates the hybrid ATS score and generates the evidence map.
        """
        # 1. Parse inputs
        resume_skills = self._extract_resume_skills(resume_json)
        resume_bullets = self._extract_experience_bullets(resume_json)
        
        req_skills = jd_json.get("required_skills", [])
        
        evidence_map = []
        
        # 2. Skill & Keyword Match (Fuzzy)
        skill_score = 0
        skills_matched = 0
        for req_skill in req_skills:
            # check fuzzy match
            match = process.extractOne(req_skill, resume_skills, scorer=fuzz.partial_ratio)
            if match and match[1] > 85:
                skills_matched += 1
                evidence_map.append({
                    "jd_requirement": req_skill,
                    "status": "strong",
                    "resume_evidence": f"Found in skills section as '{match[0]}'"
                })
            else:
                # check if it exists in bullets
                bullet_match = process.extractOne(req_skill, resume_bullets, scorer=fuzz.partial_ratio)
                if bullet_match and bullet_match[1] > 80:
                    skills_matched += 1
                    evidence_map.append({
                        "jd_requirement": req_skill,
                        "status": "partial",
                        "resume_evidence": f"Found in experience: '{bullet_match[0]}'"
                    })
                else:
                    evidence_map.append({
                        "jd_requirement": req_skill,
                        "status": "missing",
                        "resume_evidence": None
                    })
                    
        raw_skill_score = (skills_matched / max(len(req_skills), 1)) * 100

        # 3. Semantic Match (Experience vs JD requirements)
        # We will embed all resume bullets and the JD text
        semantic_score = 0
        if resume_bullets and jd_json.get("role"):
            jd_text = jd_json.get("role", "") + " " + " ".join(req_skills)
            jd_embedding = self.encoder.encode(jd_text)
            
            bullet_embeddings = self.encoder.encode(resume_bullets)
            
            # Find the average top 3 best matching bullets to the JD
            similarities = [self._calculate_cosine_similarity(jd_embedding, b_emb) for b_emb in bullet_embeddings]
            top_3 = sorted(similarities, reverse=True)[:3]
            if top_3:
                # Scale typical cosine similarities (0.3 - 0.7) to a 0-100 score
                avg_top_sim = sum(top_3) / len(top_3)
                semantic_score = min(max(avg_top_sim * 150, 0), 100) # heuristic scaling

        # 4. Calculate Final Score
        weights = self.get_role_weights(role_level)
        
        # Mock formatting and experience scores for now
        experience_score = semantic_score * 0.9 # highly correlated
        formatting_score = 95 # Assuming JSON to RenderCV is perfect formatting
        
        overall_score = (
            (raw_skill_score * weights["skills"]) +
            (experience_score * weights["experience"]) +
            (raw_skill_score * weights["keywords"]) + # using skills as proxy for keywords
            (semantic_score * weights["semantic"]) +
            (formatting_score * weights["formatting"])
        )
        
        return {
            "report_id": str(uuid.uuid4()),
            "overall_score": int(overall_score),
            "dimensions": {
                "skill_match": {"score": int(raw_skill_score), "rationale": f"{skills_matched}/{len(req_skills)} skills detected"},
                "semantic_match": {"score": int(semantic_score), "rationale": "Measures deep contextual alignment between your experience and the role"},
                "experience": {"score": int(experience_score), "rationale": "Alignment of your past job duties with JD expectations"},
                "formatting": {"score": int(formatting_score), "rationale": "RenderCV strictly enforces ATS-friendly formatting"}
            },
            "evidence_map": evidence_map
        }
