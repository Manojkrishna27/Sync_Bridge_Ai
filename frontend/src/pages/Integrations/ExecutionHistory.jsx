import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import Breadcrumb from '../../components/Common/Breadcrumb';
import { TableSkeleton } from '../../components/Common/LoadingSkeleton';
import EmptyState from '../../components/Common/EmptyState';
import { History, Search, Filter, Eye, ChevronLeft, ChevronRight, Activity, Clock, AlertOctagon, CheckCircle2, X } from 'lucide-react';

export default function ExecutionHistory() {
  const [executions, setExecutions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchCID, setSearchCID] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [meta, setMeta] = useState({ total: 0, pages: 1 });

  // Detail Modal State
  const [selectedExecId, setSelectedExecId] = useState(null);
  const [execDetail, setExecDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await api.get('/audit-logs', {
        params: {
          page,
          per_page: 10,
          search: searchCID || undefined,
          action: statusFilter || undefined
        }
      });
      setExecutions(res.data.data || []);
      setMeta(res.data.meta || { total: 0, pages: 1 });
    } catch (err) {
      console.error("Failed to fetch execution history:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchExecutionDetail = async (execId) => {
    setDetailLoading(true);
    try {
      const res = await api.get(`/executions/${execId}`);
      setExecDetail(res.data);
    } catch (err) {
      console.error("Failed to fetch execution trace:", err);
    } finally {
      setDetailLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, statusFilter]);

  const handleOpenDetail = (execId) => {
    setSelectedExecId(execId);
    fetchExecutionDetail(execId);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <Breadcrumb items={[{ label: "Integrations", href: "/integrations" }, { label: "Execution History" }]} />
          <h1 className="text-2xl font-black text-gray-900 dark:text-gray-100">Integration Execution History & Traces</h1>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 flex flex-col md:flex-row gap-3 justify-between items-center shadow-sm">
        <form onSubmit={(e) => { e.preventDefault(); setPage(1); fetchHistory(); }} className="relative w-full md:w-96">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-gray-400" />
          <input
            type="text"
            placeholder="Search Correlation ID or resource..."
            value={searchCID}
            onChange={(e) => setSearchCID(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm"
          />
        </form>
      </div>

      {/* Table */}
      {loading ? (
        <TableSkeleton rows={5} cols={5} />
      ) : executions.length === 0 ? (
        <EmptyState
          title="No execution logs found"
          description="Execute integration pipelines to record execution traces and duration metrics."
          icon={History}
        />
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600 dark:text-gray-300">
              <thead className="bg-gray-50 dark:bg-gray-900/60 text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider border-b border-gray-200 dark:border-gray-700">
                <tr>
                  <th className="px-6 py-4 font-bold">Correlation ID</th>
                  <th className="px-6 py-4 font-bold">Action / Event</th>
                  <th className="px-6 py-4 font-bold">Resource</th>
                  <th className="px-6 py-4 font-bold">User</th>
                  <th className="px-6 py-4 font-bold">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-700/60">
                {executions.map((ex) => (
                  <tr key={ex.id} className="hover:bg-gray-50/60 dark:hover:bg-gray-700/30 transition-colors">
                    <td className="px-6 py-4 font-mono text-xs text-indigo-600 dark:text-indigo-400 font-bold">
                      {ex.correlation_id || 'N/A'}
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 text-xs font-bold rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200">
                        {ex.action}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-medium text-gray-800 dark:text-gray-200 text-xs">{ex.resource_type} ({ex.resource_id})</td>
                    <td className="px-6 py-4 text-xs">{ex.user_email}</td>
                    <td className="px-6 py-4 text-xs text-gray-400">
                      {ex.created_at ? new Date(ex.created_at).toLocaleString() : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="p-4 bg-gray-50 dark:bg-gray-900/60 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between text-xs text-gray-500">
            <span>Showing page {page} of {meta.pages} ({meta.total} history entries)</span>
            <div className="flex space-x-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg disabled:opacity-50"
              >
                Previous
              </button>
              <button
                disabled={page >= meta.pages}
                onClick={() => setPage(page + 1)}
                className="px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
