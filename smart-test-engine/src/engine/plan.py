from __future__ import annotations

from dataclasses import asdict

from .models import RankedTest


def _priority_bucket(item: RankedTest) -> str:
    score = max(item.ml_score, item.retrieval_score)
    if "risk" in item.test.tags or item.test.last_result == "failed" or score >= 0.75:
        return "must_run"
    if score >= 0.45 or item.test.flakiness_score >= 0.1:
        return "high_priority"
    return "optional"


def build_execution_plan(ranked_tests: list[RankedTest]) -> dict:
    plan = {"must_run": [], "high_priority": [], "optional": []}
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
