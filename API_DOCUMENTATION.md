# IT Support System - API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently uses simple password authentication for manager dashboard (demo mode).

---

## Endpoints

### Health Check

#### `GET /`
Health check endpoint to verify API is running.

**Response:**
```json
{
  "status": "ok",
  "service": "IT Ticket Triage System API",
  "version": "1.0.0"
}
```

---

## Ticket Endpoints

### Create Ticket

#### `POST /tickets`
Create a new support ticket.

**Content-Type:** `multipart/form-data`

**Request Body:**
```
subject: string (required)
body: string (required)
submitter_name: string (required)
submitter_email: string (required)
attachment: file (optional, max 10MB)
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "subject": "Cannot access VPN",
  "body": "I'm unable to connect to the company VPN...",
  "submitter_name": "John Doe",
  "submitter_email": "john@company.com",
  "attachment_path": null,
  "status": "NEW",
  "predicted_queue": null,
  "queue_confidence": null,
  "is_critical": null,
  "critical_prob": null,
  "predicted_language": null,
  "created_at": "2026-02-03T10:00:00Z",
  "updated_at": "2026-02-03T10:00:00Z",
  "sent_at": null
}
```

---

### Get Ticket

#### `GET /tickets/{ticket_id}`
Get detailed information about a specific ticket.

**Path Parameters:**
- `ticket_id` (integer): The ticket ID

**Response:** `200 OK`
```json
{
  "id": 1,
  "subject": "Cannot access VPN",
  "body": "I'm unable to connect to the company VPN...",
  "submitter_name": "John Doe",
  "submitter_email": "john@company.com",
  "status": "SENT",
  "predicted_queue": "Network and Connectivity",
  "queue_confidence": 0.89,
  "is_critical": false,
  "critical_prob": 0.23,
  "responses": [
    {
      "id": 1,
      "ticket_id": 1,
      "draft_subject": "RE: Cannot access VPN",
      "draft_body": "Hi John, ...",
      "draft_confidence": 0.92,
      "needs_human_approval": false,
      "final_subject": "RE: Cannot access VPN",
      "final_body": "Hi John, ...",
      "approved_at": "2026-02-03T10:05:00Z",
      "created_at": "2026-02-03T10:02:00Z"
    }
  ],
  "approvals": []
}
```

**Error Responses:**
- `404 Not Found`: Ticket does not exist

---

### List Tickets

#### `GET /tickets`
List tickets with optional filters.

