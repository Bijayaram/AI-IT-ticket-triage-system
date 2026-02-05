# 📘 IT Ticket Triage System - Usage Examples

## 🎯 Complete Walkthrough

This guide provides step-by-step examples of using the system.

---

## 🚀 Quick Start (5 Minutes)

### 1. Start All Services

**Terminal 1:**
```bash
cd D:\Capstone
start_backend.bat
```
Wait for: `INFO: Application startup complete`

**Terminal 2:**
```bash
cd D:\Capstone
start_customer.bat
```
Browser opens to: http://localhost:8501

**Terminal 3:**
```bash
cd D:\Capstone  
start_manager.bat
```
Browser opens to: http://localhost:8502

---

## 📝 Example 1: Submit Non-Critical Ticket

### Customer Action

1. Open http://localhost:8501
2. Fill form:
   - **Name**: `Sarah Johnson`
   - **Email**: `sarah.johnson@company.com`
   - **Subject**: `Forgot password for employee portal`
   - **Body**: 
     ```
     Hi, I forgot my password for the employee self-service portal.
     Can you please reset it? My employee ID is EMP12345.
     ```
3. Click **"Submit Ticket"**

### System Response

**Automatic Triage:**
- ✅ Ticket ID created: `TKT-2026-00001`
- 🏷️ Department: `IT Support` (confidence: 92%)
- ⚠️ Criticality: `Low` (probability: 0.15)
- 📧 Status: `DRAFTED` → `SENT` (auto-sent, no approval needed)

**Customer sees:**
```
✅ Ticket submitted successfully!
Ticket ID: TKT-2026-00001
Status: Sent
Department: IT Support

Your ticket has been automatically processed and a response 
has been sent to your email.
```

**Email sent to customer:**
```
Subject: Re: Forgot password for employee portal

Hello Sarah,

Thank you for contacting IT Support. I can help you reset 
your password for the employee self-service portal.

For security reasons, please follow these steps:

1. Visit the password reset page: https://portal.company.com/reset
2. Enter your employee ID: EMP12345
3. Follow the verification steps sent to your registered email
4. Create a new strong password (min 12 characters)

If you encounter any issues, please reply to this email or 
create a new ticket.

Best regards,
IT Support Team
```

---

## ⚠️ Example 2: Submit Critical Ticket

### Customer Action

1. Open http://localhost:8501
2. Fill form:
   - **Name**: `Mike Chen`
   - **Email**: `mike.chen@company.com`
   - **Subject**: `Production server down - URGENT`
   - **Body**:
     ```
     URGENT: Our main production server (PROD-DB-01) is completely 
     unresponsive. All customer-facing services are down. Started 
     at 14:30 today. Need immediate assistance!
     
     Error log shows: Connection timeout after 30s
     Server IP: 192.168.1.100
     ```
3. Click **"Submit Ticket"**

### System Response

**Automatic Triage:**
- ✅ Ticket ID created: `TKT-2026-00002`
- 🏷️ Department: `Technical Support` (confidence: 88%)
- 🔥 Criticality: `HIGH` (probability: 0.96)
- ⏸️ Status: `PENDING_APPROVAL` (requires manager review)

**Customer sees:**
```
✅ Ticket submitted successfully!
Ticket ID: TKT-2026-00002
Status: Pending Approval
Department: Technical Support
Priority: HIGH

Your urgent ticket has been escalated to our senior support 
team for immediate review. You will receive a response shortly.
```

**Manager Dashboard shows:**
```
🔔 New Critical Ticket Pending Approval

Ticket #TKT-2026-00002
Subject: Production server down - URGENT
Priority: HIGH
Criticality Score: 96%
Department: Technical Support
Submitted: 2 minutes ago

[VIEW DETAILS] [APPROVE] [EDIT]
```

---

## 👨‍💼 Example 3: Manager Approval Workflow

### Manager Action

1. Open http://localhost:8502
2. Login with password: `admin123`
3. Navigate to **"Pending Critical Approvals"** tab
4. See ticket `TKT-2026-00002` in list
5. Click **"View Details"**

### Manager Sees:

**Original Ticket:**
```
From: Mike Chen (mike.chen@company.com)
Subject: Production server down - URGENT

URGENT: Our main production server (PROD-DB-01) is completely 
unresponsive. All customer-facing services are down...
```

