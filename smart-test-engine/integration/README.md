# Tester Repo Integration Template

This folder contains the workflow template that the tester repository can use to consume the smart test selection engine output.

## Expected flow
1. The source repo workflow dispatches the tester repo workflow.
2. The tester repo checks out its own code.
3. The tester repo checks out the engine repository containing `smart-test-engine/`.
4. The tester repo fetches PR changed files from the source repository.
5. The tester repo runs the engine CLI to generate an execution plan.
6. The tester repo runs the Playwright specs returned by the plan.

## Template file
- `tester-smoke-tests.yml`

## Engine output contract
The engine now emits an `execution_plan` object with:
- `must_run`
- `high_priority`
- `optional`

Each selected test includes:
- `execution_targets`
- `ml_score`
- `retrieval_score`
- `rationale`

## What to copy into the tester repo
Copy the workflow file into `.github/workflows/tester-smoke-tests.yml` in the tester repository.
