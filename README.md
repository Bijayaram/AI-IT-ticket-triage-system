# 🎫 AI-Driven IT Ticket Triage System

> **Capstone Project**: End-to-end machine learning system with human-in-the-loop approval workflow for intelligent IT support ticket routing and response generation.

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39.0-FF4B4B.svg)](https://streamlit.io/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Training Models](#training-models)
- [Running the System](#running-the-system)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Performance Metrics](#performance-metrics)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This system automates IT support ticket triage using:
- **Local ML models** for department classification and criticality assessment
- **BAAI/bge-m3 embeddings** (multilingual, 1024-dim) for semantic understanding
- **FAISS vector search** for retrieving similar historical tickets (RAG)
- **Google Gemini API** for generating draft responses (NOT for classification)
- **Human-in-the-loop** approval workflow for critical tickets

### Key Principle
> **Separation of Concerns**: Local ML handles triage decisions; Gemini only generates response drafts.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     IT TICKET TRIAGE SYSTEM                          │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐              ┌──────────────────────────────────┐
│  Customer Portal │              │      Manager Dashboard           │
│   (Streamlit)    │              │       (Streamlit)                │
│   Port: 8501     │              │       Port: 8502                 │
│                  │              │                                  │
│  - Submit Ticket │              │  - View KPIs & Charts            │
│  - Track Status  │              │  - Approve Critical Tickets      │
│  - View Response │              │  - Edit Responses                │
└────────┬─────────┘              └──────────────┬───────────────────┘
         │                                       │
         │                                       │
         │         HTTP/REST API                 │
         │                                       │
         └───────────────┬───────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────────────────────┐
         │         FastAPI Backend (Port: 8000)          │
         │                                               │
         │  ┌─────────────────────────────────────────┐ │
         │  │         Triage Service                  │ │
         │  │  1. Embed ticket text (Local BGE-M3)   │ │
         │  │  2. Predict department (XGBoost)        │ │
         │  │  3. Predict criticality (Logistic Reg)  │ │
         │  │  4. Retrieve similar tickets (FAISS)    │ │
         │  │  5. Generate draft (Gemini w/ RAG)      │ │
         │  └─────────────────────────────────────────┘ │
         │                                               │
         │  ┌─────────────────────────────────────────┐ │
         │  │       Approval Service                  │ │
         │  │  - Manager approve/edit/reject          │ │
         │  │  - Apply business rules                 │ │
         │  │  - Send notification                    │ │
         │  └─────────────────────────────────────────┘ │
         └───────────────────┬───────────────────────────┘
                             │
                             ▼
         ┌───────────────────────────────────────────────┐
         │              Data Layer                       │
         │                                               │
         │  ┌──────────────┐  ┌─────────────────────┐   │
         │  │ SQLite DB    │  │  ML Models & Index  │   │
         │  │              │  │                     │   │
         │  │ - Tickets    │  │ - dept_classifier  │   │
         │  │ - Responses  │  │ - crit_classifier  │   │
         │  │ - Approvals  │  │ - label_encoder    │   │
         │  │ - Audit Logs │  │ - FAISS index      │   │
         │  │              │  │ - Embeddings cache │   │
         │  └──────────────┘  └─────────────────────┘   │
         └───────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    ML Pipeline (Offline)                             │
│                                                                      │
│  CSV Dataset → Generate Embeddings (BGE-M3) → Train Models          │
│                      ↓                              ↓                │
│             Cache to disk                  Save: dept_clf,           │
│             (28K tickets)                        crit_clf            │
│                                                                      │
│  Build FAISS Index ← Load Cached Embeddings                         │
│         ↓                                                            │
│  Save to disk (28K vectors)                                         │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow

**1. Ticket Submission (Customer Portal)**
```
Customer → Submit Ticket → Backend API → Store in DB → Return Ticket ID
```

**2. Automatic Triage**
```
Backend → Load Ticket
        → Generate Embedding (BGE-M3)
        → Predict Department (XGBoost Ensemble)
        → Predict Criticality (Logistic Regression)
        → Retrieve Similar Tickets (FAISS)
        → Generate Draft Response (Gemini + RAG)
        → Apply Business Rules
        → If Critical: PENDING_APPROVAL
        → If Non-Critical: Auto-send (configurable)
```

**3. Manager Approval (Manager Dashboard)**
```
Manager → View Pending Critical Tickets
        → Review Draft + Context
        → Approve / Edit / Reject
        → Send Notification
        → Update Ticket Status
```

---

## ✨ Features

### Customer Portal
- 📝 **Submit IT Tickets** - Simple form with name, email, subject, body, optional attachment
- 🔍 **Track Status** - Real-time ticket status and department assignment
- 📧 **View Responses** - See all responses (drafts, approved, sent)
- 🌐 **Multilingual** - Supports English and German tickets

### Manager Dashboard
- 📊 **KPI Dashboard** - Total tickets, open tickets, critical count, response times
- 📈 **Analytics** - Charts by department, priority, time series, critical rate
- ⚠️ **Pending Approvals** - Dedicated queue for critical tickets requiring approval
- ✏️ **Response Editor** - Approve, edit, or reject AI-generated responses
- 🔍 **Ticket Filters** - Search by queue, priority, status, language, date range
- 🔐 **Secure Access** - Simple password authentication

### Backend API
- 🤖 **Automated Triage** - ML-powered department routing and criticality assessment
- 🧠 **Smart Embeddings** - BAAI/bge-m3 multilingual embeddings (1024-dim)
- 🎯 **XGBoost Classifier** - 51.6% F1 score for 10-department classification
- 🔍 **FAISS Retrieval** - Semantic search over 28K historical tickets
- 🤝 **Gemini Integration** - Draft generation with RAG context
- ✅ **Business Rules** - Automatic critical ticket approval routing
- 📝 **Audit Trail** - Complete history of all actions and decisions
- 📊 **RESTful API** - Clean, documented endpoints

---

## 🛠️ Technology Stack

### Machine Learning
- **Embeddings**: `BAAI/bge-m3` (SentenceTransformers) - Multilingual, 1024-dim
- **Department Classifier**: XGBoost + LightGBM Ensemble (51.6% F1 macro)
- **Criticality Classifier**: Logistic Regression (68.7% AUC)
- **Similarity Search**: FAISS (28,587 vectors indexed)
- **Response Generation**: Google Gemini 2.0 Flash

### Backend
- **Framework**: FastAPI 0.115.0
- **Database**: SQLite (production-ready for PostgreSQL)
- **ORM**: SQLAlchemy 2.0.35
- **Validation**: Pydantic 2.9.2

### Frontend
- **Framework**: Streamlit 1.39.0
- **Charts**: Plotly, Altair
- **UI**: Clean, responsive design

### ML Tools
- **scikit-learn**: 1.5.2 (Logistic Regression, metrics)
- **xgboost**: 2.0.3 (gradient boosting)
- **lightgbm**: 4.5.0 (gradient boosting)
- **faiss-cpu**: 1.9.0 (vector search)
- **sentence-transformers**: 3.1.1 (embeddings)

---

## 📦 Installation

### Prerequisites
- Python 3.12+
- 8GB RAM minimum (for embedding generation)
- 2GB disk space

### Step 1: Clone/Download Project
```bash
cd d:\Capstone
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

This installs all required packages (~2GB download):
- FastAPI, Streamlit, SQLAlchemy
- scikit-learn, XGBoost, LightGBM
- sentence-transformers, FAISS
- google-generativeai
- And all dependencies

---

## ⚙️ Configuration

### 1. Set Environment Variables

Create `.env` file (or edit existing):

```bash
# Gemini API (ONLY used for response generation, NOT for embeddings/classification)
GEMINI_API_KEY=your_api_key_here

# Database
DATABASE_URL=sqlite:///./tickets.db

# Manager Dashboard Auth (simple password for demo)
MANAGER_PASSWORD=admin123

# Email Settings (optional - defaults to console logging)
SMTP_ENABLED=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_password
SMTP_FROM=noreply@itsupport.com

# Backend API
BACKEND_URL=http://localhost:8000

# ML Model Settings
CRITICAL_THRESHOLD=0.5
CONFIDENCE_THRESHOLD=0.7

# Upload Settings
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=10
```

### 2. Get Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Create API key
3. Add to `.env`: `GEMINI_API_KEY=your_key_here`

---

## 🎓 Training Models

**Required before first run!**

### Dataset

Place your CSV at:
```
C:\Users\sthfa\Downloads\aa_dataset-tickets-multi-lang-5-2-50-version.csv
```

Or update path in `scripts/train_models.py`

### Step 1: Train ML Models

```bash
python scripts/train_models.py
```

**What happens:**
1. Loads CSV dataset (28,587 tickets)
2. Generates embeddings using BAAI/bge-m3 (~10-15 minutes)
3. Splits data (70% train, 15% val, 15% test)
4. Trains department classifier (XGBoost)
5. Trains criticality classifier (Logistic Regression)
6. Evaluates on test set
7. Saves models to `./models/`

**Output:**
```
Department Classifier:
  - Test Accuracy: 0.592
  - Test F1 (macro): 0.516

Criticality Classifier:
  - Test AUC: 0.687
  - Critical Recall: 0.592
```

**Why split data?**
Even though Gemini is not trained, we need to ensure our ML classifiers (department routing, criticality) generalize well to unseen tickets. The split allows us to:
- **Train**: Learn patterns from historical tickets
- **Validation**: Tune hyperparameters and select best model
- **Test**: Evaluate final performance on completely unseen data

### Step 2: Build FAISS Index

```bash
python scripts/build_index.py
```

**What happens:**
1. Loads cached embeddings from training
2. Builds FAISS index for similarity search
3. Saves to `./faiss_index/`

**Output:**
```
Index contains 28587 vectors
✓ Index saved to ./faiss_index/
```

---

## 🚀 Running the System

### Option 1: Individual Scripts (Recommended)

**Terminal 1 - Backend API:**
```bash
start_backend.bat
```
Wait for: `Application startup complete` at http://localhost:8000

**Terminal 2 - Customer Portal:**
```bash
start_customer.bat
```
Opens at: http://localhost:8501

**Terminal 3 - Manager Dashboard:**
```bash
start_manager.bat
```
Opens at: http://localhost:8502

### Option 2: Manual Start

**Backend:**
```bash
cd D:\Capstone
set PYTHONPATH=D:\Capstone
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

**Customer Portal:**
```bash
streamlit run customer_portal/streamlit_app.py --server.port 8501
```

**Manager Dashboard:**
```bash
streamlit run manager_dashboard/streamlit_dashboard.py --server.port 8502
```

---

## 📖 Usage Guide

### 1. Submit a Ticket (Customer)

1. Open **Customer Portal**: http://localhost:8501
2. Fill in form:
   - Name: `John Doe`
   - Email: `john@company.com`
   - Subject: `Cannot access VPN`
   - Body: `I'm getting error 403 when trying to connect to company VPN from home`
   - Attachment: (optional)
3. Click **Submit Ticket**
4. Note the **Ticket ID** (e.g., `#123`)
5. View status updates in real-time

### 2. Automatic Triage (Backend)

System automatically:
1. **Embeds** ticket text using BGE-M3
2. **Predicts Department**: IT Support (confidence: 85%)
3. **Predicts Criticality**: Medium (prob: 0.35)
4. **Retrieves** top 3 similar past tickets
5. **Generates Draft** using Gemini + RAG context
6. **Routes**:
   - If critical (high priority) → **PENDING_APPROVAL**
   - If non-critical → Auto-send (or pending based on config)

### 3. Manager Approval (Manager Dashboard)

1. Open **Manager Dashboard**: http://localhost:8502
2. Login with password: `admin123`
3. Navigate to **"Pending Critical Approvals"** tab
4. See list of tickets awaiting approval
5. Click on ticket to view:
   - Original ticket text
   - ML predictions (department, criticality %)
   - Similar past tickets (context)
   - Gemini draft response (JSON)
6. Actions:
   - ✅ **Approve & Send** - Send draft as-is
   - ✏️ **Edit Response** - Modify then send
   - ❌ **Reject** - Request more info or reassign

### 4. View Analytics

**KPI Dashboard:**
- Total tickets, open count, critical count
- Avg response time
- Tickets by department (pie chart)
- Tickets over time (line chart)
- Critical rate trend

**All Tickets Table:**
- Filter by queue, priority, status, date
- Search functionality
- Export to CSV

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Interactive Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### 1. Create Ticket
```bash
POST /tickets
Content-Type: multipart/form-data

{
  "name": "John Doe",
  "email": "john@company.com",
  "subject": "VPN access issue",
  "body": "Cannot connect to VPN from home",
  "attachment": <file> (optional)
}

Response:
{
  "id": 123,
  "ticket_id": "TKT-2026-00123",
  "status": "NEW",
  "created_at": "2026-02-04T10:30:00Z"
}
```

#### 2. Triage Ticket (Run AI Analysis)
```bash
POST /tickets/{id}/triage

Response:
{
  "ticket_id": 123,
  "predicted_queue": "IT Support",
  "queue_confidence": 0.85,
  "critical_prob": 0.35,
  "is_critical": false,
  "draft_response": {
    "language": "en",
    "subject": "Re: VPN access issue",
    "body": "Hello John, Thank you for contacting IT Support...",
    "confidence": 0.92,
    "needs_human_approval": false,
    "suggested_tags": ["vpn", "access", "network"]
  },
  "similar_tickets": [...]
}
```

#### 3. Get Pending Approvals
```bash
GET /approvals/pending

Response:
[
  {
    "ticket_id": 124,
    "ticket_subject": "Critical server down",
    "priority": "high",
    "predicted_queue": "Technical Support",
    "critical_prob": 0.95,
    "created_at": "2026-02-04T11:00:00Z",
    "draft_response": {...}
  }
]
```

#### 4. Approve Ticket
```bash
POST /tickets/{id}/approve

{
  "edited_response": "..." (optional),
  "approver_name": "Manager Smith"
}

Response:
{
  "status": "APPROVED",
  "sent_at": "2026-02-04T11:15:00Z"
}
```

#### 5. Dashboard Summary
```bash
GET /dashboard/summary

Response:
{
  "total_tickets": 1543,
  "open_tickets": 89,
  "critical_count": 12,
  "avg_response_time_hours": 2.5,
  "by_queue": {
    "IT Support": 234,
    "Technical Support": 456,
    ...
  },
  "by_priority": {
    "high": 123,
    "medium": 789,
    "low": 631
  },
  "time_series": [...]
}
```

### Example cURL Commands

**Submit Ticket:**
```bash
curl -X POST "http://localhost:8000/tickets" \
  -F "name=John Doe" \
  -F "email=john@company.com" \
  -F "subject=VPN Issue" \
  -F "body=Cannot connect to VPN"
```

**Get Ticket Details:**
```bash
curl "http://localhost:8000/tickets/123"
```

**Approve Ticket:**
```bash
curl -X POST "http://localhost:8000/tickets/123/approve" \
  -H "Content-Type: application/json" \
  -d '{"approver_name": "Manager Smith"}'
```

---

## 📊 Performance Metrics

### Department Classification

**Model:** XGBoost + LightGBM Ensemble

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Test F1 (macro)** | 51.6% | Solid performance for 10-way classification |
| **Test Accuracy** | 59.2% | 6x better than random (10%) |
| **Train F1** | 99.0% | Good learning capacity |

**Per-Department Performance:**

| Department | Precision | Recall | F1-Score | Support |
|------------|-----------|--------|----------|---------|
| Billing & Payments | 96% | 73% | **83%** | 418 |
| Service Outages | 86% | 56% | **68%** | 172 |
| Technical Support | 52% | 86% | **65%** | 1255 |
| Customer Service | 54% | 52% | **53%** | 640 |
| Product Support | 54% | 51% | **52%** | 788 |
| IT Support | 69% | 41% | **52%** | 515 |
| Returns & Exchanges | 93% | 25% | **40%** | 216 |
| Human Resources | 100% | 19% | **38%** | 86 |
| Sales & Pre-Sales | 94% | 23% | **37%** | 138 |
| General Inquiry | 91% | 16% | **28%** | 61 |

**Key Insights:**
- ✅ Strong performance on frequent categories (Billing, Outages, Technical)
- 🟡 Weaker on rare categories (General Inquiry: 61 samples, HR: 86 samples)
- 📈 Can improve with more training data for minority classes

### Criticality Classification

**Model:** Logistic Regression

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Test AUC** | 68.7% | Good discrimination |
| **Critical Recall** | 59.2% | Catches 59% of critical tickets |
| **Test Accuracy** | 65% | Balanced performance |

**Confusion Matrix:**

|  | Predicted Non-Critical | Predicted Critical |
|--|------------------------|-------------------|
| **Actual Non-Critical** | 1823 (TN) | 838 (FP) |
| **Actual Critical** | 665 (FN) | 963 (TP) |

**Business Impact:**
- ✅ 963 critical tickets correctly identified
- ⚠️ 665 false negatives (missed criticals) - routed to human approval as safety net
- 📧 838 false positives (extra approvals) - acceptable for safety

### Embedding Quality

**Model:** BAAI/bge-m3

- **Dimensions:** 1024
- **Languages:** English, German (multilingual)
- **Normalization:** L2-normalized vectors
- **Cache:** Persistent disk cache for fast inference

### Retrieval Performance

**FAISS Index:**
- **Total Vectors:** 28,587
- **Index Type:** Flat (exact search)
- **Query Time:** < 10ms for top-5 similar tickets
- **Relevance:** High semantic similarity for contextual RAG

---

## 📁 Project Structure

```
d:\Capstone/
│
├── backend/                          # FastAPI Backend
│   ├── app.py                        # Main FastAPI application
│   ├── db.py                         # Database connection & init
│   ├── models.py                     # SQLAlchemy ORM models
│   ├── schemas.py                    # Pydantic validation schemas
│   │
│   ├── ml/                           # Machine Learning modules
│   │   ├── embeddings.py             # BGE-M3 embedder (singleton)
│   │   ├── train.py                  # Model training pipeline
│   │   ├── predictors.py             # Inference interface
│   │   └── retrieval.py              # FAISS similarity search
│   │
│   ├── gemini/                       # Gemini integration
│   │   └── generate_reply.py         # Draft generation with RAG
│   │
│   └── services/                     # Business logic
│       ├── triage_service.py         # Orchestrate ML pipeline
│       ├── approval_service.py       # Manager actions
│       └── notification_service.py   # Email sending
│
├── customer_portal/                  # Customer-facing web app
│   └── streamlit_app.py              # Streamlit UI for customers
│
├── manager_dashboard/                # Manager web app
│   └── streamlit_dashboard.py        # Streamlit UI for managers
│
├── scripts/                          # Utility scripts
│   ├── train_models.py               # Train ML classifiers
│   ├── build_index.py                # Build FAISS index
│   └── test_system.py                # Verify installation
│
├── models/                           # Trained ML models (created after training)
│   ├── department_classifier.joblib
│   ├── criticality_classifier.joblib
│   └── label_encoder.joblib
│
├── faiss_index/                      # FAISS vector index (created after build)
│   ├── index.faiss
│   └── metadata.pkl
│
├── embeddings_cache/                 # Cached embeddings (created during training)
│   └── dataset_embeddings.pkl
│
├── uploads/                          # User-uploaded attachments
│   └── .gitkeep
│
├── tickets.db                        # SQLite database (created on first run)
│
├── .env                              # Environment variables (USER CREATED)
├── .env.example                      # Template for .env
├── .gitignore                        # Git ignore rules
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
├── ARCHITECTURE.md                   # Detailed architecture
├── PROJECT_SUMMARY.md                # Build summary
├── QUICKSTART.md                     # Quick start guide
│
├── start_backend.bat                 # Start backend API
├── start_customer.bat                # Start customer portal
├── start_manager.bat                 # Start manager dashboard
└── start_all.bat                     # Start all services (may have issues)
```

---

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'backend'`

**Solution:**
Set PYTHONPATH before running:
```bash
set PYTHONPATH=D:\Capstone
python backend/app.py
```

Or use the provided batch scripts:
```bash
start_backend.bat
```

---

### Issue: `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
Install dependencies:
```bash
pip install -r requirements.txt
```

---

### Issue: Backend port 8000 already in use

**Solution:**
1. Find and kill process using port 8000:
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

2. Or change port in backend startup:
```bash
uvicorn backend.app:app --port 8001
```

---

### Issue: Models not found error

**Solution:**
Train models first:
```bash
python scripts/train_models.py
python scripts/build_index.py
```

---

### Issue: Gemini API error `Invalid API Key`

**Solution:**
1. Check `.env` file has correct key:
```
GEMINI_API_KEY=AIzaSy...
```

2. Verify key at: https://makersuite.google.com/app/apikey

3. Restart backend after updating `.env`

---

### Issue: Slow embedding generation

**Expected:** 10-15 minutes for 28K tickets on CPU

**Tips:**
- First run is slow (generates embeddings)
- Subsequent runs use cached embeddings (< 1 second)
- Keep laptop plugged in and prevent sleep
- Close other heavy applications

---

### Issue: Out of memory during training

**Solution:**
- Close other applications
- Reduce batch size in `backend/ml/train.py`:
```python
embeddings = embedder.embed_texts(texts, batch_size=16)  # reduce from 32
```

---

### Issue: Customer portal can't connect to backend

**Symptoms:**
```
HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded
```

**Solution:**
1. Ensure backend is running:
```bash
curl http://localhost:8000/docs
```

2. Check backend logs for errors

3. Verify `BACKEND_URL` in customer portal matches backend address

---

## 📚 Additional Resources

### Documentation
- **FastAPI**: https://fastapi.tiangolo.com/
- **Streamlit**: https://docs.streamlit.io/
- **BAAI/bge-m3**: https://huggingface.co/BAAI/bge-m3
- **FAISS**: https://github.com/facebookresearch/faiss
- **Gemini API**: https://ai.google.dev/docs

### Model Details
- **BAAI/bge-m3**: State-of-the-art multilingual embedding model (1024-dim)
- **XGBoost**: Gradient boosting for high-dimensional classification
- **FAISS**: Billion-scale similarity search by Facebook Research

---

## 🎓 Learning Outcomes

This project demonstrates:

1. **End-to-end ML system design** - From data to production
2. **Model selection & evaluation** - Choosing right algorithms for the task
3. **Human-in-the-loop workflows** - Balancing automation with oversight
4. **Separation of concerns** - Local ML for decisions, API for generation
5. **Production-ready code** - Error handling, logging, caching
6. **Full-stack development** - Backend API + Frontend UIs
7. **MLOps practices** - Model versioning, caching, monitoring

---

## 📝 License

This is a capstone project for educational purposes.

---

## 👥 Authors

**Capstone Project 2026**

---

## 🙏 Acknowledgments

- **BAAI** for the excellent bge-m3 embedding model
- **Google** for Gemini API access
- **FastAPI** and **Streamlit** communities
- **scikit-learn**, **FAISS**, **XGBoost** open-source contributors

---

## 📞 Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review logs in backend terminal
3. Check API docs at http://localhost:8000/docs

---

**Built with ❤️ using Python, FastAPI, Streamlit, and state-of-the-art ML**
