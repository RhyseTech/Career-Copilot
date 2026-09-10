export interface QualifierEvaluation {
  qualifier_type: string;
  expected: string;
  actual: string;
  passed: boolean;
}

export interface AtomScore {
  atom_id: string;
  atom_text: string;
  match_type: 'EXACT' | 'RELATED' | 'PARTIAL' | 'TRANSFERABLE' | 'GAP';
  contribution: number;
  contributing_evidence_ids: string[];
  contributing_match_edge_id: string | null;
}

export interface RequirementScore {
  requirement_id: string;
  requirement_text: string;
  requirement_type: 'REQUIRED' | 'PREFERRED';
  is_hard_constraint: boolean;
  weight: number;
  coverage: number;
  requirement_score: number;
  contributing_atom_ids: string[];
  contributing_evidence_ids: string[];
  contributing_match_edge_ids: string[];
  atom_scores: AtomScore[];
  qualifier_evaluations: QualifierEvaluation[];
  deterministic_explanation: string;
}

export interface Phase5Score {
  scoring_config_version: string;
  base_score: number;
  constraint_gate: number;
  final_score: number;
  required_coverage: number;
  preferred_coverage: number;
  requirement_scores: RequirementScore[];
  hard_constraints_failed: string[];
}
