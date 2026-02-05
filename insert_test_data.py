"""
Insert Test Data with Draft Responses Directly into Database
Bypasses Gemini - useful for testing approval workflow
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from backend.db import SessionLocal, init_db
from backend.models import Ticket, Response, TicketStatus
from datetime import datetime
import json

def insert_test_tickets():
    """Insert test tickets with draft responses"""
    print("\n" + "="*70)
    print("  INSERTING TEST DATA WITH DRAFT RESPONSES")
    print("="*70)
    
    # Initialize database
    init_db()
    db = SessionLocal()
    
    try:
        # Test Case 1: Critical Ticket - Server Down
        print("\n[1/5] Creating critical ticket - Production server down...")
        ticket1 = Ticket(
            subject="CRITICAL: Production server offline",
            body="Our main production server (PROD-01) crashed at 10:30 AM. All services are down. Customers cannot access the platform. Need immediate help!",
            submitter_name="Alice Manager",
            submitter_email="alice.manager@company.com",
            predicted_queue="Technical Support",
            queue_confidence=0.95,
            critical_prob=0.98,
            is_critical=True,
            predicted_language="en",
            status=TicketStatus.PENDING_APPROVAL,
            triaged_at=datetime.now()
        )
        db.add(ticket1)
        db.flush()
        
        response1 = Response(
            ticket_id=ticket1.id,
            draft_language="en",
            draft_subject="RE: CRITICAL: Production server offline [PRIORITY 1]",
            draft_body="""Hello Alice,

We understand the critical nature of this issue and have escalated it to our senior engineering team immediately.

**Immediate Actions Taken:**
1. Senior engineer John Smith has been notified (on-call)
2. Server health monitoring activated
3. Backup systems are being prepared
4. Incident #INC-2024-001 created

**Next Steps:**
1. Our senior engineer will contact you at alice.manager@company.com within 10 minutes
2. Emergency hotline: +1-555-0123 (available 24/7)
3. We will provide updates every 15 minutes until resolved

**Important:**
- Do NOT restart the server manually
- Preserve all system logs
- Document any changes made before the crash

We are treating this as Priority 1 and dedicating all resources to resolve this immediately.

Best regards,
Technical Support Team
Emergency Response Unit""",
            draft_confidence=0.95,
            needs_human_approval=True,
            suggested_tags=json.dumps(["critical", "production", "server-down", "priority-1"]),
            retrieval_context=json.dumps([
                {"subject": "Database server crashed", "answer": "Restarted services, checked logs..."},
                {"subject": "Production outage", "answer": "Identified network issue..."}
            ])
        )
        db.add(response1)
        print(f"    [OK] Ticket #{ticket1.id} created with draft response")
        
        # Test Case 2: Critical - Security Breach
        print("\n[2/5] Creating critical ticket - Security concern...")
        ticket2 = Ticket(
            subject="URGENT: Suspicious login attempts detected",
            body="I received 50+ failed login alerts for my admin account in the last hour. The attempts are coming from an IP address in a different country. My account may be compromised!",
            submitter_name="Bob Admin",
            submitter_email="bob.admin@company.com",
            predicted_queue="IT Support",
            queue_confidence=0.88,
            critical_prob=0.92,
            is_critical=True,
            predicted_language="en",
            status=TicketStatus.PENDING_APPROVAL,
            triaged_at=datetime.now()
        )
        db.add(ticket2)
        db.flush()
        
        response2 = Response(
            ticket_id=ticket2.id,
            draft_language="en",
            draft_subject="RE: URGENT: Suspicious login attempts detected [SECURITY ALERT]",
            draft_body="""Hello Bob,

Thank you for reporting this security concern immediately. We take security threats very seriously.

**Immediate Actions We've Taken:**
1. Your account has been temporarily locked for protection
2. The suspicious IP address has been blocked
3. Security team has been alerted
4. All your recent account activity is being reviewed

