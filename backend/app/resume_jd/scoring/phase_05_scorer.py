from typing import List, Dict, Optional
from app.resume_jd.models.phase_03_models import JDRequirement, ResumeEvidence
from app.resume_jd.models.phase_04_models import MatchEdge, QualifierStatus
from app.resume_jd.models.phase_05_models import Phase5Score, RequirementScore, AtomScore, QualifierEvaluation
from app.resume_jd.scoring.phase_05_config import Phase5Config

class Phase5Scorer:
    def __init__(self, config: Phase5Config = None):
        self.config = config or Phase5Config()

    def _calculate_requirement_weight(self, req: JDRequirement) -> float:
        type_factor = self.config.REQUIREMENT_TYPE_FACTORS.get(req.requirement_type, 1.0)
        
        importance_str = self.config.DEFAULT_IMPORTANCE
        if req.importance_signals:
            signals_joined = " ".join(req.importance_signals).upper()
            if "HIGH" in signals_joined or "CORE" in signals_joined or "MUST" in signals_joined:
                importance_str = "HIGH"
            elif "LOW" in signals_joined or "NICE" in signals_joined:
                importance_str = "LOW"
                
        importance_factor = self.config.IMPORTANCE_FACTORS.get(importance_str, 1.0)
        
        return type_factor * importance_factor

    def _is_hard_constraint(self, req: JDRequirement) -> bool:
        signals_joined = " ".join(req.importance_signals).upper()
        if "HARD_CONSTRAINT" in signals_joined or "MANDATORY" in signals_joined:
            return True
        return False

    def score(self, requirements: List[JDRequirement], evidence: List[ResumeEvidence], edges: List[MatchEdge]) -> Phase5Score:
        req_scores = []
        hard_constraints_failed = []
        
        total_required_weight = 0.0
        total_required_coverage = 0.0
        total_preferred_weight = 0.0
        total_preferred_coverage = 0.0

        for req in requirements:
            weight = self._calculate_requirement_weight(req)
            is_hard = self._is_hard_constraint(req)
            
            req_edges = [e for e in edges if e.requirement_id == req.requirement_id]
            
            atom_scores = []
            contributing_atom_ids = set()
            contributing_evidence_ids = set()
            contributing_match_edge_ids = set()
            
            atom_explanations = []
            qual_evals = []
            
            if not req.atoms:
                best_edge = None
                best_contribution = -1.0
                for edge in req_edges:
                    contrib = self.config.MATCH_CONTRIBUTIONS.get(edge.match_type, 0.0)
                    if contrib > best_contribution:
                        best_contribution = contrib
                        best_edge = edge
                
                if best_edge:
                    a_score = AtomScore(
                        atom_id="top_level",
                        atom_text=req.raw_value,
                        match_type=best_edge.match_type,
                        contribution=best_contribution,
                        contributing_evidence_ids=best_edge.evidence_ids,
                        contributing_match_edge_id=best_edge.edge_id
                    )
                    contributing_atom_ids.add("top_level")
                    contributing_evidence_ids.update(best_edge.evidence_ids)
                    contributing_match_edge_ids.add(best_edge.edge_id)
                    
                    ev_str = ", ".join(best_edge.evidence_ids) if best_edge.evidence_ids else "None"
                    atom_explanations.append(
                        f"'{req.raw_value}' requirement received {best_edge.match_type} coverage from evidence {ev_str} through MatchEdge {best_edge.edge_id}."
                    )
                else:
                    a_score = AtomScore(
                        atom_id="top_level",
                        atom_text=req.raw_value,
                        match_type="GAP",
                        contribution=0.0,
                        contributing_evidence_ids=[],
                        contributing_match_edge_id=None
                    )
                    atom_explanations.append(f"'{req.raw_value}' requirement received GAP coverage (no matching evidence).")
                    
                atom_scores.append(a_score)
                req_coverage = a_score.contribution
            else:
                for atom in req.atoms:
                    best_edge = None
                    best_contribution = -1.0
                    
                    # Sort edges deterministically just in case (e.g. by edge_id) to guarantee deterministic selection
                    sorted_req_edges = sorted(req_edges, key=lambda x: x.edge_id)
                    
                    for edge in sorted_req_edges:
                        if atom.atom_id in edge.satisfied_atoms:
                            contrib = self.config.MATCH_CONTRIBUTIONS.get(edge.match_type, 0.0)
                            if contrib > best_contribution:
                                best_contribution = contrib
                                best_edge = edge
                                
                    if best_edge:
                        a_score = AtomScore(
                            atom_id=atom.atom_id,
                            atom_text=atom.raw_value,
                            match_type=best_edge.match_type,
                            contribution=best_contribution,
                            contributing_evidence_ids=best_edge.evidence_ids,
                            contributing_match_edge_id=best_edge.edge_id
                        )
                        contributing_atom_ids.add(atom.atom_id)
                        contributing_evidence_ids.update(best_edge.evidence_ids)
                        contributing_match_edge_ids.add(best_edge.edge_id)
                        
                        ev_str = ", ".join(best_edge.evidence_ids) if best_edge.evidence_ids else "None"
                        expl = f"'{atom.raw_value}' requirement atom received {best_edge.match_type} coverage from evidence {ev_str} through MatchEdge {best_edge.edge_id}."
                        if best_edge.match_type == "TRANSFERABLE":
                            expl += f" Reason: {best_edge.decision_reason}"
                        atom_explanations.append(expl)
                    else:
                        a_score = AtomScore(
                            atom_id=atom.atom_id,
                            atom_text=atom.raw_value,
                            match_type="GAP",
                            contribution=0.0,
                            contributing_evidence_ids=[],
                            contributing_match_edge_id=None
                        )
                        atom_explanations.append(f"'{atom.raw_value}' requirement atom received GAP coverage (no matching evidence).")
                    atom_scores.append(a_score)
                
                req_coverage = sum(a.contribution for a in atom_scores) / len(atom_scores)
            
            # Qualifier Evaluations
            qual_explanations = []
            # Gather unique qualifier evals across best edges used
            seen_quals = set()
            for edge in req_edges:
                if edge.edge_id in contributing_match_edge_ids and edge.qualifier_results:
                    for k, v in edge.qualifier_results.items():
                        q_key = f"{edge.edge_id}_{k}"
                        if q_key not in seen_quals:
                            seen_quals.add(q_key)
                            passed = (v == QualifierStatus.SATISFIED)
                            qual_evals.append(QualifierEvaluation(
                                qualifier_type=k,
                                expected="Required in JD",
                                actual="Extracted from Resume",
                                passed=passed
                            ))
                            if not passed:
                                qual_explanations.append(f"Qualifier {k} was NOT_SATISFIED (Edge: {edge.edge_id}), reducing coverage.")

            # Construct full explanation
            lines = [
                f"Weight: {weight:.2f}, Coverage: {req_coverage:.2f}",
                "Atom Breakdown:"
            ] + ["- " + ax for ax in atom_explanations]
            
            if qual_explanations:
                lines.append("Qualifier Breakdown:")
                lines.extend(["- " + qx for qx in qual_explanations])
                
            full_explanation = "\n".join(lines)

            req_score = RequirementScore(
                requirement_id=req.requirement_id,
                requirement_text=req.raw_value,
                requirement_type=req.requirement_type,
                is_hard_constraint=is_hard,
                weight=weight,
                coverage=req_coverage,
                requirement_score=weight * req_coverage,
                contributing_atom_ids=sorted(list(contributing_atom_ids)),
                contributing_evidence_ids=sorted(list(contributing_evidence_ids)),
                contributing_match_edge_ids=sorted(list(contributing_match_edge_ids)),
                atom_scores=atom_scores,
                qualifier_evaluations=qual_evals,
                deterministic_explanation=full_explanation
            )
            req_scores.append(req_score)
            
            if is_hard and req_coverage == 0.0:
                hard_constraints_failed.append(req.requirement_id)
                
            if req.requirement_type == "REQUIRED":
                total_required_weight += weight
                total_required_coverage += (weight * req_coverage)
            elif req.requirement_type == "PREFERRED":
                total_preferred_weight += weight
                total_preferred_coverage += (weight * req_coverage)

        total_weight = total_required_weight + total_preferred_weight
        if total_weight > 0:
            base_score = 100.0 * ((total_required_coverage + total_preferred_coverage) / total_weight)
        else:
            base_score = 0.0
            
        constraint_gate = 1.0
        if len(hard_constraints_failed) > 0:
            constraint_gate = self.config.HARD_CONSTRAINT_GATE_MULTIPLIER
            
        final_score = base_score * constraint_gate

        req_cov_perc = (total_required_coverage / total_required_weight) if total_required_weight > 0 else 0.0
        pref_cov_perc = (total_preferred_coverage / total_preferred_weight) if total_preferred_weight > 0 else 0.0

        return Phase5Score(
            scoring_config_version=self.config.VERSION,
            base_score=base_score,
            constraint_gate=constraint_gate,
            final_score=final_score,
            required_coverage=req_cov_perc,
            preferred_coverage=pref_cov_perc,
            requirement_scores=req_scores,
            hard_constraints_failed=sorted(hard_constraints_failed)
        )
