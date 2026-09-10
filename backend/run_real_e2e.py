import os
import requests
import json
import uuid

def run_e2e():
    print("Starting Real E2E Test...")
    
    jd_text = """
    Looking for a Senior Python Backend Engineer.
    Required:
    - 5+ years of Python
    - FastAPI
    - AWS (S3, EC2)
    - LLM Integration (LangChain)
    - PostgreSQL
    Preferred:
    - Kubernetes
    """
    
    dummy_pdf_path = "app/uploads/7d1534ac-666a-44e4-9f6b-c698c8eab654.pdf"
    
    base_url = "http://localhost:8000"
    print("\n--- Running Independent Phases ---")
    
    # Phase 1: Parse JD
    res = requests.post(f"{base_url}/resume-jd/jd/parse", data={"jd_text": jd_text})
    jd_p1 = res.json()
    jd_id = jd_p1["jd_id"]
    
    # Phase 1: Parse Resume
    with open(dummy_pdf_path, "rb") as f:
        res = requests.post(f"{base_url}/resume-jd/resume/parse", files={"file": ("dummy.pdf", f, "application/pdf")})
    res_p1 = res.json()
    resume_id = res_p1["resume_id"]
    
    # Phase 2: Canonicalize JD
    res = requests.post(f"{base_url}/resume-jd/jd/canonicalize", data={"jd_text": jd_text})
    jd_p2 = res.json()
    canonical_jd = jd_p2["canonical_jd"]
    
    # Phase 2: Canonicalize Resume
    with open(dummy_pdf_path, "rb") as f:
        res = requests.post(f"{base_url}/resume-jd/resume/canonicalize", files={"file": ("dummy.pdf", f, "application/pdf")})
    res_p2 = res.json()
    canonical_resume = res_p2["canonical_resume"]
    
    print(f"Independent Resume ID: {canonical_resume['resume_id']}")
    print(f"Independent JD ID: {canonical_jd['jd_id']}")
    
    # Phase 3
    res = requests.post(f"{base_url}/resume-jd/analysis/requirements-evidence", json={
        "resume_id": canonical_resume['resume_id'],
        "jd_id": canonical_jd['jd_id']
    })
    p3 = res.json()
    print(f"Phase 3 Status: {res.status_code}")
    if res.status_code != 200:
        print(f"Phase 3 Error: {p3}")
        return
        
    # Phase 4
    analysis_id = f"{canonical_resume['resume_id']}_{canonical_jd['jd_id']}"
    res = requests.post(f"{base_url}/resume-jd/analysis/matches", json={
        "analysis_id": analysis_id
    })
    p4 = res.json()
    print(f"Phase 4 Status: {res.status_code}")
    
    # Phase 5
    res = requests.post(f"{base_url}/resume-jd/analysis/score", json={
        "analysis_id": analysis_id
    })
    p5 = res.json()
    print(f"Phase 5 Status: {res.status_code}")
    indep_score = p5["score"]["final_score"]
    
    print(f"Independent Final Score: {indep_score}")
    
    print("\n--- Running Orchestrator ---")
    with open(dummy_pdf_path, "rb") as f:
        res = requests.post(f"{base_url}/resume-jd/analysis/run", files={"file": ("dummy.pdf", f, "application/pdf")}, data={"jd_text": jd_text})
    orch = res.json()
    
    if "phase_5" not in orch or "score" not in orch["phase_5"]:
        print(f"Orchestrator failed: {orch}")
        return
        
    orch_score = orch["phase_5"]["score"]["final_score"]
    print(f"Orchestrated Final Score: {orch_score}")
    
    print(f"\nMatch Verification: {'SUCCESS' if indep_score == orch_score else 'FAILED'}")
    
if __name__ == "__main__":
    run_e2e()