**Required Actions from You:**
1. Change your password immediately using the password reset link sent to your registered email
2. Enable two-factor authentication (2FA) on your account
3. Review your recent account activity for any unauthorized changes
4. Check if any other accounts use the same password and change them

**Security Team Contact:**
- Email: security@company.com
- Phone: +1-555-0199 (24/7 Security Hotline)

We will monitor your account for the next 72 hours and send you a detailed security report within 24 hours.

Best regards,
IT Security Team""",
            draft_confidence=0.92,
            needs_human_approval=True,
            suggested_tags=json.dumps(["security", "critical", "breach", "admin-account"]),
            retrieval_context=json.dumps([
                {"subject": "Account hacked", "answer": "Reset password, enabled 2FA..."},
                {"subject": "Brute force attack", "answer": "Blocked IP, security audit..."}
            ])
        )
        db.add(response2)
        print(f"    [OK] Ticket #{ticket2.id} created with draft response")
        
        # Test Case 3: Non-Critical - Password Reset
        print("\n[3/5] Creating non-critical ticket - Password reset...")
        ticket3 = Ticket(
            subject="Forgot my email password",
            body="Hi, I forgot my password for my company email (charlie@company.com). Can you help me reset it?",
            submitter_name="Charlie User",
            submitter_email="charlie@company.com",
            predicted_queue="IT Support",
            queue_confidence=0.92,
            critical_prob=0.15,
            is_critical=False,
            predicted_language="en",
            status=TicketStatus.DRAFTED,
            triaged_at=datetime.now()
        )
        db.add(ticket3)
        db.flush()
        
        response3 = Response(
            ticket_id=ticket3.id,
            draft_language="en",
            draft_subject="RE: Forgot my email password",
            draft_body="""Hello Charlie,

I can help you reset your email password. Please follow these steps:

1. Visit the password reset page: https://portal.company.com/reset
2. Enter your email: charlie@company.com
3. Click "Send Reset Link"
4. Check your personal email (the one registered during onboarding) for the reset link
5. Follow the instructions in the email to create a new password

**Password Requirements:**
- Minimum 12 characters
- Include uppercase and lowercase letters
- Include at least one number and one special character
- Cannot be same as previous 5 passwords

If you don't receive the reset email within 10 minutes, please check your spam folder or reply to this ticket.

Best regards,
IT Support Team""",
            draft_confidence=0.94,
            needs_human_approval=False,
            suggested_tags=json.dumps(["password-reset", "email", "routine"]),
            retrieval_context=json.dumps([
                {"subject": "Password reset request", "answer": "Sent reset link, advised on requirements..."},
                {"subject": "Cannot access email", "answer": "Password reset successful..."}
            ])
        )
        db.add(response3)
        print(f"    [OK] Ticket #{ticket3.id} created with draft response (auto-sendable)")
        
        # Test Case 4: Non-Critical - Billing Question
        print("\n[4/5] Creating non-critical ticket - Billing inquiry...")
        ticket4 = Ticket(
            subject="Question about invoice charges",
            body="I received invoice #INV-12345 for $500 but expected $450. Can you explain the $50 difference?",
            submitter_name="Diana Customer",
            submitter_email="diana@customer.com",
            predicted_queue="Billing and Payments",
            queue_confidence=0.96,
            critical_prob=0.10,
            is_critical=False,
            predicted_language="en",
            status=TicketStatus.DRAFTED,
            triaged_at=datetime.now()
        )
        db.add(ticket4)
        db.flush()
        
        response4 = Response(
            ticket_id=ticket4.id,
            draft_language="en",
            draft_subject="RE: Question about invoice charges - Invoice #INV-12345",
            draft_body="""Hello Diana,

Thank you for reaching out regarding invoice #INV-12345.

I've reviewed your account and invoice. The $50 difference is due to:

**Invoice Breakdown:**
- Base subscription: $450.00
- Additional user license (added on Jan 15): $50.00
- **Total: $500.00**

The additional user license was added to your account on January 15th when you added a new team member. This is prorated for the remainder of the billing cycle.

