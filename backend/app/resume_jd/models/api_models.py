from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.resume_jd.models.canonical_jd import CanonicalJD
from app.resume_jd.models.canonical_models import CanonicalResume
from app.resume_jd.models.phase_03_models import JDRequirement, ResumeEvidence
from app.resume_jd.models.phase_04_models import MatchEdge
from app.resume_jd.models.phase_05_models import Phase5Score

class Phase1ResumeResponse(BaseModel):
    phase: int = 1
    resume_id: str
    status: str = "completed"
    resume: Dict[str, Any]

class Phase1JDResponse(BaseModel):
    phase: int = 1
    jd_id: str
    status: str = "completed"
    jd: Dict[str, Any]

class Phase2ResumeResponse(BaseModel):
    phase: int = 2
    resume_id: str
    canonical_resume: CanonicalResume

class Phase2JDResponse(BaseModel):
    phase: int = 2
    jd_id: str
    canonical_jd: CanonicalJD

class Phase3Request(BaseModel):
    resume_id: str
    jd_id: str

class Phase3Response(BaseModel):
    phase: int = 3
    analysis_id: str
    jd_requirements: List[JDRequirement]
    resume_evidence: List[ResumeEvidence]

class Phase4Request(BaseModel):
    analysis_id: str

class Phase4Response(BaseModel):
    phase: int = 4
    analysis_id: str
    match_edges: List[MatchEdge]

class Phase5Request(BaseModel):
    analysis_id: str

class Phase5Response(BaseModel):
    phase: int = 5
    analysis_id: str
    score: Phase5Score

class OrchestratorResponse(BaseModel):
    analysis_id: str
    phase_1: Dict[str, Any]
    phase_2: Dict[str, Any]
    phase_3: Phase3Response
    phase_4: Phase4Response
    phase_5: Phase5Response
