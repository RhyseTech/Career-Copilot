import os
import json
import requests
from typing import Dict, List
import hashlib
from app.config import settings

_CACHE = {}

class LLMOptimizer:
    def __init__(self):
        # We switch between Google Free API and Groq via settings
        self.provider = settings.LLM_PROVIDER
        self.gemini_key = settings.GEMINI_API_KEY
        self.groq_key = settings.GROQ_API_KEY
        self.gemini_model = settings.GEMINI_MODEL
        self.groq_model = settings.GROQ_MODEL
        
        # System Prompt Guardrails
        self.system_prompt = """
        You are an expert ATS optimization AI. Your task is to suggest exact text replacements for the provided resume sections.
        STRICT RULES:
        1. DO NOT fabricate, hallucinate, or invent experience, skills, or metrics the user does not possess.
        2. If a required skill is missing, categorize it as a 'Potential Skill Gap', do NOT add it to their experience.
        3. Do NOT give meta-advice (e.g., "Add a 2-3 sentence summary"). You must write the actual summary text or bullet point text yourself, so the user can directly copy and paste it into their resume.
        4. Rewrite experience bullets to be impactful using the STAR method, utilizing ONLY the facts provided.
        5. Output STRICTLY as JSON with the following schema:
           {
             "professional_summary": ["A fully written 2-3 sentence professional summary based on their experience.", "Another alternative fully written summary."],
             "experience_rewrites": [{"original": "...", "suggested": "...", "reason": "..."}],
             "skill_gaps": ["skill1", "skill2"]
           }
        """

    def generate_optimization_suggestions(self, resume_text: str, jd_text: str = None) -> Dict:
        """
        Calls the LLM to generate targeted recommendations, using an in-memory cache to save API costs and reduce latency (FrugalGPT principles).
        """
        prompt = f"Resume Text:\n{resume_text}\n\n"
        if jd_text:
            prompt += f"Job Description:\n{jd_text}\n\n"
            prompt += "Tailor the suggestions to align with the Job Description."
            
        prompt_hash = hashlib.md5(prompt.encode('utf-8')).hexdigest()
        if prompt_hash in _CACHE:
            print(f"Returning cached optimization suggestions for hash {prompt_hash[:8]} (Saved API Call & Latency!)")
            return _CACHE[prompt_hash]
            
        print(f"Calling {self.provider} API with prompt length: {len(prompt)}")
        
        try:
            result = None
            if self.provider.lower() == "gemini" and self.gemini_key:
                try:
                    result = self._call_gemini(prompt)
                except Exception as e:
                    print(f"Gemini API failed: {e}. Falling back to Groq...")
                    if self.groq_key:
                        result = self._call_groq(prompt)
                    else:
                        raise
            elif self.provider.lower() == "groq" and self.groq_key:
                try:
                    result = self._call_groq(prompt)
                except Exception as e:
                    print(f"Groq API failed: {e}. Falling back to Gemini...")
                    if self.gemini_key:
                        result = self._call_gemini(prompt)
                    else:
                        raise
            elif self.gemini_key:
                result = self._call_gemini(prompt)
            elif self.groq_key:
                result = self._call_groq(prompt)
            else:
                raise ValueError("No valid LLM provider or API keys configured.")
                
            if result:
                _CACHE[prompt_hash] = result
                return result
                
        except Exception as e:
            print(f"Error calling LLM (both providers failed): {e}")
            # Fallback mock response
            return {
                "professional_summary": ["Failed to get AI suggestions due to an error.", "Please check your API keys or try again later."],
                "experience_rewrites": [],
                "skill_gaps": []
            }

    def generate_diagnostic_report(self, resume_text: str, lagging_fields: List[str]) -> Dict:
        """
        Calls the LLM to generate explainable feedback for lagging ATS dimensions.
        """
        diagnostic_system_prompt = """
        You are an expert ATS optimization AI. Your task is to provide human-readable, explainable feedback on why a resume scored poorly in specific dimensions.
        STRICT RULES:
        1. Be highly specific to the provided resume text. Do not give generic advice.
        2. Keep the feedback concise (1-2 sentences per field).
        3. Output STRICTLY as JSON with the following schema:
           {
             "diagnostics": [
               {
                 "title": "Name of the lagging field or specific issue",
                 "badge": "e.g., Critical, Warning",
                 "description": "Specific explanation of what is missing and why it scored poorly.",
                 "recommendation": "Actionable ATS recommendation to fix the issue.",
                 "impact": "e.g., High, Medium, Low"
               }
             ]
           }
        """
        
        prompt = f"The user scored poorly on the following dimensions: {', '.join(lagging_fields)}\n\nAnalyze the resume below and explain exactly WHY these fields scored poorly.\n\nResume Text:\n{resume_text}"
        
        prompt_hash = hashlib.md5((prompt + diagnostic_system_prompt).encode('utf-8')).hexdigest()
        if prompt_hash in _CACHE:
            return _CACHE[prompt_hash]
            
        print(f"Calling {self.provider} API for diagnostics with prompt length: {len(prompt)}")
        
        try:
            result = None
            if self.provider.lower() == "gemini" and self.gemini_key:
                try:
                    result = self._call_gemini(prompt, diagnostic_system_prompt)
                except Exception:
                    if self.groq_key:
                        result = self._call_groq(prompt, diagnostic_system_prompt)
                    else:
                        raise
            elif self.provider.lower() == "groq" and self.groq_key:
                try:
                    result = self._call_groq(prompt, diagnostic_system_prompt)
                except Exception:
                    if self.gemini_key:
                        result = self._call_gemini(prompt, diagnostic_system_prompt)
                    else:
                        raise
            elif self.gemini_key:
                result = self._call_gemini(prompt, diagnostic_system_prompt)
            elif self.groq_key:
                result = self._call_groq(prompt, diagnostic_system_prompt)
            else:
                raise ValueError("No valid LLM provider.")
                
            if result:
                _CACHE[prompt_hash] = result
                return result
                
        except Exception as e:
            print(f"Error calling LLM for diagnostics: {e}")
            return {"diagnostics": [{"field": f, "feedback": "Failed to generate AI diagnostic due to an error."} for f in lagging_fields]}

    def _call_gemini(self, prompt: str, system_prompt: str = None) -> Dict:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": system_prompt or self.system_prompt}]},
            "generationConfig": {"responseMimeType": "application/json"}
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        text_response = data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text_response)

    def _call_groq(self, prompt: str, system_prompt: str = None) -> Dict:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.groq_model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt or self.system_prompt},
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        text_response = data["choices"][0]["message"]["content"]
        return json.loads(text_response)
    def generate_rendercv_json(self, resume_text: str) -> Dict:
        """
        Parses raw resume text and constructs a JSON object matching the RenderCV data model.
        """
        prompt = f"""
You are an expert ATS optimization AI. Parse the following resume text and extract all information into a strict JSON format matching the RenderCV schema.

Resume Text:
{resume_text}

OUTPUT FORMAT MUST BE STRICT JSON matching this exact structure:
{{
  "cv": {{
    "name": "John Doe",
    "email": "email@example.com",
    "phone": "+1 555-123-4567",
    "location": "City, State",
    "social_networks": [
      {{"network": "LinkedIn", "username": "johndoe"}},
      {{"network": "GitHub", "username": "johndoe"}}
    ],
    "sections": {{
      "summary": [
        "A 2-3 sentence professional summary extracted or generated from the text."
      ],
      "experience": [
        {{
          "company": "Company Name",
          "position": "Job Title",
          "location": "City, State",
          "start_date": "YYYY-MM",
          "end_date": "YYYY-MM or present",
          "highlights": [
            "Bullet point 1",
            "Bullet point 2"
          ]
        }}
      ],
      "education": [
        {{
          "institution": "University Name",
          "area": "Major",
          "degree": "BS/MS/PhD",
          "start_date": "YYYY-MM",
          "end_date": "YYYY-MM",
          "highlights": ["GPA: 3.8", "Honors"]
        }}
      ],
      "projects": [
        {{
          "name": "Project Name",
          "summary": "Short description of the project",
          "start_date": "YYYY-MM",
          "end_date": "YYYY-MM",
          "highlights": ["Bullet point 1", "Tech stack used"]
        }}
      ],
      "certifications": [
        {{
          "name": "Certification Name",
          "location": "Platform or Institution",
          "start_date": "YYYY-MM",
          "end_date": "YYYY-MM",
          "highlights": ["Detail about the certification"]
        }}
      ],
      "skills": [
        {{"label": "Languages", "details": "Python, JavaScript, SQL"}},
        {{"label": "Tools", "details": "AWS, Docker, Git"}}
      ]
    }}
  }}
}}

RULES:
1. Ensure dates follow YYYY-MM or YYYY-MM-DD or "present" formats. If month is unknown, just YYYY is fine.
2. If information is missing, leave the field empty or omit it. Do not invent information.
3. Extract all experience bullet points into the `highlights` array.
4. Make sure to capture ALL Projects and Certifications listed in the resume into their respective arrays.
5. CRITICAL: You MUST order the keys inside the `sections` object ("summary", "experience", "education", "projects", "certifications", "skills") to EXACTLY match the top-to-bottom chronological order they appeared in the original uploaded resume!
"""
        hash_key = "rendercv_" + hashlib.md5(prompt.encode('utf-8')).hexdigest()
        if hash_key in _CACHE:
            return _CACHE[hash_key]

        sys_prompt = "Return ONLY valid JSON matching the requested RenderCV schema. Do NOT include markdown code blocks like ```json."

        try:
            result = None
            if self.provider.lower() == "gemini" and self.gemini_key:
                try:
                    result = self._call_gemini(prompt, sys_prompt)
                except Exception as e:
                    print(f"Gemini API failed in RenderCV JSON: {e}. Falling back to Groq...")
                    if self.groq_key:
                        result = self._call_groq(prompt, sys_prompt)
                    else:
                        raise e
            elif self.provider.lower() == "groq" and self.groq_key:
                try:
                    result = self._call_groq(prompt, sys_prompt)
                except Exception as e:
                    print(f"Groq API failed in RenderCV JSON: {e}. Falling back to Gemini...")
                    if self.gemini_key:
                        result = self._call_gemini(prompt, sys_prompt)
                    else:
                        raise e
            elif self.gemini_key:
                result = self._call_gemini(prompt, sys_prompt)
            elif self.groq_key:
                result = self._call_groq(prompt, sys_prompt)
            else:
                raise ValueError("No valid LLM provider or API keys configured.")
            
            if result:
                _CACHE[hash_key] = result
                return result
                
        except Exception as e:
            print(f"Failed to generate RenderCV JSON (all fallbacks exhausted): {e}")
            return None
