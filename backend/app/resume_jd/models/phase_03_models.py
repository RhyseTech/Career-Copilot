from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class JDRequirementAtom(BaseModel):
    atom_id: str = Field(..., description="Unique identifier for this atom")
    raw_value: str = Field(..., description="Raw text of this specific atom")
    canonical_concept: Optional[str] = Field(None, description="Normalized representation of this atom")
    atom_type: Literal["TECHNOLOGY", "SKILL", "EXPERIENCE", "EDUCATION", "CERTIFICATION", "RESPONSIBILITY", "DOMAIN", "SOFT_SKILL"]
    action: Optional[str] = Field(None, description="Action or verb associated with this atom")
    canonical_item_ids: List[str] = Field(default_factory=list, description="Linked Phase 2 CanonicalItem IDs if deterministically available")

class JDRequirement(BaseModel):
    requirement_id: str = Field(..., description="Unique identifier for the parent requirement")
    parent_capability: str = Field(..., description="The high-level capability/responsibility")
    raw_value: str = Field(..., description="The raw target phrase from the text")
    requirement_text: str = Field(..., description="The full original requirement text")
    surrounding_context: Optional[str] = Field(None, description="Broader paragraph or context")
    expected_action: Optional[str] = Field(None, description="The action expected by the employer")
    category: str = Field(..., description="Category of the requirement")
    requirement_type: Literal["REQUIRED", "PREFERRED"]
    requirement_signal: Optional[str] = Field(None, description="e.g. 'must have', 'preferred'")
    importance_signals: List[str] = Field(default_factory=list, description="Qualitative signals e.g., CORE_RESPONSIBILITY")
    provenance: Literal["EXPLICIT", "INFERRED"] = Field("EXPLICIT")
    
    # Traceability (Graceful Degradation)
    source_document_id: str
    source_section: str
    source_field: Optional[str] = None
    source_sentence: Optional[str] = None
    source_span: Optional[str] = None # System generated
    
    atoms: List[JDRequirementAtom] = Field(default_factory=list, description="Decomposed child requirements")

class ResumeEvidence(BaseModel):
    evidence_id: str = Field(..., description="Unique identifier")
    raw_value: str = Field(..., description="The specific skill or capability phrase")
    evidence_text: str = Field(..., description="The full sentence containing the evidence")
    surrounding_context: Optional[str] = Field(None, description="Broader context")
    action: Optional[str] = Field(None, description="The action performed (e.g. 'Built', 'Led')")
    scale_impact: Optional[str] = Field(None, description="Scale or impact (e.g. '2TB daily')")
    category: str = Field(..., description="Category of the evidence")
    evidence_type: Literal["EXPLICIT", "INFERRED"] = Field("EXPLICIT")
    provenance: Literal["EXPLICIT", "INFERRED"] = Field("EXPLICIT")
    
    # Traceability (Graceful Degradation)
    source_document_id: str
    source_section: str
    source_field: Optional[str] = None
    source_sentence: Optional[str] = None
    source_span: Optional[str] = None # System generated
    
    canonical_item_ids: List[str] = Field(default_factory=list, description="Linked Phase 2 CanonicalItem IDs if deterministically available")
