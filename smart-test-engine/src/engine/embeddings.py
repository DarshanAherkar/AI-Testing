from sentence_transformers import SentenceTransformer
import numpy as np

from .config import EngineConfig


class EmbeddingService:
    def __init__(self, config: EngineConfig | None = None) -> None:
        self.config = config or EngineConfig()
        self.model = SentenceTransformer(self.config.embedding_model_name)

    def encode(self, texts: list[str]) -> np.ndarray:
        vectors = self.model.encode(texts, normalize_embeddings=True)
        return np.asarray(vectors, dtype="float32")
