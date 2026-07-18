from sklearn.ensemble import GradientBoostingClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.pipeline import Pipeline

from .models import PullRequestChange, RankedTest, TestCaseRecord


class TestRanker:
    def __init__(self) -> None:
        self.pipeline = Pipeline(
            [
                ("vectorizer", DictVectorizer(sparse=False)),
                ("model", GradientBoostingClassifier(random_state=42)),
            ]
        )
        self.is_trained = False

    def _features(self, change: PullRequestChange, test: TestCaseRecord) -> dict[str, float | int | bool]:
        touched_module = test.module in change.diff_text or any(test.module in file_path for file_path in change.changed_files)
        return {
            "runtime_seconds": test.runtime_seconds,
            "flakiness_score": test.flakiness_score,
            "has_tag_risk": int("risk" in test.tags),
            "has_module_overlap": int(touched_module),
            "changed_files_count": len(change.changed_files),
            "diff_length": len(change.diff_text),
        }

    def train(self, changes: list[PullRequestChange], tests: list[TestCaseRecord], labels: list[int]) -> None:
        feature_rows = []
        for change, test in zip(changes, tests, strict=False):
            feature_rows.append(self._features(change, test))
        self.pipeline.fit(feature_rows, labels)
        self.is_trained = True

    def score(self, change: PullRequestChange, tests: list[TestCaseRecord]) -> list[RankedTest]:
        if not self.is_trained:
            return [RankedTest(test=test, ml_score=0.0, retrieval_score=0.0) for test in tests]
        feature_rows = [self._features(change, test) for test in tests]
        probabilities = self.pipeline.predict_proba(feature_rows)[:, 1]
        ranked = [RankedTest(test=test, ml_score=float(score), retrieval_score=0.0) for test, score in zip(tests, probabilities, strict=False)]
        return sorted(ranked, key=lambda item: item.ml_score, reverse=True)
