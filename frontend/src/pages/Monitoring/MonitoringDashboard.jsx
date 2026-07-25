import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import Breadcrumb from '../../components/Common/Breadcrumb';
import {
  Activity,
  Zap,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Flame,
  ShieldAlert,
  Database,
  Server,
  RefreshCw,
  TrendingUp,
  Cpu,
  Layers
} from 'lucide-react';

export default function MonitoringDashboard() {
  const [timeRange, setTimeRange] = useState('24h');
  const [dashboardData, setDashboardData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchMonitoringData = async () => {
    setLoading(true);
    try {
      const [dashRes, alertRes, healthRes] = await Promise.all([
        api.get(`/monitoring/dashboard?time_range=${timeRange}`),
        api.get('/monitoring/alerts?status=ACTIVE'),
        api.get('/monitoring/health')
      ]);

      setDashboardData(dashRes.data);
      setAlerts(alertRes.data.alerts || []);
      setHealthData(healthRes.data);
    } catch (err) {
      console.error("Failed to fetch monitoring telemetry:", err);
    } fontally: {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMonitoringData();
  }, [timeRange]);

  const handleAcknowledgeAlert = async (alertId) => {
    try {
      await api.post(`/monitoring/alerts/${alertId}/acknowledge`);
      setAlerts(alerts.filter(a => a.id !== alertId));
    } catch (err) {
      alert("Failed to acknowledge alert");
    }
  };

  const metrics = dashboardData?.metrics || {};

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <Breadcrumb items={[{ label: "Monitoring" }, { label: "System Dashboard" }]} />
          <h1 className="text-2xl font-black text-gray-900 dark:text-gray-100">Real-Time Observability & Monitoring</h1>
        </div>

        <div className="flex items-center space-x-3">
          {healthData && (
            <div className={`px-3 py-1.5 rounded-xl font-bold text-xs flex items-center space-x-1.5 shadow-sm ${
              healthData.status === 'HEALTHY' ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300' :
              healthData.status === 'DEGRADED' ? 'bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300' :
              'bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-300'
            }`}>
              <span className="w-2 h-2 rounded-full bg-current animate-pulse"></span>
              <span>Platform Status: {healthData.status}</span>
            </div>
          )}

          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs font-bold rounded-xl px-3 py-2 shadow-sm text-gray-800 dark:text-gray-200"
          >
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
          </select>

          <button
            onClick={fetchMonitoringData}
            disabled={loading}
            className="p-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl hover:bg-gray-50 transition-colors shadow-sm"
          >
            <RefreshCw className={`w-4 h-4 text-gray-600 dark:text-gray-300 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* 6 Key Metric Telemetry Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-1">
          <span className="text-xs font-bold text-gray-400">RPM (Requests/Min)</span>
          <div className="text-2xl font-black text-indigo-600 dark:text-indigo-400">{metrics.rpm || 0}</div>
          <span className="text-[10px] text-gray-500 font-semibold">{metrics.total_requests || 0} Total Requests</span>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-1">
          <span className="text-xs font-bold text-gray-400">Avg System Latency</span>
          <div className="text-2xl font-black text-purple-600 dark:text-purple-400">{metrics.avg_latency_ms || 0} ms</div>
          <span className="text-[10px] text-gray-500 font-semibold">End-to-End Pipeline</span>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-1">
          <span className="text-xs font-bold text-gray-400">Success Rate</span>
          <div className="text-2xl font-black text-emerald-600">{metrics.success_rate || 100}%</div>
          <span className="text-[10px] text-gray-500 font-semibold">SLA Target &gt; 99.9%</span>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-1">
          <span className="text-xs font-bold text-gray-400">Failure Rate</span>
          <div className="text-2xl font-black text-red-500">{metrics.failure_rate || 0}%</div>
          <span className="text-[10px] text-gray-500 font-semibold">Uncaught Pipeline Errors</span>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-1">
          <span className="text-xs font-bold text-gray-400">Cache Hit Ratio</span>
          <div className="text-2xl font-black text-amber-500">{metrics.cache_hit_ratio || 0}%</div>
          <span className="text-[10px] text-gray-500 font-semibold">Redis Cache Optimization</span>
        </div>

        <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-1">
          <span className="text-xs font-bold text-gray-400">Rate Limited</span>
          <div className="text-2xl font-black text-rose-600">{metrics.rate_limited_count || 0}</div>
          <span className="text-[10px] text-gray-500 font-semibold">HTTP 429 Blocked</span>
        </div>
      </div>

      {/* Main Grid: Connector Performance Ranking & Active Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Connector Performance Ranking (2 cols) */}
        <div className="lg:col-span-2 bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-4">
          <div className="flex justify-between items-center pb-2 border-b border-gray-100 dark:border-gray-700">
            <h3 className="font-bold text-sm text-gray-900 dark:text-gray-100 flex items-center">
              <Cpu className="w-4 h-4 text-indigo-600 mr-2" /> Connector Performance & Availability Ranking
            </h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-gray-400 uppercase font-bold border-b border-gray-100 dark:border-gray-700">
                <tr>
                  <th className="py-2">Connector</th>
                  <th className="py-2">Status</th>
                  <th className="py-2">Total Requests</th>
                  <th className="py-2">Avg Latency</th>
                  <th className="py-2">Availability</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                {dashboardData?.connectors?.map(c => (
                  <tr key={c.connector_name} className="hover:bg-gray-50/50">
                    <td className="py-3 font-bold text-indigo-600 dark:text-indigo-400">{c.connector_name}</td>
                    <td className="py-3">
                      <span className={`px-2 py-0.5 rounded-md font-bold text-[10px] ${
                        c.status === 'HEALTHY' ? 'bg-emerald-100 text-emerald-700' :
                        c.status === 'DEGRADED' ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'
                      }`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="py-3 font-medium">{c.total_requests}</td>
                    <td className="py-3 font-mono">{c.avg_latency_ms} ms</td>
                    <td className="py-3 font-bold text-emerald-600">{c.availability_pct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Active System Alerts Drawer (1 col) */}
        <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-4">
          <div className="flex justify-between items-center pb-2 border-b border-gray-100 dark:border-gray-700">
            <h3 className="font-bold text-sm text-gray-900 dark:text-gray-100 flex items-center">
              <ShieldAlert className="w-4 h-4 text-red-500 mr-2" /> Active System Alerts ({alerts.length})
            </h3>
          </div>

          {alerts.length === 0 ? (
            <div className="p-8 text-center text-xs text-gray-400">
              <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-emerald-500 opacity-60" />
              All systems operational. No active threshold alerts.
            </div>
          ) : (
            <div className="space-y-3 max-h-[380px] overflow-y-auto">
              {alerts.map(a => (
                <div key={a.id} className="p-3 bg-red-50 dark:bg-red-950/30 rounded-xl border border-red-200 dark:border-red-800 space-y-2 text-xs">
                  <div className="flex justify-between items-center font-bold text-red-700 dark:text-red-400">
                    <span>{a.title}</span>
                    <button
                      onClick={() => handleAcknowledgeAlert(a.id)}
                      className="px-2 py-0.5 bg-red-600 text-white rounded text-[10px] font-bold hover:bg-red-700"
                    >
                      Acknowledge
                    </button>
                  </div>
                  <p className="text-gray-600 dark:text-gray-300 text-[11px]">{a.message}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
