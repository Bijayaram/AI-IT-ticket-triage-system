# Comprehensive Project Report
## AI-Driven IT Ticket Triage System with Human-in-the-Loop Approval

**Capstone Project — Final Report**  
**Date:** April 11, 2026

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement and Objectives](#2-problem-statement-and-objectives)
3. [System Architecture](#3-system-architecture)
4. [Technology Stack](#4-technology-stack)
5. [Data Understanding and Preparation](#5-data-understanding-and-preparation)
6. [Machine Learning Pipeline](#6-machine-learning-pipeline)
7. [Retrieval-Augmented Generation (RAG)](#7-retrieval-augmented-generation-rag)
8. [Backend API Development](#8-backend-api-development)
9. [Frontend Development](#9-frontend-development)
10. [Human-in-the-Loop Approval Workflow](#10-human-in-the-loop-approval-workflow)
11. [Model Evaluation and Comparison](#11-model-evaluation-and-comparison)
12. [Embedding Experiments](#12-embedding-experiments)
13. [Deployment and Operations](#13-deployment-and-operations)
14. [Complete File Inventory](#14-complete-file-inventory)
15. [Challenges Encountered and Solutions](#15-challenges-encountered-and-solutions)
16. [Business Impact and Implications](#16-business-impact-and-implications)
17. [Limitations and Future Work](#17-limitations-and-future-work)
18. [Conclusion](#18-conclusion)

---

## 1. Executive Summary

This capstone project delivers an **end-to-end AI-driven IT ticket triage system** that automates three core support operations:

1. **Department routing** — classifies incoming tickets into the correct support queue using a machine learning ensemble.
2. **Criticality detection** — flags high-priority tickets so they receive immediate attention.
3. **Draft response generation** — uses Google Gemini with retrieval-augmented generation (RAG) to draft contextual replies grounded in similar historical tickets.

All three capabilities are wrapped in a **human-in-the-loop approval workflow**: a manager reviews AI-generated outputs before any response reaches the customer. The system supports **multilingual tickets** (English and German) through local multilingual embeddings.

**Key results:**
- Department routing: **67.8% accuracy**, **0.660 macro F1**, **0.903 macro AUC** (XGBoost + LightGBM ensemble)
- Criticality detection: **0.686 AUC**, **57.5% critical recall** (balanced logistic regression)
- Full-stack deployment: FastAPI backend, Next.js frontend, SQLite database, FAISS vector index

---

## 2. Problem Statement and Objectives

### 2.1 Problem

IT support teams receive a high volume of tickets across multiple departments and priority levels. Manual triage is slow, inconsistent, and error-prone — tickets may be misrouted, critical issues may be overlooked, and response times suffer.

### 2.2 Objectives

| Objective | Approach |
|-----------|----------|
| Automate ticket routing to the correct department | ML classification on ticket text |
| Identify critical/high-priority tickets automatically | Binary criticality classifier |
| Generate draft responses to accelerate reply times | Gemini API with RAG context |
| Maintain human oversight over AI outputs | Manager approval workflow |
| Support multilingual tickets | Multilingual embedding model (BAAI/bge-m3) |
| Provide operational dashboards | Real-time KPIs, filters, and analytics |

---

## 3. System Architecture

The system follows a **layered architecture** with clear separation of concerns:

```
┌──────────────────────────────────────────────────────────────────┐
│                        FRONTEND LAYER                            │
│   Next.js 14 (React 18)  ·  Customer Portal  ·  Manager UI      │
│   Ticket Tracker  ·  Dashboard  ·  Approval Interface            │
├──────────────────────────────────────────────────────────────────┤
│                         API LAYER                                │
│   FastAPI (Python)  ·  REST endpoints  ·  CORS  ·  File upload   │
├──────────────────────────────────────────────────────────────────┤
│                       SERVICE LAYER                              │
│   TriageService  ·  ApprovalService  ·  NotificationService      │
├──────────────────────┬────────────────┬──────────────────────────┤
│     ML LAYER         │   RAG LAYER    │   GENERATION LAYER       │
│  LocalEmbedder       │  FAISS Index   │  Gemini API              │
│  TicketPredictor     │  TicketRetriever│  GeminiReplyGenerator   │
│  TicketClassifierTrainer │            │                          │
├──────────────────────┴────────────────┴──────────────────────────┤
│                      DATA LAYER                                  │
│   SQLite (SQLAlchemy ORM)  ·  Embedding Cache  ·  Model Files    │
└──────────────────────────────────────────────────────────────────┘
```

### 3.1 End-to-End Triage Flow

1. Customer submits ticket via web form (Next.js → FastAPI)
2. Ticket stored in SQLite with status `NEW`
3. **ML Prediction**: bge-m3 embedding → ensemble classifier predicts department; logistic regression predicts criticality
4. **Retrieval**: FAISS finds top-5 similar historical tickets using cosine similarity on the same embedding
5. **Generation**: Gemini drafts a response using ticket + similar ticket context (RAG)
6. **Business rules**: critical tickets and low-confidence drafts always require human approval
7. Manager reviews, optionally edits, then approves or rejects
8. Approved response sent to customer (email or console demo)
9. Full audit trail logged at every step

---

## 4. Technology Stack

### 4.1 Backend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Web framework | FastAPI | 0.115.0 | REST API with automatic OpenAPI docs |
| ASGI server | Uvicorn | 0.30.6 | High-performance async server |
| ORM | SQLAlchemy | 2.0.35 | Database abstraction |
| Validation | Pydantic | 2.9.2 | Request/response schema validation |
| Database | SQLite | — | Lightweight relational storage |

### 4.2 Machine Learning

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Embeddings | sentence-transformers | 3.1.1 | Local BAAI/bge-m3 (1024-dim, multilingual) |
| Dept classifier | XGBoost + LightGBM | 2.0.3 / 4.5.0 | Soft-voting ensemble for routing |
| Crit classifier | scikit-learn | 1.5.2 | Balanced logistic regression |
| Resampling | imbalanced-learn | 0.12.3 | Optional SMOTE for class imbalance |
| Vector search | faiss-cpu | 1.9.0 | Cosine similarity retrieval |
| Model persistence | joblib | 1.4.2 | Serialized classifiers |
| Generation | google-generativeai | 0.8.3 | Gemini 2.5 Flash for draft replies |

### 4.3 Frontend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | Next.js | 14.2 | React-based SSR/SPA framework |
| UI library | React | 18 | Component-based UI |
| Styling | Tailwind CSS | 3.x | Utility-first CSS |
| HTTP client | Axios | — | API communication |
| Charts | Recharts | — | Dashboard visualizations |
| Icons | Lucide React | — | UI iconography |
| Notifications | React Hot Toast | — | User feedback toasts |

### 4.4 Data Analysis

| Tool | Purpose |
|------|---------|
| Pandas, NumPy | Data manipulation |
| Matplotlib, Seaborn | Visualization |
| SciPy | Statistical analysis |
| Streamlit | Legacy interactive dashboards |

---

## 5. Data Understanding and Preparation

### 5.1 Dataset Overview

| Attribute | Value |
|-----------|-------|
| Source file | `aa_dataset-tickets-multi-lang-5-2-50-version.csv` |
| Total records | 28,587 valid tickets (after filtering) |
| Languages | English (en), German (de) |
| Original queues | 10 unique departments |
| Consolidated queues | 5 departments (after mapping) |
| Critical tickets | 11,178 (39.1%) |
| Non-critical tickets | 17,409 (60.9%) |

### 5.2 Fields

| Field | Description |
|-------|-------------|
| `subject` | Ticket subject line |
| `body` | Full ticket description |
| `queue` | Department/team assignment (label for routing) |
| `priority` | high/medium/low (used to derive `is_critical`) |
| `language` | en or de |
| `type` | Incident, Request, etc. |
| `answer` | Historical response (used for RAG context) |
| `tag_1` through `tag_8` | Category tags |

### 5.3 Data Preparation Steps

1. **Text combination**: `text = subject + "\n\n" + body` (missing fields filled as empty string)
2. **Label creation**: `is_critical = 1` if `priority == "high"`, else `0`
3. **Row filtering**: Dropped rows with missing `queue` or `text`
4. **Queue consolidation**: Reduced 10 overlapping queues to 5 distinct departments:

| Original Queue | Consolidated To |
|----------------|-----------------|
| General Inquiry | Customer Service |
| Human Resources | Customer Service |
| IT Support | Technical Support |
| Returns and Exchanges | Product Support |
| Sales and Pre-Sales | Product Support |
| Billing and Payments | *(unchanged)* |
| Customer Service | *(unchanged)* |
| Product Support | *(unchanged)* |
| Service Outages and Maintenance | *(unchanged)* |
| Technical Support | *(unchanged)* |

### 5.4 Train/Validation/Test Split

| Split | Samples | Proportion | Purpose |
|-------|---------|-----------|---------|
| Train | 20,010 | ~70% | Model fitting |
| Validation | 4,288 | ~15% | Hyperparameter tuning, threshold optimization |
| Test | 4,289 | ~15% | Final unbiased evaluation |

Splits are **stratified by department** to preserve class proportions. `random_state=42` for reproducibility.

---

## 6. Machine Learning Pipeline

### 6.1 Embedding Generation

| Attribute | Value |
|-----------|-------|
| Model | BAAI/bge-m3 |
| Architecture | XLM-RoBERTa (24 transformer layers, 568M parameters) |
| Embedding dimension | 1024 |
| Normalization | L2-normalized (unit vectors for cosine similarity) |
| Multilingual | Yes (English + German) |
| Caching | Embeddings serialized to `embeddings_cache/dataset_embeddings.pkl` |

The embedder is implemented as a singleton (`LocalEmbedder` in `backend/ml/embeddings.py`) that loads once and serves both training and inference. The fallback model is `intfloat/multilingual-e5-large` if bge-m3 fails to load.

**Output**: Each ticket becomes a 1024-dimensional float32 vector. For 28,587 tickets, the full embedding matrix is shape `(28587, 1024)`.

### 6.2 Department Routing Classifier

| Attribute | Value |
|-----------|-------|
| Architecture | Soft-voting ensemble (XGBoost + LightGBM) |
| Input | 1024-dim embedding vector |
| Output | 5-class probability distribution over departments |
| Label encoding | `LabelEncoder` for tree model compatibility |

**XGBoost configuration**: 120 estimators, max_depth=6, learning_rate=0.15, hist tree method.  
**LightGBM configuration**: 120 estimators, max_depth=6, learning_rate=0.15.  
**Voting**: Soft (averaged predicted probabilities).

The ensemble was chosen over individual models because it achieved the **highest accuracy (0.678)** and **highest macro AUC (0.903)** while providing stability through model diversity.

### 6.3 Criticality Classifier

| Attribute | Value |
|-----------|-------|
| Architecture | Logistic Regression |
| Input | 1024-dim embedding vector |
| Output | Probability of critical (P(critical)) |
| Class weighting | `class_weight='balanced'` (automatic inverse-frequency weighting) |
| Threshold | Default 0.5, optionally tuned via `critical_threshold.json` |

Logistic regression was chosen for **speed, calibrated probabilities**, and **interpretability**. The `class_weight='balanced'` setting mitigates the 39/61 class imbalance.

### 6.4 Training Pipeline (`TicketClassifierTrainer`)

```
CSV Dataset
    │
    ├── load_and_prepare_data()  →  Text combination, label creation, queue consolidation
    │
    ├── generate_embeddings()    →  BAAI/bge-m3 encoding (cached for repeat runs)
    │
    ├── split_data()             →  Stratified train/val/test split
    │
    ├── train_department_classifier()  →  XGBoost + LightGBM ensemble
    │
    ├── train_criticality_classifier() →  Balanced logistic regression
    │
    └── save_models()            →  joblib serialization to ./models/
```

**Saved artifacts:**
- `models/department_classifier.joblib`
- `models/criticality_classifier.joblib`
- `models/label_encoder.joblib`
- `models/critical_threshold.json` (optional, from threshold tuning)
- `embeddings_cache/dataset_embeddings.pkl`

### 6.5 Inference Pipeline (`TicketPredictor`)

```
New Ticket (subject, body)
    │
    ├── Combine text: "subject\n\nbody"
    │
    ├── embed_single() → 1024-dim vector
    │
    ├── dept_classifier.predict() → Predicted department
    │   └── predict_proba() → Confidence score
    │
    ├── critical_classifier.predict_proba() → P(critical)
    │   └── Compare to threshold → is_critical boolean
    │
    └── Return: {predicted_queue, queue_confidence, critical_prob, is_critical, embedding}
```

---

## 7. Retrieval-Augmented Generation (RAG)

### 7.1 FAISS Vector Index

The retrieval system uses **FAISS IndexFlatIP** (inner product on L2-normalized vectors = cosine similarity) for fast nearest-neighbor search.

| Attribute | Value |
|-----------|-------|
| Index type | IndexFlatIP (exact cosine similarity) |
| Vectors indexed | 28,587 ticket embeddings |
| Metadata | Subject, body, answer, queue, priority, language |
| Storage | `faiss_index/tickets.index` + `faiss_index/metadata.pkl` |

**Build process** (`scripts/build_index.py`):
1. Load CSV dataset
2. Load or generate embeddings (reuses cached `dataset_embeddings.pkl`)
3. Build FAISS index
4. Save index + metadata DataFrame

**Search**: Given a new ticket's embedding, retrieve top-k (default 5) most similar historical tickets with their answers.

### 7.2 Gemini Draft Generation

| Attribute | Value |
|-----------|-------|
| Model | Gemini 2.5 Flash |
| Purpose | Draft response generation ONLY (not embeddings, not classification) |
| Temperature | 0.3 (low for consistency) |
| Output format | Strict JSON with defined fields |
| Retries | Up to 3 on JSON/API errors |

**RAG prompt structure:**
1. System instruction: "You are an IT support agent..."
2. Current ticket: subject + body
3. Similar tickets (top 3 from FAISS): subject + body + historical answer
4. Required output fields: language, subject, body, confidence, needs_human_approval, suggested_tags

**Business rules applied after generation:**
- Critical tickets → always require human approval
- Confidence below threshold (default 0.7) → require human approval
- These rules override the model's own `needs_human_approval` flag

---

## 8. Backend API Development

### 8.1 FastAPI Application (`backend/app.py`)

The backend exposes a RESTful API with the following endpoint groups:

#### Ticket Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/tickets` | Create new ticket (multipart form with optional attachment) |
| GET | `/tickets/{id}` | Get ticket detail with responses and approvals |
| GET | `/tickets` | List tickets with filters (status, queue, critical, email) |
| POST | `/tickets/{id}/triage` | Run ML prediction + retrieval + optional Gemini draft |

#### Approval Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/approvals/pending` | List tickets awaiting manager approval |
| POST | `/tickets/{id}/approve` | Approve and send response (with optional edits) |
| POST | `/tickets/{id}/reject` | Reject ticket (request more info) |

#### Dashboard Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/dashboard/summary` | KPIs: totals, critical count, by-queue, by-status |
| GET | `/dashboard/timeseries` | Ticket counts over time (configurable days) |

#### System

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/docs` | Auto-generated Swagger UI |

### 8.2 Database Schema

**Four tables** managed by SQLAlchemy ORM:

**`tickets`** — Core entity tracking the full ticket lifecycle:
- Identity: `id`, `subject`, `body`, `submitter_name`, `submitter_email`
- Attachment: `attachment_path`
- ML predictions: `predicted_queue`, `queue_confidence`, `critical_prob`, `is_critical`, `predicted_language`
- Status: `status` (enum: NEW → TRIAGED → DRAFTED → PENDING_APPROVAL → APPROVED → SENT)
- Timestamps: `created_at`, `updated_at`, `triaged_at`, `sent_at`

**`responses`** — AI-generated and final approved responses:
- Draft: `draft_language`, `draft_subject`, `draft_body`, `draft_confidence`, `needs_human_approval`
- Context: `suggested_tags`, `retrieval_context` (JSON)
- Final: `final_subject`, `final_body`
- Timestamps: `created_at`, `approved_at`

**`approvals`** — Manager decisions:
- `approver_name`, `approver_email`, `decision` (APPROVED / REJECTED / EDITED_AND_APPROVED)
- `decision_notes`, `created_at`

**`audit_logs`** — Complete audit trail:
- `action`, `actor`, `details` (JSON text)
- Optional `ticket_id` for ticket-specific logs

### 8.3 Service Layer

**TriageService** — Orchestrates the full triage pipeline:
1. ML prediction (predictor) → update ticket fields
2. Similar ticket retrieval (FAISS) → context for Gemini
3. Draft generation (Gemini) → create Response record
4. Status management → PENDING_APPROVAL or DRAFTED
5. Audit logging at each step

**ApprovalService** — Handles manager decisions:
1. Approve: finalize response (with optional edits), trigger email, update status to SENT
2. Reject: update status to REJECTED, log reason

**NotificationService** — Email delivery:
- SMTP mode: real email via TLS connection
- Demo mode: formatted console output (default for development)

---

## 9. Frontend Development

### 9.1 Customer Portal (`/` — Submit Ticket)

A modern, glassmorphism-styled form with:
- **Step-by-step flow**: Contact info → ticket details → submit
- **Automatic triage**: After submission, immediately triggers ML prediction + Gemini draft
- **Success screen**: Displays ticket ID, assigned department, priority level, and whether manager review is needed
- **File attachment support**: Optional file upload with size limit

### 9.2 Ticket Tracker (`/track` — Track Status)

Allows customers to look up their tickets by email:
- **Email search**: Retrieves all tickets for the given email
- **Ticket list**: Priority indicators, status badges, department labels, timestamps
- **Detail modal**: Full ticket content, AI response (if approved), or "under review" status
- **Response display**: Shows final approved response with approval timestamp

### 9.3 Manager Dashboard (`/manager` — Admin Panel)

A comprehensive management interface with three tabs:

**Dashboard Tab:**
- KPI cards: total tickets, open tickets, critical count, pending approvals
- Tickets by status distribution
- Tickets by department with progress bars
- Quick action buttons

**Approvals Tab:**
- List of tickets pending manager review
- Review modal with: customer message, AI-generated draft (editable), ML analysis (queue, confidence, critical probability, language)
- Approve / Reject actions
- Edit capability for response subject and body before approval

**All Tickets Tab:**
- Searchable/filterable ticket list (by ID, subject, email, body)
- Status dropdown filter
- Critical-only toggle
- Detail modal for any ticket

**Access control**: Password-protected (demo password for development).

### 9.4 API Integration (`frontend/lib/api.ts`)

Centralized Axios client with:
- Configurable base URL via environment variable
- Multipart form data for ticket creation
- JSON for all other endpoints
- Next.js API rewrites (`/api/*` → `localhost:8000`) for development proxy

---

## 10. Human-in-the-Loop Approval Workflow

The system enforces human oversight through a multi-stage workflow:

```
Ticket Created (NEW)
       │
       ▼
  ML Prediction (TRIAGED)
       │
       ▼
  Gemini Draft (DRAFTED)
       │
       ├── Critical ticket?        ──── YES ──→ PENDING_APPROVAL
       ├── Low confidence (<0.7)?  ──── YES ──→ PENDING_APPROVAL
       └── High confidence + non-critical ──→ PENDING_APPROVAL (configurable)
                                                      │
                                                      ▼
                                              Manager Reviews
                                                      │
                                         ┌────────────┴────────────┐
                                         │                         │
                                    APPROVE                    REJECT
                                  (edit optional)          (with reason)
                                         │                         │
                                         ▼                         ▼
                                   Email Sent              REJECTED status
                                    (SENT)                Needs follow-up
```

**Audit trail**: Every step (prediction, draft generation, approval/rejection, email delivery) is logged to the `audit_logs` table with actor, action, and JSON details.

---

## 11. Model Evaluation and Comparison

### 11.1 Department Routing — Model Comparison

Five models were evaluated on the same stratified test set:

| Model | Test Accuracy | Test F1 (macro) | Macro AUC |
|-------|--------------|-----------------|-----------|
| **Ensemble (XGB + LGBM)** | **0.678** | 0.660 | **0.903** |
| LightGBM | 0.678 | **0.666** | 0.896 |
| XGBoost | 0.661 | 0.638 | 0.894 |
| LinearSVC | 0.544 | 0.533 | 0.817 |
| Logistic Regression | 0.497 | 0.497 | 0.810 |

**Selected model**: XGBoost + LightGBM ensemble — best macro AUC and accuracy, stable probability estimates.

### 11.2 Department Routing — Per-Class Performance (Ensemble, Test Set)

| Department | Precision | Recall | F1 | Support |
|------------|-----------|--------|-----|---------|
| Billing and Payments | 0.97 | 0.68 | 0.80 | 418 |
| Customer Service | 0.66 | 0.38 | 0.49 | 788 |
| Product Support | 0.63 | 0.57 | 0.60 | 1141 |
| Service Outages and Maintenance | 0.88 | 0.51 | 0.64 | 172 |
| Technical Support | 0.64 | 0.87 | 0.74 | 1770 |

**Observations**: Billing and Payments has the highest precision (0.97). Technical Support has the highest recall (0.87) but pulls recall from other classes. Customer Service is the hardest to classify (F1 = 0.49), likely due to overlap with Product Support and Technical Support.

### 11.3 Criticality Detection — Model Comparison

| Model | Test AUC | Test Recall (Critical) |
|-------|----------|----------------------|
| **Random Forest** | **0.862** | 0.404 |
| XGBoost | 0.822 | 0.511 |
| LinearSVC | 0.699 | 0.601 |
| **Logistic Regression** | 0.686 | **0.575** |

**Selected model**: Logistic Regression — prioritizes calibrated probabilities, speed, and higher recall at the default threshold. Optional threshold tuning available to further trade precision for recall.

### 11.4 Key Evaluation Insights

1. **Nonlinear models dominate** for department routing on dense embeddings — boosting gains +18% accuracy over logistic regression.
2. **Macro metrics reveal class-level weaknesses** that overall accuracy hides — essential for rare departments like Service Outages.
3. **AUC vs recall at threshold tell different stories** for criticality — Random Forest has the best ranking (AUC 0.862) but lowest recall at 0.5; logistic regression balances both.
4. **Queue consolidation** from 10 to 5 classes was critical for reducing label ambiguity and improving classifier signal.

---

## 12. Embedding Experiments

Two experiments were conducted to investigate whether injecting IT-domain knowledge could improve classification accuracy beyond the base bge-m3 embeddings.

### 12.1 Experiment A — Handcrafted IT Keyword Features

**Hypothesis**: Adding 13 binary/count features for IT-domain keyword categories would give extra discriminative signal.

**Features added**: text_length, word_count, avg_word_length, has_network_words, has_account_words, has_billing_words, has_product_words, has_hardware_words, has_software_words, is_german, is_english, has_urgent_words, has_question.

**Result** (1024 + 13 = 1037 features):

| Metric | Baseline | Enhanced | Delta |
|--------|----------|----------|-------|
| Dept Test Accuracy | 0.678 | 0.667 | -0.011 |
| Dept Test F1 | 0.660 | 0.651 | -0.009 |
| Criticality AUC | 0.686 | 0.673 | -0.013 |
| Critical Recall | 0.575 | 0.567 | -0.008 |

**Conclusion**: Negative result. The keyword features are redundant with information already captured by bge-m3's neural representations.

### 12.2 Experiment B — Contrastive Fine-Tuning of bge-m3

**Hypothesis**: Fine-tuning the embedding encoder on ticket data using contrastive learning would produce more IT-domain-aware representations.

**Setup**: 1,500 same-department positive pairs, Multiple Negatives Ranking Loss, 1 epoch, 187 steps, layers 0-21 frozen (only 4.6% of parameters trainable), CPU training for 54.6 minutes.

**Training loss**: Decreased from 2.37 → 1.81 (per-step) showing clear learning signal.

**Result** (fine-tuned embeddings, 1024 features):

| Metric | Baseline | Fine-Tuned | Delta |
|--------|----------|------------|-------|
| Dept Test Accuracy | 0.678 | 0.666 | -0.012 |
| Dept Test F1 | 0.660 | 0.653 | -0.007 |
| Criticality AUC | 0.686 | 0.669 | -0.017 |
| Critical Recall | 0.575 | 0.550 | -0.025 |

**Conclusion**: Negative result under CPU constraints. The fine-tuning was too shallow (187 steps, 4.6% of parameters) to overcome the base model's strong general-purpose representations. GPU resources with 10K+ pairs and multiple epochs would be needed.

**Final decision**: Reverted to the original base bge-m3 embeddings, which remain the production default.

---

## 13. Deployment and Operations

### 13.1 System Startup

The system runs three processes:

| Process | Command | Port | Purpose |
|---------|---------|------|---------|
| Backend API | `uvicorn backend.app:app` | 8000 | REST API + ML inference |
| Frontend | `npm run dev` (in `frontend/`) | 3000 | Customer + Manager UI |
| *(Optional)* Streamlit | `streamlit run` | 8501/8502 | Legacy dashboards |

**Automated start**: `start_all.bat` launches backend and frontend with correct `PYTHONPATH`.

### 13.2 Pre-Deployment Steps

```
1. Install dependencies:     pip install -r requirements.txt
                              cd frontend && npm install
2. Configure environment:    Copy .env.example → .env, set GEMINI_API_KEY
3. Train ML models:          python scripts/train_models.py <dataset.csv>
4. Build FAISS index:        python scripts/build_index.py <dataset.csv>
5. Verify system:            python scripts/test_system.py
6. Start services:           start_all.bat
```

### 13.3 Environment Configuration

Key environment variables (from `.env.example`):

| Variable | Purpose | Default |
|----------|---------|---------|
| `GEMINI_API_KEY` | Google Gemini API key (required for drafts) | — |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./tickets.db` |
| `MANAGER_PASSWORD` | Dashboard access password | — |
| `CRITICAL_THRESHOLD` | P(critical) threshold for flagging | 0.5 |
| `CONFIDENCE_THRESHOLD` | Draft confidence threshold for auto-approve | 0.7 |
| `SMTP_ENABLED` | Enable real email delivery | false |
| `UPLOAD_DIR` | File attachment storage path | `./uploads` |
| `MAX_FILE_SIZE_MB` | Maximum attachment size | 10 |

### 13.4 Trained Model Artifacts

| File | Size | Contents |
|------|------|----------|
| `models/department_classifier.joblib` | ~50 MB | XGBoost + LightGBM ensemble |
| `models/criticality_classifier.joblib` | ~5 MB | Balanced logistic regression |
| `models/label_encoder.joblib` | <1 KB | Department name ↔ integer mapping |
| `models/critical_threshold.json` | <1 KB | Optional tuned threshold |
| `embeddings_cache/dataset_embeddings.pkl` | ~112 MB | 28,587 × 1024 float32 vectors |
| `faiss_index/tickets.index` | ~112 MB | FAISS IndexFlatIP |
| `faiss_index/metadata.pkl` | ~50 MB | Ticket metadata DataFrame |

---

## 14. Complete File Inventory

### 14.1 Backend (`backend/`)

| File | Purpose |
|------|---------|
| `app.py` | FastAPI application with all REST endpoints |
| `db.py` | SQLAlchemy engine, session, init/reset database |
| `models.py` | ORM models: Ticket, Response, Approval, AuditLog |
| `schemas.py` | Pydantic request/response schemas |
| `ml/embeddings.py` | BAAI/bge-m3 embedding generator (singleton) |
| `ml/train.py` | Full training pipeline: data prep → embeddings → split → train → save |
| `ml/predictors.py` | Inference: load models → embed ticket → predict dept + criticality |
| `ml/retrieval.py` | FAISS index build, save, load, and similarity search |
| `gemini/generate_reply.py` | Gemini draft generation with RAG prompt and business rules |
| `services/triage_service.py` | Orchestration: predict → retrieve → draft → update DB |
| `services/approval_service.py` | Approve/reject workflow with email trigger |
| `services/notification_service.py` | SMTP or console-mode email delivery |

### 14.2 Frontend (`frontend/`)

| File | Purpose |
|------|---------|
| `app/page.tsx` | Customer portal: submit ticket form |
| `app/track/page.tsx` | Ticket tracker: search by email, view status/responses |
| `app/manager/page.tsx` | Manager dashboard: KPIs, approvals, ticket management |
| `app/layout.tsx` | Root layout with global styling |
| `app/globals.css` | Tailwind CSS + custom theme (gradients, glassmorphism) |
| `lib/api.ts` | Centralized Axios API client |
| `lib/types.ts` | TypeScript type definitions |
| `next.config.js` | API proxy rewrites for development |
| `tailwind.config.ts` | Tailwind theme configuration |
| `package.json` | Dependencies and scripts |

### 14.3 Scripts (`scripts/`)

| File | Purpose |
|------|---------|
| `train_models.py` | CLI entry point for full model training |
| `build_index.py` | Build FAISS similarity index from dataset |
| `test_system.py` | System smoke tests (imports, embedding, DB) |
| `finetune_embedder.py` | Contrastive fine-tuning experiment for bge-m3 |
| `generate_finetuned_embeddings.py` | Weight-patching + batch embedding generation |

### 14.4 Analysis and Evaluation (root)

| File | Purpose |
|------|---------|
| `comprehensive_ticket_analysis.py` | 12-plot EDA of the ticket dataset |
| `evaluate_models.py` | Offline model evaluation |
| `evaluate_models_with_plots.py` | Evaluation with confusion matrices and ROC curves |
| `model_comparison_visualizations.py` | Multi-model comparison charts |
| `tune_critical_threshold.py` | Criticality threshold optimization on validation set |
| `build_pre_embedding_dataset.py` | Feature engineering for pre-embedding dataset |

### 14.5 Startup Scripts (root)

| File | Purpose |
|------|---------|
| `start_all.bat` | Start backend + frontend together |
| `start_backend.bat` | Start FastAPI only |
| `start_frontend.bat` | Start Next.js only |
| `start_customer.bat` | Start legacy Streamlit customer app |
| `start_manager.bat` | Start legacy Streamlit manager dashboard |
| `run_analysis.bat` | Run EDA analysis script |

---

## 15. Challenges Encountered and Solutions

### 15.1 Feature Mismatch (1037 vs 1024)

**Problem**: Models initially trained with 1037 features (1024 embeddings + 13 handcrafted) could not run inference with 1024-dim embeddings alone.  
**Solution**: Retrained models with embeddings-only (1024 features) as the default, keeping handcrafted features as an optional experimental path.

### 15.2 Fine-Tuned Model Reload Crash on Windows

**Problem**: The 2.3 GB fine-tuned model safetensors file caused access violation (0xC0000005) when reloading on Windows due to memory constraints.  
**Solution**: Developed a weight-patching approach: load original bge-m3 from HuggingFace cache, then patch only the 34 modified parameter tensors (layers 22-23) from the fine-tuned file.

### 15.3 Python Output Buffering in Background Processes

**Problem**: Training and fine-tuning scripts produced no visible output when run in the background due to Python's stdout buffering.  
**Solution**: Added `flush=True` to all print statements and set `PYTHONUNBUFFERED=1` environment variable.

### 15.4 Library Version Compatibility

**Problem**: `SentenceTransformerTrainer` from sentence-transformers 3.1.1 was incompatible with the installed `transformers` library version (missing `num_items_in_batch` parameter).  
**Solution**: Replaced the Trainer-based approach with a manual PyTorch training loop for full control over the training process.

### 15.5 Criticality Class Imbalance

**Problem**: 39.1% critical vs 60.9% non-critical creates bias toward the majority class.  
**Solution**: Used `class_weight='balanced'` in logistic regression (automatic inverse-frequency weighting) plus optional threshold tuning for operational recall targets.

---

## 16. Business Impact and Implications

| Area | Impact |
|------|--------|
| **Response time** | Automated triage + draft generation reduces manual processing from minutes to seconds per ticket |
| **Routing accuracy** | Consistent ML-based routing reduces misassignment and inter-department transfers |
| **Critical incident handling** | Automatic flagging ensures high-priority tickets get immediate visibility |
| **Agent productivity** | Pre-drafted responses (with RAG context) reduce time-to-first-response |
| **Quality assurance** | Human-in-the-loop approval ensures no AI-generated response reaches customers unchecked |
| **Audit compliance** | Full audit trail of every prediction, draft, approval, and delivery |
| **Scalability** | Local embeddings + lightweight classifiers handle batch triage; no per-ticket API cost for prediction |
| **Multilingual support** | bge-m3 handles English and German tickets without separate models |

**Risks acknowledged:**
- Misrouting still occurs on ambiguous or multi-issue tickets
- Domain drift (new products, new teams) requires periodic retraining
- Gemini API dependency for draft generation (predictions work offline)
- Demo authentication in manager UI needs hardening for production

---

## 17. Limitations and Future Work

### 17.1 Current Limitations

1. **Classification ceiling**: ~68% department accuracy reflects inherent class overlap, especially Customer Service vs Product Support
2. **CPU-only training**: Fine-tuning large language models is impractical without GPU resources
3. **SQLite**: Suitable for development/demo but not concurrent production workloads
4. **Single-language pair**: Only English + German; adding languages requires retraining validation
5. **No active learning loop**: Model doesn't learn from manager corrections

### 17.2 Recommended Future Work

| Enhancement | Effort | Expected Impact |
|-------------|--------|-----------------|
| GPU-based fine-tuning of bge-m3 (10K+ pairs, full model) | High | +2-5% F1 improvement |
| Active learning from manager approvals/corrections | Medium | Continuous model improvement |
| PostgreSQL migration for production concurrency | Medium | Production readiness |
| Proper authentication (JWT/OAuth) for manager UI | Medium | Security hardening |
| More granular queue definitions with clearer boundaries | Medium | Reduced class overlap |
| Additional languages beyond en/de | Medium | Wider applicability |
| Hyperparameter tuning (GridSearchCV for ensemble) | Low | +1-2% marginal improvement |
| A/B testing framework for model updates | High | Safe rollout of improvements |

---

## 18. Conclusion

This capstone project successfully demonstrates a **production-grade AI-driven IT ticket triage system** that combines:

- **Local machine learning** (BAAI/bge-m3 embeddings + XGBoost/LightGBM ensemble) for fast, private, multilingual ticket classification
- **Retrieval-augmented generation** (FAISS + Google Gemini) for contextual draft responses grounded in historical data
- **Human-in-the-loop governance** ensuring AI outputs are reviewed before reaching customers
- **Full-stack engineering** with a FastAPI backend, Next.js frontend, and comprehensive API design

The system processes a ticket from submission to approved response in a single workflow, with complete audit logging at every step. While the embedding experiments showed that the base bge-m3 model is already near-optimal for this dataset size, the rigorous experimental methodology — testing handcrafted features and contrastive fine-tuning, documenting negative results — demonstrates sound ML engineering practice.

The architecture is designed for extensibility: the modular service layer, configurable thresholds, and pluggable components (embedder, classifier, generator) make it straightforward to swap models, add languages, or scale to production infrastructure.
