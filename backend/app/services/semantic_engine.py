from sentence_transformers import SentenceTransformer
import numpy as np

class SemanticEngine:
    def __init__(self):
        # Load the pre-trained model (all-MiniLM-L6-v2 is fast and effective)
        # Note: This will download the model on first run, which takes time.
        # In production, the model would be baked into the Docker image.
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculates cosine similarity between two texts.
        Returns a score between 0.0 and 1.0
        """
        if not text1 or not text2:
            return 0.0
            
        embeddings = self.model.encode([text1, text2])
        vec1 = embeddings[0]
        vec2 = embeddings[1]
        
        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        similarity = dot_product / (norm_a * norm_b)
        return float(max(0.0, min(1.0, similarity))) # Clamp between 0 and 1
