import threading

from fastapi import APIRouter, HTTPException, Header, Depends
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


DEMO_SESSION = "demo"


def get_session_id(x_session_id: str | None = Header(None)) -> str:
    return x_session_id or DEMO_SESSION


def _app():
    from app.main import app
    return app


def _frontend_url():
    url = settings.frontend_url
    if url and not url.startswith("http"):
        url = f"https://{url}"
    return url.rstrip("/")


@router.get("/auth/google")
async def auth_google(session_id: str):
    url = drive_service.get_auth_url(session_id)
    return RedirectResponse(url)


@router.get("/auth/callback")
async def auth_callback(code: str, state: str):
    try:
        drive_service.handle_callback(code, state)
        return RedirectResponse(f"{_frontend_url()}/?auth=success")
    except Exception as e:
        logger.error(f"Auth callback error: {e}")
        return RedirectResponse(f"{_frontend_url()}/?auth=error&message={str(e)[:100]}")


@router.get("/auth/status")
async def auth_status(session_id: str = Depends(get_session_id)):
    connected = drive_service.is_connected(session_id)
    return {"connected": connected}


@router.post("/auth/disconnect")
async def auth_disconnect(session_id: str = Depends(get_session_id)):
    drive_service.disconnect(session_id)
    return {"message": "Disconnected from Google Drive"}


@router.post("/sync-drive")
async def sync_drive(request: SyncRequest, session_id: str = Depends(get_session_id)):
    state = drive_service.get_sync_state(session_id)
    if state["is_syncing"]:
        raise HTTPException(status_code=409, detail="Sync already in progress.")
    try:
        app_state = _app().state

        def run_sync():
            try:
                drive_service.sync(session_id, app_state.processing_service, app_state.vector_store, request.force_resync)
            except Exception as e:
                logger.error(f"Background sync error for {session_id}: {e}")

        threading.Thread(target=run_sync, daemon=True).start()
        return {"message": "Sync started. Poll /api/sync-drive/status for progress."}
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Sync error for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)[:200]}")


@router.get("/sync-drive/status")
async def sync_status(session_id: str = Depends(get_session_id)):
    return drive_service.get_sync_state(session_id)


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest, session_id: str = Depends(get_session_id)):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        vs = _app().state.vector_store
        if vs.get_total_vectors(session_id) == 0:
            return AskResponse(answer="No documents indexed yet. Please sync your Google Drive first.", sources=[], query=query)

        answer, results = rag_service.answer_question(session_id, vs, query=query, top_k=request.top_k)
        sources = [
            Source(file_name=r["file_name"], doc_id=r["doc_id"],
                   chunk_text=r["chunk_text"][:500], score=r["score"], page=r.get("page"))
            for r in results
        ]
        return AskResponse(answer=answer, sources=sources, query=query)
    except Exception as e:
        logger.error(f"Ask error for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {str(e)[:200]}")


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents(session_id: str = Depends(get_session_id)):
    docs = drive_service.get_all_documents(session_id)
    return [
        DocumentResponse(id=d["id"], file_name=d["file_name"], status=d["status"],
                         chunk_count=d["chunk_count"] or 0, last_synced=d.get("last_synced"),
                         mime_type=d.get("mime_type"), error_message=d.get("error_message"))
        for d in docs
    ]


@router.get("/documents/stats", response_model=StatsResponse)
async def get_stats(session_id: str = Depends(get_session_id)):
    return StatsResponse(**drive_service.get_stats(session_id))


@router.delete("/documents/{doc_id}", response_model=DeleteResponse)
async def delete_document(doc_id: str, session_id: str = Depends(get_session_id)):
    doc = drive_service.get_document(session_id, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    chunks = _app().state.vector_store.delete_by_doc_id(session_id, doc_id)
    drive_service.delete_document(session_id, doc_id)
    return DeleteResponse(message=f"Document '{doc['file_name']}' deleted.", doc_id=doc_id, chunks_removed=chunks)
