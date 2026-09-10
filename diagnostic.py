import json
import os

P3_JD = r"backend/app/uploads/phase_03/jd_requirements_24b2b657-1553-4d40-a5aa-08b22cd0a4ec.json"
P3_RES = r"backend/app/uploads/phase_03/resume_evidence_15027ab8-89a2-4d8d-b74f-e132f70050bc.json"
P4 = r"backend/app/uploads/phase_04/match_edges_20260910_144726_15027ab8-89a2-4d8d-b74f-e132f70050bc_24b2b657-1553-4d40-a5aa-08b22cd0a4ec.json"
P5 = r"backend/app/uploads/phase_05/phase5_score_20260910_144726_15027ab8-89a2-4d8d-b74f-e132f70050bc_24b2b657-1553-4d40-a5aa-08b22cd0a4ec.json"

with open(P3_JD, 'r') as f:
    jd_reqs = json.load(f)['requirements']
with open(P3_RES, 'r') as f:
    resume_ev = json.load(f)['evidence']
with open(P4, 'r') as f:
    match_edges = json.load(f)['match_edges']
with open(P5, 'r') as f:
    score_data = json.load(f)

print("==== PART 2: PHASE 3 AUDIT ====")
req_count = len(jd_reqs)
req_required = sum(1 for r in jd_reqs if r.get('requirement_type') == 'REQUIRED')
req_preferred = sum(1 for r in jd_reqs if r.get('requirement_type') == 'PREFERRED')
atom_count = sum(len(r.get('atoms', [])) for r in jd_reqs)

print(f"TOTAL JD REQUIREMENTS = {req_count}")
print(f"REQUIRED = {req_required}")
print(f"PREFERRED = {req_preferred}")
print(f"ATOM COUNT = {atom_count}\n")

for r in jd_reqs:
    print(f"ID: {r['requirement_id']}\nText: {r['raw_value']}\nCat: {r.get('category')}, Type: {r.get('requirement_type')}")
    print(f"Atoms: {len(r.get('atoms', []))}")
    for a in r.get('atoms', []):
        print(f"  - {a.get('raw_value')}")
    print("---")

print("\n==== PART 3: RESUME EVIDENCE AUDIT ====")
print(f"TOTAL RESUME EVIDENCE = {len(resume_ev)}\n")
for e in resume_ev:
    print(f"ID: {e['evidence_id']}\nRaw: {e.get('raw_value')}\nCategory: {e.get('category')}\nText: {e.get('evidence_text')}\n---")

print("\n==== PART 4: MATCH EDGE FORENSICS ====")
exact, related, partial, transferable, gap = 0, 0, 0, 0, 0
for edge in match_edges:
    mt = edge.get('match_type')
    if mt == 'EXACT': exact += 1
    elif mt == 'RELATED': related += 1
    elif mt == 'PARTIAL': partial += 1
    elif mt == 'TRANSFERABLE': transferable += 1
    elif mt == 'GAP': gap += 1

print(f"EXACT = {exact}")
print(f"RELATED = {related}")
print(f"PARTIAL = {partial}")
print(f"TRANSFERABLE = {transferable}")
print(f"GAP = {gap}\n")

for edge in match_edges:
    req_text = next((r['raw_value'] for r in jd_reqs if r['requirement_id'] == edge['requirement_id']), "UNKNOWN")
    ev_texts = [next((e.get('raw_value', 'Unknown') for e in resume_ev if e['evidence_id'] == ev_id), "UNKNOWN") for ev_id in edge.get('evidence_ids', [])]
    print(f"Req: {req_text}")
    print(f"Evidence: {ev_texts}")
    print(f"Match: {edge.get('match_type')}")
    print(f"Decision: {edge.get('decision_reason')}")
    print("---")

print("\n==== PART 6: PHASE 5 RECOMPUTATION ====")
total_reqs = score_data.get('requirement_scores', [])
sum_wt_cov = sum(r['weight'] * r['coverage'] for r in total_reqs)
sum_wt = sum(r['weight'] for r in total_reqs)
calc_score = (sum_wt_cov / sum_wt) * 100 if sum_wt else 0
print(f"Backend score: {score_data.get('final_score')}")
print(f"Independent score: {calc_score}")

print("\n==== PART 7: SCORE CONTRIBUTION TABLE ====")
for r in sorted(total_reqs, key=lambda x: x.get('requirement_score', 0), reverse=True):
    print(f"{r['requirement_text'][:40]}... | {r['requirement_type']} | Wt: {r['weight']} | Cov: {r['coverage']} | Contrib: {r.get('requirement_score')}")

