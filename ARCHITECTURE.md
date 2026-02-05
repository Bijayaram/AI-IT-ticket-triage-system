# System Architecture

## Overview

The IT Ticket Triage System is a production-ready, end-to-end AI application with clear separation of concerns and hybrid AI architecture.

## Core Principles

### 1. Hybrid AI Architecture
- **Local ML**: Fast, deterministic classification (department routing, criticality)
- **Gemini API**: Creative, context-aware response generation
- **FAISS Retrieval**: RAG-lite for grounded responses
- **Human-in-the-Loop**: Critical approval workflow

### 2. Separation of Concerns
```
┌─────────────────────────────────────────────┐
│           PRESENTATION LAYER                │
│  (Two separate Streamlit apps)              │
│  • Customer Portal                          │
│  • Manager Dashboard                        │
└────────────────┬────────────────────────────┘
                 │ REST API
┌────────────────▼────────────────────────────┐
│           APPLICATION LAYER                 │
│  (FastAPI backend)                          │
│  • Request validation (Pydantic)            │
│  • Business logic (Services)                │
│  • Orchestration (Triage workflow)          │
└────┬──────────┬──────────┬──────────────────┘
     │          │          │
     │          │          │
┌────▼────┐ ┌──▼───┐  ┌───▼────┐
│ ML      │ │FAISS │  │ Gemini │
│ Models  │ │Index │  │  API   │
└─────────┘ └──────┘  └────────┘
     │          │          
┌────▼──────────▼────┐
│   DATA LAYER       │
│  • SQLite DB       │
│  • Embeddings      │
│  • Models cache    │
└────────────────────┘
```

### 3. Data Flow

#### Ticket Submission Flow
```
Customer → Submit Ticket → Backend API → Database
                                        ↓
                          Trigger Triage (async)
                                        ↓
                          ┌─────────────┴──────────────┐
                          │   TRIAGE WORKFLOW          │
                          │                            │
                          │ 1. Generate embeddings     │
                          │    (local, bge-m3)         │
                          │         ↓                  │
                          │ 2. ML Prediction           │
                          │    • Department            │
                          │    • Criticality           │
                          │         ↓                  │
                          │ 3. FAISS Retrieval         │
                          │    • Find similar tickets  │
                          │    • Extract context       │
                          │         ↓                  │
                          │ 4. Gemini Generation       │
                          │    • Draft reply           │
                          │    • Confidence score      │
                          │         ↓                  │
                          │ 5. Business Rules          │
                          │    • If critical → Approve │
                          │    • If low conf → Approve │
                          │    • Else → Auto-send      │
                          └────────────────────────────┘
```

#### Approval Flow
```
Manager Dashboard → View Pending → Review Draft
                                      ↓
                          ┌───────────┴──────────┐
                          │                      │
                    ✅ APPROVE              ❌ REJECT
                          │                      │
                    Edit (optional)        Add notes
                          │                      │
                    Send Email            Mark rejected
                          │                      │
                    Update status         Notify team
                          │                      │
                    Mark SENT             Status: REJECTED
```

## Component Details

### Backend Services

#### 1. Triage Service
**Purpose**: Orchestrate ML prediction, retrieval, and drafting

**Key Methods**:
- `triage_ticket()`: Main entry point
  - Calls predictor for classification
  - Calls retriever for similar tickets
  - Calls generator for draft response
  - Applies business rules
  - Updates database

**Error Handling**:
- ML prediction failure → Default to critical
- Retrieval failure → Continue without context
- Generation failure → Route to human approval

#### 2. Approval Service
**Purpose**: Manage human approval workflow

**Key Methods**:
- `approve_and_send()`: Approve and send response
- `reject_ticket()`: Reject for revision

**Features**:
- Edit response before sending
- Audit trail (who approved, when)
- Email notification integration

#### 3. Notification Service
**Purpose**: Email delivery

**Modes**:
- **Demo mode** (default): Console logging
- **SMTP mode**: Real email sending

**Safety**:
- Template validation
- Recipient verification
- Error logging

