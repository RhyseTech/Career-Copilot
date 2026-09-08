import json
from typing import List, Dict, Any
from app.services.llm_optimizer import LLMOptimizer

class LLMExtractor:
    """
    Acts as the boundary for LLM extraction.
    Forces the LLM to return a strict JSON schema for Requirements.
    """
    def __init__(self):
        self.llm = LLMOptimizer()

    def extract_requirements(self, section_text: str, section_name: str) -> List[Dict[str, Any]]:
        """
        Calls the LLM to parse a chunk of JD text into structured Requirements.
        """
        system_prompt = """
        You are an expert technical recruiter AI.
        Your ONLY job is to extract discrete requirements (skills, experience, education, certifications) from the provided text.
        
        OUTPUT FORMAT MUST BE STRICT JSON matching this array structure exactly:
        [
          {
            "category": "SKILL" | "EXPERIENCE" | "EDUCATION" | "CERTIFICATION" | "GENERAL",
            "requirement_type": "REQUIRED" | "PREFERRED",
            "raw_text": "The exact name of the skill or requirement (e.g., 'Python', 'AWS', 'Bachelor Degree')",
            "source_span": "The EXACT matching substring from the original text that proves this requirement exists."
          }
        ]
        
        CRITICAL RULES:
        1. "source_span" MUST BE AN EXACT COPY-PASTE FROM THE INPUT TEXT. Do not alter a single character, punctuation, or capitalization. If you hallucinate, your output will be rejected.
        2. Do NOT extract obvious soft skills like 'communication' unless highly specific.
        3. Determine REQUIRED vs PREFERRED based on context (e.g., if under a 'Nice to have' header or uses words like 'plus' or 'preferred').
        """
        
        prompt = f"Section Context: {section_name}\n\nText to parse:\n{section_text}"
        
        try:
            if self.llm.provider.lower() == "gemini" and self.llm.gemini_key:
                try:
                    result = self.llm._call_gemini(prompt, system_prompt=system_prompt)
                except Exception as e:
                    if self.llm.groq_key:
                        result = self.llm._call_groq(prompt, system_prompt=system_prompt)
                    else:
                        raise e
            elif self.llm.provider.lower() == "groq" and self.llm.groq_key:
                result = self.llm._call_groq(prompt, system_prompt=system_prompt)
            else:
                return []
                
            # Parse output
            if isinstance(result, str):
                # Clean up potential markdown formatting
                cleaned = result.strip().strip('```json').strip('```').strip()
                result = json.loads(cleaned)
                
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and "requirements" in result:
                return result["requirements"]
                
            return []
        except Exception as e:
            print(f"LLM Extraction failed for section {section_name}: {e}")
            return []
