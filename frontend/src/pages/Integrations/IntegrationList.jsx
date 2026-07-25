import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import Breadcrumb from '../../components/Common/Breadcrumb';
import { TableSkeleton } from '../../components/Common/LoadingSkeleton';
import EmptyState from '../../components/Common/EmptyState';
import { Plus, Search, Filter, Workflow, Copy, Eye, ChevronLeft, ChevronRight, Activity } from 'lucide-react';

export default function IntegrationList() {
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [protocolFilter, setProtocolFilter] = useState('');
  const [envFilter, setEnvFilter] = useState('');
  const [page, setPage] = useState(1);
  const [meta, setMeta] = useState({ total: 0, pages: 1 });

  // Modal States
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [cloneIntegrationId, setCloneIntegrationId] = useState(null);
  const [cloneTargetEnv, setCloneTargetEnv] = useState('Staging');
  const [actionLoading, setActionLoading] = useState(false);

  // Clients list for client_id selection
  const [clientsList, setClientsList] = useState([]);

  // New Integration Form State
  const [formData, setFormData] = useState({
    client_id: '',
    name: '',
    description: '',
    source_system: '',
    destination_system: '',
    source_protocol: 'REST',
    destination_protocol: 'REST',
    environment: 'Development'
  });

  const fetchIntegrations = async () => {
    setLoading(true);
    try {
      const response = await api.get('/integrations', {
        params: {
          page,
          per_page: 10,
          search: search || undefined,
          protocol: protocolFilter || undefined,
          environment: envFilter || undefined
        }
      });
      setIntegrations(response.data.data);
      setMeta(response.data.meta);
    } catch (err) {
      console.error("Failed to fetch integrations:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchClients = async () => {
    try {
      const res = await api.get('/clients?per_page=100');
      setClientsList(res.data.data || []);
      if (res.data.data?.length > 0) {
        setFormData(prev => ({ ...prev, client_id: res.data.data[0].id }));
      }
    } catch (err) {
      console.error("Failed to fetch clients for dropdown:", err);
    }
  };

  useEffect(() => {
    fetchIntegrations();
  }, [page, protocolFilter, envFilter]);

  useEffect(() => {
    fetchClients();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchIntegrations();
  };

  const handleCreateIntegration = async (e) => {
    e.preventDefault();
    setActionLoading(true);
    try {
      await api.post('/integrations', formData);
      setIsAddModalOpen(false);
      fetchIntegrations();
    } catch (err) {
      alert(err.response?.data?.message || "Failed to create integration");
    } finally {
      setActionLoading(false);
    }
  };

  const handleCloneConfirm = async (e) => {
    e.preventDefault();
    if (!cloneIntegrationId) return;
    setActionLoading(true);
    try {
      await api.post(`/integrations/${cloneIntegrationId}/clone`, { target_environment: cloneTargetEnv });
      setCloneIntegrationId(null);
      fetchIntegrations();
    } catch (err) {
      alert(err.response?.data?.message || "Failed to clone integration");
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <Breadcrumb items={[{ label: "Integrations" }]} />
          <h1 className="text-2xl font-black text-gray-900 dark:text-gray-100">Integration Pipelines</h1>
        </div>
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="flex items-center justify-center space-x-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-xl shadow transition-colors shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>New Integration</span>
        </button>
      </div>

      {/* Filter & Search Toolbar */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 flex flex-col md:flex-row gap-3 justify-between items-center shadow-sm">
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-gray-400" />
          <input
            type="text"
            placeholder="Search by pipeline or system..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </form>

        <div className="flex items-center space-x-3 w-full md:w-auto">
          <select
            value={protocolFilter}
            onChange={(e) => { setProtocolFilter(e.target.value); setPage(1); }}
            className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm text-gray-900 dark:text-gray-100 px-3 py-2"
          >
            <option value="">All Protocols</option>
            <option value="REST">REST</option>
            <option value="SOAP">SOAP</option>
            <option value="XML">XML</option>
            <option value="CSV">CSV</option>
            <option value="GraphQL">GraphQL</option>
            <option value="SFTP">SFTP</option>
          </select>

          <select
            value={envFilter}
            onChange={(e) => { setEnvFilter(e.target.value); setPage(1); }}
            className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm text-gray-900 dark:text-gray-100 px-3 py-2"
          >
            <option value="">All Environments</option>
            <option value="Development">Development</option>
            <option value="Staging">Staging</option>
            <option value="Production">Production</option>
          </select>
        </div>
      </div>

      {/* Table / Skeleton / Empty State */}
      {loading ? (
        <TableSkeleton rows={5} cols={6} />
      ) : integrations.length === 0 ? (
        <EmptyState
          title="No integrations found"
          description="Build your first enterprise integration pipeline."
          actionLabel="Create Integration"
          onAction={() => setIsAddModalOpen(true)}
          icon={Workflow}
        />
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600 dark:text-gray-300">
              <thead className="bg-gray-50 dark:bg-gray-900/60 text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider border-b border-gray-200 dark:border-gray-700">
                <tr>
                  <th className="px-6 py-4 font-bold">Integration Name</th>
                  <th className="px-6 py-4 font-bold">Client / Tenant</th>
                  <th className="px-6 py-4 font-bold">Source → Dest</th>
                  <th className="px-6 py-4 font-bold">Environment</th>
                  <th className="px-6 py-4 font-bold">Health</th>
                  <th className="px-6 py-4 font-bold">Version</th>
                  <th className="px-6 py-4 font-bold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-700/60">
                {integrations.map((i) => (
                  <tr key={i.id} className="hover:bg-gray-50/60 dark:hover:bg-gray-700/30 transition-colors">
                    <td className="px-6 py-4">
                      <Link to={`/integrations/${i.id}`} className="font-bold text-indigo-600 dark:text-indigo-400 hover:underline">
                        {i.name}
                      </Link>
                    </td>
                    <td className="px-6 py-4 font-medium text-gray-800 dark:text-gray-200">{i.client_name || '—'}</td>
                    <td className="px-6 py-4 text-xs font-mono">
                      {i.source_system} ({i.source_protocol}) → {i.destination_system} ({i.destination_protocol})
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-purple-50 text-purple-700 dark:bg-purple-950/60 dark:text-purple-300">
                        {i.environment}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 text-xs font-bold rounded-full bg-green-100 text-green-700 dark:bg-green-950/60 dark:text-green-400 flex items-center w-fit space-x-1">
                        <Activity className="w-3 h-3" />
                        <span>{i.health_status} ({i.health_score}%)</span>
                      </span>
                    </td>
                    <td className="px-6 py-4 font-bold text-gray-800 dark:text-gray-200 text-xs">v{i.version}</td>
                    <td className="px-6 py-4 text-right space-x-2">
                      <Link
                        to={`/integrations/${i.id}`}
                        className="p-2 inline-flex items-center justify-center text-gray-500 hover:text-indigo-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                        title="View & Edit Configuration"
                      >
                        <Eye className="w-4 h-4" />
                      </Link>
                      <button
                        onClick={() => setCloneIntegrationId(i.id)}
                        className="p-2 inline-flex items-center justify-center text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 rounded-lg transition-colors"
                        title="Clone Integration to Environment"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Toolbar */}
          <div className="p-4 bg-gray-50 dark:bg-gray-900/60 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between text-xs text-gray-500">
            <span>Showing page {page} of {meta.pages} ({meta.total} integrations)</span>
            <div className="flex space-x-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg disabled:opacity-50 hover:bg-gray-100 flex items-center"
              >
                <ChevronLeft className="w-3.5 h-3.5 mr-1" /> Previous
              </button>
              <button
                disabled={page >= meta.pages}
                onClick={() => setPage(page + 1)}
                className="px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg disabled:opacity-50 hover:bg-gray-100 flex items-center"
              >
                Next <ChevronRight className="w-3.5 h-3.5 ml-1" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Integration Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-lg w-full p-6 shadow-xl border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">Create Integration Pipeline</h3>
            <form onSubmit={handleCreateIntegration} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Select Client / Tenant *</label>
                <select
                  required
                  value={formData.client_id}
                  onChange={(e) => setFormData({ ...formData, client_id: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm"
                >
                  {clientsList.map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Integration Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Salesforce to SAP Invoice Sync"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Source System</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Salesforce"
                    value={formData.source_system}
                    onChange={(e) => setFormData({ ...formData, source_system: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Source Protocol</label>
                  <select
                    value={formData.source_protocol}
                    onChange={(e) => setFormData({ ...formData, source_protocol: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm"
                  >
                    <option value="REST">REST</option>
                    <option value="SOAP">SOAP</option>
                    <option value="XML">XML</option>
                    <option value="CSV">CSV</option>
                    <option value="GraphQL">GraphQL</option>
                    <option value="SFTP">SFTP</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Destination System</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. SAP ERP"
                    value={formData.destination_system}
                    onChange={(e) => setFormData({ ...formData, destination_system: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Destination Protocol</label>
                  <select
                    value={formData.destination_protocol}
                    onChange={(e) => setFormData({ ...formData, destination_protocol: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm"
                  >
                    <option value="REST">REST</option>
                    <option value="SOAP">SOAP</option>
                    <option value="XML">XML</option>
                    <option value="CSV">CSV</option>
                    <option value="GraphQL">GraphQL</option>
                    <option value="SFTP">SFTP</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Environment</label>
                <select
                  value={formData.environment}
                  onChange={(e) => setFormData({ ...formData, environment: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm"
                >
                  <option value="Development">Development</option>
                  <option value="Staging">Staging</option>
                  <option value="Production">Production</option>
                </select>
              </div>

              <div className="flex justify-end space-x-3 pt-3">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow"
                >
                  {actionLoading ? "Creating..." : "Create Pipeline"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Clone Integration Modal */}
      {cloneIntegrationId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-md w-full p-6 shadow-xl border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-2">Clone Integration Pipeline</h3>
            <p className="text-xs text-gray-500 mb-4">Duplicate this pipeline configuration into a target environment.</p>

            <form onSubmit={handleCloneConfirm} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Target Environment</label>
                <select
                  value={cloneTargetEnv}
                  onChange={(e) => setCloneTargetEnv(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm"
                >
                  <option value="Staging">Staging</option>
                  <option value="Production">Production</option>
                  <option value="Development">Development</option>
                </select>
              </div>

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setCloneIntegrationId(null)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow"
                >
                  {actionLoading ? "Cloning..." : "Clone Pipeline"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
