import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)

def test_resume_parse():
    # Use the sample resume
    sample_resume = os.path.join("..", "docs", "Sample_Resume.pdf")
    if not os.path.exists(sample_resume):
        pytest.skip("Sample resume not found")
        
    with open(sample_resume, "rb") as f:
        response = client.post(
            "/resume-jd/resume/parse",
            files={"file": ("Sample_Resume.pdf", f, "application/pdf")}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["phase"] == 1
    assert "resume_id" in data
    assert "resume" in data

def test_jd_parse():
    jd_text = "Looking for a Python Developer with 5 years of experience in AWS."
    response = client.post(
        "/resume-jd/jd/parse",
        data={"jd_text": jd_text}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["phase"] == 1
    assert "jd_id" in data
    assert "jd" in data

def test_invalid_resume():
    response = client.post(
        "/resume-jd/resume/parse",
        files={"file": ("test.txt", b"invalid format", "text/plain")}
    )
    assert response.status_code == 500

def test_missing_jd():
    response = client.post(
        "/resume-jd/jd/parse",
        data={}
    )
    assert response.status_code == 422 # FastAPI validation error for missing Form field

def test_analysis_run():
    # E2E test for orchestrator
    sample_resume = os.path.join("..", "docs", "Sample_Resume.pdf")
    if not os.path.exists(sample_resume):
        pytest.skip("Sample resume not found")
        
    jd_text = "Looking for a Python Developer with 5 years of experience in AWS and LLMs."
    
    with open(sample_resume, "rb") as f:
        response = client.post(
            "/resume-jd/analysis/run",
            files={"file": ("Sample_Resume.pdf", f, "application/pdf")},
            data={"jd_text": jd_text}
        )
        
    assert response.status_code == 200
    data = response.json()
    
    # Verify orchestrated outputs
    assert "analysis_id" in data
    assert "phase_1" in data
    assert "phase_2" in data
    assert "phase_3" in data
    assert "phase_4" in data
    assert "phase_5" in data
    
    # Check Phase 5 score exists
    assert "score" in data["phase_5"]
    assert "final_score" in data["phase_5"]["score"]

def test_phase_dependency_error():
    # Phase 4 requires an analysis ID that exists. 
    # If we pass a fake one, it should return 400.
    response = client.post(
        "/resume-jd/analysis/matches",
        json={"analysis_id": "fake_jd_fake"}
    )
    assert response.status_code == 400
    assert "Phase 3 requirements/evidence are required" in response.json()["detail"]
    
def test_phase5_dependency_error():
    response = client.post(
        "/resume-jd/analysis/score",
        json={"analysis_id": "fake_jd_fake"}
    )
    assert response.status_code == 400
    assert "Phase 3 requirements/evidence are required" in response.json()["detail"]

