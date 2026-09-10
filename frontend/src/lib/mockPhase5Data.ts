import { Phase5Score } from '../types/phase5';

export const mockPhase5Data: Phase5Score = {
  scoring_config_version: "1.0.0",
  base_score: 87.5,
  constraint_gate: 1.0,
  final_score: 87.5,
  required_coverage: 0.92,
  preferred_coverage: 0.68,
  hard_constraints_failed: [],
  requirement_scores: [
    {
      requirement_id: "req1",
      requirement_text: "Python",
      requirement_type: "REQUIRED",
      is_hard_constraint: false,
      weight: 1.0,
      coverage: 1.0,
      requirement_score: 1.0,
      contributing_atom_ids: ["atom1"],
      contributing_evidence_ids: ["ev1", "ev2"],
      contributing_match_edge_ids: ["edge1"],
      atom_scores: [
        {
          atom_id: "atom1",
          atom_text: "Python",
          match_type: "EXACT",
          contribution: 1.0,
          contributing_evidence_ids: ["ev1"],
          contributing_match_edge_id: "edge1"
        }
      ],
      qualifier_evaluations: [],
      deterministic_explanation: "Weight: 1.00, Coverage: 1.00\nAtom Breakdown:\n- 'Python' requirement atom received EXACT coverage from evidence ev1 through MatchEdge edge1."
    },
    {
      requirement_id: "req2",
      requirement_text: "5+ years experience",
      requirement_type: "REQUIRED",
      is_hard_constraint: false,
      weight: 1.0,
      coverage: 0.5,
      requirement_score: 0.5,
      contributing_atom_ids: ["atom2"],
      contributing_evidence_ids: ["ev3"],
      contributing_match_edge_ids: ["edge2"],
      atom_scores: [
        {
          atom_id: "atom2",
          atom_text: "Experience",
          match_type: "PARTIAL",
          contribution: 0.5,
          contributing_evidence_ids: ["ev3"],
          contributing_match_edge_id: "edge2"
        }
      ],
      qualifier_evaluations: [
        {
          qualifier_type: "YOE",
          expected: "5+ years",
          actual: "2 years",
          passed: false
        }
      ],
      deterministic_explanation: "Weight: 1.00, Coverage: 0.50\nAtom Breakdown:\n- 'Experience' requirement atom received PARTIAL coverage.\nQualifier Breakdown:\n- Qualifier YOE was NOT_SATISFIED, reducing coverage."
    },
    {
      requirement_id: "req3",
      requirement_text: "GCP Dataflow",
      requirement_type: "PREFERRED",
      is_hard_constraint: false,
      weight: 0.35,
      coverage: 0.35,
      requirement_score: 0.1225,
      contributing_atom_ids: ["atom3"],
      contributing_evidence_ids: ["ev4"],
      contributing_match_edge_ids: ["edge3"],
      atom_scores: [
        {
          atom_id: "atom3",
          atom_text: "GCP Dataflow",
          match_type: "TRANSFERABLE",
          contribution: 0.35,
          contributing_evidence_ids: ["ev4"],
          contributing_match_edge_id: "edge3"
        }
      ],
      qualifier_evaluations: [],
      deterministic_explanation: "Weight: 0.35, Coverage: 0.35\nAtom Breakdown:\n- 'GCP Dataflow' requirement atom received TRANSFERABLE coverage from evidence ev4. Reason: Built production pipelines using AWS Glue."
    },
    {
      requirement_id: "req4",
      requirement_text: "Terraform",
      requirement_type: "REQUIRED",
      is_hard_constraint: false,
      weight: 1.0,
      coverage: 0.0,
      requirement_score: 0.0,
      contributing_atom_ids: ["atom4"],
      contributing_evidence_ids: [],
      contributing_match_edge_ids: [],
      atom_scores: [
        {
          atom_id: "atom4",
          atom_text: "Terraform",
          match_type: "GAP",
          contribution: 0.0,
          contributing_evidence_ids: [],
          contributing_match_edge_id: null
        }
      ],
      qualifier_evaluations: [],
      deterministic_explanation: "Weight: 1.00, Coverage: 0.00\nAtom Breakdown:\n- 'Terraform' requirement atom received GAP coverage (no matching evidence)."
    }
  ]
};
