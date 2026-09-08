from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class CanonicalItem(BaseModel):
    id: str = Field(..., description="Stable unique identifier")
    raw_value: str = Field(..., description="Original extracted text")
    normalized_value: Optional[str] = Field(None, description="Mapped canonical representation")
    category: Literal["TECHNOLOGY", "SKILL", "EXPERIENCE", "EDUCATION", "CERTIFICATION", "DOMAIN", "SOFT_SKILL", "RESPONSIBILITY", "GENERAL"]
    provenance: Literal["EXTRACTED", "INFERRED"] = Field("EXTRACTED")
    source_location: str = Field(..., description="Section or exact sentence where it was found")
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    
    # Optional downstream metadata preserved for backwards compatibility with MatchEngine
    requirement_type: Optional[Literal["REQUIRED", "PREFERRED"]] = None
    weight: Optional[float] = 1.0

class CanonicalResume(BaseModel):
    resume_id: str = Field(..., description="Unique UUID for this resume")
    file_name: str
    items: List[CanonicalItem] = Field(default_factory=list, description="All extracted canonical items")
