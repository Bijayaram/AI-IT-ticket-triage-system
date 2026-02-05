"""
Approval workflow service for human-in-the-loop.
"""
from sqlalchemy.orm import Session
from backend.models import Ticket, Response, Approval, ApprovalDecision, TicketStatus, AuditLog
from backend.services.notification_service import get_notification_service
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class ApprovalService:
    """
    Manages approval workflow for critical tickets.
    """
    
    def __init__(self):
        self.notification_service = get_notification_service()
    
    def approve_and_send(
        self,
        ticket_id: int,
        approver_name: str,
        approver_email: str,
        db: Session,
        edited_subject: str = None,
        edited_body: str = None,
        decision_notes: str = None
    ) -> dict:
        """
        Approve a ticket and send the response.
        
        Args:
            ticket_id: Ticket ID
            approver_name: Name of approver
            approver_email: Email of approver
            db: Database session
            edited_subject: Edited subject (optional)
            edited_body: Edited body (optional)
            decision_notes: Approval notes (optional)
            
        Returns:
            Dictionary with approval result
        """
        # Get ticket and response
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")
        
        response = db.query(Response).filter(Response.ticket_id == ticket_id).first()
        if not response:
            raise ValueError(f"No response found for ticket {ticket_id}")
        
        logger.info(f"Approving ticket {ticket_id}")
        
        # Determine final content
        final_subject = edited_subject or response.draft_subject
        final_body = edited_body or response.draft_body
        
        # Update response
        response.final_subject = final_subject
        response.final_body = final_body
        response.approved_at = datetime.utcnow()
        
        # Create approval record
        decision = ApprovalDecision.EDITED_AND_APPROVED if (edited_subject or edited_body) else ApprovalDecision.APPROVED
        approval = Approval(
            ticket_id=ticket_id,
            approver_name=approver_name,
            approver_email=approver_email,
            decision=decision,
            decision_notes=decision_notes
        )
        db.add(approval)
        
        # Update ticket status
        ticket.status = TicketStatus.APPROVED
        
        # Log action
        self._log_action(db, ticket_id, "APPROVED", approver_email, {
            "decision": decision.value,
            "edited": bool(edited_subject or edited_body)
        })
        
        # Send email
        send_result = self.notification_service.send_response_email(
            to_email=ticket.submitter_email,
            to_name=ticket.submitter_name,
            subject=final_subject,
            body=final_body,
            ticket_id=ticket_id
        )
        
        if send_result["success"]:
            ticket.status = TicketStatus.SENT
            ticket.sent_at = datetime.utcnow()
            self._log_action(db, ticket_id, "EMAIL_SENT", "system", {
                "to": ticket.submitter_email
            })
            logger.info(f"  ✓ Email sent to {ticket.submitter_email}")
        else:
            logger.warning(f"  ! Email sending failed: {send_result.get('error')}")
        
        db.commit()
        db.refresh(ticket)
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "status": ticket.status,
            "email_sent": send_result["success"]
        }
    
    def reject_ticket(
        self,
        ticket_id: int,
        approver_name: str,
        approver_email: str,
        db: Session,
        decision_notes: str = None
    ) -> dict:
        """
        Reject a ticket (request more info or changes).
        
        Args:
            ticket_id: Ticket ID
            approver_name: Name of approver
            approver_email: Email of approver
            db: Database session
            decision_notes: Rejection reason
            
        Returns:
            Dictionary with rejection result
        """
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")
        
        logger.info(f"Rejecting ticket {ticket_id}")
        
        # Create approval record
        approval = Approval(
            ticket_id=ticket_id,
            approver_name=approver_name,
            approver_email=approver_email,
            decision=ApprovalDecision.REJECTED,
            decision_notes=decision_notes
        )
        db.add(approval)
        
        # Update ticket status
        ticket.status = TicketStatus.REJECTED
        
        # Log action
        self._log_action(db, ticket_id, "REJECTED", approver_email, {
            "reason": decision_notes
        })
        
        db.commit()
        db.refresh(ticket)
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "status": ticket.status
        }
    
    def _log_action(self, db: Session, ticket_id: int, action: str, actor: str, details: dict):
        """Log an action to audit log"""
        log = AuditLog(
            ticket_id=ticket_id,
            action=action,
            actor=actor,
            details=json.dumps(details)
        )
        db.add(log)


def get_approval_service() -> ApprovalService:
    """Get approval service instance"""
    return ApprovalService()
