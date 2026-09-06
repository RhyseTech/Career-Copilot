import json
from typing import Dict, Any
from .llm_optimizer import LLMOptimizer

class JDAnalyzer:
    def __init__(self):
        self.llm = LLMOptimizer()
        
    def analyze_jd(self, jd_text: str) -> Dict[str, Any]:
        """
        Parses raw job description text and extracts rigid requirements into structured JSON.
        """
        system_prompt = """
        You are an expert technical recruiter and HR intelligence AI.
        Your task is to extract exact requirements from the provided Job Description text.
        
        OUTPUT FORMAT MUST BE STRICT JSON matching this structure exactly:
        {
          "role": "string",
          "seniority_level": "string",
          "years_experience_required": integer or null,
          "required_skills": ["skill1", "skill2"],
          "preferred_skills": ["skill3"],
          "education_requirements": ["degree1"],
          "certifications": ["cert1"]
        }
        
        RULES:
        1. Only extract information explicitly mentioned in the JD.
        2. Normalize skill names (e.g., "Amazon Web Services" -> "AWS").
        3. If a field is not specified, leave it as an empty array or null.
        """
        
        prompt = f"Job Description:\n{jd_text}"
        
        try:
            # Reusing the existing _call_gemini / _call_groq from LLMOptimizer
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
                raise ValueError("No valid LLM provider configured")
                
            return result
        except Exception as e:
            print(f"Error analyzing JD: {e}")
            # Fallback
            return {
                "role": "Unknown",
                "seniority_level": "Unknown",
                "years_experience_required": None,
                "required_skills": [],
                "preferred_skills": [],
                "education_requirements": [],
                "certifications": []
            }
