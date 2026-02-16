"""
Ticket triage service: orchestrates ML prediction, retrieval, and Gemini drafting.
"""
from sqlalchemy.orm import Session
from backend.models import Ticket, Response, TicketStatus, AuditLog
from backend.ml.predictors import get_predictor
from backend.ml.retrieval import get_retriever
from backend.gemini.generate_reply import get_generator
from datetime import datetime
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class TriageService:
    """
    Orchestrates the full triage workflow:
    1. ML prediction (department + criticality)
    2. Retrieval (find similar tickets)
    3. Gemini drafting (generate response)
    4. Apply business rules
    """
    
    def __init__(self):
        self.predictor = get_predictor()
        self.retriever = get_retriever()
        self.generator = get_generator()
    
    def triage_ticket(
        self,
        ticket_id: int,
        db: Session,
        run_draft: bool = True
    ) -> Dict[str, Any]:
        """
        Run full triage on a ticket.
        
        Args:
            ticket_id: Ticket ID
            db: Database session
            run_draft: Whether to generate draft reply (default: True)
            
        Returns:
            Dictionary with triage results
        """
        # Get ticket
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")
        
        logger.info(f"Starting triage for ticket {ticket_id}")
        
        # Step 1: ML Prediction
        try:
            prediction = self.predictor.predict_ticket(ticket.subject, ticket.body)
            
            # Update ticket with predictions
            ticket.predicted_queue = prediction["predicted_queue"]
            ticket.queue_confidence = prediction["queue_confidence"]
            ticket.critical_prob = prediction["critical_prob"]
            ticket.is_critical = prediction["is_critical"]
            ticket.status = TicketStatus.TRIAGED
            ticket.triaged_at = datetime.utcnow()
            
            # Log prediction
            self._log_action(db, ticket_id, "ML_PREDICTION", "system", {
                "queue": prediction["predicted_queue"],
                "confidence": prediction["queue_confidence"],
                "critical_prob": prediction["critical_prob"]
            })
            
            logger.info(f"  ✓ Predicted: {prediction['predicted_queue']} (conf={prediction['queue_confidence']:.2f}, crit={prediction['critical_prob']:.2f})")
            
        except Exception as e:
            logger.error(f"  ✗ Prediction failed: {e}")
            # Set safe defaults
            ticket.predicted_queue = "Technical Support"
            ticket.queue_confidence = 0.0
            ticket.critical_prob = 0.5
            ticket.is_critical = True  # Err on the side of caution
            ticket.status = TicketStatus.TRIAGED
        
        # Step 2: Retrieval (find similar tickets)
        similar_tickets = []
        try:
            similar_tickets = self.retriever.search_by_embedding(
                prediction["embedding"],
                k=5
            )
            logger.info(f"  ✓ Found {len(similar_tickets)} similar tickets")
        except Exception as e:
            logger.warning(f"  ! Retrieval failed: {e} (continuing without context)")
        
        # Step 3: Generate draft reply (if requested)
        draft_generated = False
        needs_approval = ticket.is_critical  # Default: critical needs approval
        
        if run_draft:
            try:
                draft_result = self.generator.generate_reply(
                    subject=ticket.subject,
                    body=ticket.body,
                    predicted_queue=ticket.predicted_queue,
                    is_critical=ticket.is_critical,
                    similar_tickets=similar_tickets
                )
                
                if draft_result.get("success", False):
                    # Create response record
                    response = Response(
                        ticket_id=ticket_id,
                        draft_language=draft_result.get("language"),
                        draft_subject=draft_result.get("subject"),
                        draft_body=draft_result.get("body"),
                        draft_confidence=draft_result.get("confidence"),
                        needs_human_approval=draft_result.get("needs_human_approval", True),
                        suggested_tags=json.dumps(draft_result.get("suggested_tags", [])),
                        retrieval_context=json.dumps([
                            {"subject": t["subject"], "answer": t["answer"][:200]}
                            for t in similar_tickets[:3]
                        ]) if similar_tickets else None
                    )
                    db.add(response)
                    
                    # Copy detected language to ticket for ML analysis display
                    ticket.predicted_language = draft_result.get("language")
                    
                    needs_approval = draft_result.get("needs_human_approval", True)
                    draft_generated = True
                    
                    # Update ticket status
                    if needs_approval:
                        ticket.status = TicketStatus.PENDING_APPROVAL
                    else:
                        ticket.status = TicketStatus.DRAFTED
                    
                    self._log_action(db, ticket_id, "DRAFT_GENERATED", "system", {
                        "confidence": draft_result.get("confidence"),
                        "needs_approval": needs_approval
                    })
                    
                    logger.info(f"  ✓ Draft generated (conf={draft_result.get('confidence', 0):.2f}, approval={needs_approval})")
                else:
                    logger.warning(f"  ! Draft generation failed: {draft_result.get('error')}")
                    # Route to human on failure
                    ticket.status = TicketStatus.PENDING_APPROVAL
                    needs_approval = True
                    
            except Exception as e:
                logger.error(f"  ✗ Draft generation error: {e}")
                ticket.status = TicketStatus.PENDING_APPROVAL
                needs_approval = True
        
        # Commit changes
        db.commit()
        db.refresh(ticket)
        
        logger.info(f"✓ Triage complete for ticket {ticket_id}")
        
        return {
            "success": True,
            "message": f"Ticket triaged successfully. Status: {ticket.status.value}",
            "ticket_id": ticket_id,
            "predicted_queue": ticket.predicted_queue,
            "queue_confidence": ticket.queue_confidence,
            "critical_prob": ticket.critical_prob,
            "is_critical": ticket.is_critical,
            "predicted_language": ticket.predicted_language,
            "draft_generated": draft_generated,
            "needs_approval": needs_approval,
            "status": ticket.status
        }
    
    def _log_action(self, db: Session, ticket_id: int, action: str, actor: str, details: Dict):
        """Log an action to audit log"""
        log = AuditLog(
            ticket_id=ticket_id,
            action=action,
            actor=actor,
            details=json.dumps(details)
        )
        db.add(log)


# Global service instance
_service = None


def get_triage_service() -> TriageService:
    """Get global triage service instance"""
    global _service
    if _service is None:
        _service = TriageService()
    return _service
