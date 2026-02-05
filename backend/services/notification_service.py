"""
Email notification service.
Default: console logging (demo mode).
Optional: SMTP sending via environment variables.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Email notification service with demo mode and optional SMTP.
    """
    
    def __init__(self):
        self.smtp_enabled = os.getenv("SMTP_ENABLED", "false").lower() == "true"
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from = os.getenv("SMTP_FROM", "noreply@itsupport.com")
        
        if self.smtp_enabled:
            logger.info("✓ Email notification: SMTP enabled")
        else:
            logger.info("✓ Email notification: Console demo mode")
    
    def send_response_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        body: str,
        ticket_id: int
    ) -> Dict[str, Any]:
        """
        Send response email to customer.
        
        Args:
            to_email: Recipient email
            to_name: Recipient name
            subject: Email subject
            body: Email body
            ticket_id: Ticket ID (for reference)
            
        Returns:
            Dictionary with send result
        """
        if self.smtp_enabled:
            return self._send_smtp(to_email, to_name, subject, body, ticket_id)
        else:
            return self._log_to_console(to_email, to_name, subject, body, ticket_id)
    
    def _send_smtp(self, to_email: str, to_name: str, subject: str, body: str, ticket_id: int) -> Dict[str, Any]:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_from
            msg['To'] = to_email
            msg['Subject'] = f"Re: {subject} [Ticket #{ticket_id}]"
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✓ Email sent via SMTP to {to_email}")
            return {"success": True}
            
        except Exception as e:
            logger.error(f"✗ SMTP send failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _log_to_console(self, to_email: str, to_name: str, subject: str, body: str, ticket_id: int) -> Dict[str, Any]:
        """Log email to console (demo mode)"""
        
        email_log = f"""
{'='*80}
EMAIL NOTIFICATION (DEMO MODE - NOT ACTUALLY SENT)
{'='*80}
To: {to_name} <{to_email}>
From: IT Support <{self.smtp_from}>
Subject: Re: {subject} [Ticket #{ticket_id}]

{body}
{'='*80}
"""
        print(email_log)
        logger.info(f"✓ Email logged to console for {to_email} (ticket #{ticket_id})")
        
        return {"success": True}


# Global service instance
_notification_service = None


def get_notification_service() -> NotificationService:
    """Get global notification service instance"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
