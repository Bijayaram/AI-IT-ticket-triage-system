"""
Manager Dashboard - Streamlit App #2
Modern, professional dashboard for ticket management and analytics.
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
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern Professional CSS
st.markdown("""
    <style>
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Professional dark gradient background */
    .stApp {
        background: linear-gradient(135deg, #1e3a8a 0%, #7c3aed 50%, #db2777 100%);
    }
    
    /* Main container with modern card style */
    .main .block-container {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 2.5rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        margin-top: 1.5rem;
    }
    
    /* Professional header */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1e3a8a 0%, #7c3aed 50%, #db2777 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeInDown 0.8s ease-out;
        letter-spacing: -1px;
    }
    
    .sub-header {
        text-align: center;
        color: #64748b;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    /* Modern tabs with professional look */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: transparent;
        padding: 1rem 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #1e3a8a 0%, #7c3aed 100%);
        color: white;
        border-radius: 16px;
        padding: 14px 28px;
        font-weight: 700;
        font-size: 1.05rem;
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #7c3aed 0%, #db2777 100%);
        box-shadow: 0 8px 20px rgba(124, 58, 237, 0.5);
        transform: translateY(-3px);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(30, 58, 138, 0.4);
    }
    
    /* Professional metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1e293b;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    /* Professional input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 12px 16px;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: white;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #7c3aed;
        box-shadow: 0 0 0 4px rgba(124, 58, 237, 0.1);
    }
    
    /* Professional buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1e3a8a 0%, #7c3aed 100%);
        color: white;
        border-radius: 12px;
        padding: 12px 32px;
        font-weight: 700;
        font-size: 1rem;
        border: none;
        box-shadow: 0 4px 16px rgba(30, 58, 138, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(30, 58, 138, 0.4);
        background: linear-gradient(135deg, #7c3aed 0%, #db2777 100%);
    }
    
    /* Professional card design */
    .approval-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: none;
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 24px rgba(251, 191, 36, 0.3);
        transition: all 0.3s ease;
    }
    
    .approval-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(251, 191, 36, 0.4);
    }
    
    /* Professional expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 16px;
        font-weight: 700;
        font-size: 1.1rem;
        padding: 1.2rem;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        border-color: #7c3aed;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.2);
        transform: translateX(4px);
    }
    
    /* Status indicators with professional styling */
    .status-badge {
        padding: 0.6rem 1.2rem;
        border-radius: 24px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Professional alerts */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 16px;
        padding: 1.2rem;
        border: none;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    /* Form styling */
    .stForm {
        background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
        padding: 2rem;
        border-radius: 20px;
        border: 2px solid #e5e7eb;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    }
    
    /* Login container */
    .login-container {
        max-width: 500px;
        margin: 4rem auto;
        padding: 3rem;
        background: white;
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }
    
    /* Professional charts */
    .js-plotly-plot {
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Checkbox styling */
    .stCheckbox {
        padding: 0.5rem 0;
    }
    
    /* Professional divider */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
    }
    </style>
""", unsafe_allow_html=True)


def check_authentication():
    """Professional login page"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown('<p class="main-header">🔐 Manager Dashboard</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Secure Access Portal</p>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            with st.container():
                st.markdown("### 🔑 Authentication Required")
                st.markdown("<br>", unsafe_allow_html=True)
                
                password = st.text_input(
                    "Manager Password",
                    type="password",
                    placeholder="Enter your secure password"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("🚀 Access Dashboard"):
                    if password == MANAGER_PASSWORD:
                        st.session_state.authenticated = True
                        st.success("✅ Authentication successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Access denied.")
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.info("💡 **Default Password:** admin123")
        
        st.stop()


def main():
    """Main professional dashboard"""
    check_authentication()
    
    st.markdown('<p class="main-header">📊 IT Manager Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time Ticket Management & Analytics</p>', unsafe_allow_html=True)
    
    # Logout button with modern styling
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Professional navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Overview",
        "⏳ Approvals",
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
    """Professional overview with modern KPIs"""
    st.markdown("### 📊 Real-Time Dashboard")
    st.markdown("<br>", unsafe_allow_html=True)
    
    try:
        response = requests.get(f"{BACKEND_URL}/dashboard/summary")
        if response.status_code == 200:
            summary = response.json()
            
            # Modern KPI Cards
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    "📋 Total Tickets",
                    summary["total_tickets"],
                    delta=None,
                    help="Total tickets in the system"
                )
            
            with col2:
                st.metric(
                    "🔓 Open Tickets",
                    summary["open_tickets"],
                    delta=f"{summary['open_tickets']} active",
                    help="Currently open tickets"
                )
            
            with col3:
                st.metric(
                    "🔴 Critical",
                    summary["critical_count"],
                    delta="High Priority" if summary["critical_count"] > 0 else "None",
                    delta_color="inverse",
                    help="High priority tickets"
                )
            
            with col4:
                st.metric(
                    "⏳ Pending",
                    summary["pending_approval_count"],
                    delta="Action Required" if summary["pending_approval_count"] > 0 else "Clear",
                    delta_color="inverse",
                    help="Tickets awaiting approval"
                )
            
            with col5:
                avg_time = summary.get("avg_response_time_hours")
                if avg_time:
                    st.metric(
                        "⚡ Avg Time",
                        f"{avg_time:.1f}h",
                        delta=f"{avg_time:.1f}h" if avg_time < 24 else "Slow",
                        delta_color="normal" if avg_time < 24 else "inverse",
                        help="Average response time"
                    )
                else:
                    st.metric("⚡ Avg Time", "N/A", help="No data yet")
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # Professional Charts
            st.markdown("### 📊 Ticket Distribution Analytics")
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Department distribution with modern styling
                if summary["tickets_by_queue"]:
                    df_queue = pd.DataFrame(
                        list(summary["tickets_by_queue"].items()),
                        columns=["Department", "Count"]
                    )
                    fig = px.bar(
                        df_queue,
                        x="Department",
                        y="Count",
                        title="<b>Tickets by Department</b>",
                        color="Count",
                        color_continuous_scale="Viridis",
                        template="plotly_white"
                    )
                    fig.update_layout(
                        title_font_size=18,
                        title_font_color="#1e293b",
                        title_font_family="Inter",
                        font=dict(family="Inter", size=12),
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        showlegend=False,
                        margin=dict(t=50, b=50, l=50, r=50)
                    )
                    fig.update_traces(marker_line_color="white", marker_line_width=2)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Status distribution with modern pie chart
                if summary["tickets_by_status"]:
                    df_status = pd.DataFrame(
                        list(summary["tickets_by_status"].items()),
                        columns=["Status", "Count"]
                    )
                    fig = px.pie(
                        df_status,
                        values="Count",
                        names="Status",
                        title="<b>Tickets by Status</b>",
                        color_discrete_sequence=px.colors.qualitative.Set3,
                        template="plotly_white",
                        hole=0.4
                    )
                    fig.update_layout(
                        title_font_size=18,
                        title_font_color="#1e293b",
                        title_font_family="Inter",
                        font=dict(family="Inter", size=12),
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        margin=dict(t=50, b=50, l=50, r=50)
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
            
            # Time series with professional styling
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 📈 Ticket Trends Over Time")
            st.markdown("<br>", unsafe_allow_html=True)
            
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
                        line=dict(color="#1e3a8a", width=3),
                        marker=dict(size=8, symbol="circle"),
                        fill='tozeroy',
                        fillcolor="rgba(30, 58, 138, 0.1)"
                    ))
                    fig.add_trace(go.Scatter(
                        x=df_ts["date"],
                        y=df_ts["critical_count"],
                        mode="lines+markers",
                        name="Critical Tickets",
                        line=dict(color="#db2777", width=3),
                        marker=dict(size=8, symbol="diamond")
                    ))
                    fig.update_layout(
                        title="<b>Ticket Volume - Last 30 Days</b>",
                        title_font_size=18,
                        title_font_color="#1e293b",
                        title_font_family="Inter",
                        xaxis_title="Date",
                        yaxis_title="Number of Tickets",
                        font=dict(family="Inter", size=12),
                        template="plotly_white",
                        hovermode="x unified",
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        margin=dict(t=80, b=60, l=60, r=60)
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.error("❌ Failed to load dashboard data")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to the backend server. Please ensure it's running.")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


def approvals_page():
    """Professional approvals interface"""
    st.markdown("### ⏳ Pending Critical Ticket Approvals")
    st.write("Review and approve AI-generated responses for critical priority tickets.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    try:
        response = requests.get(f"{BACKEND_URL}/approvals/pending")
        if response.status_code == 200:
            pending = response.json()
            
            if not pending:
                st.success("🎉 **All caught up!** No tickets pending approval.")
                st.balloons()
                return
            
            st.warning(f"⚠️ **{len(pending)} ticket(s)** require your immediate attention")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Display each pending ticket with professional design
            for item in pending:
                ticket_id = item["ticket_id"]
                
                st.markdown(f"""
                <div class="approval-card">
                    <h2 style="margin: 0; color: #92400e;">🎫 Ticket #{ticket_id}</h2>
                    <h3 style="margin: 0.5rem 0 0 0; color: #78350f;">{item['subject']}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Get full ticket details
                detail_response = requests.get(f"{BACKEND_URL}/tickets/{ticket_id}")
                if detail_response.status_code == 200:
                    ticket = detail_response.json()
                    
                    # Key metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("🏢 Department", item["predicted_queue"])
                    with col2:
                        st.metric("🔥 Critical Score", f"{item['critical_prob']:.0%}")
                    with col3:
                        st.metric("👤 Submitter", item["submitter_email"].split('@')[0])
                    with col4:
                        created = datetime.fromisoformat(item["created_at"].replace('Z', '+00:00'))
                        hours_ago = (datetime.now(created.tzinfo) - created).total_seconds() / 3600
                        st.metric("⏱️ Submitted", f"{hours_ago:.1f}h ago")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Original ticket
                    with st.expander("📧 Original Ticket", expanded=True):
                        st.markdown(f"**From:** {ticket['submitter_name']} ({ticket['submitter_email']})")
                        st.markdown(f"**Subject:** {ticket['subject']}")
                        st.markdown("**Message:**")
                        st.info(ticket['body'])
                    
                    # AI Draft response
                    if ticket.get('responses') and len(ticket['responses']) > 0:
                        response_data = ticket['responses'][0]
                        
                        with st.expander("🤖 AI-Generated Draft Response", expanded=True):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**Language:** {response_data.get('draft_language', 'en').upper()}")
                            with col2:
                                confidence = response_data.get('draft_confidence', 0)
                                color = "green" if confidence > 0.8 else "orange" if confidence > 0.6 else "red"
                                st.markdown(f"**Confidence:** <span style='color: {color}; font-weight: bold;'>{confidence:.0%}</span>", unsafe_allow_html=True)
                            
                            st.markdown(f"**Subject:** {response_data.get('draft_subject')}")
                            st.markdown("**Response Body:**")
                            st.success(response_data.get('draft_body'))
                        
                        # RAG context
                        if response_data.get('retrieval_context'):
                            with st.expander("🔍 Similar Historical Tickets (RAG Context)"):
                                import json
                                context = json.loads(response_data['retrieval_context'])
                                for i, ctx in enumerate(context, 1):
                                    st.markdown(f"**{i}. {ctx['subject']}**")
                                    st.write(f"**Answer:** {ctx['answer']}")
                                    if i < len(context):
                                        st.markdown("---")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Approval actions
                    st.markdown("### 🎯 Decision Required")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        with st.form(f"approve_form_{ticket_id}"):
                            st.markdown("#### ✅ Approve & Send Response")
                            
                            approver_name = st.text_input("Your Name", value="Manager", key=f"name_approve_{ticket_id}")
                            approver_email = st.text_input("Your Email", value="manager@company.com", key=f"email_approve_{ticket_id}")
                            
                            edit_response = st.checkbox("✏️ Edit response before sending", key=f"edit_{ticket_id}")
                            
                            edited_subject = None
                            edited_body = None
                            
                            if edit_response and ticket.get('responses'):
                                st.markdown("**Edit Response:**")
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
                            
                            notes = st.text_input("Approval Notes (optional)", key=f"notes_approve_{ticket_id}")
                            
                            if st.form_submit_button("✅ Approve & Send to Customer", use_container_width=True):
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
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error(f"❌ Failed to approve: {approve_response.text}")
                    
                    with col2:
                        with st.form(f"reject_form_{ticket_id}"):
                            st.markdown("#### ❌ Reject / Request Revision")
                            
                            approver_name = st.text_input("Your Name", value="Manager", key=f"name_reject_{ticket_id}")
                            approver_email = st.text_input("Your Email", value="manager@company.com", key=f"email_reject_{ticket_id}")
                            
                            reject_notes = st.text_area(
                                "Rejection Reason (required)",
                                placeholder="Explain why this response needs to be revised...",
                                key=f"reject_notes_{ticket_id}",
                                height=150
                            )
                            
                            if st.form_submit_button("❌ Reject & Request Revision", use_container_width=True):
                                if not reject_notes:
                                    st.error("⚠️ Please provide a reason for rejection")
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
                                        st.success("✅ Ticket rejected. Agent will revise the response.")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Failed to reject: {reject_response.text}")
                    
                    st.markdown("---")
                    st.markdown("<br>", unsafe_allow_html=True)
        
        else:
            st.error("❌ Failed to load pending approvals")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to the backend server")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


def all_tickets_page():
    """Professional all tickets view"""
    st.markdown("### 🎫 All Tickets Management")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Professional filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox(
            "📊 Status Filter",
            ["All", "NEW", "TRIAGED", "DRAFTED", "PENDING_APPROVAL", "APPROVED", "SENT", "REJECTED"]
        )
    
    with col2:
        queue_filter = st.text_input("🏢 Department", placeholder="e.g., Network")
    
    with col3:
        critical_filter = st.selectbox(
            "⚡ Priority",
            ["All", "Critical Only", "Non-Critical Only"]
        )
    
    with col4:
        if st.button("🚀 Auto-Send Drafted", help="Auto-send all non-critical drafted tickets"):
            auto_send_drafted_tickets()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
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
            
            st.markdown(f"**Found {len(tickets)} ticket(s)**")
            
            if tickets:
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Display tickets with professional cards
                for ticket in tickets:
                    ticket_id = ticket["id"]
                    subject = ticket["subject"]
                    status = ticket["status"]
                    is_critical = ticket.get("is_critical", False)
                    
                    # Professional status icons
                    status_emoji = {
                        "NEW": "🆕",
                        "TRIAGED": "🔍",
                        "DRAFTED": "✍️",
                        "PENDING_APPROVAL": "⏳",
                        "APPROVED": "✅",
                        "SENT": "📤",
                        "REJECTED": "❌"
                    }.get(status, "📋")
                    
                    priority_icon = "🔴" if is_critical else "🟢"
                    priority_text = "CRITICAL" if is_critical else "NORMAL"
                    
                    with st.expander(
                        f"{status_emoji} Ticket #{ticket_id} | {subject} | {priority_icon} {priority_text} | Status: {status}",
                        expanded=False
                    ):
                        show_ticket_details(ticket_id)
            else:
                st.info("📭 No tickets found matching your filters")
        
        else:
            st.error("❌ Failed to load tickets")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to the backend server")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


def show_ticket_details(ticket_id):
    """Show professional detailed ticket information"""
    try:
        response = requests.get(f"{BACKEND_URL}/tickets/{ticket_id}")
        if response.status_code != 200:
            st.error("❌ Failed to load ticket details")
            return
        
        ticket = response.json()
        
        # Professional ticket info layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📬 Original Ticket")
            st.write(f"**From:** {ticket['submitter_name']}")
            st.write(f"**Email:** {ticket['submitter_email']}")
            st.write(f"**Subject:** {ticket['subject']}")
            st.write(f"**Submitted:** {ticket['created_at']}")
        
        with col2:
            st.markdown("#### 🤖 ML Predictions")
            st.write(f"**Department:** {ticket.get('predicted_queue', 'N/A')}")
            st.write(f"**Confidence:** {ticket.get('queue_confidence', 0):.1%}")
            st.write(f"**Criticality:** {ticket.get('critical_prob', 0):.1%}")
            st.write(f"**Status:** {ticket['status']}")
        
        st.markdown("---")
        st.markdown("#### 📝 Customer Message")
        st.info(ticket['body'])
        
        # Show response
        if ticket.get('responses') and len(ticket['responses']) > 0:
            st.markdown("---")
            st.markdown("#### 📧 Support Response")
            
            for idx, resp in enumerate(ticket['responses'], 1):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**Subject:** {resp.get('draft_subject') or resp.get('final_subject', 'N/A')}")
                with col2:
                    confidence = resp.get('draft_confidence', 0)
                    st.write(f"**AI Confidence:** {confidence:.0%}")
                
                # Response body
                response_body = resp.get('final_body') or resp.get('draft_body')
                if response_body:
                    st.success(response_body)
                else:
                    st.warning("⚠️ No response body available")
                
                if resp.get('approved_at'):
                    st.caption(f"✅ Approved and sent: {resp['approved_at']}")
        else:
            st.warning("⏳ Response is being generated...")
        
        # Approval history
        if ticket.get('approvals') and len(ticket['approvals']) > 0:
            st.markdown("---")
            st.markdown("#### ✅ Approval History")
            for approval in ticket['approvals']:
                decision_color = "green" if approval['decision'] == "APPROVED" else "red"
                st.markdown(f"**<span style='color: {decision_color};'>{approval['decision']}</span>** by **{approval['approver_name']}** at {approval['created_at']}", unsafe_allow_html=True)
                if approval.get('decision_notes'):
                    st.caption(f"📝 Notes: {approval['decision_notes']}")
    
    except Exception as e:
        st.error(f"❌ Error loading ticket details: {str(e)}")


def auto_send_drafted_tickets():
    """Auto-send non-critical drafted tickets"""
    try:
        response = requests.get(f"{BACKEND_URL}/tickets", params={"status": "DRAFTED"})
        
        if response.status_code != 200:
            st.error("❌ Failed to get drafted tickets")
            return
        
        tickets = response.json()
        
        if not tickets:
            st.info("📭 No drafted tickets to send")
            return
        
        success_count = 0
        with st.spinner(f"📤 Sending {len(tickets)} drafted ticket(s)..."):
            for ticket in tickets:
                ticket_id = ticket["id"]
                
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
        
        st.success(f"✅ Successfully sent {success_count}/{len(tickets)} drafted ticket(s)!")
        st.balloons()
        st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error auto-sending: {str(e)}")


def analytics_page():
    """Professional analytics page"""
    st.markdown("### 📊 Advanced Analytics & Insights")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Create a professional "coming soon" page
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <h1 style="font-size: 4rem; margin-bottom: 1rem;">🚧</h1>
            <h2 style="color: #1e293b; margin-bottom: 1rem;">Advanced Analytics Coming Soon</h2>
            <p style="color: #64748b; font-size: 1.1rem;">We're building powerful analytics features for you!</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Feature roadmap
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Planned Features")
        st.markdown("""
        - **ML Model Performance**
          - Department classification accuracy trends
          - Criticality prediction calibration
          - Confidence score distribution analysis
        
        - **Response Time Analytics**
          - Average, median, P95 response times
          - Response time by department
          - SLA compliance tracking
        """)
    
    with col2:
        st.markdown("#### 📈 Future Insights")
        st.markdown("""
        - **Workload Analysis**
          - Department ticket distribution
          - Agent workload balancing
          - Peak hours analysis
        
        - **Customer Satisfaction**
          - Feedback sentiment analysis
          - Resolution rate tracking
          - Customer satisfaction scores
        """)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("💡 These features will be available in the next release!")


if __name__ == "__main__":
    main()
