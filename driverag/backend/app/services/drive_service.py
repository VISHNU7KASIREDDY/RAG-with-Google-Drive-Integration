import os
import io
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SUPPORTED_MIME_TYPES = [
    "application/pdf",
    "application/vnd.google-apps.document",
    "text/plain",
]
def _get_token_file(session_id: str) -> str:
    return f"./data/tokens/{session_id}.json"

_sync_states: dict[str, dict] = {}

def get_sync_state(session_id: str) -> dict:
    if session_id not in _sync_states:
        _sync_states[session_id] = {"is_syncing": False, "current_file": None, "files_processed": 0, "total_files": 0}
    return _sync_states[session_id]


def _get_oauth_config():
    return {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uris": [settings.google_redirect_uri],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }


def _create_flow() -> Flow:
    flow = Flow.from_client_config(_get_oauth_config(), scopes=SCOPES)
    flow.redirect_uri = settings.google_redirect_uri
    return flow


_pending_verifiers: dict[str, str] = {}


def get_auth_url(session_id: str) -> str:
    flow = _create_flow()
    auth_url, _ = flow.authorization_url(access_type="offline", prompt="consent", state=session_id)
    if hasattr(flow, 'code_verifier') and flow.code_verifier:
        _pending_verifiers[session_id] = flow.code_verifier
    return auth_url


def handle_callback(code: str, state: str) -> dict:
    flow = _create_flow()
    code_verifier = _pending_verifiers.pop(state, None)
    flow.fetch_token(code=code, code_verifier=code_verifier)
    creds = flow.credentials

    token_file = _get_token_file(state)
    os.makedirs(os.path.dirname(os.path.abspath(token_file)), exist_ok=True)
    with open(token_file, "w") as f:
        f.write(creds.to_json())

    return {"message": "Google Drive connected successfully"}


def is_connected(session_id: str) -> bool:
    return os.path.exists(_get_token_file(session_id))


def _get_credentials(session_id: str) -> Credentials:
    token_file = _get_token_file(session_id)
    if not os.path.exists(token_file):
        raise FileNotFoundError("Not authenticated. Visit /api/auth/google first.")

    creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_file, "w") as f:
            f.write(creds.to_json())

    if not creds or not creds.valid:
        raise ValueError("Token expired. Re-authenticate at /api/auth/google")

    return creds


def authenticate(session_id: str):
    creds = _get_credentials(session_id)
    return build("drive", "v3", credentials=creds)


def list_files(service) -> list[dict]:
    query = " or ".join(f"mimeType='{mt}'" for mt in SUPPORTED_MIME_TYPES)
    files, page_token = [], None
    while True:
        resp = service.files().list(
            q=query, spaces="drive",
            fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
            pageToken=page_token, pageSize=100, orderBy="modifiedTime desc",
        ).execute()
        for f in resp.get("files", []):
            files.append({"file_id": f["id"], "file_name": f["name"],
                         "mime_type": f["mimeType"], "modified_time": f["modifiedTime"]})
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    logger.info(f"Found {len(files)} files in Google Drive")
    return files


def download_file(service, file_info: dict) -> Optional[bytes]:
    try:
        fid, mime = file_info["file_id"], file_info["mime_type"]
        if mime == "application/vnd.google-apps.document":
            request = service.files().export_media(fileId=fid, mimeType="text/plain")
        else:
            request = service.files().get_media(fileId=fid)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return buffer.getvalue()
    except Exception as e:
        logger.error(f"Download failed for '{file_info.get('file_name')}': {e}")
        return None


def _get_db():
    os.makedirs(os.path.dirname(os.path.abspath(settings.database_url)), exist_ok=True)
    conn = sqlite3.connect(settings.database_url)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _get_db()
    cursor = conn.execute("PRAGMA table_info(documents)")
    columns = [row[1] for row in cursor.fetchall()]

    if columns and "session_id" not in columns:
        conn.execute("DROP TABLE documents")
        logger.info("Migrated old documents table to multi-tenant schema")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT, session_id TEXT, file_name TEXT NOT NULL, mime_type TEXT,
            status TEXT DEFAULT 'pending', chunk_count INTEGER DEFAULT 0,
            last_synced TIMESTAMP, modified_time TEXT, error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id, session_id)
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Database initialized")


