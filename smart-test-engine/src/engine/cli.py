from __future__ import annotations

import argparse
import json
from pathlib import Path

from .catalog import TestCatalog
from .config import EngineConfig
from .models import PullRequestChange
from .plan import build_execution_plan
from .service import SmartTestSelectionEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Smart test selection engine")
    parser.add_argument("--pr-number", type=int, required=True)
    parser.add_argument("--title", type=str, required=True)
    parser.add_argument("--description", type=str, default="")
    parser.add_argument("--changed-files", type=str, default="", help="Comma separated list")
    parser.add_argument("--diff-file", type=str, default="")
    parser.add_argument("--catalog", type=str, default="smart-test-engine/data/test_catalog.json")
    parser.add_argument("--output", type=str, default="smart-test-engine/data/test_plan.json")
    return parser


def run_selection(
    *,
    pr_number: int,
    title: str,
    description: str,
    changed_files: list[str],
    diff_text: str,
    catalog_path: str,
    output_path: str,
) -> dict:
    config = EngineConfig()
    engine = SmartTestSelectionEngine(config)
    catalog = TestCatalog(catalog_path).load()
    if catalog:
        engine.build_index(catalog)
    change = PullRequestChange(
        pr_number=pr_number,
        title=title,
        description=description,
        changed_files=changed_files,
        diff_text=diff_text,
    )
    ranked = engine.prioritize(change, catalog)
    output = {
        "pr_number": pr_number,
        "execution_plan": build_execution_plan(ranked),
    }
    Path(output_path).write_text(json.dumps(output, indent=2), encoding="utf-8")
    return output


def main() -> None:
    args = build_parser().parse_args()
    diff_text = Path(args.diff_file).read_text(encoding="utf-8") if args.diff_file else ""
    output = run_selection(
        pr_number=args.pr_number,
        title=args.title,
        description=args.description,
        changed_files=[item.strip() for item in args.changed_files.split(",") if item.strip()],
        diff_text=diff_text,
        catalog_path=args.catalog,
        output_path=args.output,
    )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
