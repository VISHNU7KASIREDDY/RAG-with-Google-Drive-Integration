"""
Seed the app with sample documents for local testing.
Run once:  python seed_demo.py
"""

import os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings
from app.services.drive_service import init_db, upsert_document, update_status
from app.services.embedding_service import EmbeddingService
from app.services import processing_service
from app.db.vector_store import VectorStore

SAMPLE_DOCS = [
    {
        "id": "gdoc_company_leave_policy",
        "file_name": "Company Leave Policy.docx",
        "mime_type": "application/vnd.google-apps.document",
        "content": """Company Leave Policy — 2025 Edition

1. Annual Leave
All full-time employees are entitled to 24 days of paid annual leave per calendar year. Leave accrues at the rate of 2 days per month from the date of joining. Unused leave can be carried forward up to a maximum of 10 days into the next calendar year.

2. Sick Leave
Employees are entitled to 12 days of paid sick leave per year. A medical certificate is required for absences exceeding 3 consecutive working days.

3. Maternity & Paternity Leave
Female employees are entitled to 26 weeks of paid maternity leave. Male employees are entitled to 2 weeks of paid paternity leave.

4. Casual Leave
Employees may take up to 6 days of casual leave per year for personal reasons.

5. Leave Application Process
All leave requests must be submitted through the HR Portal at least 3 working days in advance. Managers are expected to approve or reject requests within 24 hours.
""",
    },
    {
        "id": "gdoc_project_proposal_q3",
        "file_name": "Q3 Project Proposal - AI Chatbot.pdf",
        "mime_type": "application/pdf",
        "content": """Q3 Project Proposal: AI-Powered Customer Support Chatbot

Executive Summary
We propose building an AI-powered chatbot to handle Tier-1 customer support queries, reducing average response time from 4 hours to under 30 seconds.

Budget Estimate
- Cloud Infrastructure (AWS): $2,400/month
- LLM API Costs: $800/month
- Development Team: 3 engineers × 12 weeks = $108,000
- Total Q3 Budget: $147,200

Team
- Project Lead: Priya Sharma
- ML Engineers: Arjun Patel, Sneha Reddy
- Backend Developer: Vishnu Kasireddy
""",
    },
]


def main():
    print("Seeding sample documents...")
    init_db()
    embedding_service = EmbeddingService()
    vector_store = VectorStore(embedding_service)
    now = datetime.now(timezone.utc).isoformat()

    for doc_info in SAMPLE_DOCS:
        doc_id = doc_info["id"]
        upsert_document({"id": doc_id, "file_name": doc_info["file_name"],
                         "mime_type": doc_info["mime_type"], "modified_time": now})
        chunks = processing_service.chunk_text(doc_info["content"], doc_id=doc_id, file_name=doc_info["file_name"])
        vector_store.delete_by_doc_id(doc_id)
        vector_store.add_documents(chunks, doc_id=doc_id)
        update_status(doc_id, "indexed", chunk_count=len(chunks))
        print(f"  ✓ {doc_info['file_name']} ({len(chunks)} chunks)")

    print(f"\n✅ Done! {vector_store.get_total_vectors()} vectors indexed.")


if __name__ == "__main__":
    main()
