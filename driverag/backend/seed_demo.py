"""
Seed the demo session with sample Google-Drive-style documents.
Run once:  python seed_demo.py
The script populates the FAISS vector index and SQLite metadata DB
so that the app works out-of-the-box without requiring OAuth.
"""

import os, sys, uuid
from datetime import datetime, timezone

# Ensure the backend package is importable
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.core.config import settings
from app.services.drive_service import init_db, upsert_document, update_status
from app.services.embedding_service import EmbeddingService
from app.services import processing_service
from app.db.vector_store import VectorStore

SESSION_ID = "demo"

# ── Sample documents (simulate files that would come from Google Drive) ──────

SAMPLE_DOCS = [
    {
        "id": "gdoc_company_leave_policy",
        "file_name": "Company Leave Policy.docx",
        "mime_type": "application/vnd.google-apps.document",
        "content": """Company Leave Policy — 2025 Edition

1. Annual Leave
All full-time employees are entitled to 24 days of paid annual leave per calendar year. Leave accrues at the rate of 2 days per month from the date of joining. Unused leave can be carried forward up to a maximum of 10 days into the next calendar year. Any leave beyond 10 days will lapse on December 31.

2. Sick Leave
Employees are entitled to 12 days of paid sick leave per year. A medical certificate is required for absences exceeding 3 consecutive working days. Sick leave does not carry forward and resets on January 1 each year.

3. Maternity & Paternity Leave
Female employees are entitled to 26 weeks of paid maternity leave. Male employees are entitled to 2 weeks of paid paternity leave within 6 months of the child's birth or adoption.

4. Casual Leave
Employees may take up to 6 days of casual leave per year for personal reasons. Casual leave cannot be combined with other leave types and must be approved by the reporting manager at least 1 day in advance.

5. Public Holidays
The company observes 12 public holidays per year. The list of holidays is published at the beginning of each year. If an employee is required to work on a public holiday, they will receive compensatory leave.

6. Leave Application Process
All leave requests must be submitted through the HR Portal at least 3 working days in advance (except for emergencies). Managers are expected to approve or reject requests within 24 hours. In case of emergency leave, employees must notify their manager by phone or email before their shift begins.

7. Leave Without Pay (LWP)
If an employee has exhausted their paid leave balance, they may apply for unpaid leave with prior approval from their department head. LWP exceeding 30 days in a year may affect annual appraisals and benefits.
""",
    },
    {
        "id": "gdoc_project_proposal_q3",
        "file_name": "Q3 Project Proposal - AI Chatbot.pdf",
        "mime_type": "application/pdf",
        "content": """Q3 Project Proposal: AI-Powered Customer Support Chatbot

Executive Summary
We propose building an AI-powered chatbot to handle Tier-1 customer support queries, reducing average response time from 4 hours to under 30 seconds and freeing the human support team to focus on complex escalations.

Project Objectives
1. Automate 60% of repetitive support tickets (password resets, order tracking, FAQ queries).
2. Reduce customer wait time by 85% using real-time AI responses.
3. Integrate with existing CRM (Salesforce) and ticketing systems (Zendesk).
4. Achieve a customer satisfaction score (CSAT) of 4.2 or above within 3 months of launch.

Technical Architecture
- LLM Backend: Fine-tuned Llama 3 model hosted on AWS Bedrock.
- RAG Pipeline: Retrieval-augmented generation using company knowledge base (500+ FAQ articles).
- Embedding Model: all-MiniLM-L6-v2 for semantic search across documentation.
- Frontend: React widget embeddable in the company website and mobile app.
- Monitoring: LangSmith for tracing LLM calls, Datadog for infrastructure metrics.

Timeline
Phase 1 (Weeks 1-4): Data collection and knowledge base preparation.
Phase 2 (Weeks 5-8): Model fine-tuning and RAG pipeline development.
Phase 3 (Weeks 9-10): Integration with Salesforce and Zendesk APIs.
Phase 4 (Weeks 11-12): UAT, load testing, and production deployment.

Budget Estimate
- Cloud Infrastructure (AWS): $2,400/month
- LLM API Costs: $800/month (estimated 50,000 queries/month)
- Development Team: 3 engineers × 12 weeks = $108,000
- Total Q3 Budget: $147,200

Risks and Mitigation
1. Hallucination Risk: Implement strict guardrails and confidence thresholds. Responses below 0.7 confidence are escalated to human agents.
2. Data Privacy: All customer data processed in-region (US-East). No PII stored in LLM context windows.
3. Adoption: Gradual rollout starting with internal testing, then beta with 10% of traffic.

Team
- Project Lead: Priya Sharma
- ML Engineers: Arjun Patel, Sneha Reddy
- Backend Developer: Vishnu Kasireddy
- QA: Meera Joshi
""",
    },
    {
        "id": "gdoc_onboarding_guide",
        "file_name": "New Employee Onboarding Guide.docx",
        "mime_type": "application/vnd.google-apps.document",
        "content": """New Employee Onboarding Guide

Welcome to the team! This guide will help you get started on your first week.

Day 1: Orientation
- Report to HR at 9:00 AM for badge and laptop collection.
- Complete mandatory compliance training modules (approximately 2 hours).
- IT will set up your email, Slack workspace, and VPN access.
- Meet your buddy (assigned peer mentor) for a welcome lunch.

Day 2-3: Team Integration
- Attend team standup meetings and introduce yourself.
- Review the team wiki and project documentation on Confluence.
- Set up your development environment following the Dev Setup Guide.
- Complete security awareness training and sign the NDA.

Day 4-5: Getting Productive
- Pick up your first onboarding task from the Jira board (labeled "good-first-issue").
- Schedule 1-on-1 meetings with key stakeholders.
- Review the code review guidelines and contribution workflow.

Tools You'll Need
1. Slack — Team communication (channels: #general, #engineering, #random)
2. Jira — Project management and ticket tracking
3. Confluence — Documentation wiki
4. GitHub — Source code repositories
5. Figma — Design files and prototypes
6. Google Drive — Shared documents and spreadsheets

IT Support
For any technical issues, reach out to #it-helpdesk on Slack or email support@company.com. Standard response time is within 2 hours during business hours.

Key Contacts
- HR Manager: Anita Desai (anita@company.com)
- IT Admin: Ravi Kumar (ravi@company.com)
- Engineering Lead: Vikram Singh (vikram@company.com)

Performance Reviews
Your first performance check-in will be at the 30-day mark, followed by reviews at 90 days and 6 months. Goals and expectations will be set during your first week with your manager.
""",
    },
    {
        "id": "gdoc_meeting_notes_apr",
        "file_name": "Sprint Retrospective Notes - April 2025.docx",
        "mime_type": "application/vnd.google-apps.document",
        "content": """Sprint Retrospective Notes — April 14, 2025

Sprint: Sprint 23 (March 31 - April 11, 2025)
Team: Backend Engineering
Facilitator: Vikram Singh

What Went Well
1. Deployed the new authentication microservice 2 days ahead of schedule.
2. Reduced API response latency by 40% after implementing Redis caching layer.
3. Zero critical bugs reported in production during the sprint.
4. Pair programming sessions significantly improved code quality — PR rejection rate dropped from 18% to 5%.

What Could Be Improved
1. Sprint planning underestimated the complexity of the payment gateway integration — carried over 3 story points.
2. Test coverage for the notification service is still at 62% (target: 80%).
3. Daily standups are running long (15-20 min instead of the target 10 min). Suggestion: use a timer and defer detailed discussions to breakout sessions.
4. Documentation for the new API endpoints was delayed — API docs should be written alongside the code, not after.

Action Items
1. [Arjun] Break down the payment gateway epic into smaller stories for Sprint 24.
2. [Sneha] Add unit tests for notification service — target 80% coverage by end of Sprint 24.
3. [Vikram] Introduce a 10-minute timer for standups starting next sprint.
4. [All] Adopt the "docs-as-code" approach — no PR merged without updated API documentation.

Sprint 24 Goals
- Complete payment gateway integration (Stripe + Razorpay).
- Launch the internal admin dashboard (MVP).
- Migrate legacy user table to the new multi-tenant schema.
- Achieve 80% test coverage across all microservices.

Velocity: 42 story points completed (Sprint 23) vs. 38 (Sprint 22). Trend: Improving.
""",
    },
    {
        "id": "gdoc_expense_reimbursement",
        "file_name": "Expense Reimbursement Policy.pdf",
        "mime_type": "application/pdf",
        "content": """Expense Reimbursement Policy

1. Eligible Expenses
The following expenses are eligible for reimbursement:
- Travel: Economy-class airfare, train tickets, cab/Uber for official travel.
- Accommodation: Hotel stays up to ₹5,000/night for domestic travel, $150/night for international travel.
- Meals: Up to ₹500/meal for domestic travel, $30/meal for international travel. Alcohol is not reimbursable.
- Software & Tools: Pre-approved software subscriptions up to ₹2,000/month.
- Training & Conferences: Registration fees for pre-approved professional development events.
- Internet: ₹1,000/month for remote work internet reimbursement.

2. Submission Process
- All claims must be submitted within 30 days of the expense date.
- Attach original receipts or digital copies (photos/scans accepted).
- Submit claims through the Expense Portal (expenses.company.com).
- Claims above ₹10,000 require department head approval.

3. Approval Workflow
- Claims under ₹5,000: Auto-approved with valid receipts.
- Claims ₹5,000 - ₹25,000: Manager approval required.
- Claims above ₹25,000: Manager + Finance Director approval required.

4. Reimbursement Timeline
Approved claims are processed in the next payroll cycle (15th or last day of the month). Typical processing time is 5-7 business days after approval.

5. Non-Reimbursable Items
- Personal expenses, entertainment, and alcohol.
- First-class or business-class airfare (unless pre-approved for international flights over 8 hours).
- Expenses without valid receipts.
- Late submissions (older than 30 days).

6. Travel Advance
Employees may request a travel advance for trips exceeding 3 days. Submit a Travel Advance Request form at least 7 days before departure. Advances must be settled within 10 days of return.

Contact: For questions, email finance@company.com or reach out on #finance-help on Slack.
""",
    },
]


