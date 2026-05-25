'use client';

import { useState, useEffect } from 'react';
import { 
  Users, 
  Clock, 
  AlertCircle, 
  CheckCircle2, 
  XCircle, 
  TrendingUp,
  Send,
  Eye,
  Edit3,
  Shield,
  Lock,
  LogOut,
  List,
  BarChart3,
  Filter,
  Search,
  Ticket as TicketIcon
} from 'lucide-react';
import { 
  getPendingApprovals, 
  approveTicket, 
  rejectTicket, 
  getTicket, 
  listTickets,
  getDashboardSummary 
} from '@/lib/api';
import type { PendingApprovalItem, TicketDetail, Ticket, DashboardSummary } from '@/lib/types';
import toast from 'react-hot-toast';

type TabType = 'dashboard' | 'approvals' | 'tickets';

const MANAGER_PASSWORD = 'admin123'; // In production, use environment variable

export default function ManagerDashboard() {
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');

  // Tab navigation
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');

  // Dashboard state
  const [dashboardData, setDashboardData] = useState<DashboardSummary | null>(null);

  // Approvals state
  const [pendingApprovals, setPendingApprovals] = useState<PendingApprovalItem[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<TicketDetail | null>(null);
  const [approving, setApproving] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [editedSubject, setEditedSubject] = useState('');
  const [editedBody, setEditedBody] = useState('');

  // All tickets state
  const [allTickets, setAllTickets] = useState<Ticket[]>([]);
  const [filteredTickets, setFilteredTickets] = useState<Ticket[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [showCriticalOnly, setShowCriticalOnly] = useState(false);

  // Loading states
  const [loading, setLoading] = useState(false);

  // Load data when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      loadDashboardData();
      loadPendingApprovals();
      loadAllTickets();
    }
  }, [isAuthenticated]);

  // Filter tickets when filters change
  useEffect(() => {
    filterTickets();
  }, [allTickets, statusFilter, searchTerm, showCriticalOnly]);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (password === MANAGER_PASSWORD) {
      setIsAuthenticated(true);
      setLoginError('');
      toast.success('Welcome, Manager!');
    } else {
      setLoginError('Invalid password');
      toast.error('Invalid password');
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setPassword('');
    setActiveTab('dashboard');
    toast.success('Logged out successfully');
  };

  const loadDashboardData = async () => {
    try {
      const data = await getDashboardSummary();
      setDashboardData(data);
    } catch (error: any) {
      toast.error('Failed to load dashboard data');
    }
  };

  const loadPendingApprovals = async () => {
    try {
      setLoading(true);
      const data = await getPendingApprovals();
      setPendingApprovals(data);
    } catch (error: any) {
      toast.error('Failed to load pending approvals');
    } finally {
      setLoading(false);
    }
  };

  const loadAllTickets = async () => {
    try {
      setLoading(true);
      const data = await listTickets({});
      setAllTickets(data);
    } catch (error: any) {
      toast.error('Failed to load tickets');
    } finally {
      setLoading(false);
    }
  };

  const filterTickets = () => {
    let filtered = [...allTickets];

    // Status filter
    if (statusFilter !== 'ALL') {
      filtered = filtered.filter(t => t.status === statusFilter);
    }

    // Critical filter
    if (showCriticalOnly) {
      filtered = filtered.filter(t => t.is_critical);
    }

    // Search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(t => 
        t.subject.toLowerCase().includes(term) ||
        t.body.toLowerCase().includes(term) ||
        t.submitter_email.toLowerCase().includes(term) ||
        t.id.toString().includes(term)
      );
    }

    setFilteredTickets(filtered);
  };

  const handleViewTicket = async (ticketId: number) => {
    try {
      const ticket = await getTicket(ticketId);
      console.log('Ticket data received:', ticket);
      console.log('Responses:', ticket.responses);
      console.log('Number of responses:', ticket.responses?.length || 0);
      
      setSelectedTicket(ticket);
      
      // Initialize edit fields with draft content
      if (ticket.responses && ticket.responses.length > 0) {
        console.log('First response draft:', {
          subject: ticket.responses[0].draft_subject,
          body: ticket.responses[0].draft_body,
          confidence: ticket.responses[0].draft_confidence
        });
        setEditedSubject(ticket.responses[0].draft_subject || '');
        setEditedBody(ticket.responses[0].draft_body || '');
      } else {
        console.warn('No responses found in ticket data');
      }
      setEditMode(false);
    } catch (error: any) {
      console.error('Failed to load ticket:', error);
      toast.error('Failed to load ticket details');
    }
  };

  const handleApprove = async () => {
    if (!selectedTicket) return;

    try {
      setApproving(true);
      
      const approvalData = {
        approver_name: 'Manager',
        approver_email: 'manager@company.com',
        decision: editMode ? 'EDITED_AND_APPROVED' : 'APPROVED',
        decision_notes: editMode ? 'Edited and approved' : 'Approved as drafted',
        edited_subject: editMode ? editedSubject : undefined,
        edited_body: editMode ? editedBody : undefined,
      };

      await approveTicket(selectedTicket.id, approvalData);
      
      toast.success('✅ Response approved and sent!');
      setSelectedTicket(null);
      loadPendingApprovals();
      loadAllTickets();
      loadDashboardData();
    } catch (error: any) {
      toast.error('Failed to approve ticket');
    } finally {
      setApproving(false);
    }
  };

  const handleReject = async () => {
    if (!selectedTicket) return;

    const reason = prompt('Please provide a reason for rejection:');
    if (!reason) return;

    try {
      setApproving(true);
      
      const rejectionData = {
        approver_name: 'Manager',
        approver_email: 'manager@company.com',
        decision: 'REJECTED',
        decision_notes: reason,
      };

      await rejectTicket(selectedTicket.id, rejectionData);
      
      toast.success('❌ Response rejected');
      setSelectedTicket(null);
      loadPendingApprovals();
      loadAllTickets();
      loadDashboardData();
    } catch (error: any) {
      toast.error('Failed to reject ticket');
    } finally {
      setApproving(false);
    }
  };

  const getTimeSince = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const hours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      NEW: 'bg-blue-100 text-blue-700',
      TRIAGED: 'bg-purple-100 text-purple-700',
      DRAFTED: 'bg-yellow-100 text-yellow-700',
      PENDING_APPROVAL: 'bg-orange-100 text-orange-700',
      APPROVED: 'bg-green-100 text-green-700',
      SENT: 'bg-green-100 text-green-700',
      REJECTED: 'bg-red-100 text-red-700',
    };
    return colors[status] || 'bg-gray-100 text-gray-700';
  };

  // Login Screen
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center p-4">
        <div className="glass rounded-3xl p-12 max-w-md w-full">
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Lock className="w-10 h-10 text-purple-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Manager Login</h1>
            <p className="text-gray-600">Enter password to access the dashboard</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring focus:ring-purple-200 transition-all"
                autoFocus
              />
              {loginError && (
                <p className="text-red-600 text-sm mt-2">{loginError}</p>
              )}
            </div>

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-4 px-6 rounded-xl font-bold text-lg hover:shadow-xl transition-all"
            >
              Access Dashboard
            </button>

            <div className="text-center text-sm text-gray-500">
              💡 Default password: <code className="bg-gray-100 px-2 py-1 rounded">admin123</code>
            </div>
          </form>

          <div className="text-center mt-8">
            <button
              onClick={() => (window.location.href = '/')}
              className="text-gray-600 hover:text-purple-600 transition-colors font-semibold"
            >
              ← Back to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Main Dashboard
  return (
    <div className="min-h-screen gradient-bg">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="inline-block bg-purple-100 text-purple-700 px-6 py-2 rounded-full font-semibold text-sm mb-2">
              🛡️ MANAGER DASHBOARD
            </div>
            <h1 className="text-4xl font-bold text-white">
              Support <span className="text-yellow-300">Management</span>
            </h1>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 bg-white/20 hover:bg-white/30 text-white px-6 py-3 rounded-xl font-semibold transition-all"
          >
            <LogOut className="w-5 h-5" />
            Logout
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="glass rounded-2xl p-2 mb-8 flex gap-2">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${
              activeTab === 'dashboard'
                ? 'bg-white text-purple-600 shadow-lg'
                : 'text-gray-600 hover:bg-white/50'
            }`}
          >
            <BarChart3 className="w-5 h-5" />
            Dashboard
          </button>
          <button
            onClick={() => setActiveTab('approvals')}
            className={`flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${
              activeTab === 'approvals'
                ? 'bg-white text-purple-600 shadow-lg'
                : 'text-gray-600 hover:bg-white/50'
            }`}
          >
            <Clock className="w-5 h-5" />
            Approvals
            {pendingApprovals.length > 0 && (
              <span className="bg-orange-500 text-white text-xs px-2 py-1 rounded-full">
                {pendingApprovals.length}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('tickets')}
            className={`flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${
              activeTab === 'tickets'
                ? 'bg-white text-purple-600 shadow-lg'
                : 'text-gray-600 hover:bg-white/50'
            }`}
          >
            <List className="w-5 h-5" />
            All Tickets
            <span className="text-xs text-gray-500">
              ({allTickets.length})
            </span>
          </button>
        </div>

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="glass rounded-2xl p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
                    <TicketIcon className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 font-medium">Total Tickets</div>
                    <div className="text-3xl font-bold text-gray-900">
                      {dashboardData?.total_tickets || 0}
                    </div>
                  </div>
                </div>
              </div>

              <div className="glass rounded-2xl p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center">
                    <Clock className="w-6 h-6 text-orange-600" />
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 font-medium">Open Tickets</div>
                    <div className="text-3xl font-bold text-gray-900">
                      {dashboardData?.open_tickets || 0}
                    </div>
                  </div>
                </div>
              </div>

              <div className="glass rounded-2xl p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-red-100 flex items-center justify-center">
                    <AlertCircle className="w-6 h-6 text-red-600" />
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 font-medium">Critical</div>
                    <div className="text-3xl font-bold text-gray-900">
                      {dashboardData?.critical_count || 0}
                    </div>
                  </div>
                </div>
              </div>

              <div className="glass rounded-2xl p-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-yellow-100 flex items-center justify-center">
                    <Shield className="w-6 h-6 text-yellow-600" />
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 font-medium">Pending Approval</div>
                    <div className="text-3xl font-bold text-gray-900">
                      {dashboardData?.pending_approval_count || 0}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Status Distribution */}
            <div className="glass rounded-2xl p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Tickets by Status</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {dashboardData?.tickets_by_status && Object.entries(dashboardData.tickets_by_status).map(([status, count]) => (
                  <div key={status} className="bg-white/50 rounded-xl p-4">
                    <div className={`inline-block px-3 py-1 rounded-lg text-sm font-semibold mb-2 ${getStatusColor(status)}`}>
                      {status.replace('_', ' ')}
                    </div>
                    <div className="text-2xl font-bold text-gray-900">{count}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Department Distribution */}
            {dashboardData?.tickets_by_queue && Object.keys(dashboardData.tickets_by_queue).length > 0 && (
              <div className="glass rounded-2xl p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Tickets by Department</h2>
                <div className="space-y-3">
                  {Object.entries(dashboardData.tickets_by_queue).map(([dept, count]) => {
                    const total = dashboardData.total_tickets || 1;
                    const percentage = ((count / total) * 100).toFixed(1);
                    return (
                      <div key={dept}>
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-semibold text-gray-700">{dept}</span>
                          <span className="text-gray-600">{count} ({percentage}%)</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div 
                            className="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full transition-all"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="glass rounded-2xl p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Quick Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  onClick={() => setActiveTab('approvals')}
                  className="bg-gradient-to-r from-orange-500 to-red-500 text-white p-6 rounded-xl font-bold hover:shadow-xl transition-all text-left"
                >
                  <Clock className="w-8 h-8 mb-2" />
                  <div className="text-lg">Review Approvals</div>
                  <div className="text-sm opacity-90">{pendingApprovals.length} pending</div>
                </button>

                <button
                  onClick={() => {
                    setActiveTab('tickets');
                    setShowCriticalOnly(true);
                  }}
                  className="bg-gradient-to-r from-red-500 to-pink-500 text-white p-6 rounded-xl font-bold hover:shadow-xl transition-all text-left"
                >
                  <AlertCircle className="w-8 h-8 mb-2" />
                  <div className="text-lg">Critical Tickets</div>
                  <div className="text-sm opacity-90">{allTickets.filter(t => t.is_critical).length} critical</div>
                </button>

                <button
                  onClick={() => setActiveTab('tickets')}
                  className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white p-6 rounded-xl font-bold hover:shadow-xl transition-all text-left"
                >
                  <List className="w-8 h-8 mb-2" />
                  <div className="text-lg">View All Tickets</div>
                  <div className="text-sm opacity-90">{allTickets.length} total</div>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Approvals Tab */}
        {activeTab === 'approvals' && (
          <div className="space-y-4">
            <div className="glass rounded-2xl p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Pending Approvals</h2>
              <p className="text-gray-600">Review and approve AI-generated responses before sending to customers</p>
            </div>

            {loading ? (
              <div className="glass rounded-3xl p-12 text-center">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-500 mx-auto mb-4"></div>
                <p className="text-gray-600 font-medium">Loading...</p>
              </div>
            ) : pendingApprovals.length === 0 ? (
              <div className="glass rounded-3xl p-12 text-center">
                <div className="text-6xl mb-4">✅</div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">All Clear!</h3>
                <p className="text-gray-600">No tickets pending approval at this time.</p>
              </div>
            ) : (
              pendingApprovals.map((item) => (
                <div
                  key={item.ticket_id}
                  className="glass rounded-2xl p-6 hover:shadow-xl transition-all"
                >
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-start gap-3 mb-3">
                        <div className="w-10 h-10 rounded-lg bg-orange-100 flex items-center justify-center flex-shrink-0">
                          <AlertCircle className="w-6 h-6 text-orange-600" />
                        </div>
                        <div className="flex-1">
                          <h3 className="text-xl font-bold text-gray-900 mb-1">
                            Ticket #{item.ticket_id}: {item.subject}
                          </h3>
                          <div className="flex flex-wrap gap-3 text-sm text-gray-600">
                            <span className="flex items-center gap-1">
                              <Users className="w-4 h-4" />
                              {item.submitter_email}
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="w-4 h-4" />
                              {getTimeSince(item.created_at)}
                            </span>
                            {item.predicted_queue && (
                              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-lg font-medium">
                                {item.predicted_queue}
                              </span>
                            )}
                            {item.critical_prob > 0.7 && (
                              <span className="px-2 py-1 bg-red-100 text-red-700 rounded-lg font-medium">
                                🔴 Critical {(item.critical_prob * 100).toFixed(0)}%
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => handleViewTicket(item.ticket_id)}
                      className="bg-gradient-to-r from-cyan-500 to-blue-500 text-white py-3 px-6 rounded-xl font-bold hover:shadow-xl transition-all flex items-center gap-2 whitespace-nowrap"
                    >
                      <Eye className="w-5 h-5" />
                      Review & Approve
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* All Tickets Tab */}
        {activeTab === 'tickets' && (
          <div className="space-y-4">
            {/* Filters */}
            <div className="glass rounded-2xl p-6">
              <div className="flex flex-col lg:flex-row gap-4">
                {/* Search */}
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      placeholder="Search tickets by ID, subject, email..."
                      className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring focus:ring-purple-200"
                    />
                  </div>
                </div>

                {/* Status Filter */}
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring focus:ring-purple-200"
                >
                  <option value="ALL">All Status</option>
                  <option value="NEW">New</option>
                  <option value="TRIAGED">Triaged</option>
                  <option value="DRAFTED">Drafted</option>
                  <option value="PENDING_APPROVAL">Pending Approval</option>
                  <option value="APPROVED">Approved</option>
                  <option value="SENT">Sent</option>
                  <option value="REJECTED">Rejected</option>
                </select>

                {/* Critical Filter */}
                <button
                  onClick={() => setShowCriticalOnly(!showCriticalOnly)}
                  className={`px-6 py-3 rounded-xl font-semibold transition-all whitespace-nowrap ${
                    showCriticalOnly
                      ? 'bg-red-500 text-white'
                      : 'bg-white border-2 border-gray-200 text-gray-700 hover:border-red-500'
                  }`}
                >
                  <span className="flex items-center gap-2">
                    <Filter className="w-5 h-5" />
                    {showCriticalOnly ? 'Critical Only' : 'All Priorities'}
                  </span>
                </button>
              </div>

              <div className="mt-4 text-sm text-gray-600">
                Showing <span className="font-semibold">{filteredTickets.length}</span> of <span className="font-semibold">{allTickets.length}</span> tickets
              </div>
            </div>

            {/* Tickets List */}
            {loading ? (
              <div className="glass rounded-3xl p-12 text-center">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-500 mx-auto mb-4"></div>
                <p className="text-gray-600 font-medium">Loading tickets...</p>
              </div>
            ) : filteredTickets.length === 0 ? (
              <div className="glass rounded-3xl p-12 text-center">
                <div className="text-6xl mb-4">🔍</div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">No Tickets Found</h3>
                <p className="text-gray-600">Try adjusting your filters or search term.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {filteredTickets.map((ticket) => (
                  <div
                    key={ticket.id}
                    className="glass rounded-xl p-6 hover:shadow-lg transition-all cursor-pointer"
                    onClick={() => handleViewTicket(ticket.id)}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="font-bold text-gray-900">#{ticket.id}</span>
                          {ticket.is_critical && (
                            <span className="text-red-500 text-lg">🔴</span>
                          )}
                          <span className={`px-3 py-1 rounded-lg text-xs font-semibold uppercase ${getStatusColor(ticket.status)}`}>
                            {ticket.status.replace('_', ' ')}
                          </span>
                          {ticket.predicted_queue && (
                            <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-lg text-xs font-semibold">
                              {ticket.predicted_queue}
                            </span>
                          )}
                        </div>
                        <h3 className="text-lg font-bold text-gray-900 mb-1">
                          {ticket.subject}
                        </h3>
                        <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                          {ticket.body}
                        </p>
                        <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                          <span className="flex items-center gap-1">
                            <Users className="w-4 h-4" />
                            {ticket.submitter_email}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            {getTimeSince(ticket.created_at)}
                          </span>
                        </div>
                      </div>
                      <Eye className="w-5 h-5 text-gray-400" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Ticket Detail Modal (same as before) */}
        {selectedTicket && (
          <div
            className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
            onClick={() => setSelectedTicket(null)}
          >
            <div
              className="glass rounded-3xl p-8 max-w-5xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-3xl font-bold text-gray-900 mb-2">
                    Ticket #{selectedTicket.id}
                  </h2>
                  <div className="flex gap-2">
                    <span className={`px-4 py-2 rounded-full text-sm font-semibold uppercase ${getStatusColor(selectedTicket.status)}`}>
                      {selectedTicket.status.replace('_', ' ')}
                    </span>
                    {selectedTicket.is_critical && (
                      <span className="px-4 py-2 rounded-full text-sm font-semibold uppercase bg-red-100 text-red-700">
                        🔴 CRITICAL
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => setSelectedTicket(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
                >
                  ×
                </button>
              </div>

              {/* Customer Message */}
              <div className="mb-6">
                <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <Users className="w-5 h-5 text-blue-500" />
                  Customer Message
                </h3>
                <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-4">
                  <div className="text-sm text-gray-600 mb-2">
                    From: <span className="font-semibold">{selectedTicket.submitter_name}</span> ({selectedTicket.submitter_email})
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-2">
                    {selectedTicket.subject}
                  </h4>
                  <p className="text-gray-700 whitespace-pre-wrap">{selectedTicket.body}</p>
                </div>
              </div>

              {/* AI-Generated Response */}
              {selectedTicket.responses && selectedTicket.responses.length > 0 && (
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                      <Shield className="w-5 h-5 text-purple-500" />
                      AI-Generated Response
                    </h3>
                    {!editMode && selectedTicket.status === 'PENDING_APPROVAL' && (
                      <button
                        onClick={() => setEditMode(true)}
                        className="flex items-center gap-2 text-cyan-600 hover:text-cyan-700 font-semibold"
                      >
                        <Edit3 className="w-4 h-4" />
                        Edit Response
                      </button>
                    )}
                  </div>

                  {editMode ? (
                    <div className="bg-yellow-50 border-l-4 border-yellow-500 rounded-lg p-4">
                      <div className="mb-4">
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          Subject:
                        </label>
                        <input
                          type="text"
                          value={editedSubject}
                          onChange={(e) => setEditedSubject(e.target.value)}
                          className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-cyan-500 focus:ring focus:ring-cyan-200"
                        />
                      </div>
                      <div className="mb-4">
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          Body:
                        </label>
                        <textarea
                          value={editedBody}
                          onChange={(e) => setEditedBody(e.target.value)}
                          rows={8}
                          className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-cyan-500 focus:ring focus:ring-cyan-200"
                        />
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => setEditMode(false)}
                          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300"
                        >
                          Cancel Edit
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-green-50 border-l-4 border-green-500 rounded-lg p-4">
                      {selectedTicket.responses[0].draft_subject && (
                        <h4 className="font-semibold text-gray-900 mb-2">
                          {selectedTicket.responses[0].draft_subject}
                        </h4>
                      )}
                      {selectedTicket.responses[0].draft_body ? (
                        <p className="text-gray-700 whitespace-pre-wrap">
                          {selectedTicket.responses[0].draft_body}
                        </p>
                      ) : (
                        <p className="text-gray-500 italic">
                          No draft response generated yet. AI may still be processing this ticket.
                        </p>
                      )}
                      {selectedTicket.responses[0].draft_confidence && (
                        <div className="mt-3 text-sm text-gray-600">
                          AI Confidence: {(selectedTicket.responses[0].draft_confidence * 100).toFixed(0)}%
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
              
              {/* Show message if no responses at all */}
              {(!selectedTicket.responses || selectedTicket.responses.length === 0) && selectedTicket.status === 'PENDING_APPROVAL' && (
                <div className="mb-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                    <Shield className="w-5 h-5 text-purple-500" />
                    AI-Generated Response
                  </h3>
                  <div className="bg-yellow-50 border-l-4 border-yellow-500 rounded-lg p-4">
                    <p className="text-gray-700 font-semibold mb-2">
                      ⚠️ No AI response found for this ticket
                    </p>
                    <p className="text-gray-600 text-sm mb-3">
                      This ticket is marked as PENDING_APPROVAL but has no AI-generated response. 
                      This may happen if:
                    </p>
                    <ul className="text-gray-600 text-sm list-disc list-inside mb-3 space-y-1">
                      <li>The ticket was manually set to PENDING_APPROVAL</li>
                      <li>The draft generation failed or timed out</li>
                      <li>The Gemini API key is missing or invalid</li>
                    </ul>
                    <p className="text-gray-600 text-sm">
                      <strong>Solution:</strong> Try re-triaging the ticket from the backend to generate a response, 
                      or manually create a response to approve.
                    </p>
                  </div>
                </div>
              )}

              {/* ML Analysis */}
              <div className="mb-6">
                <h3 className="text-lg font-bold text-gray-900 mb-3">ML Analysis</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="bg-white/50 rounded-xl p-3">
                    <div className="text-xs text-gray-600 mb-1">Queue</div>
                    <div className="font-semibold text-gray-900 text-sm">
                      {selectedTicket.predicted_queue || 'N/A'}
                    </div>
                  </div>
                  <div className="bg-white/50 rounded-xl p-3">
                    <div className="text-xs text-gray-600 mb-1">Confidence</div>
                    <div className="font-semibold text-gray-900 text-sm">
                      {selectedTicket.queue_confidence ? (selectedTicket.queue_confidence * 100).toFixed(0) + '%' : 'N/A'}
                    </div>
                  </div>
                  <div className="bg-white/50 rounded-xl p-3">
                    <div className="text-xs text-gray-600 mb-1">Critical Prob</div>
                    <div className="font-semibold text-gray-900 text-sm">
                      {selectedTicket.critical_prob ? (selectedTicket.critical_prob * 100).toFixed(0) + '%' : 'N/A'}
                    </div>
                  </div>
                  <div className="bg-white/50 rounded-xl p-3">
                    <div className="text-xs text-gray-600 mb-1">Language</div>
                    <div className="font-semibold text-gray-900 text-sm">
                      {selectedTicket.predicted_language?.toUpperCase() || 'N/A'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              {selectedTicket.status === 'PENDING_APPROVAL' && (
                <div className="flex flex-col sm:flex-row gap-4">
                  <button
                    onClick={handleApprove}
                    disabled={approving}
                    className="flex-1 bg-gradient-to-r from-green-500 to-emerald-500 text-white py-4 px-6 rounded-xl font-bold text-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {approving ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        Approving...
                      </>
                    ) : (
                      <>
                        <CheckCircle2 className="w-5 h-5" />
                        {editMode ? 'Approve Edited Response' : 'Approve & Send'}
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleReject}
                    disabled={approving}
                    className="flex-1 bg-gradient-to-r from-red-500 to-pink-500 text-white py-4 px-6 rounded-xl font-bold text-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    <XCircle className="w-5 h-5" />
                    Reject
                  </button>

                  <button
                    onClick={() => setSelectedTicket(null)}
                    className="px-6 py-4 bg-gray-200 text-gray-700 rounded-xl font-bold text-lg hover:bg-gray-300 transition-all"
                  >
                    Close
                  </button>
                </div>
              )}

              {selectedTicket.status !== 'PENDING_APPROVAL' && (
                <div className="flex justify-end">
                  <button
                    onClick={() => setSelectedTicket(null)}
                    className="px-8 py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-bold text-lg hover:shadow-xl transition-all"
                  >
                    Close
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Back Home Link */}
        <div className="text-center mt-8">
          <button
            onClick={() => (window.location.href = '/')}
            className="text-white text-lg hover:text-yellow-300 transition-colors font-semibold"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}
