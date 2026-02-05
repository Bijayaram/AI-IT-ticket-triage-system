"""
Comprehensive Test Script for IT Ticket Triage System
Tests multiple scenarios end-to-end
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def test_case_1_non_critical_password_reset():
    """Test Case 1: Non-Critical Password Reset Ticket"""
    print_section("TEST 1: Non-Critical Password Reset")
    
    ticket_data = {
        "subject": "Cannot access my email account",
        "body": "Hi, I forgot my password for my company email. Can you help me reset it? My username is john.doe@company.com",
        "submitter_name": "John Doe",
        "submitter_email": "john.doe@company.com"
    }
    
    # Create ticket
    response = requests.post(f"{BASE_URL}/tickets", data=ticket_data)
    if response.status_code == 200:
        ticket = response.json()
        print(f"[OK] Ticket created: #{ticket['id']}")
        print(f"    Subject: {ticket['subject']}")
        print(f"    Status: {ticket['status']}")
        return ticket['id']
    else:
        print(f"[ERROR] Failed to create ticket: {response.status_code}")
        print(response.text)
        return None

def test_case_2_critical_server_down():
    """Test Case 2: Critical Server Outage"""
    print_section("TEST 2: Critical Production Server Down")
    
    ticket_data = {
        "subject": "URGENT: Production database server offline",
        "body": "Our main production database server (PROD-DB-01) is completely offline. All customer transactions are failing. This started 10 minutes ago. ERROR: Connection timeout. Need immediate assistance!",
        "submitter_name": "Sarah Manager",
        "submitter_email": "sarah.manager@company.com"
    }
    
    response = requests.post(f"{BASE_URL}/tickets", data=ticket_data)
    if response.status_code == 200:
        ticket = response.json()
        print(f"[OK] Ticket created: #{ticket['id']}")
        print(f"    Subject: {ticket['subject']}")
        print(f"    Status: {ticket['status']}")
        return ticket['id']
    else:
        print(f"[ERROR] Failed to create ticket: {response.status_code}")
        return None

def test_case_3_billing_question():
    """Test Case 3: Billing Question"""
    print_section("TEST 3: Billing Inquiry")
    
    ticket_data = {
        "subject": "Question about my last invoice",
        "body": "I received an invoice for $500 but I expected it to be $450. Can you explain the difference? Invoice #12345",
        "submitter_name": "Mike Customer",
        "submitter_email": "mike.customer@company.com"
    }
    
    response = requests.post(f"{BASE_URL}/tickets", data=ticket_data)
    if response.status_code == 200:
        ticket = response.json()
        print(f"[OK] Ticket created: #{ticket['id']}")
        print(f"    Subject: {ticket['subject']}")
        print(f"    Status: {ticket['status']}")
        return ticket['id']
    else:
        print(f"[ERROR] Failed to create ticket: {response.status_code}")
        return None

def test_case_4_software_bug():
    """Test Case 4: Software Bug Report"""
    print_section("TEST 4: Software Bug")
    
    ticket_data = {
        "subject": "Application crashes when uploading files",
        "body": "When I try to upload a PDF file larger than 5MB in the portal, the application crashes with error 500. This happens consistently. Using Chrome browser on Windows 10.",
        "submitter_name": "Lisa Developer",
        "submitter_email": "lisa.dev@company.com"
    }
    
    response = requests.post(f"{BASE_URL}/tickets", data=ticket_data)
    if response.status_code == 200:
        ticket = response.json()
        print(f"[OK] Ticket created: #{ticket['id']}")
        print(f"    Subject: {ticket['subject']}")
        print(f"    Status: {ticket['status']}")
        return ticket['id']
    else:
        print(f"[ERROR] Failed to create ticket: {response.status_code}")
        return None

def test_case_5_network_issue():
    """Test Case 5: Network Connectivity"""
    print_section("TEST 5: Network Issue")
    
    ticket_data = {
        "subject": "Cannot connect to company VPN from home",
        "body": "I'm trying to connect to the company VPN from my home office but getting error 403. I've tried restarting my computer and router. Need this fixed ASAP as I need to access internal systems.",
        "submitter_name": "Tom Remote",
        "submitter_email": "tom.remote@company.com"
    }
    
    response = requests.post(f"{BASE_URL}/tickets", data=ticket_data)
    if response.status_code == 200:
        ticket = response.json()
        print(f"[OK] Ticket created: #{ticket['id']}")
        print(f"    Subject: {ticket['subject']}")
        print(f"    Status: {ticket['status']}")
        return ticket['id']
    else:
        print(f"[ERROR] Failed to create ticket: {response.status_code}")
        return None

def triage_ticket(ticket_id):
    """Trigger triage for a ticket"""
    print(f"\n  [*] Triggering triage for ticket #{ticket_id}...")
    try:
        response = requests.post(f"{BASE_URL}/tickets/{ticket_id}/triage", json={})
        if response.status_code == 200:
            result = response.json()
            print(f"  [OK] Triage completed")
            print(f"      Department: {result.get('predicted_queue', 'N/A')}")
            print(f"      Critical: {result.get('is_critical', False)} ({result.get('critical_prob', 0)*100:.1f}%)")
            print(f"      Draft Generated: {result.get('draft_generated', False)}")
            print(f"      Needs Approval: {result.get('needs_approval', False)}")
            return result
        else:
            print(f"  [ERROR] Triage failed: {response.status_code}")
            print(f"  {response.text[:200]}")
            return None
    except Exception as e:
        print(f"  [ERROR] Triage error: {e}")
        return None

def get_ticket_details(ticket_id):
    """Get ticket details"""
    try:
        response = requests.get(f"{BASE_URL}/tickets/{ticket_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_dashboard_summary():
    """Get dashboard summary"""
    print_section("DASHBOARD SUMMARY")
    try:
        response = requests.get(f"{BASE_URL}/dashboard/summary")
        if response.status_code == 200:
            summary = response.json()
            print(f"  Total Tickets: {summary.get('total_tickets', 0)}")
            print(f"  Open Tickets: {summary.get('open_tickets', 0)}")
            print(f"  Critical Count: {summary.get('critical_count', 0)}")
            print(f"  Avg Response Time: {summary.get('avg_response_time_hours', 0):.2f} hours")
            
            print(f"\n  By Department:")
            for dept, count in summary.get('by_queue', {}).items():
                print(f"    - {dept}: {count}")
            
            print(f"\n  By Priority:")
            for priority, count in summary.get('by_priority', {}).items():
                print(f"    - {priority}: {count}")
            
            return summary
        else:
            print(f"  [ERROR] Failed to get summary: {response.status_code}")
            return None
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None

def get_pending_approvals():
    """Get pending approvals"""
    print_section("PENDING APPROVALS")
    try:
        response = requests.get(f"{BASE_URL}/approvals/pending")
        if response.status_code == 200:
            approvals = response.json()
            if approvals:
                print(f"  Found {len(approvals)} pending approvals:")
                for item in approvals:
                    print(f"\n  Ticket #{item.get('ticket_id')}")
                    print(f"    Subject: {item.get('ticket_subject', 'N/A')[:50]}...")
                    print(f"    Priority: {item.get('priority', 'N/A')}")
                    print(f"    Department: {item.get('predicted_queue', 'N/A')}")
                    print(f"    Critical Prob: {item.get('critical_prob', 0)*100:.1f}%")
            else:
                print("  No pending approvals")
            return approvals
        else:
            print(f"  [ERROR] Failed to get approvals: {response.status_code}")
            return []
    except Exception as e:
        print(f"  [ERROR] {e}")
        return []

def main():
    """Run all test cases"""
    print("\n" + "="*70)
    print("  IT TICKET TRIAGE SYSTEM - COMPREHENSIVE TEST SUITE")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*70)
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print("\n[OK] Backend is running")
    except:
        print("\n[ERROR] Backend is not running!")
        print("Please start backend first: cd D:\\Capstone && start_backend.bat")
        return
    
    ticket_ids = []
    
    # Create test tickets
    print("\n" + "="*70)
    print("  PHASE 1: Creating Test Tickets")
    print("="*70)
    
    tid1 = test_case_1_non_critical_password_reset()
    if tid1: ticket_ids.append(tid1)
    time.sleep(1)
    
    tid2 = test_case_2_critical_server_down()
    if tid2: ticket_ids.append(tid2)
    time.sleep(1)
    
    tid3 = test_case_3_billing_question()
    if tid3: ticket_ids.append(tid3)
    time.sleep(1)
    
    tid4 = test_case_4_software_bug()
    if tid4: ticket_ids.append(tid4)
    time.sleep(1)
    
    tid5 = test_case_5_network_issue()
    if tid5: ticket_ids.append(tid5)
    
    # Triage all tickets
    print("\n" + "="*70)
    print("  PHASE 2: Running Triage (ML + Gemini)")
    print("="*70)
    
    for ticket_id in ticket_ids:
        triage_ticket(ticket_id)
        time.sleep(2)
    
    # Get pending approvals
    time.sleep(1)
    pending = get_pending_approvals()
    
    # Get dashboard summary
    time.sleep(1)
    summary = get_dashboard_summary()
    
    # Summary
    print("\n" + "="*70)
    print("  TEST RESULTS SUMMARY")
    print("="*70)
    print(f"  Total tickets created: {len(ticket_ids)}")
    print(f"  Tickets pending approval: {len(pending)}")
    print(f"\n  Next steps:")
    print(f"  1. Open Manager Dashboard: http://localhost:8502")
    print(f"  2. Login with password: admin123")
    print(f"  3. Go to 'Pending Critical Approvals' tab")
    print(f"  4. Review and approve critical tickets")
    print("\n  Next steps:")
    print(f"  1. Open Customer Portal: http://localhost:8501")
    print(f"  2. Use 'Track Ticket Status' to check ticket #1, #2, etc.")
    print(f"  3. View responses and status updates")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[*] Test interrupted by user")
    except Exception as e:
        print(f"\n\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
