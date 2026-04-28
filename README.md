# DriveRAG — AI-Powered Document Assistant

A full-stack Retrieval-Augmented Generation (RAG) application that connects to your Google Drive, indexes your documents, and lets you ask natural language questions with source citations.

**Demo Mode**: The app ships with 5 pre-indexed sample documents and works out-of-the-box — no Google account or API keys needed to try it. Connect your own Drive for real documents.

---

## Architecture

```
┌──────────────────┐        ┌───────────────────────────────────────────────┐
│  React Frontend  │  HTTP  │  FastAPI Backend                              │
│  (Vite + TS)     │───────>│                                               │
│                  │<───────│  GET  /api/auth/google    → OAuth redirect    │
│  ┌────────────┐  │        │  GET  /api/auth/callback  → Save credentials  │
│  │ Chat UI    │  │        │  POST /api/sync-drive     → Background sync   │
│  │ Doc Mgmt   │  │        │  POST /api/ask            → RAG pipeline      │
│  └────────────┘  │        │                                               │
└──────────────────┘        └───────────────────────────────────────────────┘
```

### Sync Pipeline (Incremental)

```
Google Drive → List files → Compare modified_time → Download ONLY new/changed files → Extract text → Chunk → Embed → FAISS
```

Runs in a background thread. The frontend polls `/api/sync-drive/status` for real-time progress.
Files whose `modified_time` hasn't changed since the last sync are automatically skipped.

### Query Pipeline

```
User question → FAISS similarity search → Build context from top-K chunks → LLM → Answer + sources
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript, Vite 8, Tailwind CSS 4 |
| Backend | FastAPI, Python 3.10+ |
| Vector Store | FAISS (one index per user session) |
| Embeddings | all-MiniLM-L6-v2 via FastEmbed |
| LLM | Groq (default) / Google Gemini / OpenAI |
| Document Processing | PyMuPDF |
| Metadata Database | SQLite |
| Auth | Google OAuth 2.0 with PKCE |

---

## Project Structure

```
driverag/
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI entry point and lifespan
│   │   ├── api/routes.py                # All API route handlers
│   │   ├── services/
│   │   │   ├── drive_service.py         # Google Drive OAuth, sync, SQLite
│   │   │   ├── processing_service.py    # Text extraction and chunking
│   │   │   ├── embedding_service.py     # FastEmbed wrapper
│   │   │   └── rag_service.py           # Context building and LLM calls
│   │   ├── db/vector_store.py           # Per-session FAISS index management
│   │   ├── models/schemas.py            # Pydantic request/response models
│   │   ├── core/config.py               # Environment variable settings
│   │   └── utils/logger.py              # Structured logging
│   ├── data/                            # Pre-seeded demo data (committed)
│   │   ├── tokens/demo.json             # Demo session marker
│   │   ├── faiss_index_demo/            # Pre-built vector index (25 vectors)
│   │   └── driverag.db                  # SQLite with 5 sample documents
│   ├── seed_demo.py                     # Script to re-seed demo data
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── pages/                       # Chat.tsx, Documents.tsx
│   │   ├── components/                  # Sidebar, ChatWindow, SyncButton, etc.
│   │   ├── hooks/                       # useChat, useDocuments
│   │   ├── api/client.ts                # Axios client with session headers
│   │   └── types/index.ts              
│   ├── index.html
│   ├── vite.config.ts
│   ├── package.json
│   └── .env.example
```

---

## Prerequisites

Before starting, make sure you have the following installed:

- **Python 3.10 or later** — [Download](https://www.python.org/downloads/)
- **Node.js 18 or later** — [Download](https://nodejs.org/)
- **Git** — [Download](https://git-scm.com/)
- **A Google account** with access to Google Drive
- **An LLM API key** from one of: Groq (free), Google Gemini, or OpenAI

---

## Step 1: Set Up Google Cloud OAuth

This is the most important step. The app uses OAuth 2.0 to access Google Drive on behalf of each user.

### 1.1 Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top → **New Project**
3. Give it a name (e.g., `DriveRAG`) and click **Create**
4. Make sure your new project is selected in the dropdown

### 1.2 Enable the Google Drive API

1. In the left sidebar, go to **APIs & Services → Library**
2. Search for **Google Drive API**
3. Click on it → Click **Enable**

### 1.3 Configure the OAuth Consent Screen

1. Go to **APIs & Services → OAuth consent screen**
2. Select **External** as the user type → Click **Create**
3. Fill in the required fields:
   - **App name**: `DriveRAG`
   - **User support email**: Your email
   - **Developer contact email**: Your email
4. Click **Save and Continue**
5. On the **Scopes** page, click **Add or Remove Scopes**
   - Search for `https://www.googleapis.com/auth/drive.readonly`
   - Check it and click **Update** → **Save and Continue**
