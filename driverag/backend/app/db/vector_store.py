import os
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class VectorStore:

    def __init__(self, embedding_service):
        self._embeddings = embedding_service.langchain_embeddings
        self._store = None
        self._load_or_create()

    def _load_or_create(self):
        path = settings.faiss_store_path
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

        if os.path.exists(path):
            try:
                self._store = FAISS.load_local(path, self._embeddings, allow_dangerous_deserialization=True)
                logger.info(f"Loaded FAISS index: {self._store.index.ntotal} vectors")
                return
            except Exception as e:
                logger.warning(f"Failed to load index: {e}")

        index = faiss.IndexFlatL2(settings.embedding_dimension)
        self._store = FAISS(
            embedding_function=self._embeddings, index=index,
            docstore=InMemoryDocstore(), index_to_docstore_id={},
        )
        logger.info("Created new empty FAISS index")

    def _save(self):
        self._store.save_local(settings.faiss_store_path)

    @property
    def total_vectors(self) -> int:
        return self._store.index.ntotal

    def add_documents(self, documents: list[Document], doc_id: str) -> int:
        if not documents:
            return 0
        ids = [f"{doc_id}_{d.metadata.get('chunk_index', i)}" for i, d in enumerate(documents)]
        self._store.add_documents(documents=documents, ids=ids)
        self._save()
        return len(documents)

    def similarity_search(self, query: str, k: int = 5) -> list[dict]:
        if self.total_vectors == 0:
            return []
        k = min(k, self.total_vectors)
        results = self._store.similarity_search_with_score(query, k=k)
        return [
            {
                "chunk_text": doc.page_content,
                "score": round(float(1.0 / (1.0 + score)), 4),
                "doc_id": doc.metadata.get("doc_id", ""),
                "file_name": doc.metadata.get("file_name", ""),
                "page": doc.metadata.get("page"),
            }
            for doc, score in results
        ]

    def delete_by_doc_id(self, doc_id: str) -> int:
        ids = [sid for sid in self._store.index_to_docstore_id.values() if sid.startswith(f"{doc_id}_")]
        if ids:
            self._store.delete(ids=ids)
            self._save()
        return len(ids)