**Your invoice #INV-12345 includes:**
- Period: January 1 - January 31, 2026
- Base plan: Professional ($450/month)
- Additional user (from Jan 15): $50 (half month pro-rated)

If you have any questions about these charges or would like to review your subscription details, please let me know.

Best regards,
Billing Support Team""",
            draft_confidence=0.91,
            needs_human_approval=False,
            suggested_tags=json.dumps(["billing", "invoice", "charges"]),
            retrieval_context=json.dumps([
                {"subject": "Billing discrepancy", "answer": "Explained pro-rated charges..."},
                {"subject": "Invoice question", "answer": "Provided breakdown..."}
            ])
        )
        db.add(response4)
        print(f"    [OK] Ticket #{ticket4.id} created with draft response (auto-sendable)")
        
        # Test Case 5: Medium Priority - VPN Issue
        print("\n[5/5] Creating medium priority ticket - VPN connection...")
        ticket5 = Ticket(
            subject="Cannot connect to VPN from home",
            body="I'm trying to connect to company VPN but getting error 403. Tried restarting my computer. Need to access internal systems for important meeting in 2 hours!",
            submitter_name="Eve Remote",
            submitter_email="eve.remote@company.com",
            predicted_queue="Technical Support",
            queue_confidence=0.87,
            critical_prob=0.45,
            is_critical=False,
            predicted_language="en",
            status=TicketStatus.DRAFTED,
            triaged_at=datetime.now()
        )
        db.add(ticket5)
        db.flush()
        
        response5 = Response(
            ticket_id=ticket5.id,
            draft_language="en",
            draft_subject="RE: Cannot connect to VPN from home - Error 403",
            draft_body="""Hello Eve,

I can help you resolve the VPN connection issue. Error 403 typically indicates an authentication problem.

**Please try these solutions in order:**

1. **Clear VPN credentials:**
   - Open VPN client
   - Go to Settings > Remove saved credentials
   - Restart VPN client
   - Try connecting again with your current password

2. **Check VPN client version:**
   - Ensure you're using the latest version (v5.2.1)
   - Download from: https://vpn.company.com/download

3. **Verify your VPN account status:**
   - Go to: https://portal.company.com/vpn-status
   - Login to check if your VPN account is active

4. **Reset your VPN password:**
   - Visit: https://portal.company.com/vpn-reset
   - You'll receive a new temporary password via email

If none of these steps work, please call our VPN support hotline at +1-555-0155 (available 8 AM - 8 PM) and mention ticket #TKT-{ticket5.id}.

We understand you have an important meeting in 2 hours, so we've marked this as medium priority for faster response.

Best regards,
Technical Support Team""",
            draft_confidence=0.89,
            needs_human_approval=False,
            suggested_tags=json.dumps(["vpn", "connection", "error-403", "remote-access"]),
            retrieval_context=json.dumps([
                {"subject": "VPN connection failed", "answer": "Cleared credentials, updated client..."},
                {"subject": "VPN error 403", "answer": "Reset VPN password, successful connection..."}
            ])
        )
        db.add(response5)
        print(f"    [OK] Ticket #{ticket5.id} created with draft response (auto-sendable)")
        
        # Commit all changes
        db.commit()
        
        print("\n" + "="*70)
        print("  SUCCESS! Test data inserted")
        print("="*70)
        print(f"\n  Tickets Created:")
        print(f"    - 2 Critical tickets (pending approval)")
        print(f"    - 3 Non-critical tickets (can be auto-sent)")
        print(f"\n  Next Steps:")
        print(f"    1. Open Manager Dashboard: http://localhost:8502")
        print(f"    2. Login: admin123")
        print(f"    3. Go to 'Pending Critical Approvals' tab")
        print(f"    4. You should see 2 tickets waiting for approval")
        print(f"    5. Click on each ticket to review the AI-generated draft")
        print(f"    6. Approve, edit, or reject the responses")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to insert test data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    insert_test_tickets()
