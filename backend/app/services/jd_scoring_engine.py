import warnings
from typing import Dict, List
from .semantic_engine import SemanticEngine

class JDScoringEngine:
    def __init__(self):
        warnings.warn("JDScoringEngine is deprecated and should not be used as the authoritative score.", DeprecationWarning, stacklevel=2)
        self.semantic_engine = SemanticEngine()
        self.STABILITY_CONSTANT = 100 # Represents C in the formula, scaled to 100

    def calculate_match_score(self, resume_data: Dict, jd_data: Dict) -> Dict:
        """
        Calculates Job Match Score using Hybrid Formula: 
        Score = 0.55*Sk + 0.25*Se + 0.15*So + 0.05*C - Penalties
        """
        res_skills = set(resume_data.get("skills", []))
        jd_skills = set(jd_data.get("required_skills", []))
        
        # 1. Skill Match (Sk) - 55%
        if not jd_skills:
            sk_score = 100.0 # If JD has no skills, assume 100% match
        else:
            matched_skills = res_skills.intersection(jd_skills)
            sk_score = (len(matched_skills) / len(jd_skills)) * 100.0
            
        # 2. Experience Score (Se) - 25%
        res_exp = resume_data.get("experience", {}).get("total_years", 0)
        jd_exp = jd_data.get("required_experience_years", 0)
        
        if jd_exp == 0:
            se_score = 100.0
        else:
            if res_exp >= jd_exp:
                se_score = 100.0
            else:
                se_score = max(0, 100.0 - 20 * (jd_exp - res_exp)) # Deduct 20% per year missing
                
        # 3. Other Factors (Semantic Similarity) (So) - 15%
        res_text = resume_data.get("parsed_data", {}).get("raw_text", "")
        jd_text = jd_data.get("raw_text", "")
        
        similarity = self.semantic_engine.calculate_similarity(res_text, jd_text)
        so_score = similarity * 100.0
        
        # 4. Penalties
        penalties = 0.0
        if res_exp > jd_exp + 10 and jd_exp > 0: # Overqualified by 10+ years
            penalties += 10.0
            
        # Final calculation
        final_score = (0.55 * sk_score) + (0.25 * se_score) + (0.15 * so_score) + (0.05 * self.STABILITY_CONSTANT) - penalties
        final_score = max(0.0, min(100.0, final_score))
        
        # Detailed Checks Generation for Premium UI
        detailed_checks = {
            "Match Analysis": [],
            "Experience": []
        }
        
        # Skill Match Check
        missing_skills = list(jd_skills - res_skills)
        if sk_score >= 80:
            detailed_checks["Match Analysis"].append({"name": "Skill Match", "status": "pass", "score": sk_score, "message": f"Strong skill alignment! You match {len(matched_skills)} out of {len(jd_skills)} required skills."})
        else:
            detailed_checks["Match Analysis"].append({"name": "Skill Match", "status": "warn" if sk_score >= 50 else "fail", "score": sk_score, "message": f"Missing {len(missing_skills)} key skills from the job description (e.g., {', '.join(missing_skills[:3])})."})
            
        # Experience Check
        if se_score == 100:
            detailed_checks["Experience"].append({"name": "Required Experience", "status": "pass", "score": 100, "message": f"You meet or exceed the required {jd_exp} years of experience."})
        else:
            detailed_checks["Experience"].append({"name": "Required Experience", "status": "fail", "score": se_score, "message": f"You have {res_exp} years of experience, but the job requires {jd_exp} years."})
            
        # Semantic Match Check
        if so_score >= 70:
            detailed_checks["Match Analysis"].append({"name": "Semantic Context Match", "status": "pass", "score": so_score, "message": "High semantic similarity between your resume and the JD."})
        else:
            detailed_checks["Match Analysis"].append({"name": "Semantic Context Match", "status": "warn", "score": so_score, "message": "The overall context and phrasing of your resume could be tailored closer to the JD language."})

        return {
            "overall_match_score": round(final_score, 2),
            "breakdown": {
                "skill_match_score": round(sk_score, 2),
                "experience_match_score": round(se_score, 2),
                "semantic_match_score": round(so_score, 2),
                "penalties": round(penalties, 2)
            },
            "missing_skills": missing_skills,
            "matched_skills": list(matched_skills),
            "detailed_checks": detailed_checks
        }
