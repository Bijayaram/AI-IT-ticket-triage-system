"""
Manager Dashboard - Streamlit App #2
Professional dashboard inspired by Pandora design - clean, symmetrical, data-focused.
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
    page_title="Support Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional Pandora-inspired CSS
st.markdown("""
    <style>
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Dark professional background like Pandora */
    .stApp {
        background: linear-gradient(180deg, #1a1d2e 0%, #2d1b4e 100%);
    }
    
    /* Main container - full width, minimal padding */
    .main .block-container {
        padding: 1.5rem 2rem 2rem 2rem;
        max-width: 100%;
    }
    
    /* Dashboard header */
    .dashboard-header {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
    }
    
    /* White metric cards like Pandora */
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        height: 100%;
        position: relative;
    }
    
    .metric-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .metric-icon.purple { background: #8b5cf6; }
    .metric-icon.blue { background: #3b82f6; }
    .metric-icon.green { background: #10b981; }
    .metric-icon.orange { background: #f59e0b; }
    .metric-icon.red { background: #ef4444; }
    
    .metric-label {
        color: #6b7280;
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        color: #111827;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .metric-change {
        font-size: 0.875rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .metric-change.positive { color: #10b981; }
    .metric-change.negative { color: #ef4444; }
    
    .metric-info {
        position: absolute;
        top: 1rem;
        right: 1rem;
        color: #d1d5db;
        cursor: pointer;
    }
    
    /* Chart container */
    .chart-container {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-top: 1.5rem;
    }
    
    .chart-title {
        color: #111827;
        font-size: 1.125rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    /* Streamlit metric styling override */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #111827;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        font-weight: 500;
        color: #6b7280;
    }
    
    [data-testid="metric-container"] {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Clean tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 0.25rem;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: rgba(255, 255, 255, 0.7);
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: #1a1d2e;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Professional buttons */
    .stButton > button {
        background: white;
        color: #1a1d2e;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transform: translateY(-1px);
    }
    
    /* Professional input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        background: white;
    }
    
    /* Clean expander */
    .streamlit-expanderHeader {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        font-weight: 600;
        padding: 1rem;
    }
    
    /* Approval card - warning style */
    .approval-card {
        background: white;
        border-left: 4px solid #f59e0b;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .approval-card-header {
        color: #111827;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    /* Form styling */
    .stForm {
        background: #f9fafb;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }
    
    /* Status badges */
    .status-badge {
        padding: 0.375rem 0.75rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.75rem;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-new { background: #dbeafe; color: #1e40af; }
    .status-triaged { background: #e9d5ff; color: #7c3aed; }
    .status-drafted { background: #fef3c7; color: #d97706; }
    .status-pending_approval { background: #fed7aa; color: #ea580c; }
    .status-approved { background: #d1fae5; color: #047857; }
    .status-sent { background: #d1fae5; color: #059669; }
    .status-rejected { background: #fee2e2; color: #dc2626; }
    
    /* Success/Error alerts */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 8px;
        padding: 1rem;
        border: none;
    }
    
    /* Remove padding from columns for tighter layout */
    [data-testid="column"] {
        padding: 0 0.5rem;
    }
    
    [data-testid="column"]:first-child {
        padding-left: 0;
    }
    
    [data-testid="column"]:last-child {
        padding-right: 0;
    }
    
    /* Hide empty space */
    .element-container:has(> .stMarkdown:empty) {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)


def check_authentication():
    """Professional login"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("""
                <div style="background: white; padding: 3rem; border-radius: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.2);">
                    <h2 style="color: #1a1d2e; text-align: center; margin-bottom: 2rem;">🔐 Manager Login</h2>
                </div>
            """, unsafe_allow_html=True)
            
            password = st.text_input("Password", type="password", placeholder="Enter manager password")
            
            if st.button("Access Dashboard", use_container_width=True):
                if password == MANAGER_PASSWORD:
                    st.session_state.authenticated = True
                    st.success("✅ Access granted")
                    st.rerun()
                else:
                    st.error("❌ Invalid password")
            
            st.info("💡 Default: admin123")
        
        st.stop()


def main():
    """Main dashboard"""
    check_authentication()
    
    # Header with logout
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown('<h1 class="dashboard-header">Dashboard</h1>', unsafe_allow_html=True)
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "⏳ Approvals",
        "🎫 Tickets",
        "📈 Analytics"
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
    """Professional overview with Pandora-style layout"""
    try:
        response = requests.get(f"{BACKEND_URL}/dashboard/summary")
        if response.status_code == 200:
            summary = response.json()
            
            # Top metrics row - 5 cards
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-icon purple">💼</div>
                        <div class="metric-label">Total Tickets</div>
                        <div class="metric-value">{summary["total_tickets"]:,}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-icon blue">📞</div>
                        <div class="metric-label">Open Tickets</div>
                        <div class="metric-value">{summary["open_tickets"]:,}</div>
                        <div class="metric-change positive">↑ Active</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-icon red">🔴</div>
                        <div class="metric-label">Critical Tickets</div>
                        <div class="metric-value">{summary["critical_count"]:,}</div>
                        <div class="metric-change {'negative' if summary['critical_count'] > 0 else 'positive'}">
                            {'⚠️ High Priority' if summary['critical_count'] > 0 else '✓ None'}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-icon orange">⏳</div>
                        <div class="metric-label">Pending Approval</div>
                        <div class="metric-value">{summary["pending_approval_count"]:,}</div>
                        <div class="metric-change {'negative' if summary['pending_approval_count'] > 0 else 'positive'}">
                            {'🔔 Action Required' if summary['pending_approval_count'] > 0 else '✓ Clear'}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col5:
                avg_time = summary.get("avg_response_time_hours", 0)
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-icon green">⚡</div>
                        <div class="metric-label">Avg Response Time</div>
                        <div class="metric-value">{avg_time:.1f}h</div>
                        <div class="metric-change {'positive' if avg_time < 24 else 'negative'}">
                            {'✓ Fast' if avg_time < 24 else '⚠️ Slow'}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Charts row
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Tickets by Department (Bar chart like Pandora)
                if summary["tickets_by_queue"]:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.markdown('<div class="chart-title">Ticket Volume by Department</div>', unsafe_allow_html=True)
                    
                    df_queue = pd.DataFrame(
                        list(summary["tickets_by_queue"].items()),
                        columns=["Department", "Count"]
                    )
                    
                    fig = px.bar(
                        df_queue,
                        x="Department",
                        y="Count",
                        color="Count",
                        color_continuous_scale=[[0, "#c4b5fd"], [0.5, "#a78bfa"], [1, "#8b5cf6"]],
                        template="plotly_white"
                    )
                    
                    fig.update_layout(
                        showlegend=False,
                        plot_bgcolor="white",
                        paper_bgcolor="white",
                        font=dict(family="Inter", size=12, color="#6b7280"),
                        xaxis=dict(showgrid=False, title=""),
                        yaxis=dict(showgrid=True, gridcolor="#f3f4f6", title=""),
                        margin=dict(t=10, b=40, l=40, r=10),
                        height=300
                    )
                    
                    fig.update_traces(marker_line_width=0)
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                # Status Distribution (Donut chart)
                if summary["tickets_by_status"]:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.markdown('<div class="chart-title">Status Distribution</div>', unsafe_allow_html=True)
                    
                    df_status = pd.DataFrame(
                        list(summary["tickets_by_status"].items()),
                        columns=["Status", "Count"]
                    )
                    
                    fig = px.pie(
                        df_status,
                        values="Count",
                        names="Status",
                        hole=0.6,
                        color_discrete_sequence=["#8b5cf6", "#3b82f6", "#10b981", "#f59e0b", "#ef4444"]
                    )
                    
                    fig.update_layout(
                        showlegend=True,
                        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
                        plot_bgcolor="white",
                        paper_bgcolor="white",
                        font=dict(family="Inter", size=11, color="#6b7280"),
                        margin=dict(t=10, b=10, l=10, r=80),
                        height=300
                    )
                    
                    fig.update_traces(textposition='inside', textinfo='percent', textfont_size=11)
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Time series chart (full width)
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">Ticket Trends - Last 30 Days</div>', unsafe_allow_html=True)
            
            timeseries_response = requests.get(f"{BACKEND_URL}/dashboard/timeseries?days=30")
            if timeseries_response.status_code == 200:
                timeseries = timeseries_response.json()
                if timeseries:
                    df_ts = pd.DataFrame(timeseries)
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=df_ts["date"],
                        y=df_ts["count"],
                        name="Total",
                        line=dict(color="#10b981", width=3),
                        mode="lines",
                        fill='tozeroy',
                        fillcolor="rgba(16, 185, 129, 0.1)"
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=df_ts["date"],
                        y=df_ts["critical_count"],
                        name="Critical",
                        line=dict(color="#8b5cf6", width=3),
                        mode="lines"
                    ))
                    
                    fig.update_layout(
                        hovermode="x unified",
                        plot_bgcolor="white",
                        paper_bgcolor="white",
                        font=dict(family="Inter", size=12, color="#6b7280"),
                        xaxis=dict(showgrid=False, title=""),
                        yaxis=dict(showgrid=True, gridcolor="#f3f4f6", title="Tickets"),
                        legend=dict(orientation="h", yanchor="top", y=1.1, xanchor="left", x=0),
                        margin=dict(t=40, b=40, l=60, r=20),
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.error("Failed to load dashboard")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend server")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


def approvals_page():
    """Professional approvals interface"""
    st.markdown("### ⏳ Pending Critical Approvals")
    
    try:
        response = requests.get(f"{BACKEND_URL}/approvals/pending")
        if response.status_code == 200:
            pending = response.json()
            
            if not pending:
                st.success("✅ All clear! No pending approvals.")
                return
            
            st.warning(f"⚠️ {len(pending)} ticket(s) require approval")
            st.markdown("<br>", unsafe_allow_html=True)
            
            for item in pending:
                ticket_id = item["ticket_id"]
                
                st.markdown(f"""
                    <div class="approval-card">
                        <div class="approval-card-header">🎫 Ticket #{ticket_id}: {item['subject']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                detail_response = requests.get(f"{BACKEND_URL}/tickets/{ticket_id}")
                if detail_response.status_code == 200:
                    ticket = detail_response.json()
                    
                    # Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Department", item["predicted_queue"])
                    with col2:
                        st.metric("Critical Score", f"{item['critical_prob']:.0%}")
                    with col3:
                        st.metric("From", item["submitter_email"].split('@')[0])
                    with col4:
                        created = datetime.fromisoformat(item["created_at"].replace('Z', '+00:00'))
                        hours = (datetime.now(created.tzinfo) - created).total_seconds() / 3600
                        st.metric("Age", f"{hours:.1f}h ago")
                    
                    # Original ticket
                    with st.expander("📧 Original Message", expanded=True):
                        st.write(f"**From:** {ticket['submitter_name']} ({ticket['submitter_email']})")
                        st.write(f"**Subject:** {ticket['subject']}")
                        st.info(ticket['body'])
                    
                    # Draft response
                    if ticket.get('responses') and len(ticket['responses']) > 0:
                        response_data = ticket['responses'][0]
                        
                        with st.expander("🤖 AI Draft Response", expanded=True):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**Subject:** {response_data.get('draft_subject')}")
                            with col2:
                                st.write(f"**Confidence:** {response_data.get('draft_confidence', 0):.0%}")
                            st.success(response_data.get('draft_body'))
                    
                    # Actions
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        with st.form(f"approve_{ticket_id}"):
                            st.subheader("✅ Approve")
                            approver_name = st.text_input("Your Name", "Manager", key=f"a_name_{ticket_id}")
                            approver_email = st.text_input("Your Email", "manager@company.com", key=f"a_email_{ticket_id}")
                            notes = st.text_input("Notes (optional)", key=f"a_notes_{ticket_id}")
                            
                            if st.form_submit_button("Approve & Send", use_container_width=True):
                                approval_data = {
                                    "approver_name": approver_name,
                                    "approver_email": approver_email,
                                    "decision": "APPROVED",
                                    "decision_notes": notes
                                }
                                
                                approve_response = requests.post(
                                    f"{BACKEND_URL}/tickets/{ticket_id}/approve",
                                    json=approval_data
                                )
                                
                                if approve_response.status_code == 200:
                                    st.success("✅ Approved!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed: {approve_response.text}")
                    
                    with col2:
                        with st.form(f"reject_{ticket_id}"):
                            st.subheader("❌ Reject")
                            approver_name = st.text_input("Your Name", "Manager", key=f"r_name_{ticket_id}")
                            approver_email = st.text_input("Your Email", "manager@company.com", key=f"r_email_{ticket_id}")
                            reject_reason = st.text_area("Reason (required)", key=f"r_reason_{ticket_id}")
                            
                            if st.form_submit_button("Reject", use_container_width=True):
                                if not reject_reason:
                                    st.error("Reason required")
                                else:
                                    reject_data = {
                                        "approver_name": approver_name,
                                        "approver_email": approver_email,
                                        "decision": "REJECTED",
                                        "decision_notes": reject_reason
                                    }
                                    
                                    reject_response = requests.post(
                                        f"{BACKEND_URL}/tickets/{ticket_id}/reject",
                                        json=reject_data
                                    )
                                    
                                    if reject_response.status_code == 200:
                                        st.success("✅ Rejected")
                                        st.rerun()
                                    else:
                                        st.error(f"Failed: {reject_response.text}")
                    
                    st.markdown("---")
        
        else:
            st.error("Failed to load approvals")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")


def all_tickets_page():
    """Professional tickets view"""
    st.markdown("### 🎫 All Tickets")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox(
            "Status",
            ["All", "NEW", "TRIAGED", "DRAFTED", "PENDING_APPROVAL", "APPROVED", "SENT", "REJECTED"]
        )
    
    with col2:
        queue_filter = st.text_input("Department")
    
    with col3:
        critical_filter = st.selectbox("Priority", ["All", "Critical Only", "Non-Critical Only"])
    
    with col4:
        if st.button("🚀 Auto-Send Drafted"):
            auto_send_drafted()
    
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
            
            st.write(f"**{len(tickets)} ticket(s) found**")
            
            if tickets:
                for ticket in tickets:
                    priority_icon = "🔴" if ticket.get("is_critical") else "🟢"
                    
                    with st.expander(
                        f"{priority_icon} #{ticket['id']}: {ticket['subject']} | {ticket['status']}",
                        expanded=False
                    ):
                        show_ticket_details(ticket["id"])
        
        else:
            st.error("Failed to load tickets")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")


def show_ticket_details(ticket_id):
    """Show ticket details"""
    try:
        response = requests.get(f"{BACKEND_URL}/tickets/{ticket_id}")
        if response.status_code != 200:
            st.error("Failed to load ticket")
            return
        
        ticket = response.json()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📬 Original Ticket**")
            st.write(f"From: {ticket['submitter_name']} ({ticket['submitter_email']})")
            st.write(f"Subject: {ticket['subject']}")
            st.info(ticket['body'])
        
        with col2:
            st.markdown("**🤖 ML Analysis**")
            st.write(f"Department: {ticket.get('predicted_queue', 'N/A')}")
            st.write(f"Confidence: {ticket.get('queue_confidence', 0):.1%}")
            st.write(f"Critical: {ticket.get('critical_prob', 0):.1%}")
            st.write(f"Status: {ticket['status']}")
        
        if ticket.get('responses'):
            st.markdown("---")
            st.markdown("**📧 Response**")
            for resp in ticket['responses']:
                body = resp.get('final_body') or resp.get('draft_body')
                if body:
                    st.success(body)
    
    except Exception as e:
        st.error(f"Error: {str(e)}")


def auto_send_drafted():
    """Auto-send drafted tickets"""
    try:
        response = requests.get(f"{BACKEND_URL}/tickets", params={"status": "DRAFTED"})
        
        if response.status_code != 200:
            st.error("Failed to get drafted tickets")
            return
        
        tickets = response.json()
        
        if not tickets:
            st.info("No drafted tickets")
            return
        
        success_count = 0
        for ticket in tickets:
            approval_data = {
                "approver_name": "System",
                "approver_email": "system@company.com",
                "decision": "APPROVED",
                "decision_notes": "Auto-approved"
            }
            
            approve_response = requests.post(
                f"{BACKEND_URL}/tickets/{ticket['id']}/approve",
                json=approval_data
            )
            
            if approve_response.status_code == 200:
                success_count += 1
        
        st.success(f"✅ Sent {success_count} ticket(s)!")
        st.rerun()
    
    except Exception as e:
        st.error(f"Error: {str(e)}")


def analytics_page():
    """Analytics page"""
    st.markdown("### 📈 Analytics")
    
    st.info("🚧 Advanced analytics coming soon")
    
    st.markdown("""
    **Planned Features:**
    - ML model performance tracking
    - Response time analytics
    - Department workload analysis
    - Customer satisfaction metrics
    - Trend analysis and forecasting
    """)


if __name__ == "__main__":
    main()
