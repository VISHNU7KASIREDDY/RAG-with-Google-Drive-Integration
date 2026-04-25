import os
import numpy as np
from langchain_community.embeddings import FastEmbedEmbeddings
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

os.environ["ONNX_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"


class EmbeddingService:

    def __init__(self):
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        self._model = FastEmbedEmbeddings(
            model_name=settings.embedding_model,
            max_length=512,
            threads=1,
        )
        logger.info("Embedding model loaded")

    @property
    def langchain_embeddings(self) -> FastEmbedEmbeddings:
        return self._model

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        return np.array(self._model.embed_documents(texts), dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        return np.array(self._model.embed_query(query), dtype=np.float32)
