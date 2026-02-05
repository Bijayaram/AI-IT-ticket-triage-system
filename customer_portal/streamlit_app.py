"""
Customer Portal - Streamlit App #1
Modern, attractive UI for submitting tickets and tracking status.
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
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern Custom CSS with gradients and animations
st.markdown("""
    <style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Modern gradient background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Main container with glassmorphism */
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        margin-top: 2rem;
    }
    
    /* Modern header with gradient text */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeInDown 1s ease-in;
    }
    
    .sub-header {
        text-align: center;
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        animation: fadeIn 1.5s ease-in;
    }
    
    /* Modern tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        transform: translateY(-2px);
    }
    
    /* Modern input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #e5e7eb;
        padding: 12px;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Modern buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 12px 32px;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
    }
    
    /* Status badges with modern design */
    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-new { 
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        color: white;
    }
    .status-triaged { 
        background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%);
        color: white;
    }
    .status-drafted {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: white;
    }
    .status-pending_approval { 
        background: linear-gradient(135deg, #fb923c 0%, #f97316 100%);
        color: white;
    }
    .status-approved { 
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
        color: white;
    }
    .status-sent { 
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    .status-rejected { 
        background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
        color: white;
    }
    
    /* Modern metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    .metric-card h3 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
    }
    
    .metric-card p {
        margin: 0.5rem 0 0 0;
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Modern expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
        border-radius: 12px;
        font-weight: 600;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #e5e7eb 0%, #d1d5db 100%);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Success/Error/Warning with modern style */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 12px;
        padding: 1rem;
        border: none;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Form styling */
    .stForm {
        background: #f9fafb;
        padding: 2rem;
        border-radius: 16px;
        border: 2px solid #e5e7eb;
    }
    
    /* Ticket card */
    .ticket-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        border: 2px solid #e5e7eb;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .ticket-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        transform: translateY(-2px);
    }
    
    /* Priority badge */
    .priority-high {
        color: #ef4444;
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    .priority-normal {
        color: #10b981;
        font-weight: 600;
        font-size: 1.1rem;
    }
    </style>
""", unsafe_allow_html=True)


def format_status_badge(status: str) -> str:
    """Format status as HTML badge"""
    status_lower = status.lower().replace(' ', '_')
    return f'<span class="status-badge status-{status_lower}">{status}</span>'


def main():
    """Main app"""
    st.markdown('<p class="main-header">🎫 IT Support Portal</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your 24/7 AI-powered IT support assistant</p>', unsafe_allow_html=True)
    
    # Navigation with modern tabs
    tab1, tab2 = st.tabs(["📝 Submit New Ticket", "📊 Track My Tickets"])
    
    with tab1:
        submit_ticket_page()
    
    with tab2:
        my_tickets_page()


def submit_ticket_page():
    """Submit new ticket page with modern design"""
    st.markdown("### ✨ Tell us how we can help you")
    st.write("Our AI will automatically route your request to the right team and provide intelligent assistance.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("ticket_form", clear_on_submit=True):
        # Personal information
        st.markdown("#### 👤 Your Information")
        col1, col2 = st.columns(2)
        
        with col1:
            submitter_name = st.text_input(
                "Full Name",
                placeholder="e.g., John Doe",
                help="Enter your full name"
            )
        
        with col2:
            submitter_email = st.text_input(
                "Email Address",
                placeholder="e.g., john.doe@company.com",
                help="We'll use this to send updates"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Issue details
        st.markdown("#### 🎯 Issue Details")
        
        subject = st.text_input(
            "Subject",
            placeholder="e.g., Unable to access company VPN",
            help="Brief description of your issue"
        )
        
        body = st.text_area(
            "Detailed Description",
            placeholder="Please describe your issue in detail. Include:\n• What you were trying to do\n• What happened instead\n• Any error messages you saw\n• Steps to reproduce the issue",
            height=200,
            help="The more details you provide, the better we can help!"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.form_submit_button("🚀 Submit Ticket", use_container_width=True)
        
        if submit_button:
            # Validate
            if not submitter_name or not submitter_email or not subject or not body:
                st.error("⚠️ Please fill in all fields")
                return
            
            # Email validation
            if "@" not in submitter_email or "." not in submitter_email:
                st.error("⚠️ Please enter a valid email address")
                return
            
            # Submit ticket
            with st.spinner("🔄 Processing your request..."):
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
                        
                        st.success(f"✅ Ticket #{ticket_id} submitted successfully!")
                        
                        # Auto-triage
                        st.info("🤖 AI is analyzing your ticket...")
                        triage_response = requests.post(
                            f"{BACKEND_URL}/tickets/{ticket_id}/triage",
                            json={"run_draft": True}
                        )
                        
                        if triage_response.status_code == 200:
                            triage_result = triage_response.json()
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            st.markdown("### 📋 Ticket Information")
                            
                            # Modern metric cards
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h3>🏢</h3>
                                    <p style="font-size: 1.2rem; font-weight: 600; margin-top: 0.5rem;">{triage_result["predicted_queue"]}</p>
                                    <p style="font-size: 0.9rem;">Assigned Department</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                priority_icon = "🔴" if triage_result["is_critical"] else "🟢"
                                priority_text = "HIGH" if triage_result["is_critical"] else "NORMAL"
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h3>{priority_icon}</h3>
                                    <p style="font-size: 1.2rem; font-weight: 600; margin-top: 0.5rem;">{priority_text}</p>
                                    <p style="font-size: 0.9rem;">Priority Level</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col3:
                                status_icon = "⏳" if triage_result["needs_approval"] else "⚡"
                                status_text = "Pending Review" if triage_result["needs_approval"] else "Auto-Processing"
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h3>{status_icon}</h3>
                                    <p style="font-size: 1.2rem; font-weight: 600; margin-top: 0.5rem;">{status_text}</p>
                                    <p style="font-size: 0.9rem;">Current Status</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            if triage_result["needs_approval"]:
                                st.warning("⏳ Your ticket is marked as **critical** and requires manager approval. You'll receive a response within 2 hours.")
                            else:
                                st.success("✅ Your ticket is being processed automatically. You'll receive a response shortly!")
                            
                            st.info(f"💡 **Save this Ticket ID:** **#{ticket_id}**\n\nYou can track your ticket status in the 'Track My Tickets' tab using your email address.")
                    
                    else:
                        st.error(f"❌ Failed to submit ticket. Please try again.")
                
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to the server. Please ensure the backend is running.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


def my_tickets_page():
    """View tickets by email with modern design"""
    st.markdown("### 🔍 Track Your Tickets")
    st.write("Enter your email address to view all your submitted tickets and their current status.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input(
            "📧 Your Email Address",
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
                        st.info(f"📭 No tickets found for **{email}**\n\nSubmit your first ticket in the 'Submit New Ticket' tab!")
                        return
                    
                    st.success(f"📊 Found **{len(tickets)}** ticket(s)")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Display tickets with modern card design
                    for ticket in sorted(tickets, key=lambda x: x['id'], reverse=True):
                        priority_class = "priority-high" if ticket.get('is_critical') else "priority-normal"
                        priority_icon = "🔴" if ticket.get('is_critical') else "🟢"
                        priority_text = "HIGH PRIORITY" if ticket.get('is_critical') else "NORMAL"
                        
                        with st.expander(
                            f"{priority_icon} Ticket #{ticket['id']}: {ticket['subject']}",
                            expanded=False
                        ):
                            # Header with status
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"### 🎫 Ticket #{ticket['id']}")
                            with col2:
                                st.markdown(format_status_badge(ticket['status']), unsafe_allow_html=True)
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            # Ticket details in columns
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown("**📅 Submitted**")
                                created = datetime.fromisoformat(ticket['created_at'].replace('Z', '+00:00'))
                                st.write(created.strftime("%b %d, %Y %I:%M %p"))
                            
                            with col2:
                                st.markdown("**🏢 Department**")
                                st.write(ticket.get('predicted_queue', 'Not assigned'))
                            
                            with col3:
                                st.markdown("**⚡ Priority**")
                                st.markdown(f'<span class="{priority_class}">{priority_icon} {priority_text}</span>', unsafe_allow_html=True)
                            
                            st.markdown("---")
                            
                            # Message
                            st.markdown("**📝 Your Message**")
                            st.info(ticket['body'])
                            
                            # Get detailed info for responses
                            detail_response = requests.get(f"{BACKEND_URL}/tickets/{ticket['id']}")
                            if detail_response.status_code == 200:
                                detail = detail_response.json()
                                
                                # Show responses
                                if detail.get('responses'):
                                    st.markdown("---")
                                    st.markdown("**📧 Response from Support Team**")
                                    
                                    for response in detail['responses']:
                                        if response.get('final_body'):
                                            st.success(response['final_body'])
                                            if response.get('approved_at'):
                                                approved_time = datetime.fromisoformat(response['approved_at'].replace('Z', '+00:00'))
                                                st.caption(f"✅ Sent: {approved_time.strftime('%b %d, %Y %I:%M %p')}")
                                        elif response.get('draft_body'):
                                            if response.get('needs_human_approval'):
                                                st.warning("⏳ **Response pending manager approval**")
                                                st.write(response['draft_body'])
                                            else:
                                                st.info("📝 **Draft response generated**")
                                                st.write(response['draft_body'])
                                else:
                                    st.warning("⏳ Response is being prepared. Please check back soon!")
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                
                else:
                    st.error("❌ Failed to load tickets. Please try again.")
            
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to the server. Please ensure the backend is running.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
