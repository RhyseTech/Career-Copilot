import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app.services.parser import ResumeParser

router = APIRouter(prefix="/resumes", tags=["resumes"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)) -> Dict:
    if not file.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    
    file_id = str(uuid.uuid4())
    extension = os.path.splitext(file.filename)[1]
    saved_filename = f"{file_id}{extension}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Parse the uploaded resume
    parser = ResumeParser()
    try:
        parsed_data = parser.parse_resume(file_path)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing resume: {str(e)}")
        
    return {
        "resume_id": file_id,
        "filename": saved_filename,
        "message": "Resume uploaded and parsed successfully",
        "parsed_data": parsed_data
    }
