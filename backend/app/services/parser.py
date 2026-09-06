import os
import re
import pymupdf as fitz  # PyMuPDF
from docx import Document
from typing import Dict, Optional

class ResumeParser:
    def __init__(self):
        # Basic heuristic headers for section detection
        self.section_headers = {
            "summary": [r"summary", r"objective", r"profile", r"about me", r"professional summary", r"career objective"],
            "experience": [r"experience", r"employment", r"work history", r"professional experience", r"work experience", r"employment history"],
            "education": [r"education", r"academic background", r"qualifications", r"academic qualifications", r"academic details"],
            "skills": [r"skills", r"technologies", r"core competencies", r"technical skills", r"it skills", r"technical expertise"],
            "projects": [r"projects", r"personal projects", r"academic projects", r"key projects", r"technical projects"],
            "certifications": [r"certifications", r"licenses", r"courses", r"achievements"]
        }

    def _extract_text_pdf(self, file_path: str) -> str:
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
        return text

    def _extract_text_docx(self, file_path: str) -> str:
        text = ""
        try:
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {e}")
        return text

    def _clean_and_normalize(self, text: str) -> str:
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text)
        # Basic normalization (more to be added in next sprints)
        return text.strip()

    def _detect_sections(self, text: str) -> Dict[str, str]:
        # A basic section detector for MVP. 
        # In later sprints, this will be improved with NLP or LLM.
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        sections = {
            "summary": "",
            "experience": "",
            "education": "",
            "skills": "",
            "projects": "",
            "certifications": "",
            "uncategorized": ""
        }
        
        current_section = "uncategorized"
        
        for line in lines:
            line_lower = line.lower()
            found_header = False
            
            # Check if line matches any section header (allowing optional numbering and colons)
            for section_name, keywords in self.section_headers.items():
                if any(re.match(rf"^\s*(?:[0-9ivx]+\.\s*)?{kw}\s*:?\s*$", line_lower) for kw in keywords):
                    current_section = section_name
                    found_header = True
                    break
            
            if not found_header:
                sections[current_section] += line + "\n"
                
        # Clean up sections
        for k in sections:
            sections[k] = sections[k].strip()
            
        return sections

    def parse_resume(self, file_path: str) -> Dict:
        if file_path.lower().endswith('.pdf'):
            raw_text = self._extract_text_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            raw_text = self._extract_text_docx(file_path)
        else:
            raise ValueError("Unsupported file format")

        cleaned_text = self._clean_and_normalize(raw_text)
        # Using raw text for section detection to preserve line breaks
        sections = self._detect_sections(raw_text)

        # Validation: check if it's actually a resume
        meaningful_sections = ["summary", "experience", "education", "skills", "projects"]
        has_resume_sections = any(len(sections[sec].strip()) > 10 for sec in meaningful_sections)
        
        # If no resume sections are found and the document is very short or doesn't have resume keywords, reject it.
        if not has_resume_sections:
            raise ValueError("The uploaded document does not appear to be a valid resume. Please upload a standard resume with clear headers (e.g., Experience, Education, Skills).")

        return {
            "raw_text": raw_text,
            "cleaned_text": cleaned_text,
            "sections": sections
        }
