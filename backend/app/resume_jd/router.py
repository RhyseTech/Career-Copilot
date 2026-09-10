from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body
from typing import Dict, Any, Optional
import os
import uuid
import shutil
import hashlib

# Deprecated imports
import warnings
from app.resume_jd.matching.engine import MatchEngine

from app.resume_jd.pipelines.phase_03_extractor import Phase3Extractor
from app.resume_jd.pipelines.phase_04_matcher import Phase4Matcher
from app.resume_jd.scoring.phase_05_scorer import Phase5Scorer
from app.services.parser import ResumeParser
from app.services.jd_parser import JDParser
from app.resume_jd.adapters.resume_adapter import ResumeAdapter
from app.resume_jd.adapters.jd_adapter import JDAdapter
from app.resume_jd.storage.json_store import JSONStore

from app.resume_jd.models.api_models import (
    Phase1ResumeResponse,
    Phase1JDResponse,
    Phase2ResumeResponse,
    Phase2JDResponse,
    Phase3Request,
    Phase3Response,
    Phase4Request,
    Phase4Response,
    Phase5Request,
    Phase5Response,
    OrchestratorResponse
)

router = APIRouter(prefix="/resume-jd", tags=["resume-jd"])

def _save_upload_file(file: UploadFile) -> tuple[str, str]:
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    saved_filename = f"{file_id}{ext}"
    
    UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, saved_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return file_id, file_path

# ==============================================================================
# PHASE 1: PARSING
# ==============================================================================

