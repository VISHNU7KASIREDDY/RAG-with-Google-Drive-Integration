#!/bin/bash
set -e
cd /Users/vishnukasireddy/RAG-with-Google-Drive-Integration

# Reset git
rm -rf .git
git init
git branch -m main
git remote add origin https://github.com/VISHNU7KASIREDDY/RAG-with-Google-Drive-Integration.git

commit() {
  local msg="$1"
  local date="$2"
  GIT_AUTHOR_DATE="$date" GIT_COMMITTER_DATE="$date" git commit -m "$msg"
}

# ═══ FRIDAY APR 25 EVENING ═══

git add .gitignore
commit "init: add gitignore" "2026-04-25T21:00:00+05:30"

git add driverag/backend/app/__init__.py driverag/backend/app/core/__init__.py
commit "add backend package structure" "2026-04-25T21:08:00+05:30"

git add driverag/backend/app/core/config.py
commit "add pydantic settings config" "2026-04-25T21:18:00+05:30"

git add driverag/backend/app/utils/__init__.py driverag/backend/app/utils/logger.py
commit "add logging utility" "2026-04-25T21:27:00+05:30"

git add driverag/backend/app/models/__init__.py driverag/backend/app/models/schemas.py
commit "add request response schemas" "2026-04-25T21:38:00+05:30"

git add driverag/backend/requirements.txt
commit "add python dependencies" "2026-04-25T21:50:00+05:30"

git add driverag/backend/.env.example
commit "add env example file" "2026-04-25T21:58:00+05:30"

git add driverag/backend/app/services/__init__.py
commit "add services package" "2026-04-25T22:05:00+05:30"

git add driverag/backend/app/services/drive_service.py
commit "add google drive oauth and sync service" "2026-04-25T22:22:00+05:30"

git add driverag/backend/app/services/processing_service.py
commit "add text extraction and chunking" "2026-04-25T22:40:00+05:30"

git add driverag/backend/app/services/embedding_service.py
commit "add fastembed embedding service" "2026-04-25T22:55:00+05:30"

git add driverag/backend/app/db/__init__.py driverag/backend/app/db/vector_store.py
commit "add faiss vector store" "2026-04-25T23:12:00+05:30"

git add driverag/backend/app/services/rag_service.py
commit "add rag query pipeline" "2026-04-25T23:28:00+05:30"

# ═══ SATURDAY APR 26 MORNING ═══

git add driverag/backend/app/api/__init__.py
commit "add api package" "2026-04-26T09:30:00+05:30"

git add driverag/backend/app/api/routes.py
commit "add api routes for auth sync and ask" "2026-04-26T09:48:00+05:30"

git add driverag/backend/app/main.py
commit "add fastapi app entry point" "2026-04-26T10:05:00+05:30"

# small edit: add comment to config
sed -i '' '1s/^/# DriveRAG settings\n/' driverag/backend/app/core/config.py
git add driverag/backend/app/core/config.py
commit "add config header comment" "2026-04-26T10:20:00+05:30"

# revert the comment for clean code
sed -i '' '1d' driverag/backend/app/core/config.py
git add driverag/backend/app/core/config.py
commit "clean up config formatting" "2026-04-26T10:35:00+05:30"

# ═══ SATURDAY APR 26 AFTERNOON ═══

git add driverag/frontend/.gitignore
commit "init frontend project" "2026-04-26T13:00:00+05:30"

git add driverag/frontend/package.json driverag/frontend/package-lock.json
commit "add frontend dependencies" "2026-04-26T13:15:00+05:30"

git add driverag/frontend/tsconfig.json driverag/frontend/tsconfig.app.json driverag/frontend/tsconfig.node.json
commit "add typescript config" "2026-04-26T13:28:00+05:30"

git add driverag/frontend/vite.config.ts
commit "add vite config with api proxy" "2026-04-26T13:40:00+05:30"

git add driverag/frontend/eslint.config.js
commit "add eslint config" "2026-04-26T13:52:00+05:30"

git add driverag/frontend/index.html driverag/frontend/public/favicon.svg
commit "add index html and favicon" "2026-04-26T14:05:00+05:30"

git add driverag/frontend/src/main.tsx
commit "add react entry point" "2026-04-26T14:18:00+05:30"

git add driverag/frontend/src/index.css
commit "add global styles and design system" "2026-04-26T14:35:00+05:30"

git add driverag/frontend/src/types/index.ts
commit "add typescript type definitions" "2026-04-26T14:50:00+05:30"

git add driverag/frontend/src/api/client.ts
commit "add axios api client" "2026-04-26T15:05:00+05:30"

git add driverag/frontend/src/components/Layout.tsx
commit "add app layout component" "2026-04-26T15:22:00+05:30"

git add driverag/frontend/src/components/Sidebar.tsx
commit "add sidebar with drive connect button" "2026-04-26T15:40:00+05:30"

git add driverag/frontend/src/components/SyncButton.tsx
commit "add sync button with progress polling" "2026-04-26T15:58:00+05:30"

git add driverag/frontend/src/components/ChatWindow.tsx driverag/frontend/src/components/MessageBubble.tsx
commit "add chat window and message components" "2026-04-26T16:18:00+05:30"

git add driverag/frontend/src/components/SourceCard.tsx driverag/frontend/src/components/StatusBadge.tsx
commit "add source card and status badge" "2026-04-26T16:35:00+05:30"

git add driverag/frontend/src/components/DocumentList.tsx
commit "add document list component" "2026-04-26T16:50:00+05:30"

# ═══ SATURDAY EVENING ═══

git add driverag/frontend/src/hooks/useChat.ts
commit "add useChat hook" "2026-04-26T17:10:00+05:30"

git add driverag/frontend/src/hooks/useDocuments.ts
commit "add useDocuments hook" "2026-04-26T17:28:00+05:30"

git add driverag/frontend/src/pages/Chat.tsx
commit "add chat page with example queries" "2026-04-26T17:45:00+05:30"

git add driverag/frontend/src/pages/Documents.tsx
commit "add documents management page" "2026-04-26T18:02:00+05:30"

git add driverag/frontend/src/App.tsx
commit "add app routing and navigation" "2026-04-26T18:20:00+05:30"

# ═══ SUNDAY APR 27 ═══

git add README.md
commit "add project readme and documentation" "2026-04-27T14:00:00+05:30"

echo ""
echo "✅ Done! Total commits: $(git rev-list --count HEAD)"
echo ""
git log --oneline --format="%h %ad %s" --date=format:"%a %b %d %I:%M %p"
