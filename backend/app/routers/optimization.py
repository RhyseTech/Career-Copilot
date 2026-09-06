from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Optional
from ..services.llm_optimizer import LLMOptimizer

router = APIRouter(prefix="/optimization", tags=["optimization"])

class OptimizationRequest(BaseModel):
    resume_text: str
    jd_text: Optional[str] = None
    resume_version_id: str
    theme: Optional[str] = "classic"

@router.post("/suggest")
async def get_suggestions(request: OptimizationRequest) -> Dict:
    try:
        optimizer = LLMOptimizer()
        suggestions = optimizer.generate_optimization_suggestions(
            resume_text=request.resume_text,
            jd_text=request.jd_text
        )
        
        return {
            "resume_version_id": request.resume_version_id,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")

import yaml
import subprocess
import os
import uuid
from fastapi.responses import FileResponse
import shutil

def cleanup_old_temp_dirs(base_dir: str, keep_count: int = 3):
    temp_dirs = []
    for d in os.listdir(base_dir):
        path = os.path.join(base_dir, d)
        if d.startswith("temp_") and os.path.isdir(path):
            temp_dirs.append(path)
            
    # Sort by modification time, newest first
    temp_dirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # Delete older directories
    for d in temp_dirs[keep_count:]:
        try:
            shutil.rmtree(d, ignore_errors=True)
        except Exception as e:
            print(f"Failed to delete {d}: {e}")

import re

# Fields that must be omitted entirely if empty (RenderCV validates them with regex)
REQUIRED_FORMAT_FIELDS = {"email", "phone", "location", "website"}

def fallback_rendercv_data(resume_text: str) -> Dict:
    """Produce a minimal, truthful CV when the optional LLM extraction is unavailable."""
    lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
    name = next((line for line in lines if not line.lower().startswith("last updated") and "@" not in line and len(line) < 70), "Resume")
    email_match = re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", resume_text)
    highlights = [line for line in lines if line != name and not line.lower().startswith("last updated")][:18]
    cv = {
        "name": name,
        "sections": {"experience": [{"company": "Experience", "position": "Resume details", "highlights": highlights or ["Resume uploaded successfully."]}]},
    }
    if email_match:
        cv["email"] = email_match.group(0)
    return {"cv": cv}

def is_valid_rendercv_field(field: str, value) -> bool:
    """Keep only values RenderCV can validate; optional contact fields must not block a preview."""
    value = str(value).strip()
    if not value:
        return False
    if field == "email":
        return bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", value))
    if field == "phone":
        # RenderCV expects an internationally formatted phone number. A bare
        # local number is still preserved in the original resume, but omitted
        # from this generated preview rather than failing the entire request.
        return bool(re.match(r"^\+\d[\d .()-]{6,}$", value))
    return True

def fix_skills_list(skills_list):
    new_skills = []
    for item in skills_list:
        if isinstance(item, str):
            new_skills.append({"label": item[:20] if len(item) > 20 else item, "details": item})
        elif isinstance(item, dict):
            label = item.get("label") or item.get("name") or item.get("category") or "Skill"
            details = item.get("details") or item.get("items") or item.get("value") or item.get("keywords") or ""
            if isinstance(details, list):
                details = ", ".join([str(d) for d in details])
            if not str(details).strip():
                details = str(label)
            new_skills.append({"label": str(label), "details": str(details)})
    return new_skills

def clean_rendercv_data(d):
    if isinstance(d, dict):
        keys_to_delete = []
        for k, v in list(d.items()):
            if k == "skills" and isinstance(v, list):
                d[k] = fix_skills_list(v)
                v = d[k]
            elif k in ["experience", "education", "projects", "certifications"] and isinstance(v, list):
                d[k] = [item for item in v if isinstance(item, dict)]
                v = d[k]
                
            if k in ["start_date", "end_date", "date"]:
                if not v or str(v).strip() == "":
                    keys_to_delete.append(k)
                elif str(v).lower() != "present" and not re.match(r"^\d{4}(-\d{2}(-\d{2})?)?$", str(v)):
                    keys_to_delete.append(k)
            elif k in REQUIRED_FORMAT_FIELDS:
                if not is_valid_rendercv_field(k, v):
                    keys_to_delete.append(k)
            elif v is None:
                d[k] = "Unknown" if k in ["company", "position", "institution", "degree", "title", "name"] else ""
            else:
                clean_rendercv_data(d[k])
        for k in keys_to_delete:
            del d[k]
    elif isinstance(d, list):
        for item in d:
            clean_rendercv_data(item)

@router.post("/render-pdf")
async def render_pdf(request: OptimizationRequest, background_tasks: BackgroundTasks):
    try:
        optimizer = LLMOptimizer()
        rendercv_json = optimizer.generate_rendercv_json(request.resume_text)
        if not rendercv_json:
            print("LLM RenderCV extraction unavailable; using local source-text fallback.")
            rendercv_json = fallback_rendercv_data(request.resume_text)
            
        # Ensure we have a rendercv-compatible 'cv' root if missing
        if "cv" not in rendercv_json:
            rendercv_json = {"cv": rendercv_json}
            
        # Forcefully set design to prevent LLM from generating invalid schema fields
        rendercv_json["design"] = {
            "theme": request.theme or "classic"
        }
        if "design" in rendercv_json["cv"]:
            del rendercv_json["cv"]["design"]
            
        # Remove any invalid dates or None values that would crash rendercv
        clean_rendercv_data(rendercv_json)

        # Create a unique temporary directory and filename
        run_id = str(uuid.uuid4())
        temp_dir = os.path.join(os.getcwd(), f"temp_{run_id}")
        os.makedirs(temp_dir, exist_ok=True)
        
        yaml_path = os.path.join(temp_dir, f"{run_id}_CV.yaml")
        
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(rendercv_json, f, allow_unicode=True, sort_keys=False)
            
        # Call rendercv
        # rendercv render temp.yaml
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        import sys
        result = subprocess.run(
            [sys.executable, "-m", "rendercv", "render", yaml_path],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env
        )
        
        # Find the output PDF
        output_dir = os.path.join(temp_dir, "rendercv_output")
        # RenderCV usually names it based on the name field or filename
        pdf_files = [f for f in os.listdir(output_dir) if f.endswith(".pdf")] if os.path.isdir(output_dir) else []
        if not pdf_files:
            print("RenderCV Error STDOUT:", result.stdout)
            print("RenderCV Error STDERR:", result.stderr)
            raise Exception(f"RenderCV did not produce a PDF file: {result.stdout}\n{result.stderr}")

        # On Windows, RenderCV can fail only while creating its optional preview
        # directory after the PDF has already been written. The PDF is valid and
        # should remain available for the live preview in that case.
        if result.returncode != 0:
            print("RenderCV preview warning (PDF generated successfully):", result.stderr or result.stdout)
            
        pdf_path = os.path.join(output_dir, pdf_files[0])
        
        # Schedule cleanup task after response is sent
        background_tasks.add_task(cleanup_old_temp_dirs, os.getcwd(), 3)
        
        return FileResponse(
            path=pdf_path, 
            filename="Optimized_Resume.pdf", 
            media_type="application/pdf",
            headers={"Access-Control-Expose-Headers": "Content-Disposition"}
        )
        
    except Exception as e:
        print(f"Error rendering PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
