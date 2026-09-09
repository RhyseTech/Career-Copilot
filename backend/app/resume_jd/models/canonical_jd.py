from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Requirement(BaseModel):
    requirement_id: str = Field(..., description="Unique identifier")
    requirement_type: Literal["REQUIRED", "PREFERRED"]
    category: Literal["SKILL", "EXPERIENCE", "EDUCATION", "CERTIFICATION", "GENERAL"]
    raw_text: str = Field(..., description="The extracted skill or phrase")
    source_span: str = Field(..., description="Exact matching substring from the original JD text")
    source_section: str = Field(..., description="The section heading where this was found (e.g., 'Responsibilities')")
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    provenance: Literal["EXTRACTED", "INFERRED"] = Field("EXTRACTED")
    weight: float = Field(1.0, description="Importance weighting for downstream scoring")
    canonical_skills: List[str] = Field(default_factory=list, description="Normalized canonical skills")

from app.resume_jd.models.canonical_models import CanonicalItem

class CanonicalJD(BaseModel):
    jd_id: str = Field(..., description="Unique UUID for this parsed JD")
    content_hash: str = Field(..., description="SHA256 hash of the raw JD text to detect changes")
    job_title: Optional[str] = Field(None, description="Extracted job title")
    created_at: Optional[str] = Field(None, description="ISO-8601 timestamp with +05:30 timezone")
    raw_text: str = Field(..., description="The complete raw text of the JD")
    
    # Phase 2 output: normalized representation
    items: List[CanonicalItem] = Field(default_factory=list, description="All canonicalized items")
    
    # Keeping old requirements for backwards compatibility with MatchEngine temporarily if needed
    requirements: List[Requirement] = Field(default_factory=list, description="Legacy requirement format")
