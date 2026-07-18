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

    def _fallback_score(self, change: PullRequestChange, test: TestCaseRecord) -> float:
        joined_files = " ".join(change.changed_files).lower()
        joined_text = f"{change.title} {change.description} {change.diff_text}".lower()
        module = test.module.lower()

        module_overlap = int(module in joined_files or module in joined_text)
        coverage_overlap = sum(
            1
            for target in test.coverage_targets
            if target.lower() in joined_files or target.lower() in joined_text
        )

        score = 0.1
        score += 0.55 if module_overlap else 0.0
        score += min(0.25, 0.08 * coverage_overlap)
        score += 0.05 if test.last_result == "failed" else 0.0
        score += 0.05 if "risk" in test.tags else 0.0
        return min(score, 0.99)

    def train(self, changes: list[PullRequestChange], tests: list[TestCaseRecord], labels: list[int]) -> None:
        feature_rows = []
        for change, test in zip(changes, tests, strict=False):
            feature_rows.append(self._features(change, test))
        self.pipeline.fit(feature_rows, labels)
        self.is_trained = True

    def score(self, change: PullRequestChange, tests: list[TestCaseRecord]) -> list[RankedTest]:
        if not self.is_trained:
            fallback_ranked = [
                RankedTest(
                    test=test,
                    ml_score=self._fallback_score(change, test),
                    retrieval_score=0.0,
                )
                for test in tests
            ]
            return sorted(fallback_ranked, key=lambda item: item.ml_score, reverse=True)
        feature_rows = [self._features(change, test) for test in tests]
        probabilities = self.pipeline.predict_proba(feature_rows)[:, 1]
        ranked = [RankedTest(test=test, ml_score=float(score), retrieval_score=0.0) for test, score in zip(tests, probabilities, strict=False)]
        return sorted(ranked, key=lambda item: item.ml_score, reverse=True)
