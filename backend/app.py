"""
FastAPI backend for IT Ticket Triage System.
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import logging

from backend.db import get_db, init_db
from backend.models import Ticket, Response, Approval, TicketStatus, AuditLog
from backend.schemas import (
    TicketCreate, TicketResponse, TicketDetail,
    TriageRequest, TriageResponse,
    ApprovalCreate,
    DashboardSummary, TicketTimeSeriesPoint, PendingApprovalItem
)
from backend.services.triage_service import get_triage_service
from backend.services.approval_service import get_approval_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="IT Ticket Triage System API",
    description="AI-driven ticket triage with human-in-the-loop approval",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload directory
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    logger.info("✓ FastAPI backend started")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "IT Ticket Triage System API",
        "version": "1.0.0"
    }


# ============================================================================
# TICKET ENDPOINTS
# ============================================================================

@app.post("/tickets", response_model=TicketResponse, status_code=201)
async def create_ticket(
    subject: str = Form(...),
    body: str = Form(...),
    submitter_name: str = Form(...),
    submitter_email: str = Form(...),
    attachment: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Create a new ticket.
    Optionally upload an attachment.
    """
    # Handle attachment
    attachment_path = None
    if attachment:
        # Save file
        max_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
        if attachment.size and attachment.size > max_size_mb * 1024 * 1024:
            raise HTTPException(400, f"File too large (max {max_size_mb}MB)")
        
        filename = f"{datetime.utcnow().timestamp()}_{attachment.filename}"
        file_path = UPLOAD_DIR / filename
        with file_path.open("wb") as f:
            shutil.copyfileobj(attachment.file, f)
        attachment_path = str(file_path)
    
    # Create ticket
    ticket = Ticket(
        subject=subject,
        body=body,
        submitter_name=submitter_name,
        submitter_email=submitter_email,
        attachment_path=attachment_path,
        status=TicketStatus.NEW
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    
    logger.info(f"✓ Created ticket #{ticket.id}: {subject}")
    return ticket


@app.get("/tickets/{ticket_id}", response_model=TicketDetail)
async def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Get ticket details including responses and approvals"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(404, f"Ticket {ticket_id} not found")
    return ticket


@app.get("/tickets", response_model=List[TicketResponse])
async def list_tickets(
    status: Optional[TicketStatus] = None,
    queue: Optional[str] = None,
    is_critical: Optional[bool] = None,
    submitter_email: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List tickets with optional filters.
    """
    query = db.query(Ticket)
    
    # Apply filters
    if status:
        query = query.filter(Ticket.status == status)
    if queue:
        query = query.filter(Ticket.predicted_queue == queue)
    if is_critical is not None:
        query = query.filter(Ticket.is_critical == is_critical)
    if submitter_email:
        query = query.filter(Ticket.submitter_email == submitter_email)
    
    # Order by created_at desc
    query = query.order_by(desc(Ticket.created_at))
    
    tickets = query.offset(skip).limit(limit).all()
    return tickets


@app.post("/tickets/{ticket_id}/triage", response_model=TriageResponse)
async def triage_ticket(
    ticket_id: int,
    request: TriageRequest,
    db: Session = Depends(get_db)
):
    """
    Run triage on a ticket:
    1. ML prediction (department + criticality)
    2. Retrieval (similar tickets)
    3. Gemini draft generation (optional)
    """
    try:
        triage_service = get_triage_service()
        result = triage_service.triage_ticket(
            ticket_id=ticket_id,
            db=db,
            run_draft=request.run_draft
        )
        
        return TriageResponse(
            success=result["success"],
            message="Triage completed successfully",
            predicted_queue=result["predicted_queue"],
            queue_confidence=result["queue_confidence"],
            critical_prob=result["critical_prob"],
            is_critical=result["is_critical"],
            draft_generated=result["draft_generated"],
            needs_approval=result["needs_approval"]
        )
    except Exception as e:
        logger.error(f"Triage failed for ticket {ticket_id}: {e}")
        raise HTTPException(500, f"Triage failed: {str(e)}")


# ============================================================================
# APPROVAL ENDPOINTS
# ============================================================================

@app.get("/approvals/pending", response_model=List[PendingApprovalItem])
async def get_pending_approvals(db: Session = Depends(get_db)):
    """Get list of tickets pending approval"""
    tickets = db.query(Ticket).filter(
        Ticket.status == TicketStatus.PENDING_APPROVAL
    ).order_by(desc(Ticket.created_at)).all()
    
    results = []
    for ticket in tickets:
        response = db.query(Response).filter(Response.ticket_id == ticket.id).first()
        results.append(PendingApprovalItem(
            ticket_id=ticket.id,
            subject=ticket.subject,
            submitter_email=ticket.submitter_email,
            predicted_queue=ticket.predicted_queue or "Unknown",
            critical_prob=ticket.critical_prob or 0.0,
            created_at=ticket.created_at,
            draft_subject=response.draft_subject if response else None,
            draft_body=response.draft_body if response else None
        ))
    
    return results


@app.post("/tickets/{ticket_id}/approve")
async def approve_ticket(
    ticket_id: int,
    approval: ApprovalCreate,
    db: Session = Depends(get_db)
):
    """
    Approve a ticket and send response.
    Optionally edit the response before sending.
    """
    try:
        approval_service = get_approval_service()
        result = approval_service.approve_and_send(
            ticket_id=ticket_id,
            approver_name=approval.approver_name,
            approver_email=approval.approver_email,
            db=db,
            edited_subject=approval.edited_subject,
            edited_body=approval.edited_body,
            decision_notes=approval.decision_notes
        )
        return result
    except Exception as e:
        logger.error(f"Approval failed for ticket {ticket_id}: {e}")
        raise HTTPException(500, f"Approval failed: {str(e)}")


@app.post("/tickets/{ticket_id}/reject")
async def reject_ticket(
    ticket_id: int,
    approval: ApprovalCreate,
    db: Session = Depends(get_db)
):
    """
    Reject a ticket (request more info or changes).
    """
    try:
        approval_service = get_approval_service()
        result = approval_service.reject_ticket(
            ticket_id=ticket_id,
            approver_name=approval.approver_name,
            approver_email=approval.approver_email,
            db=db,
            decision_notes=approval.decision_notes
        )
        return result
    except Exception as e:
        logger.error(f"Rejection failed for ticket {ticket_id}: {e}")
        raise HTTPException(500, f"Rejection failed: {str(e)}")


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@app.get("/dashboard/summary", response_model=DashboardSummary)
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard KPI summary"""
    
    # Total tickets
    total_tickets = db.query(func.count(Ticket.id)).scalar()
    
    # Open tickets (not sent)
    open_tickets = db.query(func.count(Ticket.id)).filter(
        Ticket.status != TicketStatus.SENT
    ).scalar()
    
    # Critical count
    critical_count = db.query(func.count(Ticket.id)).filter(
        Ticket.is_critical == True
    ).scalar()
    
    # Pending approval count
    pending_approval_count = db.query(func.count(Ticket.id)).filter(
        Ticket.status == TicketStatus.PENDING_APPROVAL
    ).scalar()
    
    # Average response time (hours) for sent tickets
    sent_tickets = db.query(Ticket).filter(
        Ticket.sent_at.isnot(None),
        Ticket.created_at.isnot(None)
    ).all()
    
    if sent_tickets:
        response_times = [
            (t.sent_at - t.created_at).total_seconds() / 3600
            for t in sent_tickets
        ]
        avg_response_time = sum(response_times) / len(response_times)
    else:
        avg_response_time = None
    
    # Tickets by queue
    queue_counts = db.query(
        Ticket.predicted_queue,
        func.count(Ticket.id)
    ).filter(
        Ticket.predicted_queue.isnot(None)
    ).group_by(Ticket.predicted_queue).all()
    tickets_by_queue = {queue: count for queue, count in queue_counts}
    
    # Tickets by priority (using critical flag)
    tickets_by_priority = {
        "high": db.query(func.count(Ticket.id)).filter(Ticket.is_critical == True).scalar(),
        "medium": db.query(func.count(Ticket.id)).filter(Ticket.is_critical == False).scalar()
    }
    
    # Tickets by status
    status_counts = db.query(
        Ticket.status,
        func.count(Ticket.id)
    ).group_by(Ticket.status).all()
    tickets_by_status = {status.value: count for status, count in status_counts}
    
    return DashboardSummary(
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        critical_count=critical_count,
        pending_approval_count=pending_approval_count,
        avg_response_time_hours=avg_response_time,
        tickets_by_queue=tickets_by_queue,
        tickets_by_priority=tickets_by_priority,
        tickets_by_status=tickets_by_status
    )


@app.get("/dashboard/timeseries", response_model=List[TicketTimeSeriesPoint])
async def get_ticket_timeseries(days: int = 30, db: Session = Depends(get_db)):
    """Get ticket counts over time"""
    
    # Get tickets from last N days
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    tickets = db.query(Ticket).filter(
        Ticket.created_at >= cutoff_date
    ).all()
    
    # Group by date
    date_counts = {}
    for ticket in tickets:
        date_str = ticket.created_at.strftime("%Y-%m-%d")
        if date_str not in date_counts:
            date_counts[date_str] = {"total": 0, "critical": 0}
        date_counts[date_str]["total"] += 1
        if ticket.is_critical:
            date_counts[date_str]["critical"] += 1
    
    # Convert to list
    results = [
        TicketTimeSeriesPoint(
            date=date_str,
            count=counts["total"],
            critical_count=counts["critical"]
        )
        for date_str, counts in sorted(date_counts.items())
    ]
    
    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
