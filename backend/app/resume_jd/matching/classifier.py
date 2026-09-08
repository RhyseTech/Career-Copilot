from typing import Dict, Any

class MatchClassifier:
    def __init__(self):
        # Conservative thresholds to avoid false positives
        self.exact_thresh_fuzzy = 0.95
        self.related_thresh_sem = 0.80
        self.related_thresh_fuzzy = 0.40
        self.partial_thresh_fuzzy = 0.60
        self.partial_thresh_sem = 0.70
        self.transf_thresh_sem = 0.50

    def classify(self, scores: Dict[str, float], canonical_overlap: bool) -> str:
        """
        Classifies the match into one of: Exact, Related, Partial, Transferable, Gap
        """
        exact = scores.get("exact", 0.0)
        fuzzy = scores.get("fuzzy", 0.0)
        semantic = scores.get("semantic", 0.0)
        
        # 1. Exact
        # Require canonical overlap AND a decent semantic score to ensure context (like years) is covered
        # Or require very high fuzzy/exact match
        if exact == 1.0 or fuzzy >= self.exact_thresh_fuzzy or (canonical_overlap and semantic >= 0.70):
            return "Exact"
            
        # 2. Related
        if semantic >= self.related_thresh_sem and fuzzy >= self.related_thresh_fuzzy:
            return "Related"
            
        # 3. Partial
        # If there's canonical overlap but low semantic match, it's partially covered (e.g. missing years)
        if canonical_overlap or fuzzy >= self.partial_thresh_fuzzy or semantic >= self.partial_thresh_sem:
            return "Partial"
            
        # 4. Transferable
        if semantic >= self.transf_thresh_sem:
            return "Transferable"
            
        # 5. Gap
        return "Gap"