6. On the **Test users** page:
   - Click **Add Users**
   - Add the Gmail addresses of anyone who will use the app
   - Click **Save and Continue**

> **Note**: While in "Testing" mode, only listed test users can connect. To allow anyone, click **Publish App** on the consent screen page. Users will see a "This app isn't verified" warning but can proceed by clicking Advanced → Go to DriveRAG.

### 1.4 Create OAuth Credentials

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth client ID**
3. Select **Web application** as the application type
4. Under **Authorized redirect URIs**, add:
   - For local development: `http://localhost:8000/api/auth/callback`
   - For production: `https://your-backend-url.onrender.com/api/auth/callback`
5. Click **Create**
6. Copy the **Client ID** and **Client Secret** — you will need these next

---

## Step 2: Get an LLM API Key

You need an API key from at least one LLM provider. Groq is recommended because it is free.

| Provider | Sign Up | Free Tier | Model Used |
|---|---|---|---|
| **Groq** (recommended) | [console.groq.com/keys](https://console.groq.com/keys) | Yes, generous | Llama 3.3 70B |
| Google Gemini | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | Yes | Gemini 2.0 Flash |
| OpenAI | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | No (paid) | GPT-3.5 Turbo |

Copy your API key — you will need it in the next step.

---

## Step 3: Clone the Repository

```bash
git clone https://github.com/VISHNU7KASIREDDY/RAG-with-Google-Drive-Integration.git
cd RAG-with-Google-Drive-Integration
```

---

## Step 4: Set Up the Backend

### 4.1 Create a Virtual Environment

```bash
cd driverag/backend
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate          # Windows
```

### 4.2 Install Dependencies

```bash
pip install -r requirements.txt
```

> This will install FastAPI, FAISS, PyMuPDF, FastEmbed, LangChain, and all other dependencies. The first run will also download the embedding model (~90 MB).

### 4.3 Create the Environment File

```bash
cp .env.example .env
```

Open `.env` in your editor and fill in your values:

```env
GOOGLE_CLIENT_ID=your-client-id-from-step-1.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-from-step-1
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/callback
FRONTEND_URL=http://localhost:5173

LLM_PROVIDER=groq
GROQ_API_KEY=your-groq-api-key

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
FAISS_STORE_PATH=./data/faiss_index
DATABASE_URL=./data/driverag.db
MAX_CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5
```

**Explanation of each variable:**

| Variable | What It Does |
|---|---|
| `GOOGLE_CLIENT_ID` | From Google Cloud Console (Step 1.4) |
| `GOOGLE_CLIENT_SECRET` | From Google Cloud Console (Step 1.4) |
| `GOOGLE_REDIRECT_URI` | Must exactly match what you entered in Google Console |
| `FRONTEND_URL` | Where the frontend is hosted (used for post-auth redirects) |
| `LLM_PROVIDER` | Which LLM to use: `groq`, `gemini`, or `openai` |
| `GROQ_API_KEY` | Your Groq API key (only needed if `LLM_PROVIDER=groq`) |
| `GEMINI_API_KEY` | Your Gemini API key (only needed if `LLM_PROVIDER=gemini`) |
| `OPENAI_API_KEY` | Your OpenAI API key (only needed if `LLM_PROVIDER=openai`) |
| `EMBEDDING_MODEL` | HuggingFace model for text embeddings |
| `FAISS_STORE_PATH` | Where FAISS indices are saved on disk |
| `DATABASE_URL` | Path to the SQLite database file |
| `MAX_CHUNK_SIZE` | Maximum number of characters per text chunk |
| `CHUNK_OVERLAP` | Number of overlapping characters between chunks |
| `TOP_K_RESULTS` | Number of similar chunks to retrieve per query |

### 4.4 Start the Backend Server

```bash
uvicorn app.main:app --reload --port 8000
```

You should see output like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Starting DriveRAG API
INFO:     Database initialized
INFO:     Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
INFO:     Embedding model loaded
INFO:     Application startup complete.
```

Verify it works by opening http://localhost:8000/health in your browser.

---

## Step 5: Set Up the Frontend

Open a **new terminal** (keep the backend running in the first one):

### 5.1 Install Dependencies

```bash
cd driverag/frontend
npm install
```

### 5.2 Start the Development Server

```bash
npm run dev
```

You should see:

```
VITE v8.x.x  ready in xxx ms
  ➜  Local:   http://localhost:5173/
```

> The Vite dev server automatically proxies `/api` requests to `http://localhost:8000`, so no additional configuration is needed for local development.

---

## Step 6: Use the App

1. Open **http://localhost:5173** in your browser
2. Click **Connect Google Drive** in the sidebar
3. Sign in with your Google account and authorize access
4. After being redirected back, click **Sync Drive**
5. Wait for the sync to complete (progress is shown in real time)
6. Go to the **Chat** page and ask questions about your documents

---

## Production Deployment

### Backend: Deploy on Render

1. Go to [Render](https://render.com/) → **New Web Service**
2. Connect your GitHub repository
3. Configure the service:
   - **Root Directory**: `driverag/backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add **Environment Variables** (same as your `.env` file, but with production URLs):

   ```
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   GOOGLE_REDIRECT_URI=https://your-backend.onrender.com/api/auth/callback
   FRONTEND_URL=https://your-frontend.vercel.app
   LLM_PROVIDER=groq
   GROQ_API_KEY=your-groq-key
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   ONNX_NUM_THREADS=1
   ```

   > `ONNX_NUM_THREADS=1` prevents memory spikes on Render's free tier (512 MB RAM).

5. Under **Disk**, add a persistent disk:
   - **Mount Path**: `/opt/render/project/src/data`
   - This preserves FAISS indices and the SQLite database between redeploys

6. Click **Deploy**

### Frontend: Deploy on Vercel

1. Go to [Vercel](https://vercel.com/) → **Add New Project**
2. Import your GitHub repository
3. Configure:
   - **Root Directory**: `driverag/frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add the **Environment Variable**:

   ```
   VITE_API_URL=https://your-backend.onrender.com
   ```

   > Do NOT include `/api` at the end. The frontend code appends `/api` automatically.

5. Click **Deploy**

### Update Google Cloud Console

After both services are deployed, go back to Google Cloud Console:

1. Go to **APIs & Services → Credentials** → Edit your OAuth client
2. Add your production redirect URI under **Authorized redirect URIs**:
   ```
   https://your-backend.onrender.com/api/auth/callback
   ```
3. Click **Save**

---

## API Reference

All endpoints are prefixed with `/api`. Protected endpoints require the `X-Session-ID` header (sent automatically by the frontend).

### Authentication

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/auth/google?session_id=<id>` | Initiates Google OAuth flow | No |
| `GET` | `/api/auth/callback?code=<code>&state=<session_id>` | OAuth callback (handled automatically) | No |
| `GET` | `/api/auth/status` | Returns `{ connected: true/false }` | X-Session-ID |

### Documents

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/sync-drive` | Start background Drive sync | X-Session-ID |
| `GET` | `/api/sync-drive/status` | Poll sync progress | X-Session-ID |
| `GET` | `/api/documents` | List all indexed documents | X-Session-ID |
| `GET` | `/api/documents/stats` | Get index statistics | X-Session-ID |
| `DELETE` | `/api/documents/{doc_id}` | Delete a document and its vectors | X-Session-ID |

### RAG

| Method | Endpoint | Body | Auth |
|---|---|---|---|
| `POST` | `/api/ask` | `{ "query": "...", "top_k": 5 }` | X-Session-ID |

**Response:**
```json
{
  "answer": "Based on your documents...",
  "sources": [
    {
      "file_name": "report.pdf",
      "doc_id": "abc123",
      "chunk_text": "relevant passage...",
      "score": 0.85,
      "page": 3
    }
  ],
  "query": "original question"
}
```

### Health

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service info |
| `GET` | `/health` | Health check with provider details |

---

## Sample Queries and Outputs

The app ships with 5 pre-indexed sample documents. Here are example queries and their actual outputs:

### Query 1: Leave Policy

**Request:**
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: demo" \
  -d '{"query": "How many annual leave days do employees get?", "top_k": 3}'
```

**Response:**
```json
{
  "answer": "All full-time employees are entitled to **24 days** of paid annual leave per calendar year. Leave accrues at the rate of 2 days per month from the date of joining. Unused leave can be carried forward up to a maximum of 10 days into the next calendar year. (Source: Company Leave Policy.docx)",
  "sources": [
    {
      "file_name": "Company Leave Policy.docx",
      "doc_id": "gdoc_company_leave_policy",
      "chunk_text": "Company Leave Policy — 2025 Edition\n\n1. Annual Leave\nAll full-time employees are entitled to 24 days of paid annual leave per calendar year...",
      "score": 0.5707
    }
  ],
  "query": "How many annual leave days do employees get?"
}
```

---

### Query 2: Project Budget

**Request:**
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: demo" \
  -d '{"query": "What is the budget for the AI chatbot project?", "top_k": 3}'
```

**Response:**
```json
{
  "answer": "The total budget for the Q3 AI chatbot project is **$147,200**, broken down as:\n- Cloud Infrastructure (AWS): $2,400/month\n- LLM API Costs: $800/month\n- Development Team: 3 engineers × 12 weeks = $108,000\n(Source: Q3 Project Proposal - AI Chatbot.pdf)",
  "sources": [
    {
      "file_name": "Q3 Project Proposal - AI Chatbot.pdf",
      "doc_id": "gdoc_project_proposal_q3",
      "chunk_text": "Timeline\nPhase 1 (Weeks 1-4): Data collection...\n\nBudget Estimate\n- Cloud Infrastructure (AWS): $2,400/month...",
      "score": 0.4709
    }
  ],
  "query": "What is the budget for the AI chatbot project?"
}
```

---

### Query 3: Expense Reimbursement

**Request:**
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: demo" \
  -d '{"query": "What is the reimbursement limit for hotel stays?", "top_k": 3}'
```

**Response:**
```json
{
  "answer": "Hotel reimbursement limits are:\n- **Domestic travel**: Up to ₹5,000 per night\n- **International travel**: Up to $150 per night\n(Source: Expense Reimbursement Policy.pdf)",
  "sources": [
    {
      "file_name": "Expense Reimbursement Policy.pdf",
      "doc_id": "gdoc_expense_reimbursement",
      "chunk_text": "Expense Reimbursement Policy\n\n1. Eligible Expenses\n...Accommodation: Hotel stays up to ₹5,000/night for domestic travel, $150/night for international travel...",
      "score": 0.5124
    }
  ],
  "query": "What is the reimbursement limit for hotel stays?"
}
```

---

### Query 4: Sprint Retrospective

**Request:**
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: demo" \
  -d '{"query": "What were the action items from the sprint retrospective?", "top_k": 3}'
```

**Response:**
```json
{
  "answer": "Action items from the Sprint 23 retrospective (April 14, 2025):\n1. **Arjun**: Break down the payment gateway epic into smaller stories for Sprint 24\n2. **Sneha**: Add unit tests for notification service — target 80% coverage\n3. **Vikram**: Introduce a 10-minute timer for standups\n4. **All**: Adopt docs-as-code — no PR merged without updated API documentation\n(Source: Sprint Retrospective Notes - April 2025.docx)",
  "sources": [
    {
      "file_name": "Sprint Retrospective Notes - April 2025.docx",
      "doc_id": "gdoc_meeting_notes_apr",
      "chunk_text": "Action Items\n1. [Arjun] Break down the payment gateway epic...",
      "score": 0.5341
    }
  ],
  "query": "What were the action items from the sprint retrospective?"
}
```

---

### Query 5: Onboarding

**Request:**
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: demo" \
  -d '{"query": "What tools do new employees need?", "top_k": 3}'
```

**Response:**
```json
{
  "answer": "New employees need the following tools:\n1. **Slack** — Team communication\n2. **Jira** — Project management and ticket tracking\n3. **Confluence** — Documentation wiki\n4. **GitHub** — Source code repositories\n5. **Figma** — Design files and prototypes\n6. **Google Drive** — Shared documents and spreadsheets\n(Source: New Employee Onboarding Guide.docx)",
  "sources": [
    {
      "file_name": "New Employee Onboarding Guide.docx",
      "doc_id": "gdoc_onboarding_guide",
      "chunk_text": "Tools You'll Need\n1. Slack — Team communication...\n6. Google Drive — Shared documents and spreadsheets",
      "score": 0.4821
    }
  ],
  "query": "What tools do new employees need?"
}
```

### Pre-seeded Sample Documents

| # | Document | Type | Chunks |
|---|---|---|---|
| 1 | Company Leave Policy.docx | Google Doc | 5 |
| 2 | Q3 Project Proposal - AI Chatbot.pdf | PDF | 5 |
| 3 | New Employee Onboarding Guide.docx | Google Doc | 5 |
| 4 | Sprint Retrospective Notes - April 2025.docx | Google Doc | 4 |
| 5 | Expense Reimbursement Policy.pdf | PDF | 6 |
| | **Total** | | **25 chunks** |

---

## Key Features

| Feature | Status | Details |
|---|---|---|
| Google Drive OAuth 2.0 | ✅ | PKCE flow, per-session tokens |
| PDF processing | ✅ | PyMuPDF extraction |
| Google Docs processing | ✅ | Exported as plain text via Drive API |
| Plain text processing | ✅ | Direct download |
| Smart chunking | ✅ | RecursiveCharacterTextSplitter (500 chars, 50 overlap) |
| Incremental sync | ✅ | Compares `modified_time`, only re-processes changed files |
| RAG with source citations | ✅ | Top-K similarity search + LLM-generated answers |
| Multi-LLM support | ✅ | Groq / Gemini / OpenAI switchable via env var |
| Chat history persistence | ✅ | Survives page refresh (localStorage) |
| Demo mode | ✅ | 5 pre-indexed docs, works without Google account |
| Background async sync | ✅ | Non-blocking sync with real-time progress |
| Clean API design | ✅ | RESTful endpoints with Pydantic validation |

---

## Environment Variables Reference

### Backend (`driverag/backend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `GOOGLE_CLIENT_ID` | Yes | — | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Yes | — | Google OAuth client secret |
| `GOOGLE_REDIRECT_URI` | No | `http://localhost:8000/api/auth/callback` | OAuth callback URL |
| `FRONTEND_URL` | No | `http://localhost:5173` | Frontend URL for post-auth redirects |
| `LLM_PROVIDER` | No | `groq` | LLM provider: `groq`, `gemini`, or `openai` |
| `GROQ_API_KEY` | If groq | — | Groq API key |
| `GEMINI_API_KEY` | If gemini | — | Google Gemini API key |
| `OPENAI_API_KEY` | If openai | — | OpenAI API key |
| `EMBEDDING_MODEL` | No | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model name |
| `EMBEDDING_DIMENSION` | No | `384` | Embedding vector dimension |
| `FAISS_STORE_PATH` | No | `./data/faiss_index` | Base path for FAISS indices |
| `DATABASE_URL` | No | `./data/driverag.db` | SQLite database path |
| `MAX_CHUNK_SIZE` | No | `500` | Max characters per text chunk |
| `CHUNK_OVERLAP` | No | `50` | Overlap between chunks |
| `TOP_K_RESULTS` | No | `5` | Number of chunks per query |

### Frontend (`driverag/frontend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `VITE_API_URL` | Only in production | `""` (empty) | Backend base URL without `/api` |

> `VITE_` environment variables are embedded at build time. Changing them requires a rebuild.

---

## Troubleshooting

### "Connect Google Drive" button is missing

The auth status API call is failing silently. Open browser DevTools (F12) → Console tab and look for red errors. Common causes:

- **Backend is not running** or still deploying
- **CORS error**: Make sure the backend allows requests from your frontend origin
- **Double `/api`**: If you see `/api/api/...` in the network tab, your `VITE_API_URL` includes `/api` — remove it

### `redirect_uri_mismatch`

The redirect URI in your `.env` does not match what is listed in Google Cloud Console. They must be exactly identical, including the protocol (`http` vs `https`) and trailing slashes.

### `access_denied` / "The developer hasn't given you access"

Your OAuth consent screen is in Testing mode. Either:
- Add the user's email to **Test users** in Google Cloud Console
- Or click **Publish App** to allow everyone

### `(invalid_grant) Missing code verifier`

This was a PKCE issue that has been fixed. Make sure you are running the latest code.

### Out of Memory on Render Free Tier

Add this environment variable on Render:
```
ONNX_NUM_THREADS=1
```
This limits the embedding model to 1 thread, reducing memory usage from ~800 MB to ~300 MB.

### Sync completes but no documents appear

- Check that your Google Drive contains supported file types: **PDF**, **Google Docs**, or **plain text files**
- Spreadsheets, slides, images, and videos are not supported

---

## Supported File Types

| File Type | MIME Type | How It Is Processed |
|---|---|---|
| PDF | `application/pdf` | Downloaded and parsed with PyMuPDF |
| Google Docs | `application/vnd.google-apps.document` | Exported as plain text via Drive API |
| Plain Text | `text/plain` | Downloaded directly |

---

## License

MIT License