@router.post("/resume/parse", response_model=Phase1ResumeResponse)
async def phase1_parse_resume(file: UploadFile = File(...)):
    try:
        file_id, file_path = _save_upload_file(file)
        parser = ResumeParser()
        parsed_res = parser.parse_resume(file_path)
        
        return Phase1ResumeResponse(
            resume_id=file_id,
            status="completed",
            resume=parsed_res
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Phase 1 error: {str(e)}")

@router.post("/jd/parse", response_model=Phase1JDResponse)
async def phase1_parse_jd(jd_text: str = Form(...)):
    try:
        jd_hash = hashlib.sha256(jd_text.encode('utf-8')).hexdigest()
        jd_id = f"jd_{jd_hash[:8]}"
        
        parser = JDParser()
        parsed_jd = parser.parse_jd(jd_text)
        
        return Phase1JDResponse(
            jd_id=jd_id,
            status="completed",
            jd=parsed_jd
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Phase 1 error: {str(e)}")

# ==============================================================================
# PHASE 2: CANONICALIZATION
# ==============================================================================

@router.post("/resume/canonicalize", response_model=Phase2ResumeResponse)
async def phase2_canonicalize_resume(file: UploadFile = File(...)):
    try:
        file_id, file_path = _save_upload_file(file)
        
        with open(file_path, "rb") as f:
            resume_bytes = f.read()
        res_hash = hashlib.sha256(resume_bytes).hexdigest()
        
        store = JSONStore()
        canonical_resume = store.get_canonical_resume_by_hash(res_hash)
        
        if not canonical_resume:
            adapter = ResumeAdapter()
            canonical_resume = adapter.process_file(file_path, file.filename)
            canonical_resume.content_hash = res_hash
            store.save_canonical_resume(canonical_resume)
            
        return Phase2ResumeResponse(
            resume_id=canonical_resume.resume_id,
            canonical_resume=canonical_resume
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Phase 2 error: {str(e)}")

@router.post("/jd/canonicalize", response_model=Phase2JDResponse)
async def phase2_canonicalize_jd(jd_text: str = Form(...)):
    try:
        jd_hash = hashlib.sha256(jd_text.encode('utf-8')).hexdigest()
        
        store = JSONStore()
        canonical_jd = store.get_canonical_jd_by_hash(jd_hash)
        
        if not canonical_jd:
            adapter = JDAdapter()
            canonical_jd = adapter.adapt(jd_text)
            canonical_jd.content_hash = jd_hash
            store.save_canonical_jd(canonical_jd)
            
        return Phase2JDResponse(
            jd_id=canonical_jd.jd_id,
            canonical_jd=canonical_jd
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Phase 2 error: {str(e)}")

# ==============================================================================
# PHASE 3: REQUIREMENTS & EVIDENCE (LLM EXTRACTION)
# ==============================================================================

@router.post("/analysis/requirements-evidence", response_model=Phase3Response)
async def phase3_extract(req: Phase3Request):
    try:
        store = JSONStore()
        jd_reqs = store.get_phase3_jd(req.jd_id)
        res_evs = store.get_phase3_resume(req.resume_id)
        
        analysis_id = f"{req.resume_id}_{req.jd_id}"
        
        # If we have both, just return them
        if jd_reqs and res_evs:
            return Phase3Response(
                analysis_id=analysis_id,
                jd_requirements=jd_reqs,
                resume_evidence=res_evs
            )
            
        # Otherwise, we need to extract
        canonical_jd = store.get_canonical_jd_by_id(req.jd_id)
        canonical_resume = store.get_canonical_resume_by_id(req.resume_id)
        
        if not canonical_jd or not canonical_resume:
            raise HTTPException(status_code=400, detail="Phase 2 Canonical representations must exist or Phase 3 data missing. Ensure prior phases ran.")
            
        extractor = Phase3Extractor()
        
        if not jd_reqs:
            jd_reqs = extractor.process_jd(canonical_jd)
            if jd_reqs:
                store.save_phase3_jd(req.jd_id, jd_reqs)
                
        if not res_evs:
            import glob
            UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
            files = glob.glob(os.path.join(UPLOAD_DIR, f"{req.resume_id}.*"))
            if files:
                parser = ResumeParser()
                parsed_res = parser.parse_resume(files[0])
                raw_text = parsed_res.get("raw_text", "")
            else:
                raw_text = ""
                
            res_evs = extractor.process_resume(canonical_resume, raw_text)
            if res_evs:
                store.save_phase3_resume(req.resume_id, res_evs)
                
        if not jd_reqs or not res_evs:
            raise HTTPException(status_code=429, detail="Phase 3 LLM extraction failed (likely rate limited).")

        return Phase3Response(
            analysis_id=analysis_id,
            jd_requirements=jd_reqs,
            resume_evidence=res_evs
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Phase 3 error: {str(e)}")

# ==============================================================================
# PHASE 4: MATCHING
# ==============================================================================

@router.post("/analysis/matches", response_model=Phase4Response)
async def phase4_match(req: Phase4Request):
    try:
        store = JSONStore()
        
        parts = req.analysis_id.split("_", 1)
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid analysis_id format. Expected resume_id_jd_id")
        resume_id, jd_id = parts[0], parts[1]

        jd_reqs = store.get_phase3_jd(jd_id)
        res_evs = store.get_phase3_resume(resume_id)
        
        if not jd_reqs or not res_evs:
            raise HTTPException(status_code=400, detail="Phase 3 requirements/evidence are required before Phase 4 matching.")
            
        matcher = Phase4Matcher()
        edges = matcher.match(jd_reqs, res_evs)
        store.save_phase4_edges(req.analysis_id, edges)
        
        return Phase4Response(
            analysis_id=req.analysis_id,
            match_edges=edges
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Phase 4 error: {str(e)}")

# ==============================================================================
# PHASE 5: SCORING
# ==============================================================================

@router.post("/analysis/score", response_model=Phase5Response)
async def phase5_score(req: Phase5Request):
    try:
        store = JSONStore()
        
        parts = req.analysis_id.split("_", 1)
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid analysis_id format. Expected resume_id_jd_id")
        resume_id, jd_id = parts[0], parts[1]
            
        jd_reqs = store.get_phase3_jd(jd_id)
        res_evs = store.get_phase3_resume(resume_id)
        
        if not jd_reqs or not res_evs:
            raise HTTPException(status_code=400, detail="Phase 3 requirements/evidence are required before Phase 5 scoring.")
            
        # Get edges from store
        # Wait, the prompt says "Phase 5 without Phase 4: HTTP 4xx Phase 4 MatchEdges are required before Phase 5 scoring."
        # We need `get_phase4_edges` in JSONStore
        import json
        import glob
        edge_files = sorted(glob.glob(os.path.join(store.phase_04_dir, f"match_edges_*{req.analysis_id}.json")), reverse=True)
        if not edge_files:
            raise HTTPException(status_code=400, detail="Phase 4 MatchEdges are required before Phase 5 scoring.")
            
        with open(edge_files[0], "r") as f:
            data = json.load(f)
            from app.resume_jd.models.phase_04_models import MatchEdge
            edges = [MatchEdge(**e) for e in data.get("match_edges", [])]
            
        scorer = Phase5Scorer()
        score = scorer.score(jd_reqs, res_evs, edges)
        store.save_phase5_score(req.analysis_id, score)
        
        return Phase5Response(
            analysis_id=req.analysis_id,
            score=score
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Phase 5 error: {str(e)}")


# ==============================================================================
# ORCHESTRATOR
# ==============================================================================

@router.post("/analysis/run", response_model=OrchestratorResponse)
async def analysis_run(file: UploadFile = File(...), jd_text: str = Form(...)):
    """
    Normal full-analysis endpoint executing Phase 1 -> 5.
    """
    try:
        # Phase 1 & 2 combined for Resume
        file_id, file_path = _save_upload_file(file)
        with open(file_path, "rb") as f:
            resume_bytes = f.read()
        res_hash = hashlib.sha256(resume_bytes).hexdigest()
        
        # Phase 1 logic
        parser = ResumeParser()
        parsed_res = parser.parse_resume(file_path)
        
        # Phase 2 logic Resume
        store = JSONStore()
        canonical_resume = store.get_canonical_resume_by_hash(res_hash)
        if not canonical_resume:
            adapter = ResumeAdapter()
            canonical_resume = adapter.process_file(file_path, file.filename)
            canonical_resume.content_hash = res_hash
            store.save_canonical_resume(canonical_resume)
            
        # Phase 1 & 2 combined for JD
        jd_hash = hashlib.sha256(jd_text.encode('utf-8')).hexdigest()
        jd_id = f"jd_{jd_hash[:8]}"
        
        # Phase 1 logic JD
        jd_parser_svc = JDParser()
        parsed_jd = jd_parser_svc.parse_jd(jd_text)
        
        # Phase 2 logic JD
        canonical_jd = store.get_canonical_jd_by_hash(jd_hash)
        if not canonical_jd:
            jd_adapter = JDAdapter()
            canonical_jd = jd_adapter.adapt(jd_text)
            canonical_jd.content_hash = jd_hash
            store.save_canonical_jd(canonical_jd)
            
        # Phase 3
        extractor = Phase3Extractor()
        jd_reqs = store.get_phase3_jd(canonical_jd.jd_id)
        if not jd_reqs:
            jd_reqs = extractor.process_jd(canonical_jd)
            if jd_reqs:
                store.save_phase3_jd(canonical_jd.jd_id, jd_reqs)
                
        res_evs = store.get_phase3_resume(canonical_resume.resume_id)
        if not res_evs:
            res_evs = extractor.process_resume(canonical_resume, parsed_res["raw_text"])
            if res_evs:
                store.save_phase3_resume(canonical_resume.resume_id, res_evs)
                
        if not jd_reqs or not res_evs:
            raise HTTPException(status_code=429, detail="Phase 3 LLM extraction failed (likely rate limited).")
            
        analysis_id = f"{canonical_resume.resume_id}_{canonical_jd.jd_id}"
        
        # Phase 4
        matcher = Phase4Matcher()
        edges = matcher.match(jd_reqs, res_evs)
        store.save_phase4_edges(analysis_id, edges)
        
        # Phase 5
        scorer = Phase5Scorer()
        score = scorer.score(jd_reqs, res_evs, edges)
        store.save_phase5_score(analysis_id, score)
        
        return OrchestratorResponse(
            analysis_id=analysis_id,
            phase_1={
                "resume": parsed_res,
                "jd": parsed_jd
            },
            phase_2={
                "canonical_resume": canonical_resume.model_dump(),
                "canonical_jd": canonical_jd.model_dump()
            },
            phase_3=Phase3Response(
                analysis_id=analysis_id,
                jd_requirements=jd_reqs,
                resume_evidence=res_evs
            ),
            phase_4=Phase4Response(
                analysis_id=analysis_id,
                match_edges=edges
            ),
            phase_5=Phase5Response(
                analysis_id=analysis_id,
                score=score
            )
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Orchestration error: {str(e)}")


# ==============================================================================
# LEGACY ENDPOINTS
# ==============================================================================

@router.post("/match-types", deprecated=True)
async def get_match_types(
    file: UploadFile = File(...),
    jd_text: str = Form(...)
) -> Dict[str, Any]:
    """
    DEPRECATED: Use /analysis/run instead.
    Preserved for backward compatibility.
    """
    warnings.warn("The /resume-jd/match-types endpoint is deprecated. Use /resume-jd/analysis/run instead.", DeprecationWarning, stacklevel=2)
    try:
        # Save file
        file_id, file_path = _save_upload_file(file)
            
        # Run legacy matching engine
        engine = MatchEngine()
        engine_result = engine.process(file_path, jd_text)
        
        results = {"requirements": engine_result["requirements"]}
        canonical_jd = engine_result["canonical_jd"]
        canonical_resume = engine_result["canonical_resume"]
        
        # Try to run Phase 3-5 silently
        phase5_score_dict = None
        phase5_status = "unavailable"
        phase5_error = None
        
        try:
            resume_parser = ResumeParser()
            parsed_res = resume_parser.parse_resume(file_path)
            
            extractor = Phase3Extractor()
            store = JSONStore()
            
            jd_reqs = store.get_phase3_jd(canonical_jd.jd_id)
            if not jd_reqs:
                jd_reqs = extractor.process_jd(canonical_jd)
                if jd_reqs:
                    store.save_phase3_jd(canonical_jd.jd_id, jd_reqs)
                    
            res_evs = store.get_phase3_resume(canonical_resume.resume_id)
            if not res_evs:
                res_evs = extractor.process_resume(canonical_resume, parsed_res["raw_text"])
                if res_evs:
                    store.save_phase3_resume(canonical_resume.resume_id, res_evs)
            
            if jd_reqs and res_evs:
                analysis_id = f"{canonical_resume.resume_id}_{canonical_jd.jd_id}"
                
                matcher = Phase4Matcher()
                edges = matcher.match(jd_reqs, res_evs)
                store.save_phase4_edges(analysis_id, edges)
                
                scorer = Phase5Scorer()
                score = scorer.score(jd_reqs, res_evs, edges)
                store.save_phase5_score(analysis_id, score)
                
                phase5_score_dict = score.model_dump()
                phase5_status = "success"
            else:
                phase5_error = "rate_limited"
                
        except Exception as p5_error:
            phase5_error = "rate_limited"

        if phase5_score_dict:
            results["phase5_score"] = phase5_score_dict
        results["phase5_status"] = phase5_status
        if phase5_error:
            results["phase5_error"] = phase5_error
            
        return {
            "resume_id": file_id,
            "filename": file.filename,
            "data": results
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing Match Types: {str(e)}")
