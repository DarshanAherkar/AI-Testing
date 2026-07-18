from __future__ import annotations

import json
import os
from pathlib import Path

import requests

from .cli import run_selection


def _load_event() -> dict:
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        return {}
    return json.loads(Path(event_path).read_text(encoding="utf-8"))


def _extract_changed_files(event: dict) -> list[str]:
    pull_request = event.get("pull_request") or {}
    repo = os.getenv("GITHUB_REPOSITORY")
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    pr_number = pull_request.get("number") or event.get("number")
    if repo and token and pr_number:
        return _fetch_pull_request_files(repo, int(pr_number), token)
    if event.get("head_commit"):
        commit = event["head_commit"]
        return [
            *commit.get("added", []),
            *commit.get("modified", []),
            *commit.get("removed", []),
        ]
    files = os.getenv("PR_CHANGED_FILES", "")
    if files:
        return [item.strip() for item in files.split(",") if item.strip()]
    return []


def _fetch_pull_request_files(repository: str, pr_number: int, token: str) -> list[str]:
    files: list[str] = []
    page = 1
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }
    while True:
        response = requests.get(
            f"https://api.github.com/repos/{repository}/pulls/{pr_number}/files",
            headers=headers,
            params={"per_page": 100, "page": page},
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        if not payload:
            break
        files.extend(item.get("filename", "") for item in payload if item.get("filename"))
        if len(payload) < 100:
            break
        page += 1
    return files


def main() -> None:
    event = _load_event()
    pull_request = event.get("pull_request") or {}
    head_commit = event.get("head_commit") or {}
    pr_number = int(
        pull_request.get("number")
        or event.get("number")
        or os.getenv("PR_NUMBER", "0")
    )
    title = (
        pull_request.get("title")
        or head_commit.get("message")
        or os.getenv("PR_TITLE", "Manual run")
    )
    description = (
        pull_request.get("body")
        or head_commit.get("message")
        or os.getenv("PR_DESCRIPTION", "")
    )
    changed_files = _extract_changed_files(event)
    diff_text = os.getenv("PR_DIFF_TEXT", "")
    catalog_path = os.getenv("TEST_CATALOG_PATH", "smart-test-engine/data/test_catalog.json")
    output_path = os.getenv("TEST_PLAN_PATH", "smart-test-engine/data/test_plan.json")
    output = run_selection(
        pr_number=pr_number,
        title=title,
        description=description,
        changed_files=changed_files,
        diff_text=diff_text,
        catalog_path=catalog_path,
        output_path=output_path,
    )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
