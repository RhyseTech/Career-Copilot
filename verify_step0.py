import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.parser import ResumeParser
from app.resume_jd.adapters.resume_adapter import ResumeAdapter

def verify_step_0():
    dummy_pdf_path = "backend/app/uploads/7d1534ac-666a-44e4-9f6b-c698c8eab654.pdf"
    
    # 1. Parse Resume
    parser = ResumeParser()
    parsed_res = parser.parse_resume(dummy_pdf_path)
    
    # 2. Canonicalize Resume (this uses the parsed output)
    adapter = ResumeAdapter()
    canonical_resume = adapter.process_file(dummy_pdf_path, "dummy.pdf")
    
    raw_text = canonical_resume.raw_text if hasattr(canonical_resume, 'raw_text') else ""
    
    print(f"\nPhase 1 parsed keys: {parsed_res.keys()}")
    if "raw_text" in parsed_res:
        print(f"Phase 1 raw_text length: {len(parsed_res['raw_text'])}")
        
    print(f"\nPhase 2 Canonical Resume raw_text length: {len(raw_text)} chars")
    
    # In run_real_e2e, we do: res_evs = extractor.process_resume(canonical_resume, parsed_res["raw_text"])
    # So the text sent to LLM is parsed_res["raw_text"]!
    llm_input_text = parsed_res.get("raw_text", "")
    print(f"LLM input text length: {len(llm_input_text)} chars")
    
    # Check if key sections are in llm_input_text
    sections = ["SUMMARY", "SKILLS", "EXPERIENCE", "PROJECTS", "EDUCATION", "CERTIFICATIONS"]
    for s in sections:
        found = s.lower() in llm_input_text.lower()
        print(f"Contains section '{s}' evidence: {found}")
    
    print("\nSample of raw text passed to Phase 3:")
    if llm_input_text:
        print(llm_input_text[:500] + "\n...\n" + llm_input_text[-500:])

if __name__ == "__main__":
    verify_step_0()
