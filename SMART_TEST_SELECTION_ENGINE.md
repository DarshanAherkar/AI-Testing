# Smart Test Selection and Prioritisation Engine

## Goal
Use ML, RAG, and an LLM to select and prioritise the smallest useful test set for each pull request, while keeping confidence high and runtime low.

## What the engine should do
- Predict which tests are most likely to fail for a change
- Rank tests by risk and business impact
- Reduce redundant test execution
- Explain why each test was selected
- Learn from historical PRs, failures, flakiness, and fixes

## Recommended architecture

### 1. Test metadata store
Maintain a structured catalog of tests with:
- test name
- owning module/service
- historical failure rate
- average runtime
- flakiness score
- tags and coverage areas
- last run result
- linked requirements or user stories

### 2. Change intelligence layer
For each PR, extract signals such as:
- files changed
- code ownership
- diff size and churn
- touched functions/classes/endpoints
- dependency graph impact
- recent failure clusters in related modules

### 3. ML ranking model
Train a supervised model to score tests by likelihood of failure.
Useful inputs:
- changed file embeddings
- historical PR-test outcomes
- code ownership overlap
- failure recency
- runtime cost
- flakiness history

Good model options:
- gradient boosted trees for interpretability
- lightweight neural ranker for embeddings
- learning-to-rank model for final ordering

### 4. RAG layer
Use retrieval to bring in context that the model should not memorize:
- similar past PRs
- previously failing tests for related modules
- release notes
- defect tickets
- test-to-code mapping docs
- flaky test investigations

The retriever should return top-k evidence that explains why certain tests matter for this PR.

### 5. LLM reasoning and explanation layer
Use the LLM to:
- summarise the PR risk profile
- explain the top ranked tests
- suggest additional edge cases
- generate human-readable rationale for the selection
- produce a concise test plan for reviewers

The LLM should not make the final selection alone. It should justify and refine the ranked output from ML + retrieval.

## Decision flow
1. PR arrives
2. Change intelligence extracts signals
3. RAG fetches similar PRs and related test evidence
4. ML ranks candidate tests
5. LLM explains and optionally adjusts ordering using evidence
6. Engine outputs:
   - must-run tests
   - high-priority tests
   - optional tests
   - skipped tests with justification

## Prioritisation policy
A good default policy is:
- Tier 1: tests directly impacted by changed code
- Tier 2: tests in adjacent modules or shared dependencies
- Tier 3: regression tests for historically risky areas
- Tier 4: optional broad coverage if runtime budget allows

## Metrics to track
- defect detection rate
- recall of failing tests
- precision of selected tests
- average runtime saved
- false negative rate
- flakiness re-run rate
- explanation usefulness

## Phased implementation

### Phase 1: Rules + telemetry
- map tests to code areas
- compute basic risk scoring rules
- collect PR/test outcomes

### Phase 2: ML ranking
- train a first ranker on historical results
- compare against baseline selection rules

### Phase 3: RAG + explanation
- add retrieval from PR history and defect data
- generate explanation text for each selected test

### Phase 4: Production optimisation
- add runtime budgets
- experiment with active learning
- continuously retrain from new PR outcomes

## Suggested API shape
- `POST /score-tests` -> returns ranked tests for a PR
- `POST /explain-selection` -> returns human-readable rationale
- `GET /test-plan/{prId}` -> retrieves the generated prioritised plan

## Output example
- Must run: login flow, checkout flow
- High priority: payment validation, cart merge, order history
- Optional: profile settings, theme switch

## Next step
Build the test catalog and PR feature extractor first. Without those, the ML and RAG layers will not have reliable input.

## Implementation scaffold created
The repository now includes a dedicated Python scaffold under `smart-test-engine/` with:
- a FastAPI prioritisation endpoint
- scikit-learn ranking code
- FAISS retrieval over all-MiniLM-L6-v2 embeddings
- Ollama integration for Llama 3.1 explanations
- a GitHub Actions workflow configured for `runs-on: self-hosted`

This scaffold is the starting point for the Smart Test Selection and Prioritisation Engine implementation.

## Tester repo wiring
The tester repository owns and maintains `.github/workflows/tester-smoke-tests.yml` directly.

That workflow consumes the engine's `execution_plan` output and executes the collected `execution_targets` for:
- `must_run`
- `high_priority`
- `optional`

This keeps the tester repo workflow dynamic instead of relying on a static hardcoded test list.
