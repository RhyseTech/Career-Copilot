import uuid
import hashlib
from typing import List, Optional
from app.resume_jd.models.canonical_jd import CanonicalJD, Requirement
from app.resume_jd.parsing.jd.sectionizer import Sectionizer
from app.resume_jd.parsing.jd.llm_extractor import LLMExtractor
from app.services.skill_extractor import SkillExtractor
from app.resume_jd.matching.normalizer import SkillNormalizer

class HybridJDParser:
    def __init__(self):
        self.sectionizer = Sectionizer()
        self.llm_extractor = LLMExtractor()
        self.skill_extractor = SkillExtractor()
        self.normalizer = SkillNormalizer()

    def parse(self, raw_text: str, job_title: Optional[str] = None) -> CanonicalJD:
        """
        Parses JD text using a hybrid strategy (deterministic sections + LLM extraction).
        Validates LLM extraction to prevent hallucinations.
        """
        # Deterministically split text into sections
        sections = self.sectionizer.extract_sections(raw_text)
        
        all_requirements: List[Requirement] = []
        
        # Combine all sections into a single structured text to batch the LLM extraction
        batched_text = ""
        for section_name, section_text in sections.items():
            if section_text.strip():
                batched_text += f"\n--- SECTION: {section_name} ---\n{section_text}\n"

        if not batched_text:
            return CanonicalJD(
                jd_id=str(uuid.uuid4()),
                content_hash=hashlib.sha256(raw_text.encode('utf-8')).hexdigest(),
                job_title=job_title,
                raw_text=raw_text,
                requirements=[]
            )

        # Make ONE LLM call to extract requirements from all sections
        extracted_items = self.llm_extractor.extract_requirements(batched_text, "All Sections")
        
        for item in extracted_items:
            raw_extracted_text = item.get("raw_text", "")
            source_span = item.get("source_span", "")
            # The LLM should return the section name, but if it doesn't, we can fall back
            section_name = item.get("source_section", "Unknown")
            
            if not raw_extracted_text or not source_span:
                continue
                
            # VALIDATION: Anti-Hallucination check
            if source_span not in raw_text:
                print(f"[REJECTED] LLM hallucinated source span: '{source_span}'")
                continue
                
            # Determine weight based on type
            weight = 1.0
            req_type = item.get("requirement_type", "PREFERRED").upper()
            if req_type == "REQUIRED":
                weight += 0.5
                
            cat = item.get("category", "GENERAL").upper()
            if cat in ["EXPERIENCE", "EDUCATION"]:
                weight += 0.2
                
            # Extract canonical skills
            raw_skills = self.skill_extractor.extract_skills(raw_extracted_text)
            canonical_skills = self.normalizer.normalize_list(raw_skills)
            
            req = Requirement(
                requirement_id=f"req_{uuid.uuid4().hex[:8]}",
                requirement_type=req_type if req_type in ["REQUIRED", "PREFERRED"] else "PREFERRED",
                category=cat if cat in ["SKILL", "EXPERIENCE", "EDUCATION", "CERTIFICATION", "GENERAL"] else "GENERAL",
                raw_text=raw_extracted_text,
                source_span=source_span,
                source_section=section_name,
                confidence=0.9,
                provenance="EXTRACTED",
                weight=weight,
                canonical_skills=canonical_skills
            )
            
            all_requirements.append(req)

        # Generate hashes and IDs
        content_hash = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()
        jd_id = str(uuid.uuid4())
        
        return CanonicalJD(
            jd_id=jd_id,
            content_hash=content_hash,
            job_title=job_title,
            raw_text=raw_text,
            requirements=all_requirements
        )