**ML Predictions:**
```
Department: Technical Support (88% confidence)
Criticality: HIGH (96% probability)
```

**Similar Past Tickets (RAG Context):**
```
1. Ticket #5234 - "Database server not responding" (95% similar)
   Resolution: "Restarted database service, checked connection pool..."
   
2. Ticket #7891 - "Production outage - server timeout" (92% similar)
   Resolution: "Identified network configuration issue..."
   
3. Ticket #3456 - "Server connectivity issues" (89% similar)
   Resolution: "Increased timeout settings, optimized queries..."
```

**Gemini Draft Response:**
```json
{
  "language": "en",
  "subject": "RE: Production server down - URGENT [Priority Response]",
  "body": "Hello Mike,\n\nThank you for reporting this critical issue. We understand the urgency and have escalated this to our senior technical team.\n\nImmediate Actions Taken:\n1. Alert sent to on-call senior engineer\n2. Server health monitoring activated\n3. Backup systems being prepared\n\nInitial Diagnostic Steps:\n- Check server physical connectivity\n- Review system logs for PROD-DB-01\n- Verify network connectivity to 192.168.1.100\n- Test failover procedures\n\nOur senior engineer will contact you within 15 minutes at mike.chen@company.com. In the meantime, please:\n\n1. Do NOT restart the server manually\n2. Preserve all error logs\n3. Document any changes made before 14:30\n4. Prepare access credentials for remote diagnostics\n\nWe are treating this as Priority 1 and will update you every 30 minutes until resolved.\n\nBest regards,\nTechnical Support Team\nOn-Call: +1-555-0123",
  "confidence": 0.94,
  "needs_human_approval": true,
  "suggested_tags": ["production", "server-down", "critical", "urgent", "database"]
}
```

### Manager Options:

**Option A: Approve as-is**
```
✅ Click "Approve & Send"
→ Response sent immediately
→ Status: APPROVED → SENT
→ Notification logged
```

**Option B: Edit then send**
```
✏️ Click "Edit Response"
→ Modify response text:
  "Adding: Direct phone number of senior engineer John Smith: +1-555-0199"
→ Click "Save & Send"
→ Modified response sent
→ Status: APPROVED → SENT
```

**Option C: Reject / Request more info**
```
❌ Click "Reject"
→ Select reason: "Need more diagnostic info"
→ Add note: "Please run 'netstat -an' and provide output"
→ Status: NEEDS_INFO
→ Customer notified
```

---

## 📊 Example 4: View Analytics

### Manager Dashboard - KPI View

**Summary Cards:**
```
┌─────────────────────┬──────────────────────┬────────────────────┐
│  Total Tickets      │   Open Tickets       │  Critical Tickets  │
│      1,543          │        89            │        12          │
│   ↑ 5% this week    │   ↓ 12% from avg     │   ↑ 2 today        │
└─────────────────────┴──────────────────────┴────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  Avg First Response Time: 2.5 hours                            │
│  Target SLA: 4 hours                                           │
│  ✅ 94% within SLA                                             │
└────────────────────────────────────────────────────────────────┘
```

**Charts:**

1. **Tickets by Department (Pie Chart)**
```
Technical Support: 35%
IT Support: 28%
Customer Service: 15%
Product Support: 12%
Billing: 6%
Others: 4%
```

2. **Tickets by Priority (Bar Chart)**
```
High:     ████████░░ 123 (8%)
Medium:   ████████████████████ 789 (51%)
Low:      ████████████ 631 (41%)
```

3. **Tickets Over Time (Line Chart)**
```
        Tickets
100│                           ╱╲
 80│                    ╱╲    ╱  ╲
 60│          ╱╲      ╱  ╲  ╱    ╲
 40│    ╱╲   ╱  ╲    ╱    ╲╱
 20│   ╱  ╲ ╱    ╲  ╱
  0└─────────────────────────────→
    Mon  Tue Wed Thu Fri Sat Sun
```

4. **Critical Rate Trend**
```
Criticality %
12│                              ╱
10│                         ╱╲  ╱
 8│                    ╱╲  ╱  ╲╱
 6│              ╱╲   ╱  ╲╱
 4│   ╱╲   ╱╲   ╱  ╲ ╱
 2└─────────────────────────────→
   Week 1  Week 2  Week 3  Week 4
```

