import re
import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.max_chunk_size,
    chunk_overlap=settings.chunk_overlap,
    separators=["\n\n", "\n", ". ", " "],
)


def _clean_text(text: str) -> str:
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
    text = text.replace("\u00a0", " ").replace("\u200b", "").replace("\ufeff", "")
    text = re.sub(r"[^\S\n]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return "\n".join(line.strip() for line in text.split("\n")).strip()


def extract_text(content: bytes, mime_type: str) -> str:
    if mime_type == "application/pdf":
        doc = fitz.open(stream=content, filetype="pdf")
        pages = [_clean_text(page.get_text("text")) for page in doc]
        doc.close()
        return "\n\n".join(p for p in pages if p)
    elif mime_type in ("application/vnd.google-apps.document", "text/plain"):
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1")
        return _clean_text(text)
    return ""


def chunk_text(text: str, doc_id: str, file_name: str) -> list[Document]:
    if not text.strip():
        return []

    docs = _splitter.create_documents(
        texts=[text],
        metadatas=[{"doc_id": doc_id, "file_name": file_name, "source": "gdrive"}],
    )
    for i, doc in enumerate(docs):
        doc.metadata["chunk_index"] = i

    logger.info(f"Chunked '{file_name}' into {len(docs)} chunks")
    return docs
