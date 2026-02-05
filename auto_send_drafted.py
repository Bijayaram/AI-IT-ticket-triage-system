"""
Auto-send all DRAFTED (non-critical) tickets
"""
import requests

BACKEND_URL = "http://localhost:8000"

def auto_send_drafted():
    print("\n" + "="*70)
    print("  AUTO-SENDING DRAFTED TICKETS")
    print("="*70)
    
    # Get all drafted tickets
    response = requests.get(f"{BACKEND_URL}/tickets", params={"status": "DRAFTED"})
    
    if response.status_code != 200:
        print("[ERROR] Failed to get tickets")
        return
    
    tickets = response.json()
    
    if not tickets:
        print("\n[INFO] No drafted tickets found")
        return
    
    print(f"\n[INFO] Found {len(tickets)} drafted tickets to send")
    
    for ticket in tickets:
        ticket_id = ticket["id"]
        subject = ticket["subject"]
        
        print(f"\n[*] Processing Ticket #{ticket_id}: {subject[:50]}...")
        
        # Approve and send
        approval_data = {
            "approver_name": "System Auto-Send",
            "approver_email": "system@company.com",
            "decision": "APPROVED",
            "decision_notes": "Auto-approved: Non-critical ticket"
        }
        
        approve_response = requests.post(
            f"{BACKEND_URL}/tickets/{ticket_id}/approve",
            json=approval_data
        )
        
        if approve_response.status_code == 200:
            print(f"    [OK] Ticket #{ticket_id} approved and sent")
        else:
            print(f"    [ERROR] Failed to send ticket #{ticket_id}")
            print(f"    {approve_response.text[:100]}")
    
    print("\n" + "="*70)
    print("  COMPLETE")
    print("="*70)

if __name__ == "__main__":
    try:
        auto_send_drafted()
    except Exception as e:
        print(f"\n[ERROR] {e}")
