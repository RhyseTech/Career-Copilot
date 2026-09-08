from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import numpy as np

class SimilarityEngine:
    def __init__(self):
        # We use a small, fast model for CPU inference (MiniLM)
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.model_loaded = True
        except Exception as e:
            print(f"Failed to load sentence-transformers model: {e}")
            self.model_loaded = False

    def compute_lexical(self, text1: str, text2: str) -> float:
        """
        Computes fuzzy lexical similarity between 0.0 and 1.0
        Using token_set_ratio which is robust to word order and extra words.
        """
        if not text1 or not text2:
            return 0.0
        # Rapidfuzz returns 0-100, we scale to 0-1
        score = fuzz.token_set_ratio(text1.lower(), text2.lower()) / 100.0
        return float(score)

    def compute_semantic(self, text1: str, text2: str) -> float:
        """
        Computes cosine similarity between sentence embeddings.
        Returns 0.0 if model failed to load.
        """
        if not self.model_loaded or not text1 or not text2:
            return 0.0
            
        embeddings = self.model.encode([text1, text2], convert_to_tensor=True)
        # Cosine similarity
        from sentence_transformers.util import cos_sim
        similarity = cos_sim(embeddings[0], embeddings[1]).item()
        
        # Scale to 0-1, handle potential minor negative values from floating point
        return max(0.0, float(similarity))

    def compute_similarity(self, text1: str, text2: str) -> Dict[str, float]:
        """
        Returns a dictionary of all similarity scores.
        """
        # Exact Match (ignoring case/whitespace)
        t1_clean = text1.strip().lower()
        t2_clean = text2.strip().lower()
        exact = 1.0 if t1_clean == t2_clean else 0.0

        fuzzy = self.compute_lexical(text1, text2)
        semantic = self.compute_semantic(text1, text2)

        return {
            "exact": exact,
            "fuzzy": fuzzy,
            "semantic": semantic
        }
