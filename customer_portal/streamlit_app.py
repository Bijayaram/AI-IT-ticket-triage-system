"""
Customer Portal - Streamlit App #1
Clean, tutorial-style UI for submitting support tickets.
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
    page_title="IT Support - Submit a Ticket",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clean, modern CSS inspired by the tutorial design
st.markdown("""
    <style>
    /* Import clean font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Clean teal/blue gradient background */
    .stApp {
        background: linear-gradient(135deg, #0891b2 0%, #06b6d4 50%, #22d3ee 100%);
    }
    
    /* Main container - clean white card */
    .main .block-container {
        background: white;
        border-radius: 24px;
        padding: 3rem 4rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        margin-top: 2rem;
        max-width: 1400px;
    }
    
    /* Tutorial-style header */
    .tutorial-badge {
        background: #06b6d4;
        color: white;
        padding: 8px 20px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        display: inline-block;
        margin-bottom: 1.5rem;
    }
    
    /* Main heading */
    .main-heading {
        font-size: 3rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.2;
        margin-bottom: 1rem;
    }
    
    .main-heading .highlight {
        color: #0891b2;
    }
    
    .sub-heading {
        font-size: 1.3rem;
        color: #64748b;
        font-weight: 400;
        margin-bottom: 3rem;
        line-height: 1.6;
    }
    
    /* Clean section headers */
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0f172a;
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-number {
        background: #0891b2;
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        font-weight: 700;
    }
    
    /* Clean input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 14px 18px;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: #f8fafc;
        font-family: 'Poppins', sans-serif;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #0891b2;
        background: white;
        box-shadow: 0 0 0 4px rgba(8, 145, 178, 0.1);
    }
    
    /* Input labels */
    .stTextInput > label,
    .stTextArea > label {
        font-size: 0.95rem;
        font-weight: 600;
        color: #334155;
        margin-bottom: 0.5rem;
    }
    
    /* Clean button */
    .stButton > button {
        background: #0891b2;
        color: white;
        border-radius: 12px;
        padding: 16px 48px;
        font-weight: 700;
        font-size: 1.1rem;
        border: none;
        box-shadow: 0 4px 16px rgba(8, 145, 178, 0.3);
        transition: all 0.3s ease;
        width: 100%;
        text-transform: none;
    }
    
    .stButton > button:hover {
        background: #0e7490;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(8, 145, 178, 0.4);
    }
    
    /* Clean tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: #f1f5f9;
        border-radius: 12px;
        padding: 4px;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #64748b;
        border-radius: 10px;
        padding: 12px 32px;
        font-weight: 600;
        font-size: 1rem;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: #0891b2;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    /* Clean info boxes */
    .info-box {
        background: #f0f9ff;
        border-left: 4px solid #0891b2;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
    }
    
    .info-box-title {
        font-weight: 700;
        color: #0891b2;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .info-box-text {
        color: #334155;
        line-height: 1.6;
    }
    
    /* Success card */
    .success-card {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin: 2rem 0;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.3);
    }
    
    .success-card h3 {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    /* Metric card - clean design */
    .metric-card {
        background: white;
        border: 2px solid #e2e8f0;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: #0891b2;
        box-shadow: 0 4px 16px rgba(8, 145, 178, 0.1);
        transform: translateY(-4px);
    }
    
    .metric-card-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-card-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.25rem;
    }
    
    .metric-card-label {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 500;
    }
    
    /* Status badge - clean */
    .status-badge {
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
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
    
    /* Clean expander */
    .streamlit-expanderHeader {
        background: #f8fafc;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        font-weight: 600;
        padding: 1rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: #f1f5f9;
        border-color: #0891b2;
    }
    
    /* Clean alerts */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 12px;
        padding: 1rem 1.5rem;
        border: none;
        font-weight: 500;
    }
    
    /* Form container */
    .stForm {
        background: #f8fafc;
        padding: 2.5rem;
        border-radius: 16px;
        border: 2px solid #e2e8f0;
    }
    
    /* Ticket card */
    .ticket-card {
        background: white;
        border: 2px solid #e2e8f0;
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .ticket-card:hover {
        border-color: #0891b2;
        box-shadow: 0 4px 16px rgba(8, 145, 178, 0.1);
    }
    
    /* Helper text */
    .helper-text {
        font-size: 0.9rem;
        color: #64748b;
        margin-top: 0.5rem;
        font-style: italic;
    }
    
    /* Divider */
    hr {
        margin: 3rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
    }
    </style>
""", unsafe_allow_html=True)


def format_status_badge(status: str) -> str:
    """Format status as clean badge"""
    status_lower = status.lower().replace(' ', '_')
    return f'<span class="status-badge status-{status_lower}">{status}</span>'


def main():
    """Main app with tutorial-style design"""
    
    # Clean header with tutorial badge
    st.markdown('<div class="tutorial-badge">📋 SUPPORT CENTER</div>', unsafe_allow_html=True)
    
    st.markdown('''
        <h1 class="main-heading">
            How to Submit a <span class="highlight">Support Ticket</span><br>
            (That will actually help you get faster support)
        </h1>
    ''', unsafe_allow_html=True)
    
    st.markdown('''
        <p class="sub-heading">
            Our AI-powered system instantly routes your request to the right team and 
            provides intelligent assistance. Get help in minutes, not hours.
        </p>
    ''', unsafe_allow_html=True)
    
    # Clean navigation tabs
    tab1, tab2 = st.tabs(["📝 Submit New Ticket", "📊 Track My Tickets"])
    
    with tab1:
        submit_ticket_page()
    
    with tab2:
        my_tickets_page()


def submit_ticket_page():
    """Clean, tutorial-style submit page"""
    
    # Helpful info box
    st.markdown('''
        <div class="info-box">
            <div class="info-box-title">💡 Before you start</div>
            <div class="info-box-text">
                The more details you provide, the faster we can help you. Include any error messages, 
                screenshots details, or steps that led to the issue.
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    with st.form("ticket_form", clear_on_submit=True):
        # Step 1: Your Information
        st.markdown('''
            <div class="section-header">
                <span class="section-number">1</span>
                <span>Your Information</span>
            </div>
        ''', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitter_name = st.text_input(
                "Full Name",
                placeholder="John Doe",
                help="Enter your full name so we know who to help"
            )
        
        with col2:
            submitter_email = st.text_input(
                "Email Address",
                placeholder="john.doe@company.com",
                help="We'll send updates and responses to this email"
            )
        
        # Step 2: Describe Your Issue
        st.markdown('''
            <div class="section-header">
                <span class="section-number">2</span>
                <span>Describe Your Issue</span>
            </div>
        ''', unsafe_allow_html=True)
        
        subject = st.text_input(
            "What's the problem?",
            placeholder="e.g., Can't access company VPN from home",
            help="Brief one-line summary of your issue"
        )
        
        body = st.text_area(
            "Give us the details",
            placeholder="""Please provide as much detail as possible:
            
• What were you trying to do?
• What happened instead?
• Any error messages you saw?
• When did this start happening?
• Have you tried any solutions?

The more details you provide, the faster we can help!""",
            height=200,
            help="Detailed description helps us understand and resolve your issue faster"
        )
        
        st.markdown('<p class="helper-text">💡 Pro tip: Include screenshots if you have them (you can attach them to the follow-up email)</p>', unsafe_allow_html=True)
        
        # Step 3: Submit
        st.markdown('''
            <div class="section-header">
                <span class="section-number">3</span>
                <span>Submit Your Ticket</span>
            </div>
        ''', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.form_submit_button("🚀 Submit Ticket", use_container_width=True)
        
        if submit_button:
            # Validate
            if not submitter_name or not submitter_email or not subject or not body:
                st.error("⚠️ Please fill in all fields to submit your ticket")
                return
            
            if "@" not in submitter_email or "." not in submitter_email:
                st.error("⚠️ Please enter a valid email address")
                return
            
            # Submit ticket
            with st.spinner("🔄 Submitting your ticket and analyzing with AI..."):
                try:
                    data = {
                        "subject": subject,
                        "body": body,
                        "submitter_name": submitter_name,
                        "submitter_email": submitter_email
                    }
                    
                    response = requests.post(f"{BACKEND_URL}/tickets", data=data)
                    
                    if response.status_code == 201:
                        ticket = response.json()
                        ticket_id = ticket["id"]
                        
                        # Auto-triage
                        triage_response = requests.post(
                            f"{BACKEND_URL}/tickets/{ticket_id}/triage",
                            json={"run_draft": True}
                        )
                        
                        if triage_response.status_code == 200:
                            triage_result = triage_response.json()
                            
                            # Success message
                            st.markdown(f'''
                                <div class="success-card">
                                    <h3>✅ Ticket Submitted Successfully!</h3>
                                    <p style="font-size: 1.1rem; margin-bottom: 1.5rem;">
                                        Your ticket <strong>#{ticket_id}</strong> has been created and our AI has analyzed it.
                                    </p>
                                    <p style="font-size: 0.95rem; opacity: 0.9;">
                                        💡 Save this ticket ID to track your request later
                                    </p>
                                </div>
                            ''', unsafe_allow_html=True)
                            
                            # Clean metric cards
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown(f'''
                                    <div class="metric-card">
                                        <div class="metric-card-icon">🏢</div>
                                        <div class="metric-card-value">{triage_result["predicted_queue"]}</div>
                                        <div class="metric-card-label">Assigned To</div>
                                    </div>
                                ''', unsafe_allow_html=True)
                            
                            with col2:
                                priority_icon = "🔴" if triage_result["is_critical"] else "🟢"
                                priority_text = "High Priority" if triage_result["is_critical"] else "Normal"
                                st.markdown(f'''
                                    <div class="metric-card">
                                        <div class="metric-card-icon">{priority_icon}</div>
                                        <div class="metric-card-value">{priority_text}</div>
                                        <div class="metric-card-label">Priority Level</div>
                                    </div>
                                ''', unsafe_allow_html=True)
                            
                            with col3:
                                status_icon = "⏳" if triage_result["needs_approval"] else "⚡"
                                status_text = "Pending Review" if triage_result["needs_approval"] else "Auto-Processing"
                                st.markdown(f'''
                                    <div class="metric-card">
                                        <div class="metric-card-icon">{status_icon}</div>
                                        <div class="metric-card-value">{status_text}</div>
                                        <div class="metric-card-label">Current Status</div>
                                    </div>
                                ''', unsafe_allow_html=True)
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            # Next steps
                            if triage_result["needs_approval"]:
                                st.info("""
                                    **What happens next?**
                                    
                                    Your ticket has been marked as **high priority** and requires manager approval. 
                                    You'll receive an email response within **2 hours**.
                                """)
                            else:
                                st.success("""
                                    **What happens next?**
                                    
                                    Your ticket is being processed automatically. You'll receive an email 
                                    response **shortly** with helpful information.
                                """)
                    
                    else:
                        st.error("❌ Failed to submit ticket. Please try again or contact support directly.")
                
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to the server. Please check your connection and try again.")
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")


def my_tickets_page():
    """Clean ticket tracking page"""
    
    st.markdown('''
        <div class="section-header">
            <span>🔍 Track Your Tickets</span>
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('''
        <p class="sub-heading">
            Enter your email address to view all your submitted tickets and their current status.
        </p>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        email = st.text_input(
            "Your Email Address",
            placeholder="john.doe@company.com",
            label_visibility="collapsed"
        )
    
    if email:
        if "@" not in email or "." not in email:
            st.warning("⚠️ Please enter a valid email address")
            return
        
        with st.spinner("🔄 Loading your tickets..."):
            try:
                response = requests.get(
                    f"{BACKEND_URL}/tickets",
                    params={"submitter_email": email}
                )
                
                if response.status_code == 200:
                    tickets = response.json()
                    
                    if not tickets:
                        st.markdown('''
                            <div class="info-box">
                                <div class="info-box-title">📭 No tickets found</div>
                                <div class="info-box-text">
                                    We couldn't find any tickets for this email address. 
                                    Submit your first ticket using the "Submit New Ticket" tab above!
                                </div>
                            </div>
                        ''', unsafe_allow_html=True)
                        return
                    
                    st.success(f"📊 Found **{len(tickets)}** ticket(s) for your account")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Display tickets
                    for ticket in sorted(tickets, key=lambda x: x['id'], reverse=True):
                        priority_icon = "🔴" if ticket.get('is_critical') else "🟢"
                        priority_text = "HIGH PRIORITY" if ticket.get('is_critical') else "NORMAL"
                        
                        with st.expander(
                            f"{priority_icon} Ticket #{ticket['id']}: {ticket['subject']}",
                            expanded=False
                        ):
                            # Header row
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"### Ticket #{ticket['id']}")
                            with col2:
                                st.markdown(format_status_badge(ticket['status']), unsafe_allow_html=True)
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            # Info grid
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown("**📅 Submitted**")
                                created = datetime.fromisoformat(ticket['created_at'].replace('Z', '+00:00'))
                                st.write(created.strftime("%b %d, %Y at %I:%M %p"))
                            
                            with col2:
                                st.markdown("**🏢 Department**")
                                st.write(ticket.get('predicted_queue', 'Not assigned yet'))
                            
                            with col3:
                                st.markdown("**⚡ Priority**")
                                st.write(f"{priority_icon} {priority_text}")
                            
                            st.markdown("---")
                            
                            # Message
                            st.markdown("**📝 Your Message**")
                            st.info(ticket['body'])
                            
                            # Response
                            detail_response = requests.get(f"{BACKEND_URL}/tickets/{ticket['id']}")
                            if detail_response.status_code == 200:
                                detail = detail_response.json()
                                
                                if detail.get('responses'):
                                    st.markdown("---")
                                    st.markdown("**📧 Response from Support Team**")
                                    
                                    for response in detail['responses']:
                                        if response.get('final_body'):
                                            st.success(response['final_body'])
                                            if response.get('approved_at'):
                                                approved_time = datetime.fromisoformat(response['approved_at'].replace('Z', '+00:00'))
                                                st.caption(f"✅ Sent on {approved_time.strftime('%b %d, %Y at %I:%M %p')}")
                                        elif response.get('draft_body'):
                                            if response.get('needs_human_approval'):
                                                st.warning("⏳ **Your response is pending manager approval**")
                                                st.write(response['draft_body'])
                                                st.caption("We'll send the final response within 2 hours")
                                            else:
                                                st.info("📝 **Response drafted and will be sent shortly**")
                                                st.write(response['draft_body'])
                                else:
                                    st.warning("⏳ **Response is being prepared...**")
                                    st.caption("Our AI is working on your ticket. Check back soon!")
                
                else:
                    st.error("❌ Failed to load tickets. Please try again.")
            
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to the server. Please ensure the backend is running.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
