import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import Breadcrumb from '../../components/Common/Breadcrumb';
import { TableSkeleton } from '../../components/Common/LoadingSkeleton';
import EmptyState from '../../components/Common/EmptyState';
import ConfirmationModal from '../../components/Common/ConfirmationModal';
import { Plus, Search, Filter, Archive, Eye, ChevronLeft, ChevronRight, Building, Mail, Phone } from 'lucide-react';

export default function ClientList() {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [meta, setMeta] = useState({ total: 0, pages: 1 });

  // Modal States
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [archiveClientId, setArchiveClientId] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  // New Client Form State
  const [formData, setFormData] = useState({
    name: '',
    industry: '',
    contact_person: '',
    contact_email: '',
    contact_phone: '',
    subscription_plan: 'Standard'
  });

  const fetchClients = async () => {
    setLoading(true);
    try {
      const response = await api.get('/clients', {
        params: {
          page,
          per_page: 10,
          search: search || undefined,
          status: statusFilter || undefined
        }
      });
      setClients(response.data.data);
      setMeta(response.data.meta);
    } catch (err) {
      console.error("Failed to fetch clients:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClients();
  }, [page, statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchClients();
  };

  const handleCreateClient = async (e) => {
    e.preventDefault();
    setActionLoading(true);
    try {
      await api.post('/clients', formData);
      setIsAddModalOpen(false);
      setFormData({ name: '', industry: '', contact_person: '', contact_email: '', contact_phone: '', subscription_plan: 'Standard' });
      fetchClients();
    } catch (err) {
      alert(err.response?.data?.message || "Failed to create client");
    } finally {
      setActionLoading(false);
    }
  };

  const handleArchiveConfirm = async () => {
    if (!archiveClientId) return;
    setActionLoading(true);
    try {
      await api.delete(`/clients/${archiveClientId}`);
      setArchiveClientId(null);
      fetchClients();
    } catch (err) {
      alert(err.response?.data?.message || "Failed to archive client");
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <Breadcrumb items={[{ label: "Clients" }]} />
          <h1 className="text-2xl font-black text-gray-900 dark:text-gray-100">Enterprise Clients & Tenants</h1>
        </div>
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="flex items-center justify-center space-x-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-xl shadow transition-colors shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Add New Client</span>
        </button>
      </div>

      {/* Filter & Search Toolbar */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 flex flex-col md:flex-row gap-3 justify-between items-center shadow-sm">
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-96">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-gray-400" />
          <input
            type="text"
            placeholder="Search by company name or contact..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </form>

        <div className="flex items-center space-x-3 w-full md:w-auto">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
              className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm text-gray-900 dark:text-gray-100 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Statuses</option>
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
              <option value="Suspended">Suspended</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table / Skeleton / Empty State */}
      {loading ? (
        <TableSkeleton rows={5} cols={6} />
      ) : clients.length === 0 ? (
        <EmptyState
          title="No clients found"
          description="Create your first client tenant to manage integrations and API keys."
          actionLabel="Add Client"
          onAction={() => setIsAddModalOpen(true)}
          icon={Building}
        />
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600 dark:text-gray-300">
              <thead className="bg-gray-50 dark:bg-gray-900/60 text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider border-b border-gray-200 dark:border-gray-700">
                <tr>
                  <th className="px-6 py-4 font-bold">Client Name</th>
                  <th className="px-6 py-4 font-bold">Industry</th>
                  <th className="px-6 py-4 font-bold">Primary Contact</th>
                  <th className="px-6 py-4 font-bold">Plan</th>
                  <th className="px-6 py-4 font-bold">Status</th>
                  <th className="px-6 py-4 font-bold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-700/60">
                {clients.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50/60 dark:hover:bg-gray-700/30 transition-colors">
                    <td className="px-6 py-4">
                      <Link to={`/clients/${c.id}`} className="font-bold text-indigo-600 dark:text-indigo-400 hover:underline">
                        {c.name}
                      </Link>
                    </td>
                    <td className="px-6 py-4 font-medium text-gray-800 dark:text-gray-200">{c.industry || '—'}</td>
                    <td className="px-6 py-4">
                      <div className="text-xs font-semibold text-gray-800 dark:text-gray-200">{c.contact_person || '—'}</div>
                      <div className="text-xs text-gray-400 flex items-center mt-0.5">
                        <Mail className="w-3 h-3 mr-1" />
                        {c.contact_email || '—'}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                        {c.subscription_plan || 'Standard'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 text-xs font-bold rounded-full ${
                        c.status === 'Active'
                          ? 'bg-green-100 text-green-700 dark:bg-green-950/60 dark:text-green-400'
                          : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'
                      }`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      <Link
                        to={`/clients/${c.id}`}
                        className="p-2 inline-flex items-center justify-center text-gray-500 hover:text-indigo-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                        title="View Details"
                      >
                        <Eye className="w-4 h-4" />
                      </Link>
                      <button
                        onClick={() => setArchiveClientId(c.id)}
                        className="p-2 inline-flex items-center justify-center text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/40 rounded-lg transition-colors"
                        title="Archive Client"
                      >
                        <Archive className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Server Pagination Toolbar */}
          <div className="p-4 bg-gray-50 dark:bg-gray-900/60 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between text-xs text-gray-500">
            <span>Showing page {page} of {meta.pages} ({meta.total} total clients)</span>
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

      {/* Add Client Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-md w-full p-6 shadow-xl border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">Create Enterprise Client</h3>
            <form onSubmit={handleCreateClient} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Company Name *</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Industry</label>
                  <input
                    type="text"
                    value={formData.industry}
                    onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Plan</label>
                  <select
                    value={formData.subscription_plan}
                    onChange={(e) => setFormData({ ...formData, subscription_plan: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="Standard">Standard</option>
                    <option value="Professional">Professional</option>
                    <option value="Enterprise">Enterprise</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Contact Person</label>
                <input
                  type="text"
                  value={formData.contact_person}
                  onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Contact Email</label>
                  <input
                    type="email"
                    value={formData.contact_email}
                    onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Contact Phone</label>
                  <input
                    type="text"
                    value={formData.contact_phone}
                    onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
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
                  {actionLoading ? "Saving..." : "Create Client"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Confirmation Modal for Soft Deletion */}
      <ConfirmationModal
        isOpen={Boolean(archiveClientId)}
        title="Archive Client"
        message="Are you sure you want to archive this client tenant? Existing integrations will be set to inactive."
        confirmLabel="Archive Tenant"
        onConfirm={handleArchiveConfirm}
        onClose={() => setArchiveClientId(null)}
        isLoading={actionLoading}
      />
    </div>
  );
}
