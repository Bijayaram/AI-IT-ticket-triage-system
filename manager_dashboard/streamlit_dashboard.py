"""
Manager Dashboard - Streamlit App #2
Monitor tickets, approve critical responses, view analytics.
"""
import streamlit as st
import requests
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
MANAGER_PASSWORD = os.getenv("MANAGER_PASSWORD", "admin123")

# Page config
st.set_page_config(
    page_title="IT Manager Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #d32f2f;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .approval-card {
        border: 2px solid #ff9800;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        background-color: #fff3e0;
    }
    </style>
""", unsafe_allow_html=True)


def check_authentication():
    """Simple password authentication"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown('<p class="main-header">🔐 Manager Dashboard Login</p>', unsafe_allow_html=True)
        
        password = st.text_input("Enter manager password:", type="password")
        
        if st.button("Login"):
            if password == MANAGER_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Invalid password")
        
        st.stop()


def main():
    """Main dashboard"""
    check_authentication()
    
    st.markdown('<p class="main-header">📊 IT Manager Dashboard</p>', unsafe_allow_html=True)
    
    # Logout button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Overview",
        "⏳ Pending Approvals",
        "🎫 All Tickets",
        "📊 Analytics"
    ])
    
    with tab1:
        overview_page()
    
    with tab2:
        approvals_page()
    
    with tab3:
        all_tickets_page()
    
    with tab4:
        analytics_page()


