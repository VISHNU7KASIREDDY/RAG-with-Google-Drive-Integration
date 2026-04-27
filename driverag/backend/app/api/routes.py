import threading

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from app.core.config import settings
from app.models.schemas import (
    SyncRequest, SyncResponse, AskRequest, AskResponse, Source,
    DocumentResponse, StatsResponse, DeleteResponse,
)
from app.services import drive_service, rag_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


def _app():
    from app.main import app
    return app


@router.get("/auth/google")
async def auth_google():
    url = drive_service.get_auth_url()
    return RedirectResponse(url)


@router.get("/auth/callback")
async def auth_callback(code: str):
    try:
        drive_service.handle_callback(code)
        return RedirectResponse(f"{settings.frontend_url}/?auth=success")
    except Exception as e:
        logger.error(f"Auth callback error: {e}")
        return RedirectResponse(f"{settings.frontend_url}/?auth=error&message={str(e)[:100]}")


@router.get("/auth/status")
async def auth_status():
    import os
    connected = os.path.exists(drive_service.TOKEN_FILE)
    return {"connected": connected}


@router.post("/sync-drive")
async def sync_drive(request: SyncRequest):
    if drive_service.sync_state["is_syncing"]:
        raise HTTPException(status_code=409, detail="Sync already in progress.")
    try:
        state = _app().state

        def run_sync():
            try:
                drive_service.sync(state.processing_service, state.vector_store, request.force_resync)
            except Exception as e:
                logger.error(f"Background sync error: {e}")

        threading.Thread(target=run_sync, daemon=True).start()
        return {"message": "Sync started. Poll /api/sync-drive/status for progress."}
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Sync error: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)[:200]}")


@router.get("/sync-drive/status")
async def sync_status():
    return drive_service.sync_state


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        vs = _app().state.vector_store
        if vs.total_vectors == 0:
            return AskResponse(answer="No documents indexed yet. Please sync your Google Drive first.", sources=[], query=query)

        answer, results = rag_service.answer_question(vs, query=query, top_k=request.top_k)
        sources = [
            Source(file_name=r["file_name"], doc_id=r["doc_id"],
                   chunk_text=r["chunk_text"][:500], score=r["score"], page=r.get("page"))
            for r in results
        ]
        return AskResponse(answer=answer, sources=sources, query=query)
    except Exception as e:
        logger.error(f"Ask error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {str(e)[:200]}")


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents():
    docs = drive_service.get_all_documents()
    return [
        DocumentResponse(id=d["id"], file_name=d["file_name"], status=d["status"],
                         chunk_count=d["chunk_count"] or 0, last_synced=d.get("last_synced"),
                         mime_type=d.get("mime_type"), error_message=d.get("error_message"))
        for d in docs
    ]


@router.get("/documents/stats", response_model=StatsResponse)
async def get_stats():
    return StatsResponse(**drive_service.get_stats())


@router.delete("/documents/{doc_id}", response_model=DeleteResponse)
async def delete_document(doc_id: str):
    doc = drive_service.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    chunks = _app().state.vector_store.delete_by_doc_id(doc_id)
    drive_service.delete_document(doc_id)
    return DeleteResponse(message=f"Document '{doc['file_name']}' deleted.", doc_id=doc_id, chunks_removed=chunks)
