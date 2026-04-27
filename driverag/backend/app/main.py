from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.utils.logger import setup_logging, get_logger

load_dotenv()
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting DriveRAG API...")

    from app.services.drive_service import init_db
    from app.services.embedding_service import EmbeddingService
    from app.services import processing_service
    from app.db.vector_store import VectorStore

    init_db()
    embedding_service = EmbeddingService()
    app.state.vector_store = VectorStore(embedding_service)
    app.state.processing_service = processing_service

    logger.info(f"✓ LLM: {settings.llm_provider} | Embeddings: {settings.embedding_model} | Vectors: {app.state.vector_store.total_vectors}")
    yield
    logger.info("👋 Shutting down...")


app = FastAPI(title="DriveRAG API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

from app.api.routes import router
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {"service": "DriveRAG API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "llm_provider": settings.llm_provider, "embedding_model": settings.embedding_model}