def main():
    print("=" * 60)
    print("  DriveRAG Demo Seed Script")
    print("=" * 60)

    # Initialise DB and services
    init_db()
    embedding_service = EmbeddingService()
    vector_store = VectorStore(embedding_service)

    now = datetime.now(timezone.utc).isoformat()

    for doc_info in SAMPLE_DOCS:
        doc_id = doc_info["id"]
        file_name = doc_info["file_name"]
        mime_type = doc_info["mime_type"]
        raw_content = doc_info["content"]

        print(f"\n→ Processing: {file_name}")

        # 1. Upsert metadata into SQLite
        upsert_document(SESSION_ID, {
            "id": doc_id,
            "file_name": file_name,
            "mime_type": mime_type,
            "modified_time": now,
        })

        # 2. Chunk the text
        chunks = processing_service.chunk_text(raw_content, doc_id=doc_id, file_name=file_name)
        if not chunks:
            update_status(SESSION_ID, doc_id, "failed", error_message="No chunks created")
            print(f"  ✗ No chunks created")
            continue

        # 3. Index into FAISS
        vector_store.delete_by_doc_id(SESSION_ID, doc_id)
        vector_store.add_documents(SESSION_ID, chunks, doc_id=doc_id)
        update_status(SESSION_ID, doc_id, "indexed", chunk_count=len(chunks))
        print(f"  ✓ Indexed {len(chunks)} chunks")

    # Mark Drive as "connected" by creating a dummy token placeholder
    token_dir = "./data/tokens"
    os.makedirs(token_dir, exist_ok=True)
    token_file = os.path.join(token_dir, f"{SESSION_ID}.json")
    if not os.path.exists(token_file):
        # Create a marker file so the UI shows "Drive Connected"
        import json
        with open(token_file, "w") as f:
            json.dump({"_note": "Demo token — pre-seeded data, no real OAuth"}, f)
        print(f"\n✓ Created demo token marker: {token_file}")

    total_vectors = vector_store.get_total_vectors(SESSION_ID)
    print(f"\n{'=' * 60}")
    print(f"  ✅ Seeding complete!")
    print(f"  Documents: {len(SAMPLE_DOCS)}")
    print(f"  Total vectors: {total_vectors}")
    print(f"  Session ID: {SESSION_ID}")
    print(f"{'=' * 60}")
    print(f"\nStart the server:  python -m uvicorn app.main:app --reload")
    print(f"Everyone will automatically use the 'demo' session.\n")


if __name__ == "__main__":
    main()
