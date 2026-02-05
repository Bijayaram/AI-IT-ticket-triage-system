// TypeScript types for the IT Support System

export interface Ticket {
  id: number;
  subject: string;
  body: string;
  submitter_name: string;
  submitter_email: string;
  attachment_path?: string;
  status: TicketStatus;
  predicted_queue?: string;
  queue_confidence?: number;
  is_critical?: boolean;
  critical_prob?: number;
  predicted_language?: string;
  created_at: string;
  updated_at: string;
  sent_at?: string;
}

export enum TicketStatus {
  NEW = "NEW",
  TRIAGED = "TRIAGED",
  DRAFTED = "DRAFTED",
  PENDING_APPROVAL = "PENDING_APPROVAL",
  APPROVED = "APPROVED",
  SENT = "SENT",
  REJECTED = "REJECTED",
}

export interface TicketDetail extends Ticket {
  responses: Response[];
  approvals: Approval[];
}

export interface Response {
  id: number;
  ticket_id: number;
  draft_language?: string;
  draft_subject?: string;
  draft_body?: string;
  draft_confidence?: number;
  needs_human_approval: boolean;
  suggested_tags?: string;
  retrieval_context?: string;
  final_subject?: string;
  final_body?: string;
  approved_at?: string;
  created_at: string;
}

export interface Approval {
  id: number;
  ticket_id: number;
  approver_name: string;
  approver_email: string;
  decision: "APPROVED" | "REJECTED";
  decision_notes?: string;
  created_at: string;
}

export interface TriageRequest {
  run_draft: boolean;
}

export interface TriageResponse {
  success: boolean;
  message: string;
  ticket_id: number;
  predicted_queue: string;
  queue_confidence: number;
  critical_prob: number;
  is_critical: boolean;
  predicted_language?: string;
  draft_generated: boolean;
  needs_approval: boolean;
  status: TicketStatus;
}

export interface DashboardSummary {
  total_tickets: number;
  open_tickets: number;
  critical_count: number;
  pending_approval_count: number;
  avg_response_time_hours?: number;
  tickets_by_queue: { [key: string]: number };
  tickets_by_priority: { [key: string]: number };
  tickets_by_status: { [key: string]: number };
}

export interface TicketTimeSeriesPoint {
  date: string;
  count: number;
  critical_count: number;
}

export interface PendingApprovalItem {
  ticket_id: number;
  subject: string;
  submitter_email: string;
  predicted_queue: string;
  critical_prob: number;
  created_at: string;
  draft_subject?: string;
  draft_body?: string;
}

export interface ApprovalPayload {
  approver_name: string;
  approver_email: string;
  decision: "APPROVED" | "REJECTED";
  decision_notes?: string;
  edited_subject?: string;
  edited_body?: string;
}