---

## 🔍 Example 5: Search and Filter

### Manager Dashboard - All Tickets View

**Filters Applied:**
```
Department: [Technical Support]
Priority: [High]
Status: [Open, Pending Approval]
Date Range: [Last 7 days]
```

**Results Table:**
```
┌──────────┬────────────────────────────┬──────────┬─────────┬───────────────────┐
│ Ticket # │ Subject                    │ Priority │ Status  │ Created           │
├──────────┼────────────────────────────┼──────────┼─────────┼───────────────────┤
│ #00002   │ Production server down     │ HIGH     │ PENDING │ 2 hours ago       │
│ #00156   │ Database query timeout     │ HIGH     │ OPEN    │ 1 day ago         │
│ #00098   │ API endpoint returning 500 │ HIGH     │ OPEN    │ 3 days ago        │
│ #00187   │ SSL certificate expired    │ HIGH     │ PENDING │ 5 days ago        │
└──────────┴────────────────────────────┴──────────┴─────────┴───────────────────┘

Showing 4 of 12 total high-priority tickets
[Export to CSV] [Clear Filters]
```

**Click on any ticket to view full details**

---

## 🧪 Example 6: API Testing

### Using curl

**1. Submit Ticket via API:**
```bash
curl -X POST "http://localhost:8000/tickets" \
  -H "Content-Type: multipart/form-data" \
  -F "name=Test User" \
  -F "email=test@company.com" \
  -F "subject=API Test Ticket" \
  -F "body=This is a test ticket submitted via API"
```

**Response:**
```json
{
  "id": 123,
  "ticket_id": "TKT-2026-00123",
  "status": "NEW",
  "name": "Test User",
  "email": "test@company.com",
  "subject": "API Test Ticket",
  "created_at": "2026-02-04T15:30:00Z"
}
```

**2. Trigger Triage:**
```bash
curl -X POST "http://localhost:8000/tickets/123/triage"
```

**Response:**
```json
{
  "ticket_id": 123,
  "predicted_queue": "IT Support",
  "queue_confidence": 0.78,
  "critical_prob": 0.12,
  "is_critical": false,
  "draft_response": {
    "language": "en",
    "subject": "Re: API Test Ticket",
    "body": "Thank you for contacting us...",
    "confidence": 0.85,
    "needs_human_approval": false,
    "suggested_tags": ["test", "api"]
  },
  "similar_tickets": [
    {
      "ticket_id": "TKT-2026-00045",
      "subject": "Testing API integration",
      "similarity": 0.92
    }
  ]
}
```

**3. Get Dashboard Summary:**
```bash
curl "http://localhost:8000/dashboard/summary"
```

**Response:**
```json
{
  "total_tickets": 1543,
  "open_tickets": 89,
  "critical_count": 12,
  "avg_response_time_hours": 2.5,
  "by_queue": {
    "IT Support": 432,
    "Technical Support": 567,
    "Customer Service": 234,
    "Product Support": 189,
    "Billing and Payments": 121
  },
  "by_priority": {
    "high": 123,
    "medium": 789,
    "low": 631
  },
  "time_series": [
    {
      "date": "2026-02-04",
      "count": 45,
      "critical_count": 3
    }
  ]
}
```

**4. Get Pending Approvals:**
```bash
curl "http://localhost:8000/approvals/pending"
```

**Response:**
```json
[
  {
    "ticket_id": 124,
    "ticket_subject": "Server outage",
    "priority": "high",
    "predicted_queue": "Technical Support",
    "critical_prob": 0.95,
    "created_at": "2026-02-04T14:00:00Z",
    "draft_response": {...}
  }
]
```

**5. Approve Ticket:**
```bash
curl -X POST "http://localhost:8000/tickets/124/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "approver_name": "Manager Smith",
    "edited_response": null
  }'
```

**Response:**
```json
{
  "ticket_id": 124,
  "status": "APPROVED",
  "approved_by": "Manager Smith",
  "approved_at": "2026-02-04T15:45:00Z",
  "sent_at": "2026-02-04T15:45:01Z"
}
```

---

## 📸 Screenshot Checklist

### Customer Portal Screenshots

