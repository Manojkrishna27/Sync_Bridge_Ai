import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import Breadcrumb from '../../components/Common/Breadcrumb';
import {
  ShieldCheck,
  Users,
  Building2,
  Key,
  Activity,
  FileText,
  ToggleLeft,
  ToggleRight,
  Server,
  Lock,
  RefreshCw
} from 'lucide-react';

export default function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [clients, setClients] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [featureFlags, setFeatureFlags] = useState({
    enable_ai_copilot: true,
    enable_token_rate_limiter: true,
    enable_redis_compression: true,
    enable_auto_retry_policy: true
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      const [uRes, cRes, aRes] = await Promise.all([
        api.get('/users?per_page=10'),
        api.get('/clients?per_page=10'),
        api.get('/audit-logs?per_page=10')
      ]);

      setUsers(uRes.data.data || []);
      setClients(cRes.data.data || []);
      setAuditLogs(aRes.data.data || []);
    } catch (err) {
      console.error("Failed to load admin data:", err);
    } finally {
      setLoading(false);
    }
  };

  const toggleFlag = (flagKey) => {
    setFeatureFlags(prev => ({ ...prev, [flagKey]: !prev[flagKey] }));
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <Breadcrumb items={[{ label: "Admin" }, { label: "Enterprise Administration" }]} />
          <h1 className="text-2xl font-black text-gray-900 dark:text-gray-100 flex items-center">
            <ShieldCheck className="w-6 h-6 text-indigo-600 mr-2" /> Enterprise Administration & Governance
          </h1>
        </div>

        <button
          onClick={fetchAdminData}
          disabled={loading}
          className="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-xs font-bold rounded-xl shadow-sm hover:bg-gray-50 flex items-center space-x-1.5"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-gray-600 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Main Admin Workbench */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* User & Client Management (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          {/* User Management Grid */}
          <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-3">
            <h3 className="font-bold text-sm text-gray-900 dark:text-gray-100 flex items-center">
              <Users className="w-4 h-4 text-indigo-600 mr-2" /> System Users ({users.length})
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="text-gray-400 font-bold uppercase border-b border-gray-100 dark:border-gray-700">
                  <tr>
                    <th className="py-2">User</th>
                    <th className="py-2">Email</th>
                    <th className="py-2">Role</th>
                    <th className="py-2">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                  {users.map(u => (
                    <tr key={u.id}>
                      <td className="py-2.5 font-bold text-gray-900 dark:text-gray-100">{u.first_name} {u.last_name}</td>
                      <td className="py-2.5 font-mono text-gray-600 dark:text-gray-400">{u.email}</td>
                      <td className="py-2.5 font-bold text-indigo-600">{u.role?.name || 'User'}</td>
                      <td className="py-2.5">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${u.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
                          {u.is_active ? 'Active' : 'Locked'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Audit Event Activity Stream */}
          <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-3">
            <h3 className="font-bold text-sm text-gray-900 dark:text-gray-100 flex items-center">
              <FileText className="w-4 h-4 text-purple-600 mr-2" /> Audit Trail Activity Stream
            </h3>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {auditLogs.map(log => (
                <div key={log.id} className="p-2.5 bg-gray-50 dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 text-xs flex justify-between items-center">
                  <div className="font-mono">
                    <strong className="text-purple-600">{log.action}</strong> on <span className="text-indigo-600">{log.resource_type}</span>
                  </div>
                  <span className="text-[10px] text-gray-400 font-mono">{log.created_at?.substring(0, 19)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Feature Flags & Security Controls (1 col) */}
        <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-4">
          <h3 className="font-bold text-sm text-gray-900 dark:text-gray-100 flex items-center">
            <Lock className="w-4 h-4 text-amber-500 mr-2" /> Dynamic Feature Flags
          </h3>

          <div className="space-y-3 text-xs">
            {Object.entries(featureFlags).map(([key, val]) => (
              <div key={key} className="p-3 bg-gray-50 dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 flex justify-between items-center">
                <span className="font-bold text-gray-700 dark:text-gray-300">{key.replace(/_/g, ' ').toUpperCase()}</span>
                <button onClick={() => toggleFlag(key)} className="text-indigo-600">
                  {val ? <ToggleRight className="w-6 h-6 text-emerald-500" /> : <ToggleLeft className="w-6 h-6 text-gray-400" />}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
