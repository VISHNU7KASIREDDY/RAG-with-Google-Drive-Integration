# 🚀 DriveRAG — AI-Powered Document Assistant

> **RAG system** that connects to Google Drive, indexes your documents, and answers questions with source citations.

```
┌─────────────────┐       ┌──────────────────────────────────────────────┐
│  React Frontend │ HTTP  │  FastAPI Backend                             │
│  (Vite + TS)    │──────▶│                                              │
│                 │◀──────│  POST /sync-drive (background thread)        │
│  ┌───────────┐  │       │    drive_service → processing_service        │
│  │ Chat UI   │  │       │    → embedding (auto) → vector_store         │
│  │ Doc Mgmt  │  │       │                                              │
│  └───────────┘  │       │  POST /ask                                   │
│                 │       │    rag_service → vector_store → LLM          │
│                 │       │    → answer + source citations                │
└─────────────────┘       └──────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
driverag/
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI entry + lifespan
│   │   ├── api/routes.py                # Auth, Sync, Ask, Documents
│   │   ├── services/
│   │   │   ├── drive_service.py         # Google Drive OAuth + sync + SQLite
│   │   │   ├── processing_service.py    # Text extraction + chunking
│   │   │   ├── embedding_service.py     # HuggingFace embeddings
│   │   │   └── rag_service.py           # RAG: search → context → LLM
│   │   ├── db/vector_store.py           # FAISS vector store
│   │   ├── models/schemas.py            # Pydantic schemas
│   │   ├── core/config.py               # Settings (env vars)
│   │   └── utils/logger.py              # Logging
│   ├── data/                            # FAISS index + SQLite (gitignored)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── pages/Chat.tsx, Documents.tsx
│   │   ├── components/Sidebar, SyncButton, ChatWindow, etc.
│   │   ├── hooks/useChat, useDocuments
│   │   ├── api/client.ts
│   │   └── types/index.ts
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
```

---

## ⚙️ How It Works

### Sync Pipeline (`POST /api/sync-drive`)
```
Google Drive → Download → Extract text (PyMuPDF) → Chunk → Embed → FAISS
```
Runs in a **background thread** — frontend polls `/api/sync-drive/status` for progress.

### Query Pipeline (`POST /api/ask`)
```
Question → FAISS similarity search → Build context → LLM → Answer + sources
```

---

## 🛠️ Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google Cloud Project with Drive API enabled

### 1. Google Cloud Console

1. Go to [console.cloud.google.com](https://console.cloud.google.com/)
2. Create a project → Enable **Google Drive API**
3. Go to **APIs & Services → OAuth consent screen** → External → add your email as test user
4. Go to **Credentials → Create OAuth Client ID → Web Application**
5. Add `http://localhost:8000/api/auth/callback` as **Authorized redirect URI**
6. Copy the **Client ID** and **Client Secret**

### 2. Get an LLM API Key

| Provider | Where | Model |
|---|---|---|
| **Groq** (recommended, free) | [console.groq.com/keys](https://console.groq.com/keys) | Llama 3.3 70B |
| Gemini | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | Gemini 2.0 Flash |
| OpenAI | [platform.openai.com](https://platform.openai.com/) | GPT-3.5 Turbo |

### 3. Backend

```bash
cd driverag/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Fill in your keys
```

### 4. Frontend

```bash
cd driverag/frontend
npm install
```

### 5. Run

```bash
# Terminal 1 — Backend
cd driverag/backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd driverag/frontend
npm run dev
```

Open **http://localhost:5173** → Click **Connect Google Drive** → Authorize → **Sync Drive** → Ask questions!

---

## 🔑 Environment Variables

| Variable | Required | Default |
|---|---|---|
| `GOOGLE_CLIENT_ID` | ✅ | — |
| `GOOGLE_CLIENT_SECRET` | ✅ | — |
| `LLM_PROVIDER` | No | `groq` |
| `GROQ_API_KEY` | ✅ (if groq) | — |
| `GEMINI_API_KEY` | Only if gemini | — |
| `OPENAI_API_KEY` | Only if openai | — |
| `GOOGLE_REDIRECT_URI` | No | `http://localhost:8000/api/auth/callback` |
| `EMBEDDING_MODEL` | No | `all-MiniLM-L6-v2` |
| `MAX_CHUNK_SIZE` | No | `500` |
| `CHUNK_OVERLAP` | No | `50` |
| `TOP_K_RESULTS` | No | `5` |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/auth/google` | Start Google OAuth flow |
| `GET` | `/api/auth/callback` | OAuth callback (auto) |
| `GET` | `/api/auth/status` | Check if Drive is connected |
| `POST` | `/api/sync-drive` | Start background sync |
| `GET` | `/api/sync-drive/status` | Sync progress |
| `POST` | `/api/ask` | Ask a question |
| `GET` | `/api/documents` | List indexed documents |
| `GET` | `/api/documents/stats` | Index statistics |
| `DELETE` | `/api/documents/{id}` | Remove a document |
| `GET` | `/health` | Health check |

---

## 🐳 Docker

```bash
docker-compose up --build
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript + Vite |
| Backend | FastAPI + Python |
| Vector DB | FAISS (local) |
| Embeddings | all-MiniLM-L6-v2 (HuggingFace) |
| LLM | Groq / Gemini / OpenAI |
| Doc Processing | PyMuPDF |
| Database | SQLite |

---

## 📜 License

MIT License