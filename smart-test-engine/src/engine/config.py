from dataclasses import dataclass


@dataclass(frozen=True)
class EngineConfig:
    embedding_model_name: str = "all-MiniLM-L6-v2"
    ollama_model_name: str = "llama3.1"
    faiss_index_path: str = "data/faiss.index"
    metadata_store_path: str = "data/test_catalog.json"
    max_tests: int = 20
