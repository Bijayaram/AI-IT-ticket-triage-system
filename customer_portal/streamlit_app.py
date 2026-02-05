"""
Customer Portal - Streamlit App #1
Submit tickets and view status.
"""
import streamlit as st
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="IT Support Portal",
    page_icon="🎫",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-weight: bold;
        display: inline-block;
    }
    .status-new { background-color: #e3f2fd; color: #1976d2; }
    .status-triaged { background-color: #f3e5f5; color: #7b1fa2; }
    .status-pending { background-color: #fff3e0; color: #f57c00; }
    .status-approved { background-color: #e8f5e9; color: #388e3c; }
    .status-sent { background-color: #c8e6c9; color: #2e7d32; }
    .status-rejected { background-color: #ffebee; color: #c62828; }
    </style>
""", unsafe_allow_html=True)


def format_status_badge(status: str) -> str:
    """Format status as HTML badge"""
    status_lower = status.lower()
    return f'<span class="status-badge status-{status_lower}">{status}</span>'


def main():
    """Main app"""
    st.markdown('<p class="main-header">🎫 IT Support Portal</p>', unsafe_allow_html=True)
    
    # Navigation
    tab1, tab2 = st.tabs(["📝 Submit Ticket", "📊 My Tickets"])
    
    with tab1:
        submit_ticket_page()
    
    with tab2:
        my_tickets_page()


def submit_ticket_page():
    """Submit new ticket page"""
    st.header("Submit New Support Ticket")
    st.write("Fill out the form below to submit your IT support request.")
    
    with st.form("ticket_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            submitter_name = st.text_input("Your Name *", placeholder="John Doe")
            submitter_email = st.text_input("Your Email *", placeholder="john.doe@company.com")
        
        with col2:
            subject = st.text_input("Subject *", placeholder="Brief description of the issue")
        
        body = st.text_area(
            "Description *",
            placeholder="Please provide detailed information about your issue...",
            height=200
        )
        
        attachment = st.file_uploader(
            "Attachment (optional)",
            type=['png', 'jpg', 'jpeg', 'pdf', 'txt', 'log'],
            help="Max 10MB"
        )
        
        submit_button = st.form_submit_button("🚀 Submit Ticket", use_container_width=True)
        
        if submit_button:
            # Validate
            if not submitter_name or not submitter_email or not subject or not body:
                st.error("⚠️ Please fill in all required fields (marked with *)")
                return
            
            # Submit ticket
            with st.spinner("Submitting ticket..."):
                try:
                    # Prepare form data
                    files = {}
                    if attachment:
                        files["attachment"] = (attachment.name, attachment.getvalue(), attachment.type)
                    
                    data = {
                        "subject": subject,
                        "body": body,
                        "submitter_name": submitter_name,
                        "submitter_email": submitter_email
                    }
                    
                    response = requests.post(
                        f"{BACKEND_URL}/tickets",
                        data=data,
                        files=files if files else None
                    )
                    
                    if response.status_code == 201:
                        ticket = response.json()
                        ticket_id = ticket["id"]
                        
                        st.success(f"✅ Ticket submitted successfully! Ticket ID: **{ticket_id}**")
                        
                        # Auto-triage
                        st.info("⚙️ Running automatic triage...")
                        triage_response = requests.post(
                            f"{BACKEND_URL}/tickets/{ticket_id}/triage",
                            json={"run_draft": True}
                        )
                        
                        if triage_response.status_code == 200:
                            triage_result = triage_response.json()
                            st.success(f"✅ Ticket triaged successfully!")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Department", triage_result["predicted_queue"])
                            with col2:
                                st.metric("Priority", "HIGH" if triage_result["is_critical"] else "NORMAL")
                            with col3:
                                status = "Pending Approval" if triage_result["needs_approval"] else "Processing"
                                st.metric("Status", status)
                            
                            if triage_result["needs_approval"]:
                                st.warning("⏳ Your ticket is marked as critical and requires manager approval before response is sent.")
                            else:
                                st.success("✅ A response has been drafted and will be sent shortly.")
                        
                        st.info(f"💡 Save your ticket ID: **{ticket_id}** to track status later.")
                        
                    else:
                        st.error(f"❌ Failed to submit ticket: {response.text}")
                
                except Exception as e:
                    st.error(f"❌ Error submitting ticket: {str(e)}")


def my_tickets_page():
    """View tickets by email"""
    st.header("Track Your Tickets")
    
    email = st.text_input(
        "Enter your email to view your tickets:",
        placeholder="john.doe@company.com"
    )
    
    if email:
        with st.spinner("Loading tickets..."):
            try:
                response = requests.get(
                    f"{BACKEND_URL}/tickets",
                    params={"submitter_email": email}
                )
                
                if response.status_code == 200:
                    tickets = response.json()
                    
                    if not tickets:
                        st.info(f"No tickets found for {email}")
                        return
                    
                    st.success(f"Found {len(tickets)} ticket(s)")
                    
                    # Display tickets
                    for ticket in tickets:
                        with st.expander(
                            f"🎫 Ticket #{ticket['id']}: {ticket['subject']} - {ticket['status']}",
                            expanded=False
                        ):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write("**Status:**")
                                st.markdown(format_status_badge(ticket['status']), unsafe_allow_html=True)
                            
                            with col2:
                                st.write("**Department:**")
                                st.write(ticket.get('predicted_queue', 'Not assigned'))
                            
                            with col3:
                                st.write("**Priority:**")
                                priority = "🔴 HIGH" if ticket.get('is_critical') else "🟢 NORMAL"
                                st.write(priority)
                            
                            st.write("**Created:**", datetime.fromisoformat(ticket['created_at'].replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M"))
                            
                            st.write("**Description:**")
                            st.write(ticket['body'])
                            
                            # Get detailed info
                            detail_response = requests.get(f"{BACKEND_URL}/tickets/{ticket['id']}")
                            if detail_response.status_code == 200:
                                detail = detail_response.json()
                                
                                # Show responses
                                if detail.get('responses'):
                                    st.write("**Responses:**")
                                    for response in detail['responses']:
                                        if response.get('final_body'):
                                            st.success("✅ Response sent:")
                                            st.write(response['final_body'])
                                        elif response.get('draft_body'):
                                            if response.get('needs_human_approval'):
                                                st.warning("⏳ Draft pending approval:")
                                            else:
                                                st.info("📝 Draft generated:")
                                            st.write(response['draft_body'])
                
                else:
                    st.error(f"Failed to load tickets: {response.text}")
            
            except Exception as e:
                st.error(f"Error loading tickets: {str(e)}")


if __name__ == "__main__":
    main()
