import uuid
from app.resume_jd.parsing.jd.hybrid_parser import HybridJDParser
from app.resume_jd.models.canonical_jd import CanonicalJD
from app.resume_jd.models.canonical_models import CanonicalItem
from app.resume_jd.matching.normalizer import SkillNormalizer
from app.services.skill_extractor import SkillExtractor

class JDAdapter:
    """
    Phase 2: Canonicalization Adapter for Job Descriptions.
    Takes output from the existing HybridJDParser and converts it into standard CanonicalItems.
    """
    def __init__(self):
        self.parser = HybridJDParser()
        self.skill_extractor = SkillExtractor()
        self.normalizer = SkillNormalizer()

    def adapt(self, jd_text: str, job_title: str = None) -> CanonicalJD:
        # Phase 1: Document Parsing via existing parser
        canonical_jd = self.parser.parse(jd_text, job_title)
        
        items = []
        
        for req in canonical_jd.requirements:
            # Phase 2: Create CanonicalItems
            raw_skills = self.skill_extractor.extract_skills(req.raw_text)
            
            if not raw_skills:
                # Try to normalize the entire raw text just in case it is a single skill phrase
                normalized_full = self.normalizer.normalize(req.raw_text)
                
                # Add as non-skill item or normalized phrase
                items.append(CanonicalItem(
                    id=f"jd_{uuid.uuid4().hex[:8]}",
                    raw_value=req.raw_text,
                    normalized_value=normalized_full,
                    category=req.category,
                    provenance=req.provenance,
                    source_location=f"Section: {req.source_section}",
                    confidence=req.confidence,
                    requirement_type=req.requirement_type,
                    weight=req.weight
                ))
            else:
                for skill in raw_skills:
                    normalized = self.normalizer.normalize(skill)
                    items.append(CanonicalItem(
                        id=f"jd_{uuid.uuid4().hex[:8]}",
                        raw_value=skill,
                        normalized_value=normalized,
                        category="TECHNOLOGY" if req.category == "SKILL" else req.category,
                        provenance=req.provenance,
                        source_location=f"Section: {req.source_section}",
                        confidence=req.confidence,
                        requirement_type=req.requirement_type,
                        weight=req.weight
                    ))
        
        canonical_jd.items = items
        return canonical_jd
