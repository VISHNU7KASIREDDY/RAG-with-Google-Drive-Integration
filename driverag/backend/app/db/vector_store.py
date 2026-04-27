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
        self._stores: dict[str, FAISS] = {}

    def _get_path(self, session_id: str) -> str:
        return f"{settings.faiss_store_path}_{session_id}"

    def _get_store(self, session_id: str) -> FAISS:
        if session_id in self._stores:
            return self._stores[session_id]

        path = self._get_path(session_id)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

        if os.path.exists(path):
            try:
                store = FAISS.load_local(path, self._embeddings, allow_dangerous_deserialization=True)
                self._stores[session_id] = store
                logger.info(f"Loaded FAISS index for {session_id}: {store.index.ntotal} vectors")
                return store
            except Exception as e:
                logger.warning(f"Failed to load index for {session_id}: {e}")

        index = faiss.IndexFlatL2(settings.embedding_dimension)
        store = FAISS(
            embedding_function=self._embeddings, index=index,
            docstore=InMemoryDocstore(), index_to_docstore_id={},
        )
        self._stores[session_id] = store
        logger.info(f"Created new empty FAISS index for {session_id}")
        return store

    def _save(self, session_id: str):
        if session_id in self._stores:
            self._stores[session_id].save_local(self._get_path(session_id))

    def get_total_vectors(self, session_id: str) -> int:
        return self._get_store(session_id).index.ntotal

    def add_documents(self, session_id: str, documents: list[Document], doc_id: str) -> int:
        if not documents:
            return 0
        store = self._get_store(session_id)
        ids = [f"{doc_id}_{d.metadata.get('chunk_index', i)}" for i, d in enumerate(documents)]
        store.add_documents(documents=documents, ids=ids)
        self._save(session_id)
        return len(documents)

    def similarity_search(self, session_id: str, query: str, k: int = 5) -> list[dict]:
        store = self._get_store(session_id)
        if store.index.ntotal == 0:
            return []
        k = min(k, store.index.ntotal)
        results = store.similarity_search_with_score(query, k=k)
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

    def delete_by_doc_id(self, session_id: str, doc_id: str) -> int:
        store = self._get_store(session_id)
        ids = [sid for sid in store.index_to_docstore_id.values() if sid.startswith(f"{doc_id}_")]
        if ids:
            store.delete(ids=ids)
            self._save(session_id)
        return len(ids)
