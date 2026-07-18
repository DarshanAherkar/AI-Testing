import json
from pathlib import Path

from .models import TestCaseRecord


class TestCatalog:
    def __init__(self, path: str) -> None:
        self.path = Path(path)

    def load(self) -> list[TestCaseRecord]:
        if not self.path.exists():
            return []
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return [TestCaseRecord(**item) for item in payload]
