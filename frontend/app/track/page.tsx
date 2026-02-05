'use client';

import { useState } from 'react';
import { Search, Mail, Clock, Building2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { listTickets, getTicket } from '@/lib/api';
import type { Ticket, TicketDetail } from '@/lib/types';
import toast from 'react-hot-toast';

export default function TrackPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<TicketDetail | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !email.includes('@')) {
      toast.error('Please enter a valid email address');
      return;
    }

    setLoading(true);
    try {
      const result = await listTickets({ submitter_email: email });
      setTickets(result);
      
      if (result.length === 0) {
        toast.error('No tickets found for this email');
      } else {
        toast.success(`Found ${result.length} ticket(s)`);
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to fetch tickets');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (ticketId: number) => {
    try {
      const detail = await getTicket(ticketId);
      setSelectedTicket(detail);
    } catch (error: any) {
      toast.error('Failed to load ticket details');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
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

  const getPriorityIcon = (isCritical: boolean) => {
    return isCritical ? '🔴' : '🟢';
  };

  return (
    <div className="min-h-screen gradient-bg">
      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-block bg-cyan-100 text-cyan-700 px-6 py-2 rounded-full font-semibold text-sm mb-4">
            🔍 TRACK TICKETS
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
            Track Your <span className="text-yellow-300">Support Requests</span>
          </h1>
          <p className="text-xl text-white/90 max-w-3xl mx-auto">
            Enter your email address to view all your tickets and their current status
          </p>
        </div>

        {/* Search Form */}
        <div className="glass rounded-3xl p-8 md:p-12 shadow-2xl mb-8">
          <form onSubmit={handleSearch} className="max-w-2xl mx-auto">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email address"
                  className="w-full pl-12 pr-4 py-4 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring focus:ring-cyan-200 transition-all text-lg"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="bg-gradient-to-r from-cyan-500 to-blue-500 text-white py-4 px-8 rounded-xl font-bold text-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 whitespace-nowrap"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="w-5 h-5" />
                    Search Tickets
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Tickets List */}
        {tickets.length > 0 && (
          <div className="space-y-4">
            <div className="glass rounded-2xl p-6 mb-4">
              <h2 className="text-2xl font-bold text-gray-900">
                Found {tickets.length} ticket{tickets.length !== 1 ? 's' : ''}
              </h2>
            </div>

            {tickets.map((ticket) => (
              <div
                key={ticket.id}
                className="glass rounded-2xl p-6 hover:shadow-xl transition-all cursor-pointer"
                onClick={() => handleViewDetails(ticket.id)}
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-start gap-3 mb-2">
                      <span className="text-2xl">
                        {getPriorityIcon(ticket.is_critical || false)}
                      </span>
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-gray-900 mb-1">
                          Ticket #{ticket.id}: {ticket.subject}
                        </h3>
                        <p className="text-gray-600 line-clamp-2">{ticket.body}</p>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-3 mt-4">
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Clock className="w-4 h-4" />
                        <span>
                          {new Date(ticket.created_at).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </span>
                      </div>

                      {ticket.predicted_queue && (
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <Building2 className="w-4 h-4" />
                          <span>{ticket.predicted_queue}</span>
                        </div>
                      )}

                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold uppercase ${getStatusColor(
                          ticket.status
                        )}`}
                      >
                        {ticket.status.replace('_', ' ')}
                      </span>

                      {ticket.is_critical && (
                        <span className="px-3 py-1 rounded-full text-xs font-semibold uppercase bg-red-100 text-red-700">
                          HIGH PRIORITY
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-center">
                    <button className="text-cyan-600 hover:text-cyan-700 font-semibold">
                      View Details →
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Ticket Detail Modal */}
        {selectedTicket && (
          <div
            className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
            onClick={() => setSelectedTicket(null)}
          >
            <div
              className="glass rounded-3xl p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-6">
                <div>
                  <h2 className="text-3xl font-bold text-gray-900 mb-2">
                    Ticket #{selectedTicket.id}
                  </h2>
                  <span
                    className={`px-4 py-2 rounded-full text-sm font-semibold uppercase ${getStatusColor(
                      selectedTicket.status
                    )}`}
                  >
                    {selectedTicket.status.replace('_', ' ')}
                  </span>
                </div>
                <button
                  onClick={() => setSelectedTicket(null)}
                  className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
                >
                  ×
                </button>
              </div>

              {/* Ticket Info */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-white/50 rounded-xl p-4">
                  <div className="text-sm text-gray-600 mb-1">Submitted</div>
                  <div className="font-semibold text-gray-900">
                    {new Date(selectedTicket.created_at).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })}
                  </div>
                </div>

                <div className="bg-white/50 rounded-xl p-4">
                  <div className="text-sm text-gray-600 mb-1">Department</div>
                  <div className="font-semibold text-gray-900">
                    {selectedTicket.predicted_queue || 'Not assigned'}
                  </div>
                </div>

                <div className="bg-white/50 rounded-xl p-4">
                  <div className="text-sm text-gray-600 mb-1">Priority</div>
                  <div className="font-semibold text-gray-900">
                    {selectedTicket.is_critical ? '🔴 HIGH' : '🟢 NORMAL'}
                  </div>
                </div>
              </div>

              {/* Original Message */}
              <div className="mb-6">
                <h3 className="text-lg font-bold text-gray-900 mb-3">Your Message</h3>
                <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">
                    {selectedTicket.subject}
                  </h4>
                  <p className="text-gray-700 whitespace-pre-wrap">{selectedTicket.body}</p>
                </div>
              </div>

              {/* Response */}
              {selectedTicket.responses && selectedTicket.responses.length > 0 && (
                <div>
                  <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                    Response from Support Team
                  </h3>

                  {selectedTicket.responses.map((response, idx) => (
                    <div key={idx} className="mb-4">
                      {response.final_body || response.draft_body ? (
                        <div
                          className={`${
                            response.final_body
                              ? 'bg-green-50 border-l-4 border-green-500'
                              : 'bg-yellow-50 border-l-4 border-yellow-500'
                          } rounded-lg p-4`}
                        >
                          {response.final_subject || response.draft_subject ? (
                            <h4 className="font-semibold text-gray-900 mb-2">
                              {response.final_subject || response.draft_subject}
                            </h4>
                          ) : null}

                          <p className="text-gray-700 whitespace-pre-wrap">
                            {response.final_body || response.draft_body}
                          </p>

                          {!response.final_body && response.needs_human_approval && (
                            <div className="mt-3 flex items-center gap-2 text-sm text-yellow-700">
                              <AlertCircle className="w-4 h-4" />
                              <span>Response pending manager approval</span>
                            </div>
                          )}

                          {response.approved_at && (
                            <div className="mt-3 text-sm text-gray-600">
                              ✅ Sent on{' '}
                              {new Date(response.approved_at).toLocaleDateString('en-US', {
                                month: 'short',
                                day: 'numeric',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="bg-gray-50 border-l-4 border-gray-300 rounded-lg p-4">
                          <div className="flex items-center gap-2 text-gray-600">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                            <span>Response is being prepared...</span>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* No Response Yet */}
              {(!selectedTicket.responses || selectedTicket.responses.length === 0) && (
                <div className="bg-gray-50 border-l-4 border-gray-300 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-gray-600">
                    <Clock className="w-5 h-5" />
                    <span>We're working on your request. You'll receive a response soon!</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && tickets.length === 0 && email && (
          <div className="glass rounded-3xl p-12 text-center">
            <div className="text-6xl mb-4">📭</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">No Tickets Found</h3>
            <p className="text-gray-600 mb-6">
              We couldn't find any tickets for <strong>{email}</strong>
            </p>
            <button
              onClick={() => (window.location.href = '/')}
              className="bg-gradient-to-r from-cyan-500 to-blue-500 text-white py-3 px-8 rounded-xl font-bold hover:shadow-xl transition-all"
            >
              Submit Your First Ticket
            </button>
          </div>
        )}

        {/* Back Home Link */}
        <div className="text-center mt-8">
          <button
            onClick={() => (window.location.href = '/')}
            className="text-white text-lg hover:text-yellow-300 transition-colors font-semibold"
          >
            ← Back to Submit Ticket
          </button>
        </div>
      </div>
    </div>
  );
}