**Query Parameters:**
- `status` (string, optional): Filter by status (NEW, TRIAGED, DRAFTED, PENDING_APPROVAL, APPROVED, SENT, REJECTED)
- `queue` (string, optional): Filter by predicted department
- `is_critical` (boolean, optional): Filter by criticality
- `submitter_email` (string, optional): Filter by submitter email
- `skip` (integer, optional, default: 0): Number of records to skip (pagination)
- `limit` (integer, optional, default: 100): Maximum number of records to return

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "subject": "Cannot access VPN",
    "status": "SENT",
    "predicted_queue": "Network and Connectivity",
    "is_critical": false,
    ...
  },
  {
    "id": 2,
    "subject": "Server is down",
    "status": "PENDING_APPROVAL",
    "predicted_queue": "Hardware and Infrastructure",
    "is_critical": true,
    ...
  }
]
```

---

### Triage Ticket

#### `POST /tickets/{ticket_id}/triage`
Run ML triage on a ticket (department classification, criticality prediction, and optional draft generation).

**Path Parameters:**
- `ticket_id` (integer): The ticket ID

**Request Body:**
```json
{
  "run_draft": true
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Triage completed successfully",
  "ticket_id": 1,
  "predicted_queue": "Network and Connectivity",
  "queue_confidence": 0.89,
  "critical_prob": 0.23,
  "is_critical": false,
  "predicted_language": "en",
  "draft_generated": true,
  "needs_approval": false,
  "status": "DRAFTED"
}
```

**Error Responses:**
- `404 Not Found`: Ticket does not exist
- `500 Internal Server Error`: Triage failed

---

## Approval Endpoints

### Get Pending Approvals

#### `GET /approvals/pending`
Get list of tickets that require manager approval.

**Response:** `200 OK`
```json
[
  {
    "ticket_id": 2,
    "subject": "Production server offline",
    "submitter_email": "alice@company.com",
    "predicted_queue": "Hardware and Infrastructure",
    "critical_prob": 0.95,
    "created_at": "2026-02-03T09:30:00Z",
    "draft_subject": "RE: Production server offline [CRITICAL]",
    "draft_body": "Dear Alice, ..."
  }
]
```

---

### Approve Ticket

#### `POST /tickets/{ticket_id}/approve`
Approve a ticket and send the response to the customer.

**Path Parameters:**
- `ticket_id` (integer): The ticket ID

**Request Body:**
```json
{
  "approver_name": "Manager Name",
  "approver_email": "manager@company.com",
  "decision": "APPROVED",
  "decision_notes": "Looks good",
  "edited_subject": "RE: Production server offline [URGENT]",
  "edited_body": "Dear Alice, ..."
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Ticket approved and response sent"
}
```

**Error Responses:**
- `404 Not Found`: Ticket does not exist
- `500 Internal Server Error`: Approval failed

---

### Reject Ticket

#### `POST /tickets/{ticket_id}/reject`
Reject a ticket (request changes or more information).

**Path Parameters:**
- `ticket_id` (integer): The ticket ID

**Request Body:**
```json
{
  "approver_name": "Manager Name",
  "approver_email": "manager@company.com",
  "decision": "REJECTED",
  "decision_notes": "Response needs to be more detailed"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Ticket rejected"
}
```

**Error Responses:**
- `404 Not Found`: Ticket does not exist
- `500 Internal Server Error`: Rejection failed

---

## Dashboard Endpoints

### Get Dashboard Summary

#### `GET /dashboard/summary`
Get KPI summary for the manager dashboard.

**Response:** `200 OK`
```json
{
  "total_tickets": 150,
  "open_tickets": 25,
  "critical_count": 3,
  "pending_approval_count": 2,
  "avg_response_time_hours": 3.5,
  "tickets_by_queue": {
    "Network and Connectivity": 45,
    "Account and Access Management": 35,
    "Hardware and Infrastructure": 20,
    ...
  },
  "tickets_by_priority": {
    "high": 15,
    "medium": 135
  },
  "tickets_by_status": {
    "NEW": 5,
    "TRIAGED": 3,
    "DRAFTED": 8,
    "PENDING_APPROVAL": 2,
    "APPROVED": 7,
    "SENT": 120,
    "REJECTED": 5
  }
}
```

---

### Get Ticket Timeseries

#### `GET /dashboard/timeseries`
Get ticket counts over time for trend visualization.

**Query Parameters:**
- `days` (integer, optional, default: 30): Number of days to include

**Response:** `200 OK`
```json
[
  {
    "date": "2026-01-05",
    "count": 12,
    "critical_count": 2
  },
  {
    "date": "2026-01-06",
    "count": 15,
    "critical_count": 1
  },
  ...
]
```

---

## Error Handling

All endpoints follow standard HTTP status codes:

### Success Codes
- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully

### Client Error Codes
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error

### Server Error Codes
- `500 Internal Server Error`: Server-side error

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limiting
Currently no rate limiting (demo mode). In production, implement rate limiting based on:
- IP address
- API key
- User tier

---

## CORS
CORS is enabled for all origins in development. In production, configure allowed origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## WebSocket Support
Not currently implemented. For real-time updates, consider adding WebSocket endpoints for:
- Live ticket status updates
- Real-time dashboard metrics
- Notification push

---

## Pagination
List endpoints support pagination via `skip` and `limit` parameters:

```
GET /tickets?skip=0&limit=20  # First page
GET /tickets?skip=20&limit=20  # Second page
```

---

## Example Usage

### cURL Examples

**Create a ticket:**
```bash
curl -X POST http://localhost:8000/tickets \
  -F "subject=Cannot access email" \
  -F "body=I'm getting an authentication error" \
  -F "submitter_name=John Doe" \
  -F "submitter_email=john@company.com"
```

**Triage a ticket:**
```bash
curl -X POST http://localhost:8000/tickets/1/triage \
  -H "Content-Type: application/json" \
  -d '{"run_draft": true}'
```

**Get dashboard summary:**
```bash
curl -X GET http://localhost:8000/dashboard/summary
```

---

## JavaScript/TypeScript Examples

See `frontend/lib/api.ts` for the complete TypeScript API client implementation.

**Create a ticket:**
```typescript
import { createTicket } from '@/lib/api';

const formData = new FormData();
formData.append('subject', 'Cannot access email');
formData.append('body', 'I\'m getting an authentication error');
formData.append('submitter_name', 'John Doe');
formData.append('submitter_email', 'john@company.com');

const ticket = await createTicket(formData);
console.log(`Created ticket #${ticket.id}`);
```

**Get pending approvals:**
```typescript
import { getPendingApprovals } from '@/lib/api';

const pending = await getPendingApprovals();
console.log(`${pending.length} tickets awaiting approval`);
```

---

**Last Updated**: 2026-02-03  
**API Version**: 1.0.0
