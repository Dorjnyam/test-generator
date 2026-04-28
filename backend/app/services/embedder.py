"""Sentence-transformer embedding helper."""

from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer

from app.config import settings


class EmbedderService:
    """Singleton-style embedder wrapper with caching."""

    def __init__(self):
        self.model = self._load_model()

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_model():
        return SentenceTransformer(settings.EMBEDDING_MODEL)

    def encode(self, texts: List[str]) -> List[List[float]]:
        """Return list of embeddings for the provided texts."""
        if not isinstance(texts, list):
            texts = [texts]
        embeddings = self.model.encode(texts)
        return [emb.tolist() for emb in embeddings]

