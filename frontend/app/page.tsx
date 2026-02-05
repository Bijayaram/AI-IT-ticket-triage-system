'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Send, Loader2, CheckCircle2 } from 'lucide-react';
import { createTicket, triageTicket } from '@/lib/api';
import toast from 'react-hot-toast';

export default function HomePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [ticketId, setTicketId] = useState<number | null>(null);
  const [triageResult, setTriageResult] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLHTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);

    try {
      const formData = new FormData(e.currentTarget);
      
      // Create ticket
      const ticket = await createTicket(formData);
      setTicketId(ticket.id);
      
      // Run triage
      const result = await triageTicket(ticket.id, { run_draft: true });
      setTriageResult(result);
      
      setSubmitted(true);
      toast.success(`Ticket #${ticket.id} created successfully!`);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to submit ticket');
    } finally {
      setLoading(false);
    }
  };

  if (submitted && ticketId && triageResult) {
    return (
      <div className="min-h-screen gradient-bg flex items-center justify-center p-4">
        <div className="glass rounded-3xl p-12 max-w-4xl w-full shadow-2xl">
          <div className="text-center mb-8">
            <CheckCircle2 className="w-20 h-20 text-green-500 mx-auto mb-4" />
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Ticket Submitted Successfully!
            </h1>
            <p className="text-xl text-gray-600">
              Your request has been received and analyzed by our AI system
            </p>
          </div>

          <div className="bg-gradient-to-r from-cyan-500 to-blue-500 rounded-2xl p-8 text-white mb-8">
            <h2 className="text-2xl font-bold mb-4">Ticket #{ticketId}</h2>
            <p className="text-lg opacity-90">
              Save this number to track your ticket status
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-white border-2 border-gray-200 rounded-xl p-6 text-center">
              <div className="text-4xl mb-2">🏢</div>
              <div className="text-sm text-gray-600 mb-1">Assigned To</div>
              <div className="text-lg font-bold text-gray-900">
                {triageResult.predicted_queue}
              </div>
            </div>

            <div className="bg-white border-2 border-gray-200 rounded-xl p-6 text-center">
              <div className="text-4xl mb-2">
                {triageResult.is_critical ? '🔴' : '🟢'}
              </div>
              <div className="text-sm text-gray-600 mb-1">Priority</div>
              <div className="text-lg font-bold text-gray-900">
                {triageResult.is_critical ? 'HIGH' : 'NORMAL'}
              </div>
            </div>

            <div className="bg-white border-2 border-gray-200 rounded-xl p-6 text-center">
              <div className="text-4xl mb-2">
                {triageResult.needs_approval ? '⏳' : '⚡'}
              </div>
              <div className="text-sm text-gray-600 mb-1">Status</div>
              <div className="text-lg font-bold text-gray-900">
                {triageResult.needs_approval ? 'Pending Review' : 'Processing'}
              </div>
            </div>
          </div>

          {triageResult.needs_approval ? (
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6 rounded-lg mb-8">
              <h3 className="font-bold text-yellow-900 mb-2">⏳ Manager Approval Required</h3>
              <p className="text-yellow-800">
                Your ticket has been marked as high priority and requires manager approval. 
                You'll receive a response within 2 hours.
              </p>
            </div>
          ) : (
            <div className="bg-green-50 border-l-4 border-green-400 p-6 rounded-lg mb-8">
              <h3 className="font-bold text-green-900 mb-2">✅ Auto-Processing</h3>
              <p className="text-green-800">
                Your ticket is being processed automatically. You'll receive a response shortly.
              </p>
            </div>
          )}

          <div className="flex gap-4">
            <button
              onClick={() => router.push('/track')}
              className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-500 text-white py-4 px-8 rounded-xl font-bold text-lg hover:shadow-lg transition-all"
            >
              Track My Ticket
            </button>
            <button
              onClick={() => window.location.reload()}
              className="flex-1 bg-white border-2 border-gray-300 text-gray-700 py-4 px-8 rounded-xl font-bold text-lg hover:border-gray-400 transition-all"
            >
              Submit Another
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen gradient-bg">
      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-block bg-cyan-100 text-cyan-700 px-6 py-2 rounded-full font-semibold text-sm mb-4">
            📋 SUPPORT CENTER
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
            How to Submit a <span className="text-yellow-300">Support Ticket</span>
          </h1>
          <p className="text-xl text-white/90 max-w-3xl mx-auto">
            Our AI-powered system instantly routes your request to the right team and 
            provides intelligent assistance. Get help in minutes, not hours.
          </p>
        </div>

        {/* Form */}
        <div className="glass rounded-3xl p-8 md:p-12 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Step 1 */}
            <div>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-cyan-500 text-white rounded-full flex items-center justify-center font-bold text-lg">
                  1
                </div>
                <h2 className="text-2xl font-bold text-gray-900">Your Information</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    name="submitter_name"
                    required
                    placeholder="John Doe"
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring focus:ring-cyan-200 transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    name="submitter_email"
                    required
                    placeholder="john.doe@company.com"
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring focus:ring-cyan-200 transition-all"
                  />
                </div>
              </div>
            </div>

            {/* Step 2 */}
            <div>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-cyan-500 text-white rounded-full flex items-center justify-center font-bold text-lg">
                  2
                </div>
                <h2 className="text-2xl font-bold text-gray-900">Describe Your Issue</h2>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    What's the problem?
                  </label>
                  <input
                    type="text"
                    name="subject"
                    required
                    placeholder="e.g., Can't access company VPN from home"
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring focus:ring-cyan-200 transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Give us the details
                  </label>
                  <textarea
                    name="body"
                    required
                    rows={6}
                    placeholder="Please provide as much detail as possible:&#10;&#10;• What were you trying to do?&#10;• What happened instead?&#10;• Any error messages you saw?&#10;• When did this start happening?"
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-cyan-500 focus:ring focus:ring-cyan-200 transition-all resize-none"
                  />
                </div>
                <p className="text-sm text-gray-500 italic">
                  💡 Pro tip: The more details you provide, the faster we can help!
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-cyan-500 text-white rounded-full flex items-center justify-center font-bold text-lg">
                  3
                </div>
                <h2 className="text-2xl font-bold text-gray-900">Submit Your Ticket</h2>
              </div>

              <div className="flex justify-center">
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-gradient-to-r from-cyan-500 to-blue-500 text-white py-4 px-12 rounded-xl font-bold text-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-6 h-6 animate-spin" />
                      Submitting...
                    </>
                  ) : (
                    <>
                      <Send className="w-6 h-6" />
                      Submit Ticket
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>
        </div>

        {/* Track Link */}
        <div className="text-center mt-8">
          <button
            onClick={() => router.push('/track')}
            className="text-white text-lg hover:text-yellow-300 transition-colors font-semibold"
          >
            Already have a ticket? Track it here →
          </button>
        </div>
      </div>
    </div>
  );
}
