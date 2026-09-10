from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class QualifierEvaluation(BaseModel):
    qualifier_type: str = Field(..., description="e.g. YOE, EDUCATION")
    expected: str = Field(...)
    actual: Optional[str] = Field(None)
    passed: bool = Field(...)

class AtomScore(BaseModel):
    atom_id: str
    atom_text: str
    match_type: str = Field(..., description="The match contribution type e.g. EXACT, RELATED, PARTIAL, TRANSFERABLE, GAP")
    contribution: float = Field(..., description="The numeric contribution (0.0 to 1.0) for this atom")
    contributing_evidence_ids: List[str] = Field(default_factory=list)
    contributing_match_edge_id: Optional[str] = Field(None)

class RequirementScore(BaseModel):
    requirement_id: str
    requirement_text: str
    requirement_type: str = Field(..., description="REQUIRED or PREFERRED")
    is_hard_constraint: bool = Field(False)
    
    weight: float = Field(..., description="The calculated weight of this requirement")
    coverage: float = Field(..., description="The raw coverage (0.0 to 1.0) satisfied by evidence")
    requirement_score: float = Field(..., description="weight * coverage")
    
    contributing_atom_ids: List[str] = Field(default_factory=list)
    contributing_evidence_ids: List[str] = Field(default_factory=list)
    contributing_match_edge_ids: List[str] = Field(default_factory=list)
    
    atom_scores: List[AtomScore] = Field(default_factory=list)
    qualifier_evaluations: List[QualifierEvaluation] = Field(default_factory=list)
    
    deterministic_explanation: str = Field(...)

class Phase5Score(BaseModel):
    scoring_config_version: str = Field(..., description="The version of the Phase5Config used")
    created_at: Optional[str] = Field(None, description="ISO-8601 timestamp with +05:30 timezone")
    
    base_score: float = Field(..., description="The 0-100 score before hard constraints")
    constraint_gate: float = Field(1.0, description="Multiplier applied if hard constraints fail")
    final_score: float = Field(..., description="base_score * constraint_gate")
    
    required_coverage: float = Field(..., description="0.0 to 1.0 coverage of REQUIRED requirements")
    preferred_coverage: float = Field(..., description="0.0 to 1.0 coverage of PREFERRED requirements")
    
    requirement_scores: List[RequirementScore] = Field(default_factory=list)
    hard_constraints_failed: List[str] = Field(default_factory=list, description="IDs of hard constraints that failed")