1. **Submit Ticket Form**
   - Clean, simple form layout
   - Name, Email, Subject, Body fields
   - Optional file attachment
   - Submit button

2. **Ticket Submitted Confirmation**
   - Success message
   - Ticket ID displayed
   - Current status
   - Assigned department

3. **Track Ticket Status**
   - Ticket ID input
   - Status timeline
   - Department assignment
   - Response preview (if available)

### Manager Dashboard Screenshots

1. **Login Page**
   - Simple password authentication
   - Company logo/branding

2. **KPI Dashboard**
   - Summary cards (total, open, critical)
   - Pie chart (tickets by department)
   - Bar chart (tickets by priority)
   - Line chart (tickets over time)

3. **Pending Critical Approvals**
   - List of tickets requiring approval
   - Ticket details view
   - ML predictions shown
   - Similar tickets (RAG context)
   - Gemini draft response (JSON)
   - Action buttons (Approve, Edit, Reject)

4. **All Tickets Table**
   - Filterable, sortable table
   - Search functionality
   - Status indicators
   - Quick actions

5. **Ticket Detail View**
   - Full ticket content
   - Complete response history
   - Audit trail
   - Status changes timeline

### Backend API Screenshots

1. **Swagger UI** (http://localhost:8000/docs)
   - All endpoints listed
   - Interactive testing
   - Request/response schemas

2. **Terminal Output**
   - Startup logs
   - Request logs
   - ML predictions logged
   - Email sending logs

---

## 🎬 Demo Script (5-Minute Presentation)

### Minute 1: Introduction
> "I built an AI-powered IT ticket triage system with human-in-the-loop approval. 
> It uses local ML for decisions and Gemini for response generation."

**Show:** Architecture diagram from README

### Minute 2: Submit Ticket (Customer)
> "Customers submit tickets through a simple web interface."

**Demo:** 
- Open customer portal
- Submit urgent production issue
- Show ticket ID and status

### Minute 3: Automatic Triage
> "The system automatically analyzes the ticket using ML embeddings, 
> predicts department and criticality, retrieves similar past tickets, 
> and generates a draft response using Gemini with RAG context."

**Show:**
- API logs showing triage process
- ML predictions (department: 88%, criticality: 96%)
- Similar tickets retrieved
- Generated draft response

### Minute 4: Manager Approval
> "Critical tickets require manager approval before sending. 
> The manager can review, edit, or reject the AI-generated response."

**Demo:**
- Open manager dashboard
- Show pending critical ticket
- Review draft response
- Approve and send

### Minute 5: Analytics & Results
> "The system provides real-time analytics and has achieved 51.6% F1 score 
> for 10-department classification, significantly better than random."

**Show:**
- KPI dashboard with charts
- Performance metrics table
- System architecture summary

**Close:** 
> "This demonstrates end-to-end ML system design, human-in-the-loop workflows, 
> and production-ready code with proper error handling and monitoring."

---

## 🔗 Quick Links

- **Customer Portal**: http://localhost:8501
- **Manager Dashboard**: http://localhost:8502
- **API Docs**: http://localhost:8000/docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📝 Testing Checklist

### Functional Tests

- [ ] Submit ticket with all fields
- [ ] Submit ticket with minimal fields
- [ ] Submit ticket with attachment
- [ ] Track ticket status
- [ ] View ticket details
- [ ] Trigger manual triage
- [ ] Manager login
- [ ] View pending approvals
- [ ] Approve ticket
- [ ] Edit and send ticket
- [ ] Reject ticket
- [ ] View KPI dashboard
- [ ] Filter tickets
- [ ] Search tickets
- [ ] Export data

### Edge Cases

- [ ] Empty subject/body
- [ ] Very long text (>10K chars)
- [ ] Special characters in text
- [ ] Invalid email format
- [ ] Duplicate ticket submission
- [ ] Concurrent approvals
- [ ] Network timeout handling
- [ ] Gemini API failure handling
- [ ] Database connection issues

### Performance Tests

- [ ] Load 100 tickets rapidly
- [ ] Triage 50 tickets in parallel
- [ ] Dashboard with 10K+ tickets
- [ ] Search with complex filters
- [ ] Embedding generation time
- [ ] FAISS query time
- [ ] API response time (<500ms)

---

**Built with ❤️ for demonstration purposes**