### ML Components

#### 1. Local Embedder
**Model**: BAAI/bge-m3 (1024-dim)

**Features**:
- Multilingual support (100+ languages)
- L2 normalization for cosine similarity
- Batch processing
- Embedding caching

**Why not Gemini?**
- Faster (no API calls)
- Free (no per-token cost)
- Deterministic
- Privacy-preserving

#### 2. Department Classifier
**Algorithm**: Logistic Regression (multinomial)

**Training**:
- Input: Local embeddings
- Labels: Queue names
- Features: 1024-dim vectors
- Optimization: LBFGS, max_iter=1000

**Inference**:
- Returns: Predicted queue + confidence
- Confidence: `max(softmax(logits))`

#### 3. Criticality Classifier
**Algorithm**: Logistic Regression (binary)

**Training**:
- Input: Local embeddings
- Labels: is_critical (0/1)
- Class balancing: Handle imbalanced data

**Inference**:
- Returns: Probability (0-1)
- Threshold: 0.5 (configurable)

#### 4. FAISS Retriever
**Index Type**: IndexFlatIP (cosine similarity)

**Process**:
1. Query embedding (same as training)
2. Search top-k (k=5)
3. Return: Similar tickets + scores

**RAG Context**:
- Similar ticket subjects
- Historical resolutions
- Department tags

### Gemini Integration

#### Response Generation
**Model**: gemini-2.0-flash-exp

**Prompt Engineering**:
```python
prompt = f"""
You are an IT support expert.

TICKET:
{subject}
{body}

SIMILAR PAST TICKETS:
{retrieved_context}

Generate a professional response in the SAME language.

OUTPUT (STRICT JSON):
{{
  "language": "en|de|...",
  "subject": "...",
  "body": "...",
  "confidence": 0.0-1.0,
  "needs_human_approval": true|false,
  "suggested_tags": [...]
}}
"""
```

**Safety**:
- JSON schema validation
- Retry logic (max 3)
- Fallback to human approval on error
- Business rule override

### Database Schema

#### Normalization
- **3NF** (Third Normal Form)
- No redundant data
- Foreign key relationships
- Indexed columns for fast queries

#### Key Tables
1. **Tickets**: Core ticket data
2. **Responses**: Draft and final responses
3. **Approvals**: Approval decisions
4. **AuditLogs**: Complete audit trail

#### Indexes
- ticket_id, status, is_critical, created_at
- Enables fast filtering and sorting

## Scalability Considerations

### Current Limitations (SQLite)
- Single-file database
- No concurrent writes
- Limited to ~1M records

### Production Migration Path

#### 1. PostgreSQL
```python
DATABASE_URL = "postgresql://user:pass@localhost/tickets"
```

#### 2. Redis Cache
```python
# Cache embeddings, predictions
redis_client = Redis(host='localhost', port=6379)
```

#### 3. Async Processing
```python
# Celery for background triage
@celery.task
def triage_ticket_async(ticket_id):
    ...
```

#### 4. Load Balancing
```
┌──────┐     ┌──────────┐
│ NGINX│────►│ FastAPI  │
│      │     │ Instance │
└──────┘     └──────────┘
    │        ┌──────────┐
    └───────►│ FastAPI  │
             │ Instance │
             └──────────┘
```

### Performance Metrics

#### Current Performance (Local)
- Embedding generation: ~50 tickets/sec
- ML prediction: ~1000 tickets/sec
- FAISS search: <10ms per query
- Gemini generation: ~2-5 sec per draft

#### Bottlenecks
1. **Gemini API**: Rate limits, latency
2. **Embedding model**: GPU recommended for large batches
3. **Database**: SQLite writes are sequential

#### Optimizations
- Batch processing for embeddings
- Async Gemini calls
- Redis caching
- Connection pooling

## Security Considerations

### Current Security
1. **API Key Management**: Environment variables
2. **Password Auth**: Simple password for demo
3. **Input Validation**: Pydantic schemas
4. **File Upload**: Size limits, type validation

