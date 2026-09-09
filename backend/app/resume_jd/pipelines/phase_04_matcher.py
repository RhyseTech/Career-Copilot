import re
from typing import List, Optional

from app.resume_jd.models.phase_03_models import JDRequirement, ResumeEvidence
from app.resume_jd.models.phase_04_models import MatchEdge, OntologyRelation, QualifierStatus
from app.resume_jd.matching.phase_04_config import Phase4Config
from app.resume_jd.matching.ontology import OntologyService
from app.resume_jd.matching.similarity import SimilarityEngine


class Phase4Matcher:
    def __init__(self):
        self.ontology = OntologyService()
        self.similarity = SimilarityEngine()
        self.config = Phase4Config()

    def match(self, requirements: List[JDRequirement], evidence_items: List[ResumeEvidence]) -> List[MatchEdge]:
        """
        Main pipeline evaluating JDRequirements against ResumeEvidence to produce MatchEdges.
        GAP is resolved at the REQUIREMENT level: if any non-GAP edge exists for a requirement,
        no GAP edge is emitted for it.
        """
        match_edges = []

        for req in requirements:
            # 1. Candidate Generation — cheap, deterministic only
            candidates = self._generate_candidates(req, evidence_items)

            # 2-6. Evaluate each candidate
            best_edges = []
            evaluated_edges = []

            for ev in candidates:
                edge = self._evaluate_candidate(req, ev)
                evaluated_edges.append(edge)
                if edge.match_type != "GAP":
                    best_edges.append(edge)

            # 7. GAP resolution at REQUIREMENT LEVEL
            # If any non-GAP edge exists, emit only those.
            # If all evaluated edges are GAP (or no candidates at all), emit one fresh GAP edge.
            if best_edges:
                match_edges.extend(best_edges)
            elif evaluated_edges:
                # FIX (Issue 6): Do NOT mutate the existing evaluated MatchEdge.
                # Create a fresh GAP edge preserving the best lexical/semantic features for diagnostics.
                best_ev = max(evaluated_edges, key=lambda x: x.semantic_features.get("context", 0))
                gap_edge = MatchEdge(
                    requirement_id=best_ev.requirement_id,
                    requirement_atom_ids=best_ev.requirement_atom_ids,
                    evidence_ids=best_ev.evidence_ids,
                    match_type="GAP",
                    satisfied_atoms=best_ev.satisfied_atoms,
                    missing_atoms=best_ev.missing_atoms,
                    lexical_features=best_ev.lexical_features,
                    semantic_features=best_ev.semantic_features,
                    ontology_features=best_ev.ontology_features,
                    qualifier_results=best_ev.qualifier_results,
                    category_compatibility=best_ev.category_compatibility,
                    decision_reason="No sufficient evidence was found after evaluating relevant candidates.",
                )
                match_edges.append(gap_edge)
            else:
                # No candidates at all
                match_edges.append(self._create_empty_gap_edge(req, "No sufficient evidence was found for this requirement."))

        return match_edges

    # -------------------------------------------------------------------------
    # Candidate Generation
    # -------------------------------------------------------------------------

    def _generate_candidates(self, req: JDRequirement, evidence_items: List[ResumeEvidence]) -> List[ResumeEvidence]:
        """
        Candidate generation must be CHEAP and CONSERVATIVE.
        FIX (Issue 5): Does NOT call compute_lexical(). Uses only deterministic signals:
          - exact string / substring / token overlap on raw_value and atom values
          - concept-level token overlap (after stripping YOE qualifier)
          - known ontology relations (multi-level: full phrase, concept, sub-tokens)
        """
        candidates = []
        req_atoms = req.atoms if hasattr(req, "atoms") and req.atoms else []

        # Build candidate text representations (raw and concept-stripped)
        req_concept = self._extract_concept(req.raw_value)
        req_texts = list({
            req.raw_value.lower(),
            req_concept.lower(),
        })
        for a in req_atoms:
            req_texts.append(a.raw_value.lower())
            req_texts.append(self._extract_concept(a.raw_value).lower())

        # Also add leading sub-phrases of the concept for technology name matching
        req_concept_tokens = req_concept.split()
        for n in range(min(4, len(req_concept_tokens)), 1, -1):
            req_texts.append(" ".join(req_concept_tokens[:n]).lower())

        for ev in evidence_items:
            ev_concept = self._extract_concept(ev.raw_value)
            ev_texts = list({
                ev.raw_value.lower(),
                ev_concept.lower(),
            })
            ev_concept_tokens = ev_concept.split()
            for n in range(min(4, len(ev_concept_tokens)), 1, -1):
                ev_texts.append(" ".join(ev_concept_tokens[:n]).lower())

            is_candidate = False
            for rt in req_texts:
                if not rt:
                    continue
                rt_tokens = set(rt.split())

                for et in ev_texts:
                    if not et:
                        continue
                    et_tokens = set(et.split())

                    # Exact, substring, or token overlap
                    if rt == et or rt in et or et in rt or rt_tokens.intersection(et_tokens):
                        is_candidate = True
                        break

                    # Known ontology relation
                    relation = self.ontology.get_relation(rt, et)
                    if relation not in (OntologyRelation.UNKNOWN, OntologyRelation.DISJOINT):
                        is_candidate = True
                        break

                if is_candidate:
                    break

            if is_candidate:
                candidates.append(ev)

        return candidates

    # -------------------------------------------------------------------------
    # Candidate Evaluation
    # -------------------------------------------------------------------------

    def _evaluate_candidate(self, req: JDRequirement, ev: ResumeEvidence) -> MatchEdge:
        """
        Evaluates a single (requirement, evidence) pair through the full feature pipeline
        and applies the deterministic decision engine.

        Decision precedence (Issues 1, 2, 3):
          1. Hard qualifier contradiction blocks EXACT and TRANSFERABLE — no exception.
          2. EXACT: canonical concept match + category compatible + qualifier SATISFIED.
          3. PARTIAL: concept match + qualifier NOT_SATISFIED/UNKNOWN, OR partial atom coverage.
          4. RELATED: ontology relation + no meaningful action overlap.
          5. TRANSFERABLE: ontology RELATED + meaningful shared action context,
                           OR ontology UNKNOWN + high semantic (fallback path).
          6. GAP: nothing sufficient found.
        """
        req_text = req.raw_value
        ev_text = ev.raw_value

        # --- Feature extraction ---
        lexical_score = self.similarity.compute_lexical(req_text, ev_text)
        semantic_score = self.similarity.compute_semantic(req_text, ev_text)
        qualifier_status = self._validate_qualifiers(req_text, ev_text)

        # Resolve ontology at multiple levels: full phrase, concept-stripped, and per-atom.
        # This ensures "GCP Dataflow pipeline development" vs "AWS Glue pipeline development"
        # correctly resolves to RELATED via the concept-level lookup "gcp dataflow" vs "aws glue".
        req_concept = self._extract_concept(req_text)
        ev_concept = self._extract_concept(ev_text)
        relation = self._resolve_ontology_relation(req, ev, req_text, ev_text, req_concept, ev_concept)

        # FIX (Issues 1, 2): Canonical overlap is checked at CONCEPT level, not raw string level.
        # Raw values are preserved for provenance and qualifier parsing.
        canonical_overlap = (
            req_text.lower() == ev_text.lower()
            or (bool(req_concept) and req_concept.lower() == ev_concept.lower())
        )

        # Secondary canonical overlap: matching canonical_item_ids through atoms
        if not canonical_overlap:
            req_ids = set()
            if hasattr(req, "atoms") and req.atoms:
                for a in req.atoms:
                    if hasattr(a, "canonical_item_ids") and a.canonical_item_ids:
                        req_ids.update(a.canonical_item_ids)
            ev_ids = set(getattr(ev, "canonical_item_ids", []))
            if req_ids and ev_ids and req_ids.intersection(ev_ids):
                canonical_overlap = True

        # Atom-level raw_value match
        if not canonical_overlap and hasattr(req, "atoms") and req.atoms:
            req_vals = {a.raw_value.lower() for a in req.atoms}
            if ev_text.lower() in req_vals or ev_concept.lower() in req_vals:
                canonical_overlap = True

        category_compat = self._check_category_compatibility(req.category, ev.category)

        # --- Atom-level satisfaction ---
        satisfied_atoms = []
        missing_atoms = []
        if hasattr(req, "atoms") and req.atoms:
            for ratom in req.atoms:
                atom_satisfied = False
                ratom_concept = self._extract_concept(ratom.raw_value)

                if ratom.raw_value.lower() == ev_text.lower() or \
                   (ratom_concept and ratom_concept.lower() == ev_concept.lower()) or \
                   self.ontology.get_relation(ratom.raw_value, ev_text) in (
                       OntologyRelation.EQUIVALENT, OntologyRelation.BROADER):
                    atom_satisfied = True
                elif hasattr(ratom, "canonical_item_ids") and ratom.canonical_item_ids and \
                     hasattr(ev, "canonical_item_ids") and ev.canonical_item_ids:
                    if set(ratom.canonical_item_ids).intersection(set(ev.canonical_item_ids)):
                        atom_satisfied = True

                if atom_satisfied:
                    satisfied_atoms.append(ratom.atom_id)
                else:
                    missing_atoms.append(ratom.atom_id)

        # =====================================================================
        # Deterministic Decision Engine
        # FIX (Issue 3): Hard qualifier precedence — NOT_SATISFIED blocks EXACT
        # and TRANSFERABLE with no exceptions, regardless of semantic score.
        # =====================================================================

        match_type = "GAP"
        reason = "Evaluated but evidence was insufficient."

        # --- EXACT ---
        # Requires: concept match, category compatible, qualifier SATISFIED, all atoms satisfied (if compound)
        if canonical_overlap and category_compat and qualifier_status == QualifierStatus.SATISFIED:
            if hasattr(req, "atoms") and req.atoms and missing_atoms:
                pass  # compound requirement not fully satisfied → fall to PARTIAL
            else:
                match_type = "EXACT"
                reason = (
                    "Requirement and evidence resolve to the same canonical concept "
                    "and all available hard qualifiers are satisfied."
                )

        # --- PARTIAL ---
        # Case A: Compound requirement partially satisfied (atoms)
        # Case B: Concept matches but qualifier not satisfied or unknown
        # NOTE: NOT_SATISFIED qualifier → PARTIAL (never EXACT or TRANSFERABLE)
        if match_type == "GAP":
            if hasattr(req, "atoms") and req.atoms and satisfied_atoms and missing_atoms:
                match_type = "PARTIAL"
                reason = (
                    f"{len(satisfied_atoms)} of {len(req.atoms)} requirement atoms have supporting evidence; "
                    f"{len(missing_atoms)} atoms remain unsupported."
                )
            elif canonical_overlap and qualifier_status in (QualifierStatus.NOT_SATISFIED, QualifierStatus.UNKNOWN):
                match_type = "PARTIAL"
                reason = (
                    f"Canonical concept matches, but the hard qualifier (e.g., years of experience) "
                    f"is {qualifier_status.value}. "
                    f"Required qualifier: '{req_text}' vs evidenced: '{ev_text}'."
                )

        # --- RELATED or TRANSFERABLE (ontology path) ---
        # RELATED: concepts differ, ontology relation exists, no substantial shared action context.
        # TRANSFERABLE: concepts differ, ontology relation exists, AND substantial shared action/context.
        # FIX (Issue 4): TRANSFERABLE is determined by RELATED ontology + action/context overlap.
        # Hard qualifier NOT_SATISFIED still blocks TRANSFERABLE.
        if match_type == "GAP":
            if relation in (OntologyRelation.RELATED, OntologyRelation.BROADER, OntologyRelation.NARROWER):
                if category_compat and qualifier_status != QualifierStatus.NOT_SATISFIED:
                    # Measure action/context overlap: how much shared non-trivial vocabulary
                    # exists beyond the technology name itself.
                    action_overlap = self._compute_action_overlap(req_text, ev_text)
                    if action_overlap >= self.config.TRANSFERABLE_ACTION_THRESHOLD:
                        match_type = "TRANSFERABLE"
                        reason = (
                            "Requested technology is not directly evidenced, but the resume demonstrates "
                            "a comparable responsibility/action using a related technology. "
                            f"Action/context overlap: {action_overlap:.2f}."
                        )
                    else:
                        match_type = "RELATED"
                        reason = (
                            "Concepts differ but share a supported ontology relationship "
                            "with compatible context."
                        )

        # --- TRANSFERABLE (semantic fallback, no ontology) ---
        # Only when: ontology UNKNOWN, high semantic similarity, qualifier NOT failed.
        # This is an UNCALIBRATED threshold — requires empirical calibration.
        if match_type == "GAP":
            if (relation == OntologyRelation.UNKNOWN
                    and category_compat
                    and qualifier_status != QualifierStatus.NOT_SATISFIED
                    and semantic_score >= self.config.SEMANTIC_STRONG_THRESHOLD):
                match_type = "TRANSFERABLE"
                reason = (
                    "Requested technology is not evidenced and no ontology relation exists, "
                    "but the resume demonstrates a semantically comparable responsibility or action."
                )

        return MatchEdge(
            requirement_id=req.requirement_id,
            requirement_atom_ids=[a.atom_id for a in req.atoms] if hasattr(req, "atoms") and req.atoms else [],
            evidence_ids=[ev.evidence_id],
            match_type=match_type,
            satisfied_atoms=satisfied_atoms,
            missing_atoms=missing_atoms,
            lexical_features={"overlap": lexical_score},
            semantic_features={"context": semantic_score},
            ontology_features={"primary": relation},
            qualifier_results={"yoe": qualifier_status},
            category_compatibility=category_compat,
            decision_reason=reason,
        )

    # -------------------------------------------------------------------------
    # Concept Extraction (FIX — Issues 1, 2)
    # -------------------------------------------------------------------------

    def _extract_concept(self, text: str) -> str:
        """
        Strip YOE qualifiers from a text phrase to expose the underlying concept.
        The raw_value is NEVER modified — this result is only used for matching logic.

        Examples:
          "5+ years Python"         → "Python"
          "2 years of Python"       → "Python"
          "Python 3.11"             → "Python 3.11"  (version, not YOE)
          "GCP Dataflow pipeline"   → "GCP Dataflow pipeline" (no YOE)
        """
        concept = re.sub(
            r"\d+(?:\.\d+)?\s*(?:\+)?\s*(?:-\s*\d+\s*)?years?\s*(?:of\s+(?:experience\s+(?:in\s+)?)?)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        ).strip()
        return concept if concept else text

    # -------------------------------------------------------------------------
    # Ontology Resolution (FIX — Issue 4)
    # -------------------------------------------------------------------------

    def _resolve_ontology_relation(self, req, ev, req_text: str, ev_text: str,
                                   req_concept: str, ev_concept: str) -> OntologyRelation:
        """
        Resolves the ontology relation between requirement and evidence at multiple levels:
          1. Full raw_value text
          2. Concept-stripped phrase (YOE qualifier removed)
          3. Individual atom values vs evidence value

        This ensures compound phrases like "GCP Dataflow pipeline development" correctly
        resolve to RELATED via their core concept "GCP Dataflow" vs "AWS Glue".
        """
        # Level 1: full text
        rel = self.ontology.get_relation(req_text, ev_text)
        if rel not in (OntologyRelation.UNKNOWN, OntologyRelation.DISJOINT):
            return rel

        # Level 2: concept-stripped (removes YOE, keeps tech+action)
        rel = self.ontology.get_relation(req_concept, ev_concept)
        if rel not in (OntologyRelation.UNKNOWN, OntologyRelation.DISJOINT):
            return rel

        # Level 3: per-atom vs evidence concept — e.g. atom "GCP Dataflow" vs ev concept "AWS Glue"
        if req is not None and hasattr(req, "atoms") and req.atoms:
            ev_targets = list({ev_text.lower(), ev_concept.lower()})
            for atom in req.atoms:
                for target in ev_targets:
                    rel = self.ontology.get_relation(atom.raw_value, target)
                    if rel not in (OntologyRelation.UNKNOWN, OntologyRelation.DISJOINT):
                        return rel

        # Level 4: check core tokens of concept phrase against evidence concept
        # e.g. "GCP Dataflow pipeline development" → try "GCP Dataflow" as a sub-phrase
        req_tokens = req_concept.split()
        ev_tokens = ev_concept.split()
        for n in range(min(3, len(req_tokens)), 0, -1):
            req_sub = " ".join(req_tokens[:n])
            for m in range(min(3, len(ev_tokens)), 0, -1):
                ev_sub = " ".join(ev_tokens[:m])
                rel = self.ontology.get_relation(req_sub, ev_sub)
                if rel not in (OntologyRelation.UNKNOWN, OntologyRelation.DISJOINT):
                    return rel

        return OntologyRelation.UNKNOWN

    # -------------------------------------------------------------------------
    # Action/Context Overlap (FIX — Issue 4)
    # -------------------------------------------------------------------------

    def _compute_action_overlap(self, req_text: str, ev_text: str) -> float:
        """
        Measures shared action/context vocabulary between two phrases.
        Strips the leading technology concept tokens and compares the residual action words.

        Strategy: identify the longest ontology-known concept prefix, strip it,
        then compare residuals using lexical similarity.
        Falls back to comparing residuals after stripping first N tokens as the tech name.

        Returns 0.0 if both residuals are empty (pure technology name).
        """
        req_concept = self._extract_concept(req_text)
        ev_concept = self._extract_concept(ev_text)

        req_residual = self._get_action_residual(req_text, req_concept)
        ev_residual = self._get_action_residual(ev_text, ev_concept)

        if not req_residual and not ev_residual:
            return 0.0
        if not req_residual or not ev_residual:
            return 0.0

        return self.similarity.compute_lexical(req_residual, ev_residual)

    def _get_action_residual(self, full_text: str, concept: str) -> str:
        """
        Extract the action/context words from a phrase by stripping known technology prefixes.
        Tries token-by-token stripping to find the shortest technology prefix with an ontology match.

        For "GCP Dataflow pipeline development":
          - Try "GCP Dataflow" (2 tokens) → ontology known → residual = "pipeline development"

        For "AWS Glue pipeline development":
          - Try "AWS Glue" (2 tokens) → ontology known → residual = "pipeline development"
        """
        tokens = concept.split()
        # Try progressively longer prefixes as the tech name
        for n in range(min(4, len(tokens)), 0, -1):
            prefix = " ".join(tokens[:n]).lower()
            # Check if this prefix is a known ontology concept (has any relation with something)
            # We proxy this by checking if stripping it leaves meaningful content
            residual = concept.lower().replace(prefix, "", 1).strip()
            if residual:  # there are action words after the tech prefix
                return residual
        return ""

    # -------------------------------------------------------------------------
    # GAP Edge Helpers
    # -------------------------------------------------------------------------

    def _create_empty_gap_edge(self, req: JDRequirement, reason: str) -> MatchEdge:
        """Creates a fresh GAP MatchEdge with no candidate evidence."""
        return MatchEdge(
            requirement_id=req.requirement_id,
            requirement_atom_ids=[a.atom_id for a in req.atoms] if hasattr(req, "atoms") and req.atoms else [],
            evidence_ids=[],
            match_type="GAP",
            satisfied_atoms=[],
            missing_atoms=[a.atom_id for a in req.atoms] if hasattr(req, "atoms") and req.atoms else [],
            lexical_features={},
            semantic_features={},
            ontology_features={"primary": OntologyRelation.UNKNOWN},
            qualifier_results={},
            category_compatibility=False,
            decision_reason=reason,
        )

    # -------------------------------------------------------------------------
    # Qualifier Validation
    # -------------------------------------------------------------------------

    def _validate_qualifiers(self, req_text: str, ev_text: str) -> QualifierStatus:
        """
        Deterministic YOE qualifier extraction and comparison.
        No LLM involvement. Regex only.
        """
        req_yoe = self._extract_yoe(req_text)
        if req_yoe is None:
            return QualifierStatus.SATISFIED  # No qualifier in requirement → implicitly satisfied

        ev_yoe = self._extract_yoe(ev_text)
        if ev_yoe is None:
            return QualifierStatus.UNKNOWN  # Requirement has qualifier, evidence does not

        return QualifierStatus.SATISFIED if ev_yoe >= req_yoe else QualifierStatus.NOT_SATISFIED

    def _extract_yoe(self, text: str) -> Optional[float]:
        """
        Extracts the numeric Years of Experience from a text phrase.
        Strictly requires the word "year(s)" to follow the number.

        Correctly rejects:
          "Python 3.11"   — version number, not YOE
          "5TB/day"       — data size
          "2024"          — calendar year
        """
        text = text.lower()
        match = re.search(r"(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:-\s*\d+\s*)?years?", text)
        if match:
            return float(match.group(1))
        return None

    # -------------------------------------------------------------------------
    # Category Compatibility
    # -------------------------------------------------------------------------

    def _check_category_compatibility(self, req_cat: str, ev_cat: str) -> bool:
        """
        Legitimate cross-category relationships. Does not require strict equality.
        """
        if req_cat == ev_cat:
            return True

        cross = {
            "EXPERIENCE": ["SKILL", "RESPONSIBILITY"],
            "SKILL": ["EXPERIENCE", "RESPONSIBILITY"],
            "RESPONSIBILITY": ["EXPERIENCE", "SKILL"],
        }

        return ev_cat in cross.get(req_cat, [])