def get_all_documents(session_id: str) -> list[dict]:
    conn = _get_db()
    rows = conn.execute("SELECT * FROM documents WHERE session_id = ? ORDER BY last_synced DESC NULLS LAST", (session_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_document(session_id: str, doc_id: str) -> Optional[dict]:
    conn = _get_db()
    row = conn.execute("SELECT * FROM documents WHERE session_id = ? AND id = ?", (session_id, doc_id)).fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_document(session_id: str, doc: dict):
    conn = _get_db()
    conn.execute("""
        INSERT INTO documents (id, session_id, file_name, mime_type, modified_time, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'pending', ?)
        ON CONFLICT(id, session_id) DO UPDATE SET file_name=excluded.file_name, mime_type=excluded.mime_type, modified_time=excluded.modified_time
    """, (doc["id"], session_id, doc["file_name"], doc.get("mime_type"), doc.get("modified_time"), datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()


def update_status(session_id: str, doc_id: str, status: str, chunk_count: Optional[int] = None, error_message: Optional[str] = None):
    conn = _get_db()
    now = datetime.now(timezone.utc).isoformat()
    if chunk_count is not None:
        conn.execute("UPDATE documents SET status=?, chunk_count=?, last_synced=?, error_message=? WHERE session_id=? AND id=?",
                     (status, chunk_count, now, error_message, session_id, doc_id))
    else:
        conn.execute("UPDATE documents SET status=?, last_synced=?, error_message=? WHERE session_id=? AND id=?",
                     (status, now, error_message, session_id, doc_id))
    conn.commit()
    conn.close()


def delete_document(session_id: str, doc_id: str):
    conn = _get_db()
    conn.execute("DELETE FROM documents WHERE session_id=? AND id=?", (session_id, doc_id))
    conn.commit()
    conn.close()


def document_needs_update(session_id: str, doc_id: str, modified_time: str) -> bool:
    doc = get_document(session_id, doc_id)
    if doc is None or doc["status"] == "failed":
        return True
    return doc["modified_time"] != modified_time


def get_stats(session_id: str) -> dict:
    conn = _get_db()
    row = conn.execute("""
        SELECT COUNT(*) as total_docs, COALESCE(SUM(chunk_count), 0) as total_chunks,
               MAX(last_synced) as last_sync_time FROM documents WHERE session_id=? AND status='indexed'
    """, (session_id,)).fetchone()
    conn.close()
    return dict(row) if row else {"total_docs": 0, "total_chunks": 0, "last_sync_time": None}


def sync(session_id: str, processing_service, vector_store, force_resync: bool = False) -> dict:
    state = get_sync_state(session_id)
    state["is_syncing"] = True
    stats = {"total_files": 0, "new_files": 0, "updated_files": 0, "skipped_files": 0, "failed_files": 0}

    try:
        service = authenticate(session_id)
        files = list_files(service)
        stats["total_files"] = len(files)
        state["total_files"] = len(files)

        for i, f in enumerate(files):
            file_id, file_name = f["file_id"], f["file_name"]
            state["current_file"] = file_name
            state["files_processed"] = i

            try:
                if not force_resync and not document_needs_update(session_id, file_id, f["modified_time"]):
                    stats["skipped_files"] += 1
                    continue

                existing = get_document(session_id, file_id)
                is_update = existing is not None and existing["status"] == "indexed"

                upsert_document(session_id, {"id": file_id, "file_name": file_name,
                                "mime_type": f["mime_type"], "modified_time": f["modified_time"]})
                update_status(session_id, file_id, "processing")

                content = download_file(service, f)
                if not content:
                    update_status(session_id, file_id, "failed", error_message="Download failed")
                    stats["failed_files"] += 1
                    continue

                text = processing_service.extract_text(content, f["mime_type"])
                if not text.strip():
                    update_status(session_id, file_id, "failed", error_message="No text extracted")
                    stats["failed_files"] += 1
                    continue

                docs = processing_service.chunk_text(text, doc_id=file_id, file_name=file_name)
                if not docs:
                    update_status(session_id, file_id, "failed", error_message="No chunks created")
                    stats["failed_files"] += 1
                    continue

                vector_store.delete_by_doc_id(session_id, file_id)
                vector_store.add_documents(session_id, docs, doc_id=file_id)
                update_status(session_id, file_id, "indexed", chunk_count=len(docs))
                stats["updated_files" if is_update else "new_files"] += 1
                logger.info(f"Indexed '{file_name}' ({len(docs)} chunks) for {session_id}")

            except Exception as e:
                logger.error(f"Failed to process '{file_name}' for {session_id}: {e}")
                try:
                    update_status(session_id, file_id, "failed", error_message=str(e)[:500])
                except Exception:
                    pass
                stats["failed_files"] += 1

        state["files_processed"] = len(files)
        logger.info(f"Sync complete for {session_id}: {stats}")
    finally:
        state["is_syncing"] = False
        state["current_file"] = None

    return stats
