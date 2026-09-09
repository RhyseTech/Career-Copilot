import asyncio
import json
import os
from app.resume_jd.pipelines.phase_03_extractor import Phase3Extractor
from app.resume_jd.models.canonical_jd import CanonicalJD
from app.resume_jd.models.canonical_models import CanonicalResume

def run():
    extractor = Phase3Extractor()
    
    jd_text = "We are looking for a Data Engineer with 5+ years of Python and AWS S3 experience. GCP Dataflow pipeline development is preferred."
    cjd = CanonicalJD(jd_id="jd_123", raw_chunks=[], items=[], content_hash="hash1", raw_text=jd_text)
    
    resume_text = "Experienced software engineer with 5 years of Python experience. Built ETL pipelines using AWS Glue and S3. Proficient in React."
    cres = CanonicalResume(resume_id="res_456", raw_chunks=[], items=[], content_hash="hash2", raw_text=resume_text, file_name="resume.pdf")
    
    print("Running Phase 3 JD Extraction...")
    reqs = extractor.process_jd(cjd, jd_text)
    
    print("Running Phase 3 Resume Extraction...")
    evs = extractor.process_resume(cres, resume_text)
    
    # Save them to the folders (mocking JSONStore structure for E2E)
    os.makedirs("data/parsed_jds", exist_ok=True)
    os.makedirs("data/parsed_resumes", exist_ok=True)
    
    with open("data/parsed_jds/reqs_canonical_jd_123.json", "w") as f:
        json.dump({"requirements": [r.model_dump() for r in reqs]}, f)
        
    with open("data/parsed_resumes/ev_canonical_resume_456.json", "w") as f:
        json.dump({"evidence": [e.model_dump() for e in evs]}, f)
        
    print("Saved Phase 3 Artifacts. Now you can run Phase 4 E2E.")

if __name__ == "__main__":
    run()
