# Smart Test Selection and Prioritisation Engine

This project scaffolds an ML + RAG + LLM engine for selecting and prioritising tests for a pull request.

## Stack
- ML ranking: scikit-learn
- Semantic retrieval: FAISS + all-MiniLM-L6-v2
- LLM reasoning: Ollama with Llama 3.1
- Execution: local self-hosted GitHub Runner

## Flow
1. Extract PR and diff features
2. Embed change/test metadata with all-MiniLM-L6-v2
3. Retrieve similar PRs and evidence with FAISS
4. Rank candidate tests with scikit-learn
5. Ask Ollama (Llama 3.1) for explanation and refinement
6. Return a prioritized execution plan with rationale and runnable targets

## Local setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ollama
Start Ollama locally and pull the model:

```bash
ollama pull llama3.1
ollama serve
```

## Self-hosted GitHub Runner
Use a local self-hosted runner for workflow execution. The runner should live on a machine that has:
- Python 3.11+
- Ollama installed and running
- Network access to GitHub
- Access to any local test metadata store or artifact cache

## Next build steps
- Create a test catalog
- Ingest historical PR/test outcomes
- Train the ranking model
- Wire FAISS retrieval into the scoring API
- Add a GitHub Actions workflow targeting `runs-on: self-hosted`

## Tester repo integration
See `smart-test-engine/integration/tester-smoke-tests.yml` for a template that the tester repository can copy into `.github/workflows/tester-smoke-tests.yml`.
