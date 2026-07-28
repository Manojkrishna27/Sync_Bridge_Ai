import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Upload, FileCode, CheckCircle2, Copy } from 'lucide-react';

export default function SchemaUploadModal({ isOpen, onClose, type, schemaText, onSaveSchema }) {
  if (!isOpen) return null;

  const [rawText, setRawText] = useState(schemaText || '');
  const [format, setFormat] = useState(type === 'source' ? 'SOAP/XML' : 'JSON');

  const handleSave = () => {
    onSaveSchema(type, rawText, format);
    onClose();
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl text-white relative overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className={`flex items-center justify-center w-10 h-10 rounded-2xl ${type === 'source' ? 'bg-indigo-500/20 text-indigo-400' : 'bg-cyan-500/20 text-cyan-400'} border border-slate-800`}>
                <Upload className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-100 capitalize">
                  Upload {type} Schema
                </h3>
                <p className="text-xs text-slate-400">Paste raw XML, WSDL, JSON Schema, or Protobuf definition</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white p-2 rounded-xl hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Format Selector */}
          <div className="flex items-center gap-2 mb-4 bg-slate-950/60 p-1.5 rounded-2xl border border-slate-800/80">
            {['JSON', 'SOAP/XML', 'CSV', 'gRPC'].map((fmt) => (
              <button
                key={fmt}
                onClick={() => setFormat(fmt)}
                className={`flex-1 py-1.5 rounded-xl text-xs font-semibold font-mono transition-all ${
                  format === fmt
                    ? 'bg-gradient-to-r from-indigo-600 to-cyan-500 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                {fmt}
              </button>
            ))}
          </div>

          {/* Text Area */}
          <div className="mb-6">
            <textarea
              rows={10}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder={`Paste raw ${format} schema payload here...`}
              className="w-full bg-slate-950 border border-slate-800 rounded-2xl p-4 text-xs font-mono text-cyan-300 placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-all resize-none"
            />
          </div>

          {/* Action Footer */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-white text-xs font-semibold shadow-lg shadow-indigo-500/30 transition-all hover:scale-105"
            >
              Parse & Load Schema
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
