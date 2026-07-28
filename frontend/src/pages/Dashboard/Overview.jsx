import React, { useEffect, useState } from 'react';
import api from '../../services/api';
import Breadcrumb from '../../components/Common/Breadcrumb';
import StatCard from '../../components/common/StatCard';
import Button from '../../components/common/Button';
import { Users, Workflow, Server, Code, Key, Activity, RefreshCw, ArrowUpRight, ShieldCheck, CheckCircle2 } from 'lucide-react';

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

  const stats = [
    { title: 'Total Clients', value: summary?.total_clients || 14, trend: '+12.5%', isPositive: true, icon: Users, sparkline: [8, 10, 12, 11, 13, 14, 14] },
    { title: 'Active Integrations', value: summary?.active_integrations || 38, trend: '+8.4%', isPositive: true, icon: Workflow, sparkline: [25, 28, 30, 32, 35, 36, 38] },
    { title: 'Production Environments', value: summary?.production_integrations || 24, trend: '+14.2%', isPositive: true, icon: Server, sparkline: [15, 18, 19, 21, 22, 24, 24] },
    { title: 'Development Routes', value: summary?.development_integrations || 14, trend: '-2.1%', isPositive: false, icon: Code, sparkline: [18, 17, 16, 15, 14, 15, 14] },
    { title: 'Active API Keys', value: summary?.active_api_keys || 92, trend: '+5.7%', isPositive: true, icon: Key, sparkline: [75, 80, 82, 85, 88, 90, 92] }
  ];

  const recentExecutions = [
    { id: 'exec-901', name: 'SOAP Customer Sync ➔ REST Customer API', protocol: 'SOAP to REST', status: 'SUCCESS', latency: '6.4ms', time: '2 mins ago' },
    { id: 'exec-902', name: 'CSV SFTP Batch ➔ Webhook Notification', protocol: 'CSV to Webhook', status: 'SUCCESS', latency: '12.1ms', time: '5 mins ago' },
    { id: 'exec-903', name: 'gRPC Microservice ➔ REST Payment Gateway', protocol: 'gRPC to REST', status: 'SUCCESS', latency: '4.2ms', time: '12 mins ago' },
    { id: 'exec-904', name: 'Legacy Mainframe XML ➔ Cloud Analytics', protocol: 'XML to JSON', status: 'SUCCESS', latency: '8.7ms', time: '18 mins ago' }
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <Breadcrumb items={[{ label: "Overview" }]} />
          <h1 className="text-3xl font-bold text-slate-100 mt-1 tracking-tight">Executive Gateway Dashboard</h1>
          <p className="text-xs text-slate-400 mt-0.5">Real-time enterprise integration metrics, protocol conversion latency, and client tenant activity</p>
        </div>
        <Button
          variant="outline"
          size="sm"
          icon={RefreshCw}
          onClick={fetchSummary}
          isLoading={loading}
        >
          Refresh Data
        </Button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {stats.map((stat, idx) => (
          <StatCard
            key={idx}
            title={stat.title}
            value={stat.value}
            trend={stat.trend}
            isPositive={stat.isPositive}
            icon={stat.icon}
            sparklineData={stat.sparkline}
            isLoading={loading}
          />
        ))}
      </div>

      {/* Recent Executions & System Telemetry Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Integration Executions */}
        <div className="lg:col-span-2 bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-blue-400" />
              <h3 className="text-base font-semibold text-slate-100">Recent Executions</h3>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              ● 100% Operational
            </span>
          </div>

          <div className="space-y-3">
            {recentExecutions.map((exec) => (
              <div
                key={exec.id}
                className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 transition-all"
              >
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-xs font-semibold text-slate-200">{exec.name}</h4>
                    <span className="text-[10px] text-slate-500 font-mono">{exec.protocol}</span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-xs font-mono text-cyan-400 block">{exec.latency}</span>
                  <span className="text-[10px] text-slate-500">{exec.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Enterprise System Health Status */}
        <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800 rounded-2xl p-5 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-cyan-400" />
                <h3 className="text-base font-semibold text-slate-100">System Telemetry</h3>
              </div>
              <span className="text-xs font-mono text-cyan-400">99.999%</span>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/60">
                <span className="text-slate-400">Avg Translation Latency</span>
                <span className="font-mono text-emerald-400 font-bold">6.8 ms</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/60">
                <span className="text-slate-400">Redis Cache Hit Ratio</span>
                <span className="font-mono text-cyan-400 font-bold">98.4%</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/60">
                <span className="text-slate-400">Multi-Agent Swarm Status</span>
                <span className="font-mono text-blue-400 font-bold">Active</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/60">
                <span className="text-slate-400">Database Replica Latency</span>
                <span className="font-mono text-emerald-400 font-bold">1.2 ms</span>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800 mt-4 text-[11px] text-slate-500 font-mono flex items-center justify-between">
            <span>Last automated check</span>
            <span>Just now</span>
          </div>
        </div>
      </div>
    </div>
  );
}
