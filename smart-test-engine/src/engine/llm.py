import os
import requests

from .models import PullRequestChange, RankedTest


class OllamaExplainer:
    def __init__(self, model_name: str = "llama3.1", base_url: str | None = None) -> None:
        self.model_name = model_name
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def explain(self, change: PullRequestChange, ranked_tests: list[RankedTest]) -> str:
        payload = {
            "model": self.model_name,
            "prompt": self._build_prompt(change, ranked_tests),
            "stream": False,
        }
        response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "")

    def _build_prompt(self, change: PullRequestChange, ranked_tests: list[RankedTest]) -> str:
        lines = [
            "You are a test prioritization assistant.",
            f"PR #{change.pr_number}: {change.title}",
            f"Files changed: {', '.join(change.changed_files)}",
            "Ranked tests:",
        ]
        for item in ranked_tests[:10]:
            lines.append(f"- {item.test.name} | ml_score={item.ml_score:.3f} | retrieval_score={item.retrieval_score:.3f}")
        lines.append("Explain why these tests should run first and identify any likely risk gaps.")
        return "\n".join(lines)
