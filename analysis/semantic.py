# analysis/semantic.py

"""
Semantic Checker — Uses sentence-transformers to find similar keys.
ONLY used inside diagnose.py as a detective tool.
Embeddings are computed on-the-fly and NEVER stored permanently.

Usage:
    checker = SemanticChecker()
    result = checker.find_similar("gathering_time", ["project_meeting_time", "wifi_password"])
    # Returns: ("project_meeting_time", 0.85) or None
"""

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    HAS_SEMANTIC = True
except ImportError:
    HAS_SEMANTIC = False


class SemanticChecker:
    """
    Lightweight semantic similarity checker.
    
    - Loads model once (lazy, on first use)
    - Embeds keys ONLY when find_similar() is called
    - Nothing is stored permanently — embeddings are temporary
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", threshold: float = 0.6):
        if not HAS_SEMANTIC:
            raise ImportError(
                "requires sentence-transformers"
            )
        self.threshold = threshold
        self._model = None
        self._model_name = model_name

    def _load_model(self):
        """Lazy load — model loads only on first actual use."""
        if self._model is None:
            self._model = SentenceTransformer(self._model_name)

    def find_similar(self, query_key: str, all_keys: list, threshold: float = None):
        """
        Find the most similar key to query_key from all_keys.
        
        Embeddings are computed fresh each call — nothing stored.
        
        Args:
            query_key: The key the LLM tried to read (e.g. "gathering_time")
            all_keys: List of all stored keys (e.g. ["project_meeting_time", "wifi_password"])
            threshold: Minimum similarity score (default: self.threshold)
        
        Returns:
            Tuple of (matched_key, similarity_score) or None if no match above threshold.
        """
        if not all_keys:
            return None

        # Don't match against itself
        candidates = [k for k in all_keys if k != query_key]
        if not candidates:
            return None

        self._load_model()
        threshold = threshold or self.threshold

        # Embed query and all candidates — temporary, not stored
        query_embedding = self._model.encode(query_key.replace("_", " "))
        candidate_embeddings = self._model.encode([k.replace("_", " ") for k in candidates])

        # Cosine similarity
        scores = np.dot(candidate_embeddings, query_embedding) / (
            np.linalg.norm(candidate_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )

        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])

        if best_score >= threshold:
            return (candidates[best_idx], round(best_score, 3))

        return None
