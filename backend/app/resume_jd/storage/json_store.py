import json
import os
from app.resume_jd.models.canonical_jd import CanonicalJD

class JSONStore:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            # __file__ is app/resume_jd/storage/json_store.py
            # 3 levels up is app/
            app_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.base_dir = os.path.join(app_dir, "uploads", "parsed_jds")
        else:
            self.base_dir = base_dir
            
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def save_canonical_jd(self, jd: CanonicalJD) -> str:
        """
        Saves the CanonicalJD model as the single source of truth JSON.
        """
        file_path = os.path.join(self.base_dir, f"{jd.jd_id}_canonical.json")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(jd.model_dump_json(indent=2))
            
        return file_path
