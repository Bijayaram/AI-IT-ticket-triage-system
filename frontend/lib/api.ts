// API client for IT Support System backend
import axios from 'axios';
import type {
  Ticket,
  TicketDetail,
  TriageRequest,
  TriageResponse,
  DashboardSummary,
  TicketTimeSeriesPoint,
  PendingApprovalItem,
  ApprovalPayload,
  TicketStatus,
} from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================================================
// TICKET ENDPOINTS
// ============================================================================

export const createTicket = async (data: FormData): Promise<Ticket> => {
  const response = await api.post<Ticket>('/tickets', data, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getTicket = async (ticketId: number): Promise<TicketDetail> => {
  const response = await api.get<TicketDetail>(`/tickets/${ticketId}`);
  return response.data;
};

export const listTickets = async (params?: {
  status?: TicketStatus;
  queue?: string;
  is_critical?: boolean;
  submitter_email?: string;
  skip?: number;
  limit?: number;
}): Promise<Ticket[]> => {
  const response = await api.get<Ticket[]>('/tickets', { params });
  return response.data;
};

export const triageTicket = async (
  ticketId: number,
  data: TriageRequest
): Promise<TriageResponse> => {
  const response = await api.post<TriageResponse>(
    `/tickets/${ticketId}/triage`,
    data
  );
  return response.data;
};

// ============================================================================
// APPROVAL ENDPOINTS
// ============================================================================

export const getPendingApprovals = async (): Promise<PendingApprovalItem[]> => {
  const response = await api.get<PendingApprovalItem[]>('/approvals/pending');
  return response.data;
};

export const approveTicket = async (
  ticketId: number,
  data: ApprovalPayload
): Promise<{ success: boolean; message: string }> => {
  const response = await api.post(`/tickets/${ticketId}/approve`, data);
  return response.data;
};

export const rejectTicket = async (
  ticketId: number,
  data: ApprovalPayload
): Promise<{ success: boolean; message: string }> => {
  const response = await api.post(`/tickets/${ticketId}/reject`, data);
  return response.data;
};

// ============================================================================
// DASHBOARD ENDPOINTS
// ============================================================================

export const getDashboardSummary = async (): Promise<DashboardSummary> => {
  const response = await api.get<DashboardSummary>('/dashboard/summary');
  return response.data;
};

export const getTicketTimeseries = async (
  days: number = 30
): Promise<TicketTimeSeriesPoint[]> => {
  const response = await api.get<TicketTimeSeriesPoint[]>('/dashboard/timeseries', {
    params: { days },
  });
  return response.data;
};

// ============================================================================
// HEALTH CHECK
// ============================================================================

export const healthCheck = async (): Promise<{ status: string; service: string; version: string }> => {
  const response = await api.get('/');
  return response.data;
};

export default api;
