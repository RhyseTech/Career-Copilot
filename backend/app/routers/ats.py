from fastapi import APIRouter, HTTPException
from typing import Dict
from ..services.parser import ResumeParser
from ..services.skill_extractor import SkillExtractor
from ..services.experience_parser import ExperienceParser
from ..services.scoring_engine import ScoringEngine
import os

router = APIRouter(prefix="/ats", tags=["ats"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")

@router.post("/analyze")
async def analyze_resume(resume_id: str, filename: str) -> Dict:
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Resume file not found")
        
    try:
        # Parse
        parser = ResumeParser()
        parsed_data = parser.parse_resume(file_path)
        
        # Extract Skills
        skill_extractor = SkillExtractor()
        extracted_skills = skill_extractor.extract_skills(parsed_data["raw_text"])
        
        # Parse Experience
        exp_parser = ExperienceParser()
        experience_data = exp_parser.parse_experience(parsed_data["sections"].get("experience", ""))
        
        # Score
        scoring_engine = ScoringEngine()
        score_result = scoring_engine.calculate_resume_score(parsed_data, extracted_skills, experience_data)
        
        return {
            "resume_id": resume_id,
            "parsed_data": parsed_data,
            "skills": extracted_skills,
            "experience": experience_data,
            "score": score_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")

from pydantic import BaseModel
class MatchRequest(BaseModel):
    resume_id: str
    filename: str
    jd_text: str

from ..services.jd_parser import JDParser
from ..services.jd_scoring_engine import JDScoringEngine

@router.post("/match")
async def match_resume_to_jd(request: MatchRequest) -> Dict:
    file_path = os.path.join(UPLOAD_DIR, request.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Resume file not found")
        
    try:
        # Resume Data
        parser = ResumeParser()
        parsed_data = parser.parse_resume(file_path)
        skill_extractor = SkillExtractor()
        extracted_skills = skill_extractor.extract_skills(parsed_data["raw_text"])
        exp_parser = ExperienceParser()
        experience_data = exp_parser.parse_experience(parsed_data["sections"].get("experience", ""))
        resume_data = {
            "parsed_data": parsed_data,
            "skills": extracted_skills,
            "experience": experience_data
        }
        
        # JD Data
        jd_parser = JDParser()
        jd_data = jd_parser.parse_jd(request.jd_text)
        
        # Match Score
        jd_scoring = JDScoringEngine()
        match_result = jd_scoring.calculate_match_score(resume_data, jd_data)
        
        return {
            "resume_id": request.resume_id,
            # Keep the exact parsed source with the match response.  The client uses
            # this as the canonical resume handed to the optimizer; omitting it made
            # the UI fall back to a previous session's resume.
            "parsed_data": parsed_data,
            "match_result": match_result,
            "jd_analysis": jd_data
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error matching resume to JD: {str(e)}")

from typing import List
from ..services.llm_optimizer import LLMOptimizer

class DiagnoseRequest(BaseModel):
    resume_text: str
    lagging_fields: List[str]

@router.post("/diagnose")
async def generate_diagnostic(request: DiagnoseRequest) -> Dict:
    if not request.lagging_fields:
        return {"diagnostics": []}
    try:
        optimizer = LLMOptimizer()
        report = optimizer.generate_diagnostic_report(request.resume_text, request.lagging_fields)
        return report
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating diagnostics: {str(e)}")
