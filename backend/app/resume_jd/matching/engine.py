from typing import Dict, Any, List
from app.resume_jd.adapters.jd_adapter import JDAdapter
from app.resume_jd.adapters.resume_adapter import ResumeAdapter
from app.resume_jd.matching.similarity import SimilarityEngine
from app.resume_jd.matching.classifier import MatchClassifier
from app.resume_jd.storage.json_store import JSONStore

class MatchEngine:
    def __init__(self):
        self.jd_adapter = JDAdapter()
        self.resume_adapter = ResumeAdapter()
        self.similarity = SimilarityEngine()
        self.classifier = MatchClassifier()
        self.json_store = JSONStore()

    def process(self, resume_file_path: str, jd_text: str) -> Dict[str, Any]:
        """
        Main pipeline:
        1. Parse & Canonicalize JD -> CanonicalJD (and save to JSON)
        2. Parse & Canonicalize Resume -> CanonicalResume
        3. For each requirement, find best evidence and classify match type
        """
        # Phase 2 Adaptation
        canonical_jd = self.jd_adapter.adapt(jd_text)
        self.json_store.save_canonical_jd(canonical_jd)
        
        canonical_resume = self.resume_adapter.process_file(resume_file_path, "resume.pdf")
        
        results = []
        
        for req in canonical_jd.items:
            best_evidence = None
            best_scores = {"exact": 0.0, "fuzzy": 0.0, "semantic": 0.0}
            best_combined_score = -1.0
            
            # Use normalized_value or fallback to raw_value
            req_canonical = {req.normalized_value} if req.normalized_value else {req.raw_value}
            req_text = req.raw_value
            
            for ev in canonical_resume.items:
                ev_canonical = {ev.normalized_value} if ev.normalized_value else {ev.raw_value}
                
                # Check canonical overlap
                canonical_overlap = bool(req_canonical and req_canonical.intersection(ev_canonical))
                
                # Compute similarities
                scores = self.similarity.compute_similarity(req_text, ev.raw_value)
                
                # Simple heuristic to pick the "best" evidence
                combined_score = scores["semantic"] + (0.5 if canonical_overlap else 0.0) + (0.2 * scores["fuzzy"])
                
                if combined_score > best_combined_score:
                    best_combined_score = combined_score
                    best_scores = scores
                    best_evidence = ev
                    
            # Classify using the best found evidence
            if best_evidence:
                canonical_overlap = bool(req_canonical and req_canonical.intersection({best_evidence.normalized_value} if best_evidence.normalized_value else {best_evidence.raw_value}))
                label = self.classifier.classify(best_scores, canonical_overlap)
            else:
                label = "Gap"
            results.append({
                "requirement_id": req.id,
                "text": req.raw_value,
                "type": req.category,
                "required": req.requirement_type == "REQUIRED" if hasattr(req, "requirement_type") else False,
                "canonical_skills": list(req_canonical),
                "match": {
                    "label": label,
                    "evidence": {
                        "section": best_evidence.source_location if best_evidence else "",
                        "text_span": best_evidence.raw_value if best_evidence else "",
                        "canonical_skills": [best_evidence.normalized_value] if best_evidence and best_evidence.normalized_value else [],
                    } if best_evidence else {},
                    "similarity_scores": best_scores
                }
            })
            
        return {"requirements": results}
