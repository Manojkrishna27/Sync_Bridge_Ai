import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../services/api';
import Breadcrumb from '../../components/Common/Breadcrumb';
import ApiKeyModal from '../../components/Common/ApiKeyModal';
import ConfirmationModal from '../../components/Common/ConfirmationModal';
import { Building, Key, Workflow, Activity, Settings, Plus, RotateCw, Trash2, CheckCircle2, Shield } from 'lucide-react';

export default function ClientDetail() {
  const { id } = useParams();
  const [client, setClient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  // API Keys state
  const [apiKeys, setApiKeys] = useState([]);
  const [isKeyModalOpen, setIsKeyModalOpen] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [rawSecret, setRawSecret] = useState(null);
  const [keyActionLoading, setKeyActionLoading] = useState(false);
  const [revokeKeyId, setRevokeKeyId] = useState(null);

  // Integrations state
  const [integrations, setIntegrations] = useState([]);

  // Audit logs state
  const [auditLogs, setAuditLogs] = useState([]);

  // Settings form state
  const [settingsForm, setSettingsForm] = useState({
    timezone: 'UTC',
    default_environment: 'Development',
    retry_policy: { max_retries: 3, backoff_factor: 2 }
  });

  const fetchClientDetails = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/clients/${id}`);
      setClient(res.data);
      if (res.data.settings) {
        setSettingsForm({
          timezone: res.data.settings.timezone || 'UTC',
          default_environment: res.data.settings.default_environment || 'Development',
          retry_policy: res.data.settings.retry_policy || { max_retries: 3, backoff_factor: 2 }
        });
      }
    } catch (err) {
      console.error("Failed to load client detail:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchApiKeys = async () => {
    try {
      const res = await api.get(`/apikeys?client_id=${id}`);
      setApiKeys(res.data.keys || []);
    } catch (err) {
      console.error("Failed to fetch API keys:", err);
    }
  };

  const fetchIntegrations = async () => {
    try {
      const res = await api.get(`/integrations?client_id=${id}`);
      setIntegrations(res.data.data || []);
    } catch (err) {
      console.error("Failed to fetch client integrations:", err);
    }
  };

  const fetchAuditLogs = async () => {
    try {
      const res = await api.get(`/audit-logs?client_id=${id}`);
      setAuditLogs(res.data.data || []);
    } catch (err) {
      console.error("Failed to fetch client audit logs:", err);
    }
  };

  useEffect(() => {
    fetchClientDetails();
  }, [id]);

  useEffect(() => {
    if (activeTab === 'apikeys') fetchApiKeys();
    if (activeTab === 'integrations') fetchIntegrations();
    if (activeTab === 'audit') fetchAuditLogs();
  }, [activeTab]);

  const handleGenerateKey = async (e) => {
    e.preventDefault();
    setKeyActionLoading(true);
    try {
      const res = await api.post('/apikeys', { client_id: id, name: newKeyName });
      setRawSecret(res.data.raw_api_key);
      setNewKeyName('');
      setIsKeyModalOpen(false);
      fetchApiKeys();
    } catch (err) {
      alert(err.response?.data?.message || "Failed to generate key");
    } finally {
      setKeyActionLoading(false);
    }
  };

  const handleRotateKey = async (keyId) => {
    setKeyActionLoading(true);
    try {
      const res = await api.post(`/apikeys/${keyId}/rotate`);
      setRawSecret(res.data.raw_api_key);
      fetchApiKeys();
    } catch (err) {
      alert(err.response?.data?.message || "Failed to rotate key");
    } finally {
      setKeyActionLoading(false);
    }
  };

  const handleRevokeKeyConfirm = async () => {
    if (!revokeKeyId) return;
    setKeyActionLoading(true);
    try {
      await api.post(`/apikeys/${revokeKeyId}/revoke`);
      setRevokeKeyId(null);
      fetchApiKeys();
    } catch (err) {
      alert(err.response?.data?.message || "Failed to revoke key");
    } finally {
      setKeyActionLoading(false);
    }
  };

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/clients/${id}/settings`, settingsForm);
      alert("Client settings updated successfully!");
    } catch (err) {
      alert(err.response?.data?.message || "Failed to update settings");
    }
  };

  if (loading || !client) {
    return <div className="p-6 max-w-7xl mx-auto">Loading Client Details...</div>;
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <Breadcrumb items={[{ label: "Clients", href: "/clients" }, { label: client.name }]} />

      {/* Header Profile Card */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex items-center space-x-4">
          <div className="p-4 bg-indigo-100 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 rounded-2xl font-black text-2xl">
            {client.name.substring(0, 2).toUpperCase()}
          </div>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-extrabold text-gray-900 dark:text-gray-100">{client.name}</h1>
              <span className="px-3 py-1 text-xs font-bold rounded-full bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300">
                {client.status}
              </span>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Industry: <strong className="text-gray-700 dark:text-gray-300">{client.industry || "General"}</strong> • Plan: <strong className="text-gray-700 dark:text-gray-300">{client.subscription_plan || "Standard"}</strong>
            </p>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-gray-200 dark:border-gray-700 space-x-6 text-sm font-medium">
        {[
          { id: 'overview', label: 'Overview & Settings', icon: Settings },
          { id: 'integrations', label: 'Integrations', icon: Workflow },
          { id: 'apikeys', label: 'API Keys', icon: Key },
          { id: 'audit', label: 'Audit Logs', icon: Activity },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-3 border-b-2 transition-colors ${
                isActive
                  ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400 dark:border-indigo-400 font-bold'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content 1: Overview & Settings */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 space-y-4 shadow-sm">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">Contact Information</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-xs text-gray-400 block">Contact Person</span>
                <span className="font-semibold text-gray-800 dark:text-gray-200">{client.contact_person || 'N/A'}</span>
              </div>
              <div>
                <span className="text-xs text-gray-400 block">Contact Email</span>
                <span className="font-semibold text-gray-800 dark:text-gray-200">{client.contact_email || 'N/A'}</span>
              </div>
              <div>
                <span className="text-xs text-gray-400 block">Phone</span>
                <span className="font-semibold text-gray-800 dark:text-gray-200">{client.contact_phone || 'N/A'}</span>
              </div>
              <div>
                <span className="text-xs text-gray-400 block">Country</span>
                <span className="font-semibold text-gray-800 dark:text-gray-200">{client.country || 'N/A'}</span>
              </div>
            </div>
          </div>

          <form onSubmit={handleSaveSettings} className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 space-y-4 shadow-sm">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">Tenant Configuration & Settings</h3>
            
            <div>
              <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Timezone</label>
              <input
                type="text"
                value={settingsForm.timezone}
                onChange={(e) => setSettingsForm({ ...settingsForm, timezone: e.target.value })}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Default Environment</label>
              <select
                value={settingsForm.default_environment}
                onChange={(e) => setSettingsForm({ ...settingsForm, default_environment: e.target.value })}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm"
              >
                <option value="Development">Development</option>
                <option value="Staging">Staging</option>
                <option value="Production">Production</option>
              </select>
            </div>

            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-xl shadow transition-colors"
            >
              Save Settings
            </button>
          </form>
        </div>
      )}

      {/* Tab Content 2: Integrations */}
      {activeTab === 'integrations' && (
        <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">Tenant Integration Pipelines</h3>
          </div>
          {integrations.length === 0 ? (
            <p className="text-sm text-gray-500 py-6 text-center">No integrations configured for this client.</p>
          ) : (
            <div className="divide-y divide-gray-100 dark:divide-gray-700">
              {integrations.map((i) => (
                <div key={i.id} className="py-4 flex justify-between items-center">
                  <div>
                    <h4 className="font-bold text-gray-900 dark:text-gray-100 text-sm">{i.name}</h4>
                    <p className="text-xs text-gray-500">{i.source_system} ({i.source_protocol}) → {i.destination_system} ({i.destination_protocol})</p>
                  </div>
                  <span className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-gray-100 dark:bg-gray-700">
                    {i.environment}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab Content 3: API Keys */}
      {activeTab === 'apikeys' && (
        <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">Client API Keys</h3>
              <p className="text-xs text-gray-500">API Keys authenticate tenant clients. Raw keys are stored hashed with SHA-256.</p>
            </div>
            <button
              onClick={() => setIsKeyModalOpen(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-xl shadow"
            >
              <Plus className="w-4 h-4" />
              <span>Generate API Key</span>
            </button>
          </div>

          <div className="divide-y divide-gray-100 dark:divide-gray-700">
            {apiKeys.length === 0 ? (
              <p className="text-sm text-gray-500 py-6 text-center">No active API keys found.</p>
            ) : (
              apiKeys.map((key) => (
                <div key={key.id} className="py-4 flex items-center justify-between">
                  <div>
                    <span className="font-bold text-gray-900 dark:text-gray-100 text-sm">{key.name}</span>
                    <div className="text-xs text-gray-400 mt-0.5">Created: {new Date(key.created_at).toLocaleDateString()}</div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className={`px-2.5 py-1 text-xs font-bold rounded-full ${
                      key.status === 'Active' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                    }`}>
                      {key.status}
                    </span>
                    {key.status === 'Active' && (
                      <>
                        <button
                          onClick={() => handleRotateKey(key.id)}
                          className="p-2 text-gray-500 hover:text-indigo-600 hover:bg-gray-100 rounded-lg text-xs flex items-center space-x-1"
                          title="Rotate Key"
                        >
                          <RotateCw className="w-3.5 h-3.5 mr-1" /> Rotate
                        </button>
                        <button
                          onClick={() => setRevokeKeyId(key.id)}
                          className="p-2 text-red-500 hover:bg-red-50 rounded-lg text-xs flex items-center space-x-1"
                          title="Revoke Key"
                        >
                          <Trash2 className="w-3.5 h-3.5 mr-1" /> Revoke
                        </button>
                      </>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Tab Content 4: Audit Logs */}
      {activeTab === 'audit' && (
        <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">Tenant Audit History</h3>
          <div className="divide-y divide-gray-100 dark:divide-gray-700">
            {auditLogs.map((log) => (
              <div key={log.id} className="py-3 flex justify-between text-sm">
                <div>
                  <span className="font-bold text-gray-800 dark:text-gray-200 mr-2">{log.action}</span>
                  <span className="text-xs text-gray-400">({log.resource_type})</span>
                </div>
                <span className="text-xs text-gray-400 font-mono">CID: {log.correlation_id?.substring(0, 8)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Generate API Key Modal */}
      {isKeyModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-md w-full p-6 shadow-xl border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">Generate API Key</h3>
            <form onSubmit={handleGenerateKey} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Key Description / Purpose *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Production ERP Sync Gateway Key"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm"
                />
              </div>
              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsKeyModalOpen(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={keyActionLoading}
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl shadow"
                >
                  {keyActionLoading ? "Generating..." : "Generate Key"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Secret One-Time Key Display Modal */}
      <ApiKeyModal
        isOpen={Boolean(rawSecret)}
        rawApiKey={rawSecret}
        keyName="Client API Secret"
        onClose={() => setRawSecret(null)}
      />

      {/* Revoke Key Confirmation Modal */}
      <ConfirmationModal
        isOpen={Boolean(revokeKeyId)}
        title="Revoke API Key"
        message="Are you sure you want to revoke this API Key? Applications using this key will immediately lose access."
        confirmLabel="Revoke Key"
        onConfirm={handleRevokeKeyConfirm}
        onClose={() => setRevokeKeyId(null)}
        isLoading={keyActionLoading}
      />
    </div>
  );
}
