from dataclasses import dataclass, field
from typing import Any


@dataclass
class TestCaseRecord:
    test_id: str
    name: str
    module: str
    tags: list[str] = field(default_factory=list)
    runtime_seconds: float = 0.0
    flakiness_score: float = 0.0
    last_result: str = "unknown"
    coverage_targets: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PullRequestChange:
    pr_number: int
    title: str
    description: str
    changed_files: list[str]
    diff_text: str
    author: str | None = None


@dataclass
class RankedTest:
    test: TestCaseRecord
    ml_score: float
    retrieval_score: float
    llm_rationale: str = ""
