from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
import os
import shutil

from ..services.document_parser import DocumentParser
from ..services.jd_analyzer import JDAnalyzer
from ..services.match_engine import MatchEngine
from ..services.evidence_optimizer import EvidenceOptimizer

router = APIRouter(prefix="/v1", tags=["intelligence"])

# ----------------- Models -----------------
class MatchRequest(BaseModel):
    resume_json: Dict[str, Any]
    jd_json: Dict[str, Any]
    role_level: str = "mid"

class OptimizeRequest(BaseModel):
    section_name: str
    original_text: str
    jd_requirements: list
    evidence_map: list

class SuggestAllRequest(BaseModel):
    raw_resume_text: str
    jd_requirements: list
    evidence_map: list

# ----------------- Endpoints -----------------

@router.post("/documents/parse")
async def parse_documents(
    file: UploadFile = File(...),
    jd_text: Optional[str] = Form(None)
):
    """
    Extracts structured JSON from a Resume PDF/DOCX and (optionally) extracts requirements from JD text.
    """
    try:
        # Save file to uploads directory so other endpoints can access it
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1]
        saved_filename = f"{file_id}{ext}"
        
        UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, saved_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        parser = DocumentParser()
        resume_data = parser.parse_resume(file_path)
            
        jd_data = None
        if jd_text:
            analyzer = JDAnalyzer()
            jd_data = analyzer.analyze_jd(jd_text)
            
        return {
            "resume_id": file_id,
            "filename": saved_filename,
            "structured_resume": resume_data["structured_data"],
            "raw_resume_text": resume_data["raw_text"],
            "structured_jd": jd_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analysis/match")
async def match_resume_to_jd(request: MatchRequest):
    """
    Calculates the Hybrid ATS Score and computes the exact Evidence Map for missing vs existing skills.
    """
    try:
        engine = MatchEngine()
        result = engine.calculate_match(
            resume_json=request.resume_json,
            jd_json=request.jd_json,
            role_level=request.role_level
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimization/suggest")
async def suggest_optimization(request: OptimizeRequest):
    """
    Provides evidence-based optimization suggestions for a specific resume section.
    """
    try:
        optimizer = EvidenceOptimizer()
        result = optimizer.optimize_section(
            section_name=request.section_name,
            original_text=request.original_text,
            jd_requirements=request.jd_requirements,
            evidence_map=request.evidence_map
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimization/suggest-all")
async def suggest_all_optimizations(request: SuggestAllRequest):
    """
    Performs a single comprehensive LLM call analyzing the full resume + evidence map
    and returns all needed changes across summary, experience, and skills.
    """
    try:
        optimizer = EvidenceOptimizer()
        result = optimizer.suggest_all_changes(
            raw_resume_text=request.raw_resume_text,
            jd_requirements=request.jd_requirements,
            evidence_map=request.evidence_map
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
