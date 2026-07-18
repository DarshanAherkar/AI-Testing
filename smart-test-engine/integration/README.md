# Tester Repo Integration Notes

This folder contains integration guidance for the tester repository consuming smart test engine output.

## Expected flow
1. The source repo workflow dispatches the tester repo workflow.
2. The tester repo checks out its own code.
3. The tester repo checks out the engine repository containing `smart-test-engine/`.
4. The tester repo fetches PR changed files from the source repository.
5. The tester repo runs the engine CLI to generate an execution plan.
6. The tester repo runs the Playwright specs returned by the plan.

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

## Tester workflow location
The tester repository maintains its workflow at `.github/workflows/tester-smoke-tests.yml`.

## Optional source repository access
If the source repository is private or the PR files API is rate-limited, pass a read-only token into the tester workflow as a secret and use it when fetching PR file lists.

Recommended secret name:
- `SOURCE_REPO_TOKEN`

Recommended usage:
- add `Authorization: Bearer <token>` when calling `GET /repos/{source_repo}/pulls/{pr_number}/files`
