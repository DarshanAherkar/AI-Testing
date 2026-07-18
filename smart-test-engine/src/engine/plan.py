from __future__ import annotations

from dataclasses import asdict

from .models import RankedTest


def _priority_bucket(item: RankedTest) -> str:
    score = max(item.ml_score, item.retrieval_score)
    if item.test.last_result == "failed" or score >= 0.75 or ("risk" in item.test.tags and score >= 0.35):
        return "must_run"
    if score >= 0.45 or (item.test.flakiness_score >= 0.1 and score >= 0.30):
        return "high_priority"
    if score >= 0.20:
        return "optional"
    return "skipped"


def build_execution_plan(ranked_tests: list[RankedTest]) -> dict:
    plan = {"must_run": [], "high_priority": [], "optional": [], "skipped": []}
    for item in ranked_tests:
        bucket = _priority_bucket(item)
        plan[bucket].append(
            {
                **asdict(item.test),
                "ml_score": item.ml_score,
                "retrieval_score": item.retrieval_score,
                "rationale": item.llm_rationale,
            }
        )
    return plan
