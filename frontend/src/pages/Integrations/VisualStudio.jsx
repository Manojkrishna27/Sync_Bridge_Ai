import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import Breadcrumb from '../../components/Common/Breadcrumb';
import {
  Sparkles,
  Layers,
  Save,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Play,
  FileCode,
  ArrowRight,
  Code2,
  ChevronRight,
  ChevronDown,
  Search,
  BookOpen
} from 'lucide-react';

export default function VisualStudio() {
  const [clients, setClients] = useState([]);
  const [selectedClientId, setSelectedClientId] = useState('');
  const [sourceFormat, setSourceFormat] = useState('SOAP');
  const [targetFormat, setTargetFormat] = useState('JSON');

  const [sourceSchemaText, setSourceSchemaText] = useState(
`<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cust="http://example.com/customer">
   <soapenv:Body>
      <cust:CustomerRecord>
         <cust:CustomerId>CUST-88392</cust:CustomerId>
         <cust:CustomerName>Acme Enterprises</cust:CustomerName>
         <cust:EmailAddress>billing@acme.com</cust:EmailAddress>
         <cust:PhoneNumber>+1-555-0199</cust:PhoneNumber>
         <cust:CreatedDate>2026-07-23T14:00:00Z</cust:CreatedDate>
      </cust:CustomerRecord>
   </soapenv:Body>
</soapenv:Envelope>`
  );

  const [targetSchemaText, setTargetSchemaText] = useState(
`{
  "id": "USER-1001",
  "fullName": "John Doe",
  "email": "john@example.com",
  "mobile": "+15550199",
  "createdAt": "2026-07-23T14:00:00Z",
  "status": "ACTIVE"
}`
  );

  const [parsedSource, setParsedSource] = useState(null);
  const [parsedTarget, setParsedTarget] = useState(null);
  const [flatSourceFields, setFlatSourceFields] = useState([]);
  const [flatTargetFields, setFlatTargetFields] = useState([]);

  // Mapping state
  const [activeRules, setActiveRules] = useState([]);
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [mappingName, setMappingName] = useState('SOAP to REST User Sync');

  // Simulation & Validation states
  const [simulationResult, setSimulationResult] = useState(null);
  const [validationDiagnostics, setValidationDiagnostics] = useState(null);
  const [activeTab, setActiveTab] = useState('canvas'); // canvas, ai, rules, preview, validation

  const [searchSource, setSearchSource] = useState('');
  const [searchTarget, setSearchTarget] = useState('');

  useEffect(() => {
    fetchClientsAndTemplates();
  }, []);

  const fetchClientsAndTemplates = async () => {
    try {
      const cRes = await api.get('/clients?per_page=100');
      setClients(cRes.data.data || []);
      if (cRes.data.data?.length > 0) setSelectedClientId(cRes.data.data[0].id);

      const tRes = await api.get('/schema/mappings/templates');
      setTemplates(tRes.data.templates || []);
    } catch (err) {
      console.error("Failed to load setup data:", err);
    }
  };

  const handleAnalyzeSchemas = async () => {
    setLoading(true);
    try {
      const resSrc = await api.post('/schema/analyze', { raw_schema: sourceSchemaText, format: sourceFormat });
      const resTgt = await api.post('/schema/analyze', { raw_schema: targetSchemaText, format: targetFormat });

      setParsedSource(resSrc.data.parsed_tree);
      setFlatSourceFields(resSrc.data.flat_fields || []);

      setParsedTarget(resTgt.data.parsed_tree);
      setFlatTargetFields(resTgt.data.flat_fields || []);
    } catch (err) {
      alert("Schema analysis failed: " + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateAIMappings = async () => {
    if (!flatSourceFields.length || !flatTargetFields.length) {
      await handleAnalyzeSchemas();
    }
    setLoading(true);
    try {
      // Direct client-side heuristic/AI fallback match simulation
      const newSuggestions = [];
      flatSourceFields.forEach(src => {
        const sLeaf = src.name.toLowerCase().replace(/[^a-z]/g, '');
        flatTargetFields.forEach(tgt => {
          const tLeaf = tgt.name.toLowerCase().replace(/[^a-z]/g, '');
          if (sLeaf.includes(tLeaf) || tLeaf.includes(sLeaf)) {
            newSuggestions.push({
              source_field: src.path,
              target_field: tgt.path,
              confidence_score: sLeaf === tLeaf ? 0.98 : 0.85,
              reason: `Semantic match between '${src.name}' and '${tgt.name}'`,
              strategy_used: 'AI_MATCH'
            });
          }
        });
      });

      setAiSuggestions(newSuggestions);
      setActiveTab('ai');
    } catch (err) {
      alert("AI mapping generation failed");
    } finally {
      setLoading(false);
    }
  };

  const handleApplySuggestion = (sug) => {
    const exists = activeRules.some(r => r.target_path === sug.target_field);
    if (exists) {
      setActiveRules(activeRules.map(r => r.target_path === sug.target_field ? {
        source_path: sug.source_field,
        target_path: sug.target_field,
        rule_type: 'STATIC',
        strategy_used: sug.strategy_used || 'AI_MATCH'
      } : r));
    } else {
      setActiveRules([...activeRules, {
        source_path: sug.source_field,
        target_path: sug.target_field,
        rule_type: 'STATIC',
        strategy_used: sug.strategy_used || 'AI_MATCH'
      }]);
    }
  };

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const samplePayload = {
        CustomerRecord: {
          CustomerId: "CUST-99100",
          CustomerName: "Global Tech LLC",
          EmailAddress: "info@globaltech.com",
          PhoneNumber: "+1-800-555-0199",
          CreatedDate: "2026-07-23T15:00:00Z"
        }
      };

      const res = await api.post('/schema/preview', {
        source_payload: samplePayload,
        rules: activeRules
      });

      setSimulationResult(res.data);
      setActiveTab('preview');
    } catch (err) {
      alert("Simulation failed");
    } finally {
      setLoading(false);
    }
  };

  const handleValidateRules = async () => {
    setLoading(true);
    try {
      const res = await api.post('/schema/validate', { rules: activeRules });
      setValidationDiagnostics(res.data);
      setActiveTab('validation');
    } catch (err) {
      alert("Validation failed");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveMapping = async () => {
    if (!selectedClientId) return alert("Select a client tenant");
    setLoading(true);
    try {
      const res = await api.post('/mappings/save', {
        client_id: selectedClientId,
        name: mappingName,
        rules: activeRules,
        change_description: "Visual studio mapping creation"
      });
      alert(`Mapping '${res.data.name}' saved as version ${res.data.version}!`);
    } catch (err) {
      alert("Save failed: " + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <Breadcrumb items={[{ label: "Integrations", href: "/integrations" }, { label: "Visual Studio" }]} />
          <h1 className="text-2xl font-black text-gray-900 dark:text-gray-100">AI Visual Mapping Studio</h1>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleGenerateAIMappings}
            disabled={loading}
            className="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-bold text-xs rounded-xl shadow-md transition-all flex items-center space-x-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Auto-Map</span>
          </button>

          <button
            onClick={handleSimulate}
            disabled={loading}
            className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-xl shadow transition-colors flex items-center space-x-1"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Simulate</span>
          </button>

          <button
            onClick={handleSaveMapping}
            disabled={loading}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-xl shadow transition-colors flex items-center space-x-1.5"
          >
            <Save className="w-3.5 h-3.5" />
            <span>Save Mapping</span>
          </button>
        </div>
      </div>

      {/* Control Header */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="flex items-center space-x-3 w-full md:w-auto">
          <Layers className="w-5 h-5 text-indigo-600" />
          <input
            type="text"
            value={mappingName}
            onChange={(e) => setMappingName(e.target.value)}
            className="font-bold text-sm bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-1.5 text-gray-900 dark:text-gray-100"
          />
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <span className="font-semibold text-gray-500">Tenant Client:</span>
          <select
            value={selectedClientId}
            onChange={(e) => setSelectedClientId(e.target.value)}
            className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl font-bold px-3 py-1.5"
          >
            {clients.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
      </div>

      {/* Main Studio Split Workbench */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Source Schema Panel */}
        <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-3">
          <div className="flex justify-between items-center pb-2 border-b border-gray-100 dark:border-gray-700">
            <span className="text-xs font-bold uppercase tracking-wider text-purple-600">Source Schema</span>
            <select
              value={sourceFormat}
              onChange={(e) => setSourceFormat(e.target.value)}
              className="text-xs font-bold bg-gray-100 dark:bg-gray-700 rounded-lg px-2 py-1"
            >
              {['SOAP', 'XML', 'JSON', 'CSV', 'OPENAPI'].map(f => <option key={f} value={f}>{f}</option>)}
            </select>
          </div>

          <textarea
            rows={8}
            value={sourceSchemaText}
            onChange={(e) => setSourceSchemaText(e.target.value)}
            className="w-full p-3 font-mono text-xs bg-gray-900 text-amber-300 rounded-xl border border-gray-700 focus:outline-none"
          />

          <button
            onClick={handleAnalyzeSchemas}
            disabled={loading}
            className="w-full py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-xs font-bold rounded-xl transition-colors"
          >
            Analyze & Extract Fields
          </button>

          {flatSourceFields.length > 0 && (
            <div className="space-y-1.5 pt-2 max-h-60 overflow-y-auto">
              <span className="text-xs font-bold text-gray-500">Source Fields ({flatSourceFields.length})</span>
              {flatSourceFields.map(f => (
                <div key={f.path} className="p-2 bg-gray-50 dark:bg-gray-900 rounded-lg text-xs flex justify-between items-center border border-gray-200 dark:border-gray-700">
                  <span className="font-mono text-indigo-600 dark:text-indigo-400 font-medium">{f.path}</span>
                  <span className="text-[10px] px-1.5 py-0.5 bg-indigo-50 dark:bg-indigo-950 text-indigo-600 font-bold rounded">{f.type}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Middle Column: React Flow Connections & Active Rules Canvas */}
        <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center pb-2 border-b border-gray-100 dark:border-gray-700 mb-3">
              <div className="flex space-x-2 text-xs font-bold">
                <button
                  onClick={() => setActiveTab('canvas')}
                  className={`px-3 py-1.5 rounded-lg transition-colors ${activeTab === 'canvas' ? 'bg-indigo-600 text-white' : 'bg-gray-100 dark:bg-gray-700'}`}
                >
                  Active Mappings ({activeRules.length})
                </button>
                <button
                  onClick={() => setActiveTab('ai')}
                  className={`px-3 py-1.5 rounded-lg transition-colors flex items-center space-x-1 ${activeTab === 'ai' ? 'bg-purple-600 text-white' : 'bg-gray-100 dark:bg-gray-700'}`}
                >
                  <Sparkles className="w-3 h-3" />
                  <span>AI Drawer ({aiSuggestions.length})</span>
                </button>
              </div>

              <button
                onClick={handleValidateRules}
                className="text-xs font-bold text-indigo-600 hover:underline"
              >
                Validate Rules
              </button>
            </div>

            {activeTab === 'canvas' && (
              activeRules.length === 0 ? (
                <div className="p-12 text-center text-gray-400 text-xs border border-dashed border-gray-300 dark:border-gray-700 rounded-xl">
                  No active mappings. Click "AI Auto-Map" or apply suggestions.
                </div>
              ) : (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {activeRules.map((rule, idx) => (
                    <div key={idx} className="p-3 bg-indigo-50/50 dark:bg-indigo-950/30 rounded-xl border border-indigo-200 dark:border-indigo-800 flex items-center justify-between text-xs">
                      <div className="flex items-center space-x-2 font-mono">
                        <span className="text-purple-600 font-bold">{rule.source_path}</span>
                        <ArrowRight className="w-3.5 h-3.5 text-gray-400" />
                        <span className="text-indigo-600 font-bold">{rule.target_path}</span>
                      </div>
                      <span className="text-[10px] px-2 py-0.5 bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 font-bold rounded-full">
                        {rule.strategy_used}
                      </span>
                    </div>
                  ))}
                </div>
              )
            )}

            {activeTab === 'ai' && (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {aiSuggestions.map((sug, idx) => (
                  <div key={idx} className="p-3 bg-purple-50/50 dark:bg-purple-950/30 rounded-xl border border-purple-200 dark:border-purple-800 space-y-2 text-xs">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-purple-700 dark:text-purple-300 flex items-center">
                        <Sparkles className="w-3 h-3 mr-1" /> {(sug.confidence_score * 100).toFixed(0)}% Match
                      </span>
                      <button
                        onClick={() => handleApplySuggestion(sug)}
                        className="px-2.5 py-1 bg-purple-600 text-white font-bold text-[10px] rounded-lg shadow hover:bg-purple-700"
                      >
                        Apply Rule
                      </button>
                    </div>
                    <div className="font-mono text-gray-700 dark:text-gray-300">
                      {sug.source_field} → {sug.target_field}
                    </div>
                    <p className="text-[11px] text-gray-500 italic">{sug.reason}</p>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'preview' && simulationResult && (
              <div className="space-y-2">
                <span className="text-xs font-bold text-emerald-600">Simulated REST Output</span>
                <pre className="p-3 font-mono text-xs bg-gray-900 text-emerald-400 rounded-xl max-h-80 overflow-y-auto">
                  {JSON.stringify(simulationResult.transformed_payload, null, 2)}
                </pre>
              </div>
            )}

            {activeTab === 'validation' && validationDiagnostics && (
              <div className="space-y-2">
                <div className="flex items-center space-x-2 font-bold text-xs">
                  {validationDiagnostics.valid ? (
                    <span className="text-emerald-600 flex items-center"><CheckCircle2 className="w-4 h-4 mr-1" /> Mappings Valid</span>
                  ) : (
                    <span className="text-amber-500 flex items-center"><AlertTriangle className="w-4 h-4 mr-1" /> Warnings Found ({validationDiagnostics.warnings_count})</span>
                  )}
                </div>
                {validationDiagnostics.diagnostics?.map((d, i) => (
                  <div key={i} className="p-2.5 bg-amber-50 text-amber-700 text-xs rounded-lg border border-amber-200">
                    <strong>{d.code}</strong>: {d.message}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Destination Schema Panel */}
        <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-3">
          <div className="flex justify-between items-center pb-2 border-b border-gray-100 dark:border-gray-700">
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-600">Destination Schema</span>
            <select
              value={targetFormat}
              onChange={(e) => setTargetFormat(e.target.value)}
              className="text-xs font-bold bg-gray-100 dark:bg-gray-700 rounded-lg px-2 py-1"
            >
              {['JSON', 'XML', 'SOAP', 'CSV', 'OPENAPI'].map(f => <option key={f} value={f}>{f}</option>)}
            </select>
          </div>

          <textarea
            rows={8}
            value={targetSchemaText}
            onChange={(e) => setTargetSchemaText(e.target.value)}
            className="w-full p-3 font-mono text-xs bg-gray-900 text-emerald-300 rounded-xl border border-gray-700 focus:outline-none"
          />

          {flatTargetFields.length > 0 && (
            <div className="space-y-1.5 pt-2 max-h-60 overflow-y-auto">
              <span className="text-xs font-bold text-gray-500">Destination Fields ({flatTargetFields.length})</span>
              {flatTargetFields.map(f => (
                <div key={f.path} className="p-2 bg-gray-50 dark:bg-gray-900 rounded-lg text-xs flex justify-between items-center border border-gray-200 dark:border-gray-700">
                  <span className="font-mono text-indigo-600 dark:text-indigo-400 font-medium">{f.path}</span>
                  <span className="text-[10px] px-1.5 py-0.5 bg-purple-50 dark:bg-purple-950 text-purple-600 font-bold rounded">{f.type}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
