import os
import requests
import json
import uuid

def run_real_validation():
    print("Starting Real E2E Test with Real JD...")
    
    with open("data/jd/data_eng_jd_1.txt", "r") as f:
        jd_text = f.read()
    
    dummy_pdf_path = "backend/app/uploads/7d1534ac-666a-44e4-9f6b-c698c8eab654.pdf"
    
    base_url = "http://localhost:8000"
    
    with open(dummy_pdf_path, "rb") as f:
        res = requests.post(f"{base_url}/resume-jd/analysis/run", files={"file": ("dummy.pdf", f, "application/pdf")}, data={"jd_text": jd_text})
    orch = res.json()
    
    if "phase_5" not in orch or "score" not in orch["phase_5"]:
        print(f"Orchestrator failed: {orch}")
        return
        
    analysis_id = orch["analysis_id"]
    resume_id = analysis_id.split("_")[0]
    jd_id = analysis_id.split("_")[1]
    
    print(f"Resume ID: {resume_id}")
    print(f"JD ID: {jd_id}")
    print(f"Analysis ID: {analysis_id}")
    
    print("----")
    print(f"Total JD Requirements: {len(orch['phase_3']['jd_requirements'])}")
    print(f"Total Resume Evidence: {len(orch['phase_3']['resume_evidence'])}")
    
    ev_types = {}
    for ev in orch['phase_3']['resume_evidence']:
        cat = ev['category']
        ev_types[cat] = ev_types.get(cat, 0) + 1
        
    print(f"Evidence Types: {ev_types}")
    print("Sample Evidence:")
    for ev in orch['phase_3']['resume_evidence'][:15]:
        print(f" - [{ev['category']}] {ev['raw_value']} (Action: {ev.get('action')}, Context: {ev.get('surrounding_context')})")
        print(f"   Source: {ev.get('source_sentence', 'N/A')}")
        
    print("----")
    edges = orch['phase_4']['match_edges']
    mt_counts = {'EXACT': 0, 'RELATED': 0, 'PARTIAL': 0, 'TRANSFERABLE': 0, 'GAP': 0}
    for e in edges:
        mt = e['match_type']
        mt_counts[mt] = mt_counts.get(mt, 0) + 1
    
    print("Phase 4 Results:")
    for k, v in mt_counts.items():
        print(f"{k}: {v}")
        
    print("----")
    score = orch['phase_5']['score']
    print("Phase 5 Results:")
    print(f"Final Score: {score['final_score']}")
    print(f"Required Coverage: {score['required_coverage']}")
    print(f"Preferred Coverage: {score['preferred_coverage']}")

if __name__ == "__main__":
    run_real_validation()
