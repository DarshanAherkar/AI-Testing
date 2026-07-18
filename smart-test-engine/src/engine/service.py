from .config import EngineConfig
from .embeddings import EmbeddingService
from .llm import OllamaExplainer
from .models import PullRequestChange, RankedTest, TestCaseRecord
from .ranking import TestRanker
from .retrieval import FaissRetriever


class SmartTestSelectionEngine:
    def __init__(self, config: EngineConfig | None = None) -> None:
        self.config = config or EngineConfig()
        self.embedding_service = EmbeddingService(self.config)
        self.retriever = FaissRetriever(self.embedding_service)
        self.ranker = TestRanker()
        self.explainer = OllamaExplainer(self.config.ollama_model_name)

    def build_index(self, tests: list[TestCaseRecord]) -> None:
        texts = [" ".join([test.name, test.module, " ".join(test.tags), " ".join(test.coverage_targets)]) for test in tests]
        self.retriever.build(tests, texts)

    def prioritize(self, change: PullRequestChange, candidate_tests: list[TestCaseRecord]) -> list[RankedTest]:
        retrieval_results = self.retriever.search(change, top_k=min(self.config.max_tests, len(candidate_tests))) if candidate_tests else []
        ranked = self.ranker.score(change, candidate_tests)
        retrieval_scores = {result.test.test_id: result.score for result in retrieval_results}
        for item in ranked:
            item.retrieval_score = retrieval_scores.get(item.test.test_id, 0.0)
        ranked.sort(key=lambda item: (item.ml_score, item.retrieval_score), reverse=True)
        rationale = self.explainer.explain(change, ranked)
        for item in ranked:
            item.llm_rationale = rationale
        return ranked
