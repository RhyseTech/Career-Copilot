from enum import Enum
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field

class OntologyRelation(str, Enum):
    EQUIVALENT = "EQUIVALENT"
    RELATED = "RELATED"
    BROADER = "BROADER"
    NARROWER = "NARROWER"
    DISJOINT = "DISJOINT"
    UNKNOWN = "UNKNOWN"

class QualifierStatus(str, Enum):
    SATISFIED = "SATISFIED"
    NOT_SATISFIED = "NOT_SATISFIED"
    UNKNOWN = "UNKNOWN"

class MatchEdge(BaseModel):
    requirement_id: str
    requirement_atom_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    match_type: Literal["EXACT", "RELATED", "PARTIAL", "TRANSFERABLE", "GAP"]
    satisfied_atoms: List[str] = Field(default_factory=list)
    missing_atoms: List[str] = Field(default_factory=list)
    lexical_features: Dict[str, float] = Field(default_factory=dict)
    semantic_features: Dict[str, float] = Field(default_factory=dict)
    ontology_features: Dict[str, OntologyRelation] = Field(default_factory=dict)
    qualifier_results: Dict[str, QualifierStatus] = Field(default_factory=dict)
    category_compatibility: bool = False
    decision_reason: str
    provenance_explanation: str = ""
    confidence: Optional[float] = None
