import pymupdf as fitz
from docx import Document
from typing import Dict, Any
from .llm_optimizer import LLMOptimizer
import re
import json

class DocumentParser:
    def __init__(self):
        self.llm = LLMOptimizer()

    def extract_text(self, file_path: str) -> str:
        text = ""
        if file_path.lower().endswith(".pdf"):
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        elif file_path.lower().endswith(".docx"):
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            raise ValueError("Unsupported file format. Use PDF or DOCX.")
            
        # Basic normalization
        text = re.sub(r'\s+', ' ', text).strip()
        return text
        
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """
        Extracts raw text from the document and uses the LLM to parse it into 
        structured JSON (RenderCV schema format).
        """
        raw_text = self.extract_text(file_path)
        
        # Use existing LLM generation logic to get structured JSON
        structured_json = self.llm.generate_rendercv_json(raw_text)
        
        return {
            "raw_text": raw_text,
            "structured_data": structured_json
        }
