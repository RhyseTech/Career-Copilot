import re
import uuid
from typing import List, Dict, Any
from app.services.parser import ResumeParser
from app.services.skill_extractor import SkillExtractor
from app.resume_jd.matching.normalizer import SkillNormalizer
from app.resume_jd.models.canonical_models import CanonicalResume, CanonicalItem

class ResumeAdapter:
    """
    Phase 2: Canonicalization Adapter for Resumes.
    Converts raw parsed resume data into CanonicalResume.
    """
    def __init__(self):
        self.base_parser = ResumeParser()
        self.skill_extractor = SkillExtractor()
        self.normalizer = SkillNormalizer()

    def process_file(self, file_path: str, filename: str) -> CanonicalResume:
        # Phase 1: Document Parsing (via existing parser)
        parsed_data = self.base_parser.parse_resume(file_path)
        sections = parsed_data.get("sections", {})
        
        items: List[CanonicalItem] = []
        resume_id = str(uuid.uuid4())
        
        for section_name, content in sections.items():
            if not content.strip():
                continue
                
            # Phase 1 chunking for evidence tracking
            chunks = re.split(r'\n|•|- ', content)
            
            for chunk in chunks:
                text_span = chunk.strip()
                if len(text_span) < 5:
                    continue
                    
                # Extract structured attributes
                raw_skills = self.skill_extractor.extract_skills(text_span)
                
                # Phase 2 Canonicalization for skills
                for raw_skill in raw_skills:
                    normalized_skill = self.normalizer.normalize(raw_skill)
                    
                    items.append(CanonicalItem(
                        id=f"res_{uuid.uuid4().hex[:8]}",
                        raw_value=raw_skill,
                        normalized_value=normalized_skill,
                        category="TECHNOLOGY" if section_name.lower() == "skills" else "SKILL",
                        provenance="EXTRACTED",
                        source_location=f"Section: {section_name}",
                        confidence=0.9
                    ))
                
                # Extract Experience
                years_match = re.search(r'\b(\d+)\+?\s*years?\b', text_span, re.IGNORECASE)
                if years_match:
                    years_text = years_match.group(0)
                    items.append(CanonicalItem(
                        id=f"res_{uuid.uuid4().hex[:8]}",
                        raw_value=years_text,
                        normalized_value=years_text, # Experience is not normalized into a skill
                        category="EXPERIENCE",
                        provenance="EXTRACTED",
                        source_location=f"Section: {section_name}",
                        confidence=0.9
                    ))
                    
        return CanonicalResume(
            resume_id=resume_id,
            file_name=filename,
            items=items
        )