### Production Security Checklist
- [ ] JWT authentication
- [ ] Role-based access control (RBAC)
- [ ] HTTPS/TLS
- [ ] Rate limiting
- [ ] SQL injection prevention (SQLAlchemy ORM ✓)
- [ ] XSS prevention (Streamlit sanitizes ✓)
- [ ] Secrets management (Vault, AWS Secrets Manager)
- [ ] Audit logging (implemented ✓)

## Testing Strategy

### Current Tests
- Component tests (`test_system.py`)
- Import verification
- Embedder functionality
- Database connectivity

### Recommended Additional Tests
1. **Unit Tests**: Each service method
2. **Integration Tests**: Full triage workflow
3. **API Tests**: All endpoints
4. **Load Tests**: Concurrent users
5. **ML Tests**: Model performance regression

### Example Test Structure
```python
def test_triage_workflow():
    # Create ticket
    ticket = create_ticket(...)
    
    # Run triage
    result = triage_service.triage_ticket(ticket.id)
    
    # Assert predictions
    assert result["predicted_queue"] in VALID_QUEUES
    assert 0 <= result["critical_prob"] <= 1
    
    # Assert draft generated
    assert result["draft_generated"] == True
```

## Deployment Options

### Option 1: Single Server (Current)
```
Server (4GB RAM, 2 CPU):
├── FastAPI backend
├── Streamlit apps (2)
└── SQLite database
```

### Option 2: Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
  
  customer_portal:
    build: ./customer_portal
    ports: ["8501:8501"]
  
  manager_dashboard:
    build: ./manager_dashboard
    ports: ["8502:8502"]
  
  postgres:
    image: postgres:15
    volumes: ["db_data:/var/lib/postgresql/data"]
```

### Option 3: Cloud Native (AWS)
```
┌─────────────────────────────────────────┐
│          CloudFront (CDN)               │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│     Application Load Balancer (ALB)     │
└────┬───────────────────┬─────────────────┘
     │                   │
┌────▼──────┐    ┌───────▼──────┐
│ ECS       │    │ ECS          │
│ Backend   │    │ Streamlit    │
│ (Fargate) │    │ (Fargate)    │
└───────────┘    └──────────────┘
     │
┌────▼──────────────┐
│ RDS PostgreSQL    │
└───────────────────┘
     │
┌────▼──────────────┐
│ S3 (attachments)  │
└───────────────────┘
```

## Monitoring & Observability

### Recommended Metrics
1. **System Metrics**
   - Request rate, latency, error rate
   - CPU, memory usage
   - Database query times

2. **Business Metrics**
   - Tickets per hour/day
   - Triage success rate
   - Approval rate (critical tickets)
   - Average response time

3. **ML Metrics**
   - Department classification accuracy (online)
   - Criticality prediction calibration
   - Retrieval relevance
   - Gemini confidence vs. human edit rate

### Logging Strategy
```python
# Structured logging
logger.info("ticket_triaged", extra={
    "ticket_id": ticket_id,
    "predicted_queue": queue,
    "critical_prob": prob,
    "duration_ms": elapsed
})
```

### Alerting Rules
- Gemini API errors > 5% → Alert
- Triage time > 30s → Alert
- Critical tickets pending > 24h → Alert
- Database errors → Immediate alert

## Future Architecture Evolution

### Phase 1: Current (Monolith)
- Single FastAPI backend
- SQLite database
- Local ML models
- Suitable for: <1000 tickets/day

### Phase 2: Microservices
- Separate services: Triage, Approval, Notification
- PostgreSQL
- Redis cache
- Suitable for: <10k tickets/day

### Phase 3: Event-Driven
- Message queue (RabbitMQ, Kafka)
- Async processing
- Service mesh
- Suitable for: 10k+ tickets/day

### Phase 4: Multi-Tenant SaaS
- Organization isolation
- White-label UI
- Usage-based billing
- Suitable for: Multiple customers

---

**Last Updated**: 2026-02-03  
**Version**: 1.0.0
