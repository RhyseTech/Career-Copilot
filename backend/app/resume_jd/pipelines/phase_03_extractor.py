import json
import uuid
from typing import List, Dict, Any, Optional

from app.services.llm_optimizer import LLMOptimizer
from app.resume_jd.models.canonical_models import CanonicalResume, CanonicalItem
from app.resume_jd.models.canonical_jd import CanonicalJD
from app.resume_jd.models.phase_03_models import (
    JDRequirement, JDRequirementAtom, ResumeEvidence
)

class Phase3Extractor:
    def __init__(self):
        # Reuse existing API client connection logic, but we own the extraction abstraction
        self._llm_client = LLMOptimizer()
    
    def process_jd(self, canonical_jd: CanonicalJD) -> List[JDRequirement]:
        raw_text = canonical_jd.raw_text
        
        system_prompt = """
        You are an expert technical recruiter AI. Extract compound requirements from a Job Description, atomize them into parent capabilities and child concepts, and return strict JSON.
        
        OUTPUT FORMAT MUST BE STRICT JSON matching this schema exactly:
        {
          "requirements": [
            {
              "parent_capability": "High-level capability",
              "raw_value": "The raw target phrase representing the requirement",
              "requirement_text": "The full original requirement sentence/text",
              "surrounding_context": "Broader context",
              "expected_action": "The action expected",
              "category": "SKILL" | "EXPERIENCE" | "EDUCATION",
              "requirement_type": "REQUIRED" or "PREFERRED",
              "requirement_signal": "e.g. 'must have'",
              "importance_signals": ["REQUIRED", "CORE_RESPONSIBILITY"],
              "provenance": "EXPLICIT" or "INFERRED",
              "source_section": "Section header",
              "source_text": "THE EXACT VERBATIM SENTENCE FROM THE DOCUMENT",
              "atoms": [
                {
                  "raw_value": "e.g. AWS",
                  "atom_type": "TECHNOLOGY" | "SKILL" | "EXPERIENCE" | "EDUCATION" | "CERTIFICATION" | "RESPONSIBILITY" | "DOMAIN" | "SOFT_SKILL",
                  "action": "e.g. build"
                }
              ]
            }
          ]
        }
        
        CRITICAL RULES:
        1. "source_text" MUST BE EXACT COPY-PASTE FROM THE INPUT TEXT. Do NOT calculate character offsets. Just return the text segment.
        2. Do NOT invent technologies not explicitly written.
        3. Do NOT match or score.
        """
        
        prompt = f"Extract requirements from this Job Description:\n\n{raw_text}"
        extracted_data = self._call_llm(prompt, system_prompt)
        requirements = []
        
        if not extracted_data or "requirements" not in extracted_data:
            return requirements
            
        for req_data in extracted_data["requirements"]:
            # Source Grounding Validation
            source_text = req_data.get("source_text", "")
            if not source_text or source_text not in raw_text:
                print(f"REJECTED: Hallucinated JD source_text: '{source_text}'")
                continue # Reject unsupported output
                
            # Calculate System offsets (source_span)
            start_index = raw_text.find(source_text)
            source_span = f"[{start_index}:{start_index+len(source_text)}]" if start_index != -1 else None
                
            atoms = []
            for atom_data in req_data.get("atoms", []):
                canonical_item_ids = self._find_matching_canonical_item_ids(
                    canonical_jd.items, atom_data.get("raw_value", "")
                )
                
                atoms.append(JDRequirementAtom(
                    atom_id=f"atom_{uuid.uuid4().hex[:8]}",
                    raw_value=atom_data.get("raw_value", ""),
                    canonical_concept=None,
                    atom_type=atom_data.get("atom_type", "SKILL"),
                    action=atom_data.get("action"),
                    canonical_item_ids=canonical_item_ids
                ))
            
            requirements.append(JDRequirement(
                requirement_id=f"req_{uuid.uuid4().hex[:8]}",
                parent_capability=req_data.get("parent_capability", ""),
                raw_value=req_data.get("raw_value", ""),
                requirement_text=req_data.get("requirement_text", ""),
                surrounding_context=req_data.get("surrounding_context"),
                expected_action=req_data.get("expected_action"),
                category=req_data.get("category", "SKILL"),
                requirement_type=req_data.get("requirement_type", "REQUIRED"),
                requirement_signal=req_data.get("requirement_signal"),
                importance_signals=req_data.get("importance_signals", []),
                provenance=req_data.get("provenance", "EXPLICIT"),
                source_document_id=canonical_jd.jd_id,
                source_section=req_data.get("source_section", "Unknown"),
                source_sentence=source_text,
                source_span=source_span,
                atoms=atoms
            ))
            
        return requirements

    def process_resume(self, canonical_resume: CanonicalResume, raw_resume_text: str) -> List[ResumeEvidence]:
        system_prompt = """
        You are an expert technical recruiter AI. Extract evidence of candidate capabilities from a Resume and return strict JSON.
        
        OUTPUT FORMAT MUST BE STRICT JSON matching this schema exactly:
        {
          "evidence": [
            {
              "raw_value": "The specific skill or capability phrase",
              "evidence_text": "The full sentence containing the evidence",
              "surrounding_context": "Broader context",
              "action": "The action performed (e.g. 'Built', 'Led')",
              "scale_impact": "Scale or impact (e.g. '2TB daily')",
              "category": "SKILL",
              "evidence_type": "EXPLICIT" or "INFERRED",
              "provenance": "EXPLICIT" or "INFERRED",
              "source_section": "e.g. 'Experience'",
              "source_text": "THE EXACT VERBATIM SENTENCE FROM THE TEXT"
            }
          ]
        }
        
        CRITICAL RULES:
        1. "source_text" MUST BE EXACT COPY-PASTE FROM THE INPUT TEXT. Do NOT calculate offsets.
        2. Do NOT invent technologies.
        3. Do NOT match or score.
        """
        
        prompt = f"Extract evidence from this Resume:\n\n{raw_resume_text}"
        extracted_data = self._call_llm(prompt, system_prompt)
        evidence_list = []
        
        if not extracted_data or "evidence" not in extracted_data:
            return evidence_list
            
        for ev_data in extracted_data["evidence"]:
            # Source Grounding Validation
            source_text = ev_data.get("source_text", "")
            if not source_text or source_text not in raw_resume_text:
                print(f"REJECTED: Hallucinated Resume source_text: '{source_text}'")
                continue
                
            start_index = raw_resume_text.find(source_text)
            source_span = f"[{start_index}:{start_index+len(source_text)}]" if start_index != -1 else None
            
            canonical_item_ids = self._find_matching_canonical_item_ids(
                canonical_resume.items, ev_data.get("raw_value", "")
            )
            
            evidence_list.append(ResumeEvidence(
                evidence_id=f"ev_{uuid.uuid4().hex[:8]}",
                raw_value=ev_data.get("raw_value", ""),
                evidence_text=ev_data.get("evidence_text", ""),
                surrounding_context=ev_data.get("surrounding_context"),
                action=ev_data.get("action"),
                scale_impact=ev_data.get("scale_impact"),
                category=ev_data.get("category", "SKILL"),
                evidence_type=ev_data.get("evidence_type", "EXPLICIT"),
                provenance=ev_data.get("provenance", "EXPLICIT"),
                source_document_id=canonical_resume.resume_id,
                source_section=ev_data.get("source_section", "Unknown"),
                source_sentence=source_text,
                source_span=source_span,
                canonical_item_ids=canonical_item_ids
            ))
            
        return evidence_list

    def _call_llm(self, prompt: str, system_prompt: str) -> Optional[Dict]:
        try:
            if self._llm_client.provider.lower() == "gemini" and self._llm_client.gemini_key:
                try:
                    result = self._llm_client._call_gemini(prompt, system_prompt=system_prompt)
                except Exception:
                    if self._llm_client.groq_key:
                        result = self._llm_client._call_groq(prompt, system_prompt=system_prompt)
                    else:
                        raise
            elif self._llm_client.provider.lower() == "groq" and self._llm_client.groq_key:
                result = self._llm_client._call_groq(prompt, system_prompt=system_prompt)
            else:
                return None
                
            if isinstance(result, str):
                cleaned = result.strip().strip('```json').strip('```').strip()
                result = json.loads(cleaned)
            return result
        except Exception as e:
            print(f"Phase 3 LLM Extraction failed: {e}")
            return None

    def _find_matching_canonical_item_ids(self, items: List[CanonicalItem], search_text: str) -> List[str]:
        """
        Conservative deterministic linking.
        Only links if the extracted raw_value exactly string-matches the Phase 2 raw_value.
        """
        matched_ids = []
        if not search_text:
            return matched_ids
            
        search_lower = search_text.lower().strip()
        for item in items:
            if search_lower == item.raw_value.lower().strip():
                matched_ids.append(item.id)
        return matched_ids
