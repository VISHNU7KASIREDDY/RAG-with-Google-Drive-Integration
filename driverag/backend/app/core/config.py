from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_provider: str = "groq"
    gemini_api_key: str = ""
    openai_api_key: str = ""
    groq_api_key: str = ""

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/auth/callback"
    frontend_url: str = "http://localhost:5173"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    max_chunk_size: int = 500
    chunk_overlap: int = 50
    faiss_store_path: str = "./data/faiss_index"
    database_url: str = "./data/driverag.db"
    top_k_results: int = 5

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
