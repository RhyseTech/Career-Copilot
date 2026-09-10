import os
import sys
from dotenv import load_dotenv

load_dotenv("backend/.env")

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.parser import ResumeParser
from app.resume_jd.adapters.resume_adapter import ResumeAdapter
from app.resume_jd.pipelines.phase_03_extractor import Phase3Extractor

def run_direct():
    print(f"Provider: {os.getenv('LLM_PROVIDER')}")
    print(f"Gemini Key length: {len(os.getenv('GEMINI_API_KEY', ''))}")
    
    dummy_pdf_path = "backend/app/uploads/7d1534ac-666a-44e4-9f6b-c698c8eab654.pdf"
    
    parser = ResumeParser()
    parsed_res = parser.parse_resume(dummy_pdf_path)
    
    adapter = ResumeAdapter()
    canonical_resume = adapter.process_file(dummy_pdf_path, "dummy.pdf")
    
    extractor = Phase3Extractor()
    print(f"Extractor Provider: {extractor._llm_client.provider}")
    
    res_evs = extractor.process_resume(canonical_resume, parsed_res["raw_text"])
    
    if res_evs:
        print(f"Extracted {len(res_evs)} valid evidence items.")
    else:
        print("Failed or extracted 0 items.")

if __name__ == "__main__":
    run_direct()
