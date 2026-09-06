from typing import Dict, Any, List
import re
from .llm_optimizer import LLMOptimizer

class EvidenceOptimizer:
    def __init__(self):
        self.llm = LLMOptimizer()
        
    def optimize_section(self, section_name: str, original_text: str, jd_requirements: List[str], evidence_map: List[Dict]) -> Dict[str, Any]:
        """
        Optimizes a specific resume section strictly bounded by evidence.
        """
        system_prompt = f"""
        You are an expert Evidence-Based ATS Optimizer. Your job is to improve the provided `{section_name}` section.
        
        CRITICAL RULES (NEVER INVENT EXPERIENCE):
        1. DO NOT fabricate, hallucinate, or invent experience, skills, metrics, or technologies the candidate does not possess.
        2. You may only incorporate requirements from the Job Description IF they exist in the provided 'Evidence Map' with a status of 'strong' or 'partial'.
        3. If a JD requirement is marked as 'missing', DO NOT add it. Instead, you can return a warning suggesting the user to add it manually if they actually have the experience.
        4. Rewrite the bullet points or text using the STAR method (Situation, Task, Action, Result) using ONLY the facts provided.
        5. Output STRICTLY as JSON with the following schema:
           {{
             "suggested_text": "The fully rewritten section text (or list of bullets if applicable).",
             "rationale": "Explain exactly why you made these changes based on the evidence.",
             "warnings": ["Warning 1", "Warning 2"] // e.g. "Missing skill X was not added because there was no evidence for it."
           }}
        """
        
        prompt = f"""
        Original Section Text:
        {original_text}
        
        Job Description Requirements:
        {jd_requirements}
        
        Evidence Map (Only use things marked 'strong' or 'partial'):
        {evidence_map}
        """
        
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
                raise ValueError("No valid LLM provider configured")
                
            return result
        except Exception as e:
            print(f"Error optimizing section: {e}")

    def suggest_all_changes(self, raw_resume_text: str, jd_requirements: List[str], evidence_map: List[Dict]) -> Dict[str, Any]:
        """
        Analyzes the full resume against the JD evidence map in a single LLM call
        and returns a comprehensive list of suggested changes for all sections.
        """
        strong_skills = [e["jd_requirement"] for e in evidence_map if e["status"] == "strong"]
        partial_skills = [e["jd_requirement"] for e in evidence_map if e["status"] == "partial"]
        missing_skills = [e["jd_requirement"] for e in evidence_map if e["status"] == "missing"]

        system_prompt = """
        You are an expert Evidence-Based ATS Resume Optimizer. You will analyze a full resume against a Job Description and generate a comprehensive, actionable list of all needed changes.

        CRITICAL RULES (NEVER INVENT EXPERIENCE):
        1. DO NOT fabricate, hallucinate, or invent experience, skills, metrics, or technologies the candidate does not have.
        2. You may only strengthen content for skills that are in the "partial_evidence" or "strong_evidence" lists.
        3. For "missing_skills" — DO NOT add them to experience. Instead, flag them as skill gaps the user should address manually.
        4. Rewrite bullets using the STAR method but only with facts present in the resume.
        5. Never introduce a number, percentage, date, speed, scale, or outcome that is not stated in the original bullet. If no measurable result is present, improve clarity without inventing one.
        5. Output STRICTLY as JSON matching this exact schema:
           {
             "summary": {
               "original": "The exact original summary text from the resume",
               "suggested_text": "A fully written 2-3 sentence professional summary highlighting strengths relevant to the JD.",
               "rationale": "Why this summary works."
             },
             "experience_rewrites": [
               {"original": "exact original bullet text", "suggested": "rewritten STAR-method bullet", "reason": "what was improved"}
             ],
             "keyword_insertions": [
               {"section": "summary|experience", "keyword": "skill name", "context": "Where/how to naturally mention it"}
             ],
             "skill_gaps": ["skill1", "skill2"],
             "overall_advice": "2-3 sentences of top-level strategic advice."
           }
        """

        prompt = f"""
        FULL RESUME TEXT:
        {raw_resume_text}

        JD REQUIRED SKILLS: {jd_requirements}

        STRONG EVIDENCE (already in resume): {strong_skills}
        PARTIAL EVIDENCE (weakly mentioned — strengthen these): {partial_skills}
        MISSING (NOT in resume — flag as gap only): {missing_skills}
        """

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
                raise ValueError("No valid LLM provider configured")
            raw_result = self._remove_unverified_metrics(result)

            suggestions = []
            import uuid

            if "summary" in raw_result and raw_result["summary"]:
                summary_data = raw_result["summary"]
                suggestions.append({
                    "id": str(uuid.uuid4()),
                    "section": "Professional Summary",
                    "badge": "Impact",
                    "original": summary_data.get("original", "Original Summary"),
                    "suggested": summary_data.get("suggested_text", ""),
                    "rationale": summary_data.get("rationale", ""),
                    "ats_points": "+10 ATS Points"
                })
                
            for rewrite in raw_result.get("experience_rewrites", []):
                suggestions.append({
                    "id": str(uuid.uuid4()),
                    "section": "Experience",
                    "badge": "STAR Metric",
                    "original": rewrite.get("original", ""),
                    "suggested": rewrite.get("suggested", ""),
                    "rationale": rewrite.get("reason", ""),
                    "ats_points": "+15 ATS Points"
                })
                
            for kw in raw_result.get("keyword_insertions", []):
                suggestions.append({
                    "id": str(uuid.uuid4()),
                    "section": str(kw.get("section", "Skills")).capitalize(),
                    "badge": "Keyword",
                    "original": f"Missing keyword: {kw.get('keyword', '')}",
                    "suggested": f"Add context: {kw.get('context', '')}",
                    "rationale": f"Enhance match for {kw.get('keyword', '')}",
                    "ats_points": "+5 ATS Points"
                })
                
            return {
                "suggestions": suggestions,
                "strategic_advice": raw_result.get("overall_advice", "")
            }
        except Exception as e:
            print(f"Error in suggest_all_changes: {e}")
            return {
                "suggestions": [],
                "strategic_advice": f"Error generating suggestions: {str(e)}"
            }

    @staticmethod
    def _remove_unverified_metrics(result: Dict[str, Any]) -> Dict[str, Any]:
        """Reject rewrites that add quantitative claims not in the source text.

        Prompt instructions alone cannot guarantee a model will not hallucinate a
        metric. This deterministic post-check protects the accept-and-render flow.
        """
        safe_rewrites = []
        for rewrite in result.get("experience_rewrites", []):
            original = str(rewrite.get("original", ""))
            suggested = str(rewrite.get("suggested", ""))
            source_numbers = set(re.findall(r"\d+(?:\.\d+)?%?", original))
            suggested_numbers = set(re.findall(r"\d+(?:\.\d+)?%?", suggested))
            if suggested_numbers.issubset(source_numbers):
                safe_rewrites.append(rewrite)
        result["experience_rewrites"] = safe_rewrites
        return result
