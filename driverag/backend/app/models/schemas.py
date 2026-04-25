from typing import Optional
from pydantic import BaseModel, Field


class SyncRequest(BaseModel):
    force_resync: bool = Field(default=False)


class SyncResponse(BaseModel):
    message: str
    total_files: int
    new_files: int
    updated_files: int
    skipped_files: int
    failed_files: int


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class Source(BaseModel):
    file_name: str
    doc_id: str
    chunk_text: str
    score: float
    page: Optional[int] = None


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    query: str


class DocumentResponse(BaseModel):
    id: str
    file_name: str
    status: str
    chunk_count: int
    last_synced: Optional[str] = None
    mime_type: Optional[str] = None
    error_message: Optional[str] = None


class StatsResponse(BaseModel):
    total_docs: int
    total_chunks: int
    last_sync_time: Optional[str] = None


class DeleteResponse(BaseModel):
    message: str
    doc_id: str
    chunks_removed: int
