from dataclasses import asdict
from pathlib import Path

from .models import RankedTest


def write_test_plan(path: str, ranked_tests: list[RankedTest], pr_number: int) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "pr_number": pr_number,
        "tests": [
            {
                **asdict(item.test),
                "ml_score": item.ml_score,
                "retrieval_score": item.retrieval_score,
                "rationale": item.llm_rationale,
            }
            for item in ranked_tests
        ],
    }
    output_path.write_text(__import__("json").dumps(payload, indent=2), encoding="utf-8")
