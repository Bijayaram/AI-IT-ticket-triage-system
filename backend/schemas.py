"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from backend.models import TicketStatus, ApprovalDecision


# Ticket Schemas
class TicketCreate(BaseModel):
    """Create ticket request"""
    subject: str = Field(..., min_length=3, max_length=500)
    body: str = Field(..., min_length=10)
    submitter_name: str = Field(..., min_length=2, max_length=200)
    submitter_email: EmailStr
    attachment_filename: Optional[str] = None


class TicketResponse(BaseModel):
    """Ticket response"""
    id: int
    subject: str
    body: str
    submitter_name: str
    submitter_email: str
    attachment_path: Optional[str]
    predicted_queue: Optional[str]
    queue_confidence: Optional[float]
    critical_prob: Optional[float]
    is_critical: bool
    predicted_language: Optional[str]
    status: TicketStatus
    created_at: datetime
    updated_at: datetime
    triaged_at: Optional[datetime]
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True


class TicketDetail(TicketResponse):
    """Ticket with responses and approvals"""
    responses: List["ResponseDetail"] = []
    approvals: List["ApprovalDetail"] = []

    class Config:
        from_attributes = True


# Response Schemas
class ResponseDetail(BaseModel):
    """Response detail"""
    id: int
    ticket_id: int
    draft_language: Optional[str]
    draft_subject: Optional[str]
    draft_body: Optional[str]
    draft_confidence: Optional[float]
    needs_human_approval: bool
    suggested_tags: Optional[str]
    retrieval_context: Optional[str]
    final_subject: Optional[str]
    final_body: Optional[str]
    created_at: datetime
    approved_at: Optional[datetime]

    class Config:
        from_attributes = True


# Approval Schemas
class ApprovalCreate(BaseModel):
    """Create approval request"""
    approver_name: str = Field(..., min_length=2, max_length=200)
    approver_email: EmailStr
    decision: ApprovalDecision
    decision_notes: Optional[str] = None
    edited_subject: Optional[str] = None
    edited_body: Optional[str] = None


class ApprovalDetail(BaseModel):
    """Approval detail"""
    id: int
    ticket_id: int
    approver_name: str
    approver_email: str
    decision: ApprovalDecision
    decision_notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard Schemas
class DashboardSummary(BaseModel):
    """Dashboard KPI summary"""
    total_tickets: int
    open_tickets: int
    critical_count: int
    pending_approval_count: int
    avg_response_time_hours: Optional[float]
    tickets_by_queue: dict
    tickets_by_priority: dict
    tickets_by_status: dict


class TicketTimeSeriesPoint(BaseModel):
    """Time series data point"""
    date: str
    count: int
    critical_count: int


class PendingApprovalItem(BaseModel):
    """Pending approval list item"""
    ticket_id: int
    subject: str
    submitter_email: str
    predicted_queue: str
    critical_prob: float
    created_at: datetime
    draft_subject: Optional[str]
    draft_body: Optional[str]


# Triage Schemas
class TriageRequest(BaseModel):
    """Triage request"""
    run_draft: bool = True


class TriageResponse(BaseModel):
    """Triage response"""
    success: bool
    message: str
    predicted_queue: str
    queue_confidence: float
    critical_prob: float
    is_critical: bool
    predicted_language: Optional[str] = None
    draft_generated: bool
    needs_approval: bool
