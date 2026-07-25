import React, { useEffect, useState } from 'react';
import api from '../../services/api';
import Breadcrumb from '../../components/Common/Breadcrumb';
import { CardSkeleton } from '../../components/Common/LoadingSkeleton';
import { Users, Workflow, Server, Code, Key, Activity, RefreshCw } from 'lucide-react';

export default function DashboardOverview() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/dashboard/summary');
      setSummary(response.data);
    } catch (err) {
      console.error("Failed to fetch dashboard summary:", err);
      setError("Failed to load dashboard metrics.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  if (loading) {
    return (
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        <Breadcrumb items={[{ label: "Overview" }]} />
        <CardSkeleton count={5} />
      </div>
    );
  }

  const cards = [
    { label: 'Total Clients', value: summary?.total_clients || 0, icon: Users, color: 'text-blue-600 bg-blue-50 dark:bg-blue-950/40 dark:text-blue-400' },
    { label: 'Active Integrations', value: summary?.active_integrations || 0, icon: Workflow, color: 'text-green-600 bg-green-50 dark:bg-green-950/40 dark:text-green-400' },
    { label: 'Production', value: summary?.production_integrations || 0, icon: Server, color: 'text-purple-600 bg-purple-50 dark:bg-purple-950/40 dark:text-purple-400' },
    { label: 'Development', value: summary?.development_integrations || 0, icon: Code, color: 'text-amber-600 bg-amber-50 dark:bg-amber-950/40 dark:text-amber-400' },
    { label: 'Active API Keys', value: summary?.active_api_keys || 0, icon: Key, color: 'text-indigo-600 bg-indigo-50 dark:bg-indigo-950/40 dark:text-indigo-400' },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Breadcrumb items={[{ label: "Overview" }]} />
          <h1 className="text-2xl font-extrabold text-gray-900 dark:text-gray-100">Executive Gateway Dashboard</h1>
        </div>
        <button
          onClick={fetchSummary}
          className="flex items-center space-x-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-xl text-sm font-medium text-gray-700 dark:text-gray-200 shadow-sm transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh Data</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-xl text-red-600 dark:text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Summary KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {cards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div
              key={idx}
              className="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700/80 shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">{card.label}</span>
                <div className={`p-2.5 rounded-xl ${card.color}`}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>
              <div className="text-3xl font-black text-gray-900 dark:text-gray-100">{card.value}</div>
            </div>
          );
        })}
      </div>

      {/* Live Recent Activity Audit Feed */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700/80 p-6 shadow-sm">
        <div className="flex items-center space-x-3 mb-6 border-b border-gray-100 dark:border-gray-700/60 pb-4">
          <div className="p-2.5 bg-indigo-100 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 rounded-xl">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">Live Activity & Audit Log Stream</h2>
            <p className="text-xs text-gray-500 dark:text-gray-400">Real-time trace stream of system operations with Correlation IDs</p>
          </div>
        </div>

        <div className="divide-y divide-gray-100 dark:divide-gray-700/60">
          {summary?.recent_activities?.length > 0 ? (
            summary.recent_activities.map((act) => (
              <div key={act.id} className="py-3.5 flex items-center justify-between hover:bg-gray-50/50 dark:hover:bg-gray-700/30 px-2 rounded-lg transition-colors">
                <div className="flex items-center space-x-3">
                  <span className="px-2.5 py-1 text-xs font-bold rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 uppercase tracking-wider">
                    {act.action}
                  </span>
                  <div>
                    <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">{act.resource_type}</span>
                    <span className="text-xs text-gray-400 ml-2">ID: {act.resource_id || 'N/A'}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                  <span className="font-mono bg-gray-100 dark:bg-gray-900 px-2 py-0.5 rounded text-indigo-600 dark:text-indigo-400">
                    CID: {act.correlation_id?.substring(0, 8)}...
                  </span>
                  <span>{act.user_email}</span>
                  <span>{act.timestamp ? new Date(act.timestamp).toLocaleTimeString() : ''}</span>
                </div>
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-500 py-6 text-center">No recent activity logged.</p>
          )}
        </div>
      </div>
    </div>
  );
}
