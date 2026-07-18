from dataclasses import dataclass
from typing import Sequence

import faiss
import numpy as np

from .embeddings import EmbeddingService
from .models import PullRequestChange, TestCaseRecord


@dataclass
class RetrievalResult:
    test: TestCaseRecord
    score: float
    evidence: str


class FaissRetriever:
    def __init__(self, embedding_service: EmbeddingService) -> None:
        self.embedding_service = embedding_service
        self.index: faiss.Index | None = None
        self.corpus: list[TestCaseRecord] = []
        self.texts: list[str] = []

    def build(self, tests: Sequence[TestCaseRecord], texts: Sequence[str]) -> None:
        vectors = self.embedding_service.encode(list(texts))
        dimension = vectors.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(vectors)
        self.corpus = list(tests)
        self.texts = list(texts)

    def search(self, change: PullRequestChange, top_k: int = 5) -> list[RetrievalResult]:
        if self.index is None:
            raise RuntimeError("FAISS index is not built")
        query = f"{change.title}\n{change.description}\n{change.diff_text}\n" + "\n".join(change.changed_files)
        query_vector = self.embedding_service.encode([query])
        scores, indices = self.index.search(query_vector, top_k)
        results: list[RetrievalResult] = []
        for rank, idx in enumerate(indices[0]):
            if idx < 0:
                continue
            test = self.corpus[idx]
            evidence = self.texts[idx]
            results.append(RetrievalResult(test=test, score=float(scores[0][rank]), evidence=evidence))
        return results
