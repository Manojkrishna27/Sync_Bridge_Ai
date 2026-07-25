import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import Breadcrumb from '../../components/Common/Breadcrumb';
import { Play, CheckCircle2, AlertTriangle, Download, Code, FileText, Upload, RefreshCw, Layers } from 'lucide-react';

export default function Playground() {
  const [integrations, setIntegrations] = useState([]);
  const [selectedIntegrationId, setSelectedIntegrationId] = useState('');
  const [protocol, setProtocol] = useState('SOAP');
  const [inputPayload, setInputPayload] = useState(
`<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="http://www.example.com/webservice">
   <soapenv:Header/>
   <soapenv:Body>
      <web:GetCustomerRequest>
         <web:CustomerId>CUST-99482</web:CustomerId>
         <web:Email>john.doe@enterprise.com</web:Email>
      </web:GetCustomerRequest>
   </soapenv:Body>
</soapenv:Envelope>`
  );

  const [loading, setLoading] = useState(false);
  const [outputResult, setOutputResult] = useState(null);
  const [validationResult, setValidationResult] = useState(null);
  const [activeView, setActiveView] = useState('output'); // output or validation

  const fetchIntegrations = async () => {
    try {
      const res = await api.get('/integrations?per_page=100');
      setIntegrations(res.data.data || []);
      if (res.data.data?.length > 0) {
        setSelectedIntegrationId(res.data.data[0].id);
      }
    } catch (err) {
      console.error("Failed to load integrations for playground:", err);
    }
  };

  useEffect(() => {
    fetchIntegrations();
  }, []);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      setInputPayload(event.target.result);
    };
    reader.readAsText(file);
  };

  const handlePreview = async () => {
    if (!selectedIntegrationId) return alert("Select an integration pipeline first.");
    setLoading(true);
    try {
      const res = await api.post(`/executions/integrations/${selectedIntegrationId}/preview`, { payload: inputPayload });
      setOutputResult(res.data);
      setActiveView('output');
    } catch (err) {
      alert(err.response?.data?.message || "Transformation preview failed");
    } finally {
      setLoading(false);
    }
  };

  const handleValidate = async () => {
    if (!selectedIntegrationId) return alert("Select an integration pipeline first.");
    setLoading(true);
    try {
      const res = await api.post(`/executions/integrations/${selectedIntegrationId}/validate`, { payload: inputPayload });
      setValidationResult(res.data);
      setActiveView('validation');
    } catch (err) {
      alert(err.response?.data?.message || "Validation failed");
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async () => {
    if (!selectedIntegrationId) return alert("Select an integration pipeline first.");
    setLoading(true);
    try {
      const res = await api.post(`/executions/integrations/${selectedIntegrationId}/execute`, { payload: inputPayload });
      setOutputResult(res.data);
      setActiveView('output');
    } catch (err) {
      alert(err.response?.data?.message || "Execution failed");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadOutput = () => {
    if (!outputResult) return;
    const blob = new Blob([JSON.stringify(outputResult, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transformed_output_${Date.now()}.json`;
    a.click();
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <Breadcrumb items={[{ label: "Integrations", href: "/integrations" }, { label: "Playground" }]} />
          <h1 className="text-2xl font-black text-gray-900 dark:text-gray-100">Integration Playground & Transformation Lab</h1>
        </div>

        <div className="flex items-center space-x-3">
          <label className="flex items-center space-x-1.5 px-3 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-xs font-medium text-gray-700 dark:text-gray-300 cursor-pointer shadow-sm hover:bg-gray-50">
            <Upload className="w-4 h-4 text-indigo-600" />
            <span>Upload File</span>
            <input type="file" accept=".xml,.json,.csv,.txt" onChange={handleFileUpload} className="hidden" />
          </label>

          <button
            onClick={handlePreview}
            disabled={loading}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold text-xs rounded-xl shadow transition-colors flex items-center space-x-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Preview Mapping</span>
          </button>

          <button
            onClick={handleExecute}
            disabled={loading}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-xl shadow transition-colors flex items-center space-x-1.5"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Run Execution</span>
          </button>
        </div>
      </div>

      {/* Pipeline & Protocol Selection Control Bar */}
      <div className="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="flex items-center space-x-3 w-full md:w-auto">
          <Layers className="w-5 h-5 text-indigo-600 dark:text-indigo-400 shrink-0" />
          <select
            value={selectedIntegrationId}
            onChange={(e) => setSelectedIntegrationId(e.target.value)}
            className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-sm font-semibold text-gray-900 dark:text-gray-100 px-3 py-2 w-full md:w-80"
          >
            {integrations.map(i => (
              <option key={i.id} value={i.id}>{i.name} ({i.environment})</option>
            ))}
          </select>
        </div>

        <div className="flex items-center space-x-2">
          {['SOAP', 'XML', 'JSON', 'CSV'].map(p => (
            <button
              key={p}
              onClick={() => setProtocol(p)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                protocol === p
                  ? 'bg-indigo-600 text-white shadow'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Dual Workbench Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Workbench: Raw Input Payload Editor */}
        <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-3">
          <div className="flex justify-between items-center pb-2 border-b border-gray-100 dark:border-gray-700">
            <div className="flex items-center space-x-2">
              <Code className="w-4 h-4 text-gray-400" />
              <span className="text-sm font-bold text-gray-800 dark:text-gray-200">Input Payload ({protocol})</span>
            </div>
            <button
              onClick={handleValidate}
              disabled={loading}
              className="text-xs text-indigo-600 dark:text-indigo-400 font-semibold hover:underline"
            >
              Validate Schema
            </button>
          </div>

          <textarea
            rows={18}
            value={inputPayload}
            onChange={(e) => setInputPayload(e.target.value)}
            className="w-full p-4 font-mono text-xs bg-gray-900 text-amber-300 rounded-xl border border-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-inner"
            placeholder="Paste raw SOAP envelope, XML document, JSON object, or CSV string..."
          />
        </div>

        {/* Right Workbench: Output Preview & Validation Viewer */}
        <div className="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm space-y-3 flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center pb-2 border-b border-gray-100 dark:border-gray-700 mb-3">
              <div className="flex space-x-3 text-xs font-bold">
                <button
                  onClick={() => setActiveView('output')}
                  className={`pb-1 border-b-2 ${activeView === 'output' ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-gray-400'}`}
                >
                  Transformed REST Output
                </button>
                <button
                  onClick={() => setActiveView('validation')}
                  className={`pb-1 border-b-2 ${activeView === 'validation' ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-gray-400'}`}
                >
                  Validation Results
                </button>
              </div>

              {outputResult && activeView === 'output' && (
                <button
                  onClick={handleDownloadOutput}
                  className="p-1.5 text-gray-500 hover:text-indigo-600 hover:bg-gray-100 rounded-lg transition-colors flex items-center text-xs"
                  title="Download JSON"
                >
                  <Download className="w-3.5 h-3.5 mr-1" /> Download
                </button>
              )}
            </div>

            {activeView === 'output' ? (
              outputResult ? (
                <pre className="p-4 font-mono text-xs bg-gray-900 text-green-400 rounded-xl border border-gray-700 overflow-x-auto max-h-[440px] shadow-inner">
                  {JSON.stringify(outputResult, null, 2)}
                </pre>
              ) : (
                <div className="flex flex-col items-center justify-center p-16 text-center text-gray-400 border border-dashed border-gray-300 dark:border-gray-700 rounded-xl">
                  <FileText className="w-8 h-8 mb-2 opacity-50" />
                  <p className="text-sm">Click "Preview Mapping" or "Run Execution" to view output.</p>
                </div>
              )
            ) : (
              validationResult ? (
                <div className="space-y-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center space-x-2 font-bold text-sm">
                    {validationResult.valid ? (
                      <span className="text-green-600 flex items-center"><CheckCircle2 className="w-4 h-4 mr-1" /> Payload Schema Valid</span>
                    ) : (
                      <span className="text-red-500 flex items-center"><AlertTriangle className="w-4 h-4 mr-1" /> Schema Validation Errors ({validationResult.errors?.length})</span>
                    )}
                  </div>
                  {validationResult.errors?.length > 0 && (
                    <div className="space-y-2">
                      {validationResult.errors.map((err, idx) => (
                        <div key={idx} className="p-2.5 bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-400 text-xs rounded-lg border border-red-200">
                          <strong>{err.field}</strong>: {err.message}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="p-12 text-center text-gray-400 text-sm">Click "Validate Schema" to test validation rules.</div>
              )
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
