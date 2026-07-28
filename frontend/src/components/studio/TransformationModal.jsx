import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles, ArrowRight, Play, CheckCircle2, RefreshCw, Layers } from 'lucide-react';

export default function TransformationModal({ edge, onClose, onSaveTransformation }) {
  if (!edge) return null;

  const [transforms, setTransforms] = useState(
    edge.transforms || [
      { id: 1, type: 'Trim', detail: 'Remove leading and trailing whitespace', active: true },
      { id: 2, type: 'Uppercase', detail: 'Convert characters to uppercase', active: true },
      { id: 3, type: 'Replace', detail: 'Replace spaces with underscore', active: true }
    ]
  );

  const [sampleInputValue, setSampleInputValue] = useState('  john.doe@example.com  ');
  const [flippedIndex, setFlippedIndex] = useState(null);

  const computeResult = (val) => {
    let result = val;
    transforms.forEach((t) => {
      if (!t.active) return;
      if (t.type === 'Trim') result = result.trim();
      if (t.type === 'Uppercase') result = result.toUpperCase();
      if (t.type === 'Replace') result = result.replace(/\s+/g, '_');
    });
    return result;
  };

  const outputValue = computeResult(sampleInputValue);

  const toggleTransform = (idx) => {
    setTransforms((prev) =>
      prev.map((t, i) => (i === idx ? { ...t, active: !t.active } : t))
    );
    setFlippedIndex(idx);
    setTimeout(() => setFlippedIndex(null), 600);
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
          <div className="flex items-center justify-between pb-4 mb-6 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-600 to-cyan-500 text-white shadow-lg">
                <RefreshCw className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                  Transformation Rules
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-mono border border-indigo-500/30">
                    {edge.source} ➔ {edge.target}
                  </span>
                </h3>
                <p className="text-xs text-slate-400">Configure function pipeline & data transformation sequence</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white p-2 rounded-xl hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Input & Output Live Tester */}
          <div className="grid grid-cols-2 gap-4 mb-6 bg-slate-950/60 p-4 rounded-2xl border border-slate-800/80">
            <div>
              <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
                Sample Input ({edge.source})
              </label>
              <input
                type="text"
                value={sampleInputValue}
                onChange={(e) => setSampleInputValue(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs font-mono text-cyan-300 focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
                Transformed Result ({edge.target})
              </label>
              <div className="w-full bg-slate-900/90 border border-emerald-500/40 rounded-xl px-3 py-2 text-xs font-mono text-emerald-400 flex items-center justify-between">
                <span>{outputValue}</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              </div>
            </div>
          </div>

          {/* Transformation Step Cards (With Card Flip Animation) */}
          <div className="mb-6">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-indigo-400" />
              Transformation Steps (Click to Toggle)
            </h4>

            <div className="space-y-3">
              {transforms.map((t, idx) => (
                <motion.div
                  key={t.id}
                  animate={{ rotateX: flippedIndex === idx ? [0, 90, 0] : 0 }}
                  transition={{ duration: 0.5 }}
                  onClick={() => toggleTransform(idx)}
                  className={`cursor-pointer p-4 rounded-2xl border transition-all flex items-center justify-between ${
                    t.active
                      ? 'bg-slate-800/80 border-indigo-500/50 shadow-md shadow-indigo-900/30'
                      : 'bg-slate-950/40 border-slate-800/80 opacity-50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="w-6 h-6 rounded-full bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 flex items-center justify-center text-xs font-mono font-bold">
                      {idx + 1}
                    </span>
                    <div>
                      <h5 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                        {t.type}()
                        {t.active ? (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-mono">
                            Enabled
                          </span>
                        ) : (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-700 text-slate-400 font-mono">
                            Disabled
                          </span>
                        )}
                      </h5>
                      <p className="text-xs text-slate-400 mt-0.5">{t.detail}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <ArrowRight className="w-4 h-4 text-slate-500" />
                  </div>
                </motion.div>
              ))}
            </div>
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
              onClick={() => {
                onSaveTransformation(edge.id, transforms);
                onClose();
              }}
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-white text-xs font-semibold shadow-lg shadow-indigo-500/30 transition-all hover:scale-105"
            >
              Save Transformation Rule
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
