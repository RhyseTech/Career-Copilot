from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any, Optional
import os
import uuid
import shutil
from app.resume_jd.matching.engine import MatchEngine

router = APIRouter(prefix="/resume-jd", tags=["resume-jd"])

@router.post("/match-types")
async def get_match_types(
    file: UploadFile = File(...),
    jd_text: str = Form(...)
) -> Dict[str, Any]:
    """
    Accepts a Resume file and JD text, and returns a deterministic 
    Match Types classification per JD requirement.
    """
    try:
        # Save file to uploads directory
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1]
        saved_filename = f"{file_id}{ext}"
        
        # We know UPLOAD_DIR is typically in app/uploads
        UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, saved_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Run matching engine
        engine = MatchEngine()
        results = engine.process(file_path, jd_text)
        
        return {
            "resume_id": file_id,
            "filename": saved_filename,
            "data": results
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing Match Types: {str(e)}")
