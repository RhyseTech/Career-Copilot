import json
import os
from datetime import datetime, timezone, timedelta
from app.resume_jd.models.canonical_jd import CanonicalJD
from app.resume_jd.models.canonical_models import CanonicalResume
from app.resume_jd.models.phase_03_models import JDRequirement, ResumeEvidence
from typing import List

class JSONStore:
    def __init__(self, base_dir: str = None, resume_dir: str = None):
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        if base_dir is None:
            self.base_dir = os.path.join(app_dir, "uploads", "parsed_jds")
        else:
            self.base_dir = base_dir
            
        if resume_dir is None:
            self.resume_dir = os.path.join(app_dir, "uploads", "parsed_resumes")
        else:
            self.resume_dir = resume_dir
            
        self.phase_03_dir = os.path.join(app_dir, "uploads", "phase_03")
        self.phase_04_dir = os.path.join(app_dir, "uploads", "phase_04")
        self.phase_05_dir = os.path.join(app_dir, "uploads", "phase_05")
            
        for d in [self.base_dir, self.resume_dir, self.phase_03_dir, self.phase_04_dir, self.phase_05_dir]:
            if not os.path.exists(d):
                os.makedirs(d)

    def _get_kolkata_now(self):
        kolkata_tz = timezone(timedelta(hours=5, minutes=30))
        return datetime.now(kolkata_tz)

    def save_canonical_jd(self, jd: CanonicalJD) -> str:
        """
        Saves the CanonicalJD model as the single source of truth JSON.
        """
        if not jd.created_at:
            now = self._get_kolkata_now()
            jd.created_at = now.isoformat(timespec='seconds')
            ts_str = now.strftime("%Y%m%d_%H%M%S")
        else:
            try:
                # Try to parse existing timestamp for filename
                dt = datetime.fromisoformat(jd.created_at)
                ts_str = dt.strftime("%Y%m%d_%H%M%S")
            except ValueError:
                ts_str = "00000000_000000"

        file_name = f"jd_{ts_str}_{jd.jd_id}.json"
        file_path = os.path.join(self.base_dir, file_name)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(jd.model_dump_json(indent=2))
            
        return file_path

    def save_canonical_resume(self, resume: CanonicalResume) -> str:
        """
        Saves the CanonicalResume model as the single source of truth JSON.
        """
        if not resume.created_at:
            now = self._get_kolkata_now()
            resume.created_at = now.isoformat(timespec='seconds')
            ts_str = now.strftime("%Y%m%d_%H%M%S")
        else:
            try:
                dt = datetime.fromisoformat(resume.created_at)
                ts_str = dt.strftime("%Y%m%d_%H%M%S")
            except ValueError:
                ts_str = "00000000_000000"

        file_name = f"resume_{ts_str}_{resume.resume_id}.json"
        file_path = os.path.join(self.resume_dir, file_name)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(resume.model_dump_json(indent=2))
            
        return file_path

    def get_canonical_jd_by_hash(self, content_hash: str) -> CanonicalJD | None:
        if not os.path.exists(self.base_dir):
            return None
        for filename in os.listdir(self.base_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.base_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if data.get("content_hash") == content_hash:
                            return CanonicalJD(**data)
                except Exception:
                    continue
        return None

    def get_canonical_resume_by_hash(self, content_hash: str) -> CanonicalResume | None:
        if not os.path.exists(self.resume_dir):
            return None
        for filename in os.listdir(self.resume_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.resume_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if data.get("content_hash") == content_hash:
                            return CanonicalResume(**data)
                except Exception:
                    continue
        return None

    def get_canonical_jd_by_id(self, jd_id: str) -> CanonicalJD | None:
        if not os.path.exists(self.base_dir):
            return None
        for filename in os.listdir(self.base_dir):
            if filename.endswith(f"_{jd_id}.json"):
                file_path = os.path.join(self.base_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        return CanonicalJD(**data)
                except Exception:
                    continue
        return None

    def get_canonical_resume_by_id(self, resume_id: str) -> CanonicalResume | None:
        if not os.path.exists(self.resume_dir):
            return None
        for filename in os.listdir(self.resume_dir):
            if filename.endswith(f"_{resume_id}.json"):
                file_path = os.path.join(self.resume_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        return CanonicalResume(**data)
                except Exception:
                    continue
        return None

    def save_phase3_jd(self, jd_id: str, requirements: List[JDRequirement]):
        now = self._get_kolkata_now()
        ts_str = now.strftime("%Y%m%d_%H%M%S")
        created_at_str = now.isoformat(timespec='seconds')
        
        file_name = f"jd_requirements_{ts_str}_{jd_id}.json"
        file_path = os.path.join(self.phase_03_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            data = {
                "jd_id": jd_id,
                "created_at": created_at_str,
                "requirements": [r.model_dump() for r in requirements]
            }
            json.dump(data, f, indent=2)

    def get_phase3_jd(self, jd_id: str) -> List[JDRequirement] | None:
        if not os.path.exists(self.phase_03_dir):
            return None
            
        # Support both new timestamped format and old format
        for filename in sorted(os.listdir(self.phase_03_dir), reverse=True):
            if filename.endswith(f"{jd_id}.json") and filename.startswith("jd_requirements_"):
                file_path = os.path.join(self.phase_03_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        return [JDRequirement(**r) for r in data.get("requirements", [])]
                except Exception:
                    pass
        return None

    def save_phase3_resume(self, resume_id: str, evidence: List[ResumeEvidence]):
        now = self._get_kolkata_now()
        ts_str = now.strftime("%Y%m%d_%H%M%S")
        created_at_str = now.isoformat(timespec='seconds')
        
        file_name = f"resume_evidence_{ts_str}_{resume_id}.json"
        file_path = os.path.join(self.phase_03_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            data = {
                "resume_id": resume_id,
                "created_at": created_at_str,
                "evidence": [e.model_dump() for e in evidence]
            }
            json.dump(data, f, indent=2)

    def get_phase3_resume(self, resume_id: str) -> List[ResumeEvidence] | None:
        if not os.path.exists(self.phase_03_dir):
            return None
            
        for filename in sorted(os.listdir(self.phase_03_dir), reverse=True):
            if filename.endswith(f"{resume_id}.json") and filename.startswith("resume_evidence_"):
                file_path = os.path.join(self.phase_03_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        return [ResumeEvidence(**e) for e in data.get("evidence", [])]
                except Exception:
                    pass
        return None

    def save_phase4_edges(self, analysis_id: str, edges: list):
        now = self._get_kolkata_now()
        ts_str = now.strftime("%Y%m%d_%H%M%S")
        created_at_str = now.isoformat(timespec='seconds')
        
        file_name = f"match_edges_{ts_str}_{analysis_id}.json"
        file_path = os.path.join(self.phase_04_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            data = {
                "analysis_id": analysis_id,
                "created_at": created_at_str,
                "match_edges": [e.model_dump() for e in edges]
            }
            json.dump(data, f, indent=2)

    def save_phase5_score(self, analysis_id: str, score):
        now = self._get_kolkata_now()
        ts_str = now.strftime("%Y%m%d_%H%M%S")
        created_at_str = now.isoformat(timespec='seconds')
        
        if not score.created_at:
            score.created_at = created_at_str
            
        file_name = f"phase5_score_{ts_str}_{analysis_id}.json"
        file_path = os.path.join(self.phase_05_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(score.model_dump_json(indent=2))