def overview_page():
    """Overview dashboard with KPIs"""
    st.header("Dashboard Overview")
    
    try:
        response = requests.get(f"{BACKEND_URL}/dashboard/summary")
        if response.status_code == 200:
            summary = response.json()
            
            # KPI Metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Tickets", summary["total_tickets"])
            
            with col2:
                st.metric("Open Tickets", summary["open_tickets"])
            
            with col3:
                st.metric("Critical Tickets", summary["critical_count"], delta="High Priority")
            
            with col4:
                st.metric(
                    "Pending Approval",
                    summary["pending_approval_count"],
                    delta="Requires Action" if summary["pending_approval_count"] > 0 else None
                )
            
            with col5:
                avg_time = summary.get("avg_response_time_hours")
                if avg_time:
                    st.metric("Avg Response Time", f"{avg_time:.1f}h")
                else:
                    st.metric("Avg Response Time", "N/A")
            
            # Charts
            st.subheader("Ticket Distribution")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Tickets by department
                if summary["tickets_by_queue"]:
                    df_queue = pd.DataFrame(
                        list(summary["tickets_by_queue"].items()),
                        columns=["Department", "Count"]
                    )
                    fig = px.bar(
                        df_queue,
                        x="Department",
                        y="Count",
                        title="Tickets by Department",
                        color="Count",
                        color_continuous_scale="Blues"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Tickets by status
                if summary["tickets_by_status"]:
                    df_status = pd.DataFrame(
                        list(summary["tickets_by_status"].items()),
                        columns=["Status", "Count"]
                    )
                    fig = px.pie(
                        df_status,
                        values="Count",
                        names="Status",
                        title="Tickets by Status"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Time series
            st.subheader("Ticket Trends")
            timeseries_response = requests.get(f"{BACKEND_URL}/dashboard/timeseries?days=30")
            if timeseries_response.status_code == 200:
                timeseries = timeseries_response.json()
                if timeseries:
                    df_ts = pd.DataFrame(timeseries)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_ts["date"],
                        y=df_ts["count"],
                        mode="lines+markers",
                        name="Total Tickets",
                        line=dict(color="blue")
                    ))
                    fig.add_trace(go.Scatter(
                        x=df_ts["date"],
                        y=df_ts["critical_count"],
                        mode="lines+markers",
                        name="Critical Tickets",
                        line=dict(color="red")
                    ))
                    fig.update_layout(
                        title="Tickets Over Time (Last 30 Days)",
                        xaxis_title="Date",
                        yaxis_title="Count"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.error("Failed to load dashboard summary")
    
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")


def approvals_page():
    """Pending approvals page"""
    st.header("⏳ Pending Critical Ticket Approvals")
    st.write("Review and approve critical ticket responses before they are sent to customers.")
    
    try:
        response = requests.get(f"{BACKEND_URL}/approvals/pending")
        if response.status_code == 200:
            pending = response.json()
            
            if not pending:
                st.success("✅ No tickets pending approval!")
                return
            
            st.warning(f"⚠️ {len(pending)} ticket(s) require your approval")
            
            # Display each pending ticket
            for item in pending:
                ticket_id = item["ticket_id"]
                
                with st.container():
                    st.markdown(f"""
                    <div class="approval-card">
                        <h3>🎫 Ticket #{ticket_id}: {item['subject']}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Get full ticket details
                    detail_response = requests.get(f"{BACKEND_URL}/tickets/{ticket_id}")
                    if detail_response.status_code == 200:
                        ticket = detail_response.json()
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Department", item["predicted_queue"])
                        with col2:
                            st.metric("Critical Probability", f"{item['critical_prob']:.2%}")
                        with col3:
                            st.metric("Submitter", item["submitter_email"])
                        with col4:
                            created = datetime.fromisoformat(item["created_at"].replace('Z', '+00:00'))
                            st.metric("Submitted", created.strftime("%Y-%m-%d %H:%M"))
                        
                        # Original ticket
                        with st.expander("📧 Original Ticket", expanded=True):
                            st.write(f"**From:** {ticket['submitter_name']} ({ticket['submitter_email']})")
                            st.write(f"**Subject:** {ticket['subject']}")
                            st.write(f"**Body:**\n{ticket['body']}")
                        
                        # Draft response
                        if ticket.get('responses') and len(ticket['responses']) > 0:
                            response_data = ticket['responses'][0]
                            
                            with st.expander("✍️ AI-Generated Draft Response", expanded=True):
                                st.write(f"**Language:** {response_data.get('draft_language', 'en')}")
                                st.write(f"**Confidence:** {response_data.get('draft_confidence', 0):.2%}")
                                st.write(f"**Subject:** {response_data.get('draft_subject')}")
                                st.write(f"**Body:**")
                                st.info(response_data.get('draft_body'))
                            
                            # Similar tickets context (outside expander to avoid nesting)
                            if response_data.get('retrieval_context'):
                                with st.expander("🔍 Similar Historical Tickets (RAG Context)"):
                                    import json
                                    context = json.loads(response_data['retrieval_context'])
                                    for i, ctx in enumerate(context, 1):
                                        st.write(f"**{i}. {ctx['subject']}**")
                                        st.write(f"Answer: {ctx['answer']}")
                                        st.write("---")
                        
                        # Approval actions
                        st.write("### 🎯 Action Required")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            with st.form(f"approve_form_{ticket_id}"):
                                st.subheader("✅ Approve & Send")
                                
                                approver_name = st.text_input("Your Name", value="Manager", key=f"name_approve_{ticket_id}")
                                approver_email = st.text_input("Your Email", value="manager@company.com", key=f"email_approve_{ticket_id}")
                                
                                edit_response = st.checkbox("Edit response before sending", key=f"edit_{ticket_id}")
                                
                                edited_subject = None
                                edited_body = None
                                
                                if edit_response and ticket.get('responses'):
                                    edited_subject = st.text_input(
                                        "Subject",
                                        value=ticket['responses'][0].get('draft_subject', ''),
                                        key=f"subj_{ticket_id}"
                                    )
                                    edited_body = st.text_area(
                                        "Body",
                                        value=ticket['responses'][0].get('draft_body', ''),
                                        height=200,
                                        key=f"body_{ticket_id}"
                                    )
                                
                                notes = st.text_input("Notes (optional)", key=f"notes_approve_{ticket_id}")
                                
                                if st.form_submit_button("✅ Approve & Send", use_container_width=True):
                                    approval_data = {
                                        "approver_name": approver_name,
                                        "approver_email": approver_email,
                                        "decision": "APPROVED",
                                        "decision_notes": notes,
                                        "edited_subject": edited_subject if edit_response else None,
                                        "edited_body": edited_body if edit_response else None
                                    }
                                    
                                    approve_response = requests.post(
                                        f"{BACKEND_URL}/tickets/{ticket_id}/approve",
                                        json=approval_data
                                    )
                                    
                                    if approve_response.status_code == 200:
                                        st.success("✅ Ticket approved and response sent!")
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to approve: {approve_response.text}")
                        
                        with col2:
                            with st.form(f"reject_form_{ticket_id}"):
                                st.subheader("❌ Reject / Request Changes")
                                
                                approver_name = st.text_input("Your Name", value="Manager", key=f"name_reject_{ticket_id}")
                                approver_email = st.text_input("Your Email", value="manager@company.com", key=f"email_reject_{ticket_id}")
                                
                                reject_notes = st.text_area(
                                    "Reason for rejection *",
                                    placeholder="Explain why this response needs revision...",
                                    key=f"reject_notes_{ticket_id}"
                                )
                                
                                if st.form_submit_button("❌ Reject", use_container_width=True):
                                    if not reject_notes:
                                        st.error("Please provide a reason for rejection")
                                    else:
                                        reject_data = {
                                            "approver_name": approver_name,
                                            "approver_email": approver_email,
                                            "decision": "REJECTED",
                                            "decision_notes": reject_notes
                                        }
                                        
                                        reject_response = requests.post(
                                            f"{BACKEND_URL}/tickets/{ticket_id}/reject",
                                            json=reject_data
                                        )
                                        
                                        if reject_response.status_code == 200:
                                            st.success("✅ Ticket rejected")
                                            st.rerun()
                                        else:
                                            st.error(f"Failed to reject: {reject_response.text}")
                        
                        st.markdown("---")
        
        else:
            st.error("Failed to load pending approvals")
    
    except Exception as e:
        st.error(f"Error loading approvals: {str(e)}")


def all_tickets_page():
    """All tickets with filters"""
    st.header("🎫 All Tickets")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox(
            "Status",
            ["All", "NEW", "TRIAGED", "DRAFTED", "PENDING_APPROVAL", "APPROVED", "SENT", "REJECTED"]
        )
    
    with col2:
        queue_filter = st.text_input("Department (optional)")
    
    with col3:
        critical_filter = st.selectbox("Priority", ["All", "Critical Only", "Non-Critical Only"])
    
    with col4:
        if st.button("🔄 Auto-Send Drafted", help="Auto-send all non-critical drafted tickets"):
            auto_send_drafted_tickets()
    
    # Build params
    params = {}
    if status_filter != "All":
        params["status"] = status_filter
    if queue_filter:
        params["queue"] = queue_filter
    if critical_filter == "Critical Only":
        params["is_critical"] = True
    elif critical_filter == "Non-Critical Only":
        params["is_critical"] = False
    
    try:
        response = requests.get(f"{BACKEND_URL}/tickets", params=params)
        if response.status_code == 200:
            tickets = response.json()
            
            st.write(f"**Found {len(tickets)} ticket(s)**")
            
            if tickets:
                # Convert to dataframe for overview
                df = pd.DataFrame(tickets)
                
                # Display each ticket with details
                for ticket in tickets:
                    ticket_id = ticket["id"]
                    subject = ticket["subject"]
                    status = ticket["status"]
                    is_critical = ticket.get("is_critical", False)
                    
                    # Status emoji
                    status_emoji = {
                        "NEW": "🆕",
                        "TRIAGED": "🔍",
                        "DRAFTED": "✍️",
                        "PENDING_APPROVAL": "⏳",
                        "APPROVED": "✅",
                        "SENT": "📤",
                        "REJECTED": "❌"
                    }.get(status, "📋")
                    
                    priority_badge = "🔴 CRITICAL" if is_critical else "🟢 NORMAL"
                    
                    with st.expander(f"{status_emoji} Ticket #{ticket_id}: {subject} | {priority_badge} | Status: {status}"):
                        show_ticket_details(ticket_id)
        
        else:
            st.error("Failed to load tickets")
    
    except Exception as e:
        st.error(f"Error loading tickets: {str(e)}")


def show_ticket_details(ticket_id):
    """Show detailed ticket information"""
    try:
        # Get full ticket details
        response = requests.get(f"{BACKEND_URL}/tickets/{ticket_id}")
        if response.status_code != 200:
            st.error("Failed to load ticket details")
            return
        
        ticket = response.json()
        
        # Ticket Information
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📬 Original Ticket")
            st.write(f"**From:** {ticket['submitter_name']} ({ticket['submitter_email']})")
            st.write(f"**Subject:** {ticket['subject']}")
            st.write(f"**Submitted:** {ticket['created_at']}")
        
        with col2:
            st.markdown("### 🤖 ML Predictions")
            st.write(f"**Department:** {ticket.get('predicted_queue', 'N/A')}")
            st.write(f"**Confidence:** {ticket.get('queue_confidence', 0):.2%}")
            st.write(f"**Criticality:** {ticket.get('critical_prob', 0):.2%}")
            st.write(f"**Status:** {ticket['status']}")
        
        st.markdown("---")
        st.markdown("### 📝 Ticket Message")
        st.info(ticket['body'])
        
        # Show response if exists
        if ticket.get('responses') and len(ticket['responses']) > 0:
            st.markdown("---")
            st.markdown("### 📧 Response")
            
            for idx, resp in enumerate(ticket['responses'], 1):
                st.markdown(f"**Response #{idx}**")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Subject:** {resp.get('draft_subject') or resp.get('final_subject', 'N/A')}")
                with col2:
                    st.write(f"**Confidence:** {resp.get('draft_confidence', 0):.0%}")
                
                # Show the actual response body
                response_body = resp.get('final_body') or resp.get('draft_body')
                if response_body:
                    st.success(response_body)
                else:
                    st.warning("No response body available")
                
                if resp.get('approved_at'):
                    st.caption(f"✅ Approved at: {resp['approved_at']}")
        else:
            st.warning("No response generated yet")
        
        # Show approvals if exists
        if ticket.get('approvals') and len(ticket['approvals']) > 0:
            st.markdown("---")
            st.markdown("### ✅ Approval History")
            for approval in ticket['approvals']:
                st.write(f"**{approval['decision']}** by {approval['approver_name']} at {approval['created_at']}")
                if approval.get('decision_notes'):
                    st.caption(f"Notes: {approval['decision_notes']}")
    
    except Exception as e:
        st.error(f"Error loading ticket details: {str(e)}")


def auto_send_drafted_tickets():
    """Auto-send all non-critical drafted tickets"""
    try:
        # Get drafted tickets
        response = requests.get(f"{BACKEND_URL}/tickets", params={"status": "DRAFTED"})
        
        if response.status_code != 200:
            st.error("Failed to get drafted tickets")
            return
        
        tickets = response.json()
        
        if not tickets:
            st.info("No drafted tickets to send")
            return
        
        success_count = 0
        for ticket in tickets:
            ticket_id = ticket["id"]
            
            # Auto-approve and send
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
                success_count += 1
        
        st.success(f"✅ Successfully sent {success_count} drafted ticket(s)!")
        st.rerun()
    
    except Exception as e:
        st.error(f"Error auto-sending: {str(e)}")


def analytics_page():
    """Analytics and insights"""
    st.header("📊 Analytics & Insights")
    
    st.info("🚧 Advanced analytics coming soon!")
    
    st.write("""
    Future features:
    - ML model performance metrics
    - Response time distributions
    - Department workload analysis
    - Customer satisfaction trends
    - Approval rate analysis
    """)


if __name__ == "__main__":
    main()
