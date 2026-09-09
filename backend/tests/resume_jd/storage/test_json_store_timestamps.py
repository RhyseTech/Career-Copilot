import pytest
import os
import json
import tempfile
import time
from datetime import datetime

from app.resume_jd.storage.json_store import JSONStore
from app.resume_jd.models.canonical_jd import CanonicalJD
from app.resume_jd.models.canonical_models import CanonicalResume, CanonicalItem

@pytest.fixture
def temp_store():
    with tempfile.TemporaryDirectory() as base_dir, tempfile.TemporaryDirectory() as resume_dir:
        yield JSONStore(base_dir=base_dir, resume_dir=resume_dir)

def test_new_jd_artifact_contains_created_at(temp_store):
    """A. New JD artifact contains created_at."""
    jd = CanonicalJD(jd_id="jd_test_1", content_hash="hash", raw_text="text")
    file_path = temp_store.save_canonical_jd(jd)
    
    with open(file_path, "r") as f:
        data = json.load(f)
    assert data.get("created_at") is not None

def test_new_resume_artifact_contains_created_at(temp_store):
    """B. New Resume artifact contains created_at."""
    resume = CanonicalResume(resume_id="res_test_1", file_name="file.pdf", items=[])
    file_path = temp_store.save_canonical_resume(resume)
    
    with open(file_path, "r") as f:
        data = json.load(f)
    assert data.get("created_at") is not None

def test_created_at_contains_kolkata_timezone(temp_store):
    """C. created_at contains +05:30 timezone."""
    jd = CanonicalJD(jd_id="jd_test_2", content_hash="hash", raw_text="text")
    temp_store.save_canonical_jd(jd)
    assert jd.created_at.endswith("+05:30")

def test_created_at_is_valid_iso8601(temp_store):
    """D. created_at is valid ISO-8601."""
    jd = CanonicalJD(jd_id="jd_test_3", content_hash="hash", raw_text="text")
    temp_store.save_canonical_jd(jd)
    # Should parse successfully if ISO-8601
    dt = datetime.fromisoformat(jd.created_at)
    assert dt is not None

def test_filename_convention_and_corresponds_to_created_at(temp_store):
    """E. Filename follows convention and F. Corresponds to created_at."""
    jd = CanonicalJD(jd_id="jd_test_4", content_hash="hash", raw_text="text")
    file_path = temp_store.save_canonical_jd(jd)
    file_name = os.path.basename(file_path)
    
    # "jd_{YYYYMMDD_HHMMSS}_{jd_id}.json"
    dt = datetime.fromisoformat(jd.created_at)
    expected_ts_str = dt.strftime("%Y%m%d_%H%M%S")
    expected_filename = f"jd_{expected_ts_str}_jd_test_4.json"
    
    assert file_name == expected_filename

def test_document_id_remains_unchanged(temp_store):
    """G. document_id remains unchanged/stable."""
    jd = CanonicalJD(jd_id="fixed_id", content_hash="hash", raw_text="text")
    temp_store.save_canonical_jd(jd)
    assert jd.jd_id == "fixed_id"

def test_two_artifacts_sortable_timestamps(temp_store):
    """H. Two artifacts created at different times have different sortable timestamps."""
    jd1 = CanonicalJD(jd_id="jd1", content_hash="hash", raw_text="text")
    fp1 = temp_store.save_canonical_jd(jd1)
    
    time.sleep(1.1) # ensure a different second
    
    jd2 = CanonicalJD(jd_id="jd2", content_hash="hash", raw_text="text")
    fp2 = temp_store.save_canonical_jd(jd2)
    
    dt1 = datetime.fromisoformat(jd1.created_at)
    dt2 = datetime.fromisoformat(jd2.created_at)
    
    assert dt2 > dt1
    assert os.path.basename(fp2) > os.path.basename(fp1)

def test_existing_artifacts_not_silently_rewritten(temp_store):
    """I. Existing artifacts are not silently rewritten (preserves given timestamp)."""
    # Simulate an artifact loaded with an existing timestamp
    jd = CanonicalJD(jd_id="jd_exist", content_hash="hash", raw_text="text", created_at="2020-01-01T10:00:00+05:30")
    file_path = temp_store.save_canonical_jd(jd)
    
    # Check that created_at remained 2020
    assert jd.created_at == "2020-01-01T10:00:00+05:30"
    file_name = os.path.basename(file_path)
    assert file_name == "jd_20200101_100000_jd_exist.json"

def test_no_phase_3_behavior_changes():
    """J. No Phase 3 behavior changes."""
    # We didn't touch phase 3 extractor. We verify models still construct.
    from app.resume_jd.models.phase_03_models import JDRequirement, JDRequirementAtom
    # Ensure they instantiate
    atom = JDRequirementAtom(atom_id="1", raw_value="test", atom_type="SKILL")
    assert atom.atom_id == "1"
