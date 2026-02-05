"""
Database models for IT Ticket Triage System.
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class TicketStatus(str, enum.Enum):
    """Ticket status enum"""
    NEW = "NEW"
    TRIAGED = "TRIAGED"
    DRAFTED = "DRAFTED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    SENT = "SENT"
    REJECTED = "REJECTED"
    NEEDS_INFO = "NEEDS_INFO"


class ApprovalDecision(str, enum.Enum):
    """Approval decision enum"""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EDITED_AND_APPROVED = "EDITED_AND_APPROVED"


class Ticket(Base):
    """Ticket model"""
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    
    # Ticket content
    subject = Column(String(500), nullable=False, index=True)
    body = Column(Text, nullable=False)
    submitter_name = Column(String(200), nullable=False)
    submitter_email = Column(String(200), nullable=False, index=True)
    attachment_path = Column(String(500), nullable=True)
    
    # ML predictions
    predicted_queue = Column(String(100), nullable=True, index=True)
    queue_confidence = Column(Float, nullable=True)
    critical_prob = Column(Float, nullable=True, index=True)
    is_critical = Column(Boolean, default=False, index=True)
    predicted_language = Column(String(10), nullable=True)
    
    # Status and metadata
    status = Column(Enum(TicketStatus), default=TicketStatus.NEW, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    triaged_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    
    # Relationships
    responses = relationship("Response", back_populates="ticket", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="ticket", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="ticket", cascade="all, delete-orphan")


class Response(Base):
    """Response draft and final content"""
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, index=True)
    
    # Gemini-generated draft (JSON)
    draft_language = Column(String(10), nullable=True)
    draft_subject = Column(String(500), nullable=True)
    draft_body = Column(Text, nullable=True)
    draft_confidence = Column(Float, nullable=True)
    needs_human_approval = Column(Boolean, default=False)
    suggested_tags = Column(Text, nullable=True)  # JSON array as text
    
    # Retrieval context (similar tickets used)
    retrieval_context = Column(Text, nullable=True)  # JSON array as text
    
    # Final approved response
    final_subject = Column(String(500), nullable=True)
    final_body = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="responses")


class Approval(Base):
    """Approval workflow tracking"""
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, index=True)
    
    # Approver info
    approver_name = Column(String(200), nullable=False)
    approver_email = Column(String(200), nullable=False)
    
    # Decision
    decision = Column(Enum(ApprovalDecision), nullable=False)
    decision_notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="approvals")


class AuditLog(Base):
    """Audit log for all ticket actions"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=True, index=True)
    
    # Action details
    action = Column(String(100), nullable=False, index=True)
    actor = Column(String(200), nullable=True)
    details = Column(Text, nullable=True)  # JSON as text
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="audit_logs")
