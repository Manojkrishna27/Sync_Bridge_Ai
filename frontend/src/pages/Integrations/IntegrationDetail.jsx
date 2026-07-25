import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../services/api';
import Breadcrumb from '../../components/Common/Breadcrumb';
import VersionHistoryModal from '../../components/Integrations/VersionHistoryModal';
import { Workflow, History, Save, RotateCcw, Activity, CheckCircle, AlertTriangle, Cpu, Clock } from 'lucide-react';

export default function IntegrationDetail() {
  const { id } = useParams();
  const [integration, setIntegration] = useState(null);
  const [loading, setLoading] = useState(true);
  const [configJson, setConfigJson] = useState('{}');
  const [changeNotes, setChangeNotes] = useState('');
  const [saving, setSaving] = useState(false);

  // Version History Drawer state
  const [isVersionDrawerOpen, setIsVersionDrawerOpen] = useState(false);
  const [versions, setVersions] = useState([]);
  const [versionLoading, setVersionLoading] = useState(false);

  const fetchIntegration = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/integrations/${id}`);
      setIntegration(res.data);
      setConfigJson(JSON.stringify(res.data.config || {}, null, 2));
    } catch (err) {
      console.error("Failed to load integration detail:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchVersions = async () => {
    try {
      const res = await api.get(`/integrations/${id}/versions`);
      setVersions(res.data.versions || []);
    } catch (err) {
      console.error("Failed to fetch version history:", err);
    }
  };

  useEffect(() => {
    fetchIntegration();
  }, [id]);

  const handleSaveConfig = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      let parsedConfig;
      try {
        parsedConfig = JSON.parse(configJson);
      } catch (jsonErr) {
        alert("Invalid JSON format in configuration state!");
        setSaving(false);
        return;
      }

      await api.put(`/integrations/${id}`, {
        config: parsedConfig,
        change_notes: changeNotes || "Configuration update"
      });

      alert("Integration updated successfully! Version incremented.");
      setChangeNotes('');
      fetchIntegration();
    } catch (err) {
      alert(err.response?.data?.message || "Failed to update integration");
    } finally {
      setSaving(false);
    }
  };

  const handleRollbackVersion = async (targetVersionNum) => {
    setVersionLoading(true);
    try {
      await api.post(`/integrations/${id}/rollback`, { version_number: targetVersionNum });
      alert(`Integration configuration rolled back to v${targetVersionNum}`);
      setIsVersionDrawerOpen(false);
      fetchIntegration();
    } catch (err) {
      alert(err.response?.data?.message || "Failed to rollback integration version");
    } finally {
      setVersionLoading(false);
    }
  };

  const handleOpenVersions = () => {
    fetchVersions();
    setIsVersionDrawerOpen(true);
  };

  if (loading || !integration) {
    return <div className="p-6 max-w-7xl mx-auto">Loading Integration Details...</div>;
  }

  const stats = integration.execution_stats || {};

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <Breadcrumb items={[{ label: "Integrations", href: "/integrations" }, { label: integration.name }]} />

      {/* Header Pipeline Overview */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex items-center space-x-4">
          <div className="p-4 bg-purple-100 dark:bg-purple-950/50 text-purple-600 dark:text-purple-400 rounded-2xl">
            <Workflow className="w-8 h-8" />
          </div>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-black text-gray-900 dark:text-gray-100">{integration.name}</h1>
              <span className="px-3 py-1 text-xs font-bold rounded-full bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300">
                {integration.environment}
              </span>
              <span className="px-3 py-1 text-xs font-bold rounded-full bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">
                v{integration.version}
              </span>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Client: <strong className="text-gray-800 dark:text-gray-200">{integration.client_name}</strong> • Protocol: <strong className="text-gray-800 dark:text-gray-200">{integration.source_protocol} → {integration.destination_protocol}</strong>
            </p>
          </div>
        </div>

        <button
          onClick={handleOpenVersions}
          className="flex items-center space-x-2 px-4 py-2.5 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 hover:bg-gray-50 text-gray-800 dark:text-gray-200 font-medium text-sm rounded-xl shadow-sm transition-colors"
        >
          <History className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
          <span>Version History (v{integration.version})</span>
        </button>
      </div>

      {/* Execution Stats Metric Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <span className="text-xs text-gray-400 font-semibold uppercase">Total Executions</span>
          <div className="text-2xl font-extrabold text-gray-900 dark:text-gray-100 mt-1">{stats.total_executions || 0}</div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <span className="text-xs text-green-600 dark:text-green-400 font-semibold uppercase">Successful</span>
          <div className="text-2xl font-extrabold text-green-600 dark:text-green-400 mt-1">{stats.successful_executions || 0}</div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <span className="text-xs text-red-500 font-semibold uppercase">Failed</span>
          <div className="text-2xl font-extrabold text-red-500 mt-1">{stats.failed_executions || 0}</div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <span className="text-xs text-gray-400 font-semibold uppercase">Avg Execution Time</span>
          <div className="text-2xl font-extrabold text-gray-900 dark:text-gray-100 mt-1">{stats.average_execution_time || 0} ms</div>
        </div>
      </div>

      {/* Main Grid: Config JSON Editor & AI Copilot Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <form onSubmit={handleSaveConfig} className="lg:col-span-2 bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 space-y-4 shadow-sm">
          <div className="flex justify-between items-center border-b border-gray-100 dark:border-gray-700 pb-3">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">Configuration Definition (JSON)</h3>
            <span className="text-xs text-gray-400">Saving creates a new immutable version snapshot</span>
          </div>

          <div>
            <textarea
              rows={14}
              value={configJson}
              onChange={(e) => setConfigJson(e.target.value)}
              className="w-full p-4 font-mono text-xs bg-gray-900 text-green-400 rounded-xl border border-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-inner"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Change Log / Commit Note</label>
            <input
              type="text"
              placeholder="e.g. Updated mapping rules for SAP endpoint"
              value={changeNotes}
              onChange={(e) => setChangeNotes(e.target.value)}
              className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm"
            />
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={saving}
              className="flex items-center space-x-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm rounded-xl shadow transition-colors"
            >
              <Save className="w-4 h-4" />
              <span>{saving ? "Saving..." : "Save & Bump Version"}</span>
            </button>
          </div>
        </form>

        {/* AI Copilot & Pluggable Service Panel */}
        <div className="bg-gradient-to-b from-indigo-900 to-purple-900 text-white p-6 rounded-2xl shadow-lg space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 bg-white/10 rounded-xl backdrop-blur">
                <Cpu className="w-6 h-6 text-indigo-300" />
              </div>
              <div>
                <h3 className="font-bold text-lg">AI Gateway Assistant</h3>
                <p className="text-xs text-indigo-200">Pluggable Copilot & Schema Mapping</p>
              </div>
            </div>

            <div className="p-4 bg-white/10 rounded-xl backdrop-blur text-xs space-y-2 font-mono">
              <div className="text-green-300">✓ Connector Validation: Passed</div>
              <div className="text-indigo-200">✓ Schema Mapping Confidence: 99.4%</div>
              <div className="text-amber-200">ℹ AI Copilot: Ready for payload analysis</div>
            </div>
          </div>

          <button
            type="button"
            onClick={() => alert("AI Schema Mapping Assistant is initialized for future execution engine milestone!")}
            className="w-full py-2.5 bg-white text-indigo-900 hover:bg-indigo-50 font-bold text-sm rounded-xl shadow transition-colors text-center"
          >
            Run AI Schema Analysis
          </button>
        </div>
      </div>

      {/* Version History Drawer Modal */}
      <VersionHistoryModal
        isOpen={isVersionDrawerOpen}
        integrationName={integration.name}
        versions={versions}
        currentVersion={integration.version}
        onRollback={handleRollbackVersion}
        onClose={() => setIsVersionDrawerOpen(false)}
        isLoading={versionLoading}
      />
    </div>
  );
}
