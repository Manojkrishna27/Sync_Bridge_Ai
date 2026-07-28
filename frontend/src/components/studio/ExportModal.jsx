import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Download, Copy, Check, FileCode, Code2 } from 'lucide-react';

export default function ExportModal({ isOpen, onClose, connections, mappingName }) {
  if (!isOpen) return null;

  const [copied, setCopied] = useState(false);

  // Generate JSLT rule payload
  const mappingRules = {
    version: '2.4',
    name: mappingName || 'SyncBridge AI Mapping',
    source_protocol: 'SOAP_XML',
    target_protocol: 'REST_JSON',
    generated_at: new Date().toISOString(),
    mappings: connections.map((conn) => ({
      source_field: conn.source,
      target_field: conn.target,
      confidence: conn.confidence,
      transforms: conn.transforms ? conn.transforms.map((t) => t.type) : ['Trim', 'Uppercase']
    }))
  };

  const jsonCode = JSON.stringify(mappingRules, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([jsonCode], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${(mappingName || 'mapping').toLowerCase().replace(/\s+/g, '_')}_spec.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl text-white relative overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-2xl bg-indigo-500/20 text-indigo-400 border border-slate-800">
                <Code2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-100">Export Mapping Definition</h3>
                <p className="text-xs text-slate-400">JSLT payload mapping specification & transformation config</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white p-2 rounded-xl hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* JSON Code Box */}
          <div className="relative mb-6">
            <pre className="w-full h-80 bg-slate-950 border border-slate-800 rounded-2xl p-4 text-xs font-mono text-cyan-300 overflow-y-auto leading-relaxed">
              {jsonCode}
            </pre>
            <button
              onClick={handleCopy}
              className="absolute top-3 right-3 flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-slate-300 hover:text-white text-xs font-semibold backdrop-blur-md transition-all"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5 text-slate-400" />
                  <span>Copy Code</span>
                </>
              )}
            </button>
          </div>

          {/* Action Footer */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors"
            >
              Close
            </button>
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-5 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-white text-xs font-semibold shadow-lg shadow-indigo-500/30 transition-all hover:scale-105"
            >
              <Download className="w-4 h-4" />
              Download JSON Spec
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
