import os
import json
from dotenv import load_dotenv

# Load env before other imports that might use config
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from app.resume_jd.storage.json_store import JSONStore
from app.resume_jd.models.canonical_jd import CanonicalJD
from app.resume_jd.pipelines.phase_03_extractor import Phase3Extractor
from app.resume_jd.adapters.resume_adapter import ResumeAdapter
from app.services.parser import ResumeParser

def run_e2e():
    print("=== STARTING PHASE 3 E2E VALIDATION ===")
    
    # 1. Setup extractors
    extractor = Phase3Extractor()
    store = JSONStore()
    
    # 2. Get the first parsed JD
    jd_files = [f for f in os.listdir(store.base_dir) if f.endswith("_canonical.json")]
    if not jd_files:
        print("No JDs found.")
        return
        
    jd_path = os.path.join(store.base_dir, jd_files[-1]) # Use latest JD
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_data = json.load(f)
        canonical_jd = CanonicalJD(**jd_data)
        
    print(f"\n[1] Extracted CanonicalJD ID: {canonical_jd.jd_id}")
    print(f"JD Raw Text Length: {len(canonical_jd.raw_text)}")
    
    # Run JD Phase 3
    print("\nRunning JD Requirement Extraction...")
    jd_reqs = extractor.process_jd(canonical_jd)
    print(f"-> Extracted {len(jd_reqs)} JD Requirements.")
    
    # Print the first one for validation
    if jd_reqs:
        req = jd_reqs[0]
        print(f"\nExample Requirement:")
        print(f"Parent: {req.parent_capability}")
        print(f"Type: {req.requirement_type}")
        print(f"Source Span: {req.source_span}")
        print(f"Atoms: {len(req.atoms)}")
        for a in req.atoms:
            print(f"  - {a.raw_value} ({a.atom_type}) [Linked: {a.canonical_item_ids}]")
            
    # 3. Resume Evidence
    print("\n[2] Loading a Resume for Evidence Extraction...")
    uploads_dir = os.path.dirname(store.base_dir) # parent of parsed_jds is uploads
    resume_files = [f for f in os.listdir(uploads_dir) if f.endswith(".pdf")]
    
    if not resume_files:
        print("No Resume PDFs found.")
        return
        
    resume_path = os.path.join(uploads_dir, resume_files[0])
    print(f"Using Resume: {resume_files[0]}")
    
    resume_adapter = ResumeAdapter()
    resume_parser = ResumeParser()
    
    try:
        parsed_res = resume_parser.parse_resume(resume_path)
        canonical_resume = resume_adapter.process_file(resume_path, resume_files[0])
        
        print("\nRunning Resume Evidence Extraction...")
        res_evs = extractor.process_resume(canonical_resume, parsed_res["raw_text"])
        print(f"-> Extracted {len(res_evs)} Resume Evidences.")
        
        if res_evs:
            ev = res_evs[0]
            print(f"\nExample Evidence:")
            print(f"Raw Value: {ev.raw_value}")
            print(f"Action: {ev.action}")
            print(f"Context: {ev.surrounding_context}")
            print(f"Source Span: {ev.source_span}")
            print(f"Linked: {ev.canonical_item_ids}")
            
        print("\n=== E2E COMPLETED SUCCESSFULLY ===")
    except Exception as e:
        print(f"Resume parsing failed: {e}")

if __name__ == "__main__":
    run_e2e()
