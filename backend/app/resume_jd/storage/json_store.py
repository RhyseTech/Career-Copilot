import json
import os
from datetime import datetime, timezone, timedelta
from app.resume_jd.models.canonical_jd import CanonicalJD
from app.resume_jd.models.canonical_models import CanonicalResume

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
            
        for d in [self.base_dir, self.resume_dir]:
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
