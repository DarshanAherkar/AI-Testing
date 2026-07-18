from fastapi import FastAPI
from pydantic import BaseModel, Field

from .config import EngineConfig
from .models import PullRequestChange, TestCaseRecord
from .plan import build_execution_plan
from .service import SmartTestSelectionEngine

app = FastAPI(title="Smart Test Selection Engine")
engine = SmartTestSelectionEngine(EngineConfig())


class PrioritizeRequest(BaseModel):
    pr_number: int
    title: str
    description: str = ""
    changed_files: list[str] = Field(default_factory=list)
    diff_text: str = ""
    candidates: list[dict] = Field(default_factory=list)


@app.post("/prioritize")
def prioritize(request: PrioritizeRequest):
    change = PullRequestChange(
        pr_number=request.pr_number,
        title=request.title,
        description=request.description,
        changed_files=request.changed_files,
        diff_text=request.diff_text,
    )
    tests = [TestCaseRecord(**candidate) for candidate in request.candidates]
    if tests:
        engine.build_index(tests)
    prioritized = engine.prioritize(change, tests)
    return build_execution_plan(prioritized)
