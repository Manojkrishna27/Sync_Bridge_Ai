import React from 'react';
import { motion } from 'framer-motion';
import { FileText, Hash, Type, Calendar, CheckCircle2, GripVertical } from 'lucide-react';

export default function TargetPanel({ fields, hoveredField, setHoveredField, selectedField, setSelectedField, searchTerm }) {
  const filteredFields = fields.filter((f) =>
    f.name.toLowerCase().includes((searchTerm || '').toLowerCase())
  );

  const getIcon = (type) => {
    switch (type) {
      case 'timestamp': return Calendar;
      case 'number': return Hash;
      default: return Type;
    }
  };

  return (
    <div className="w-80 bg-slate-900/80 backdrop-blur-xl border border-slate-800/80 rounded-3xl p-4 flex flex-col shadow-2xl overflow-hidden">
      {/* Panel Header */}
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className="flex items-center justify-center w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-slate-100 uppercase tracking-wider">Target Schema</h3>
            <span className="text-[10px] text-slate-400 font-mono">REST JSON / Modern Spec</span>
          </div>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-mono">
          {filteredFields.length} Fields
        </span>
      </div>

      {/* Field List */}
      <div className="flex-1 space-y-2 overflow-y-auto pr-1">
        {filteredFields.map((field, idx) => {
          const Icon = getIcon(field.type);
          const isHovered = hoveredField === field.name;
          const isSelected = selectedField === field.name;
          const isConnected = field.isConnected;

          return (
            <motion.div
              key={field.name}
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.04 }}
              onMouseEnter={() => setHoveredField(field.name)}
              onMouseLeave={() => setHoveredField(null)}
              onClick={() => setSelectedField(field.name)}
              className={`group relative flex items-center justify-between px-3.5 py-2.5 rounded-2xl border transition-all cursor-pointer ${
                isHovered || isSelected
                  ? 'bg-cyan-600/20 border-cyan-500 shadow-lg shadow-cyan-500/20 text-white scale-[1.02]'
                  : isConnected
                  ? 'bg-slate-900/90 border-cyan-500/40 text-slate-200'
                  : 'bg-slate-950/60 border-slate-800/80 text-slate-300 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center gap-2">
                {/* Connect handle point */}
                <div
                  id={`target-${field.name}`}
                  className={`w-3.5 h-3.5 rounded-full border-2 transition-all ${
                    isConnected
                      ? 'bg-cyan-400 border-cyan-200 shadow-md shadow-cyan-400/50 scale-110'
                      : isHovered
                      ? 'bg-emerald-400 border-white scale-125'
                      : 'bg-slate-800 border-slate-600'
                  }`}
                />
                {isConnected && (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                )}
              </div>

              <div className="flex items-center gap-2.5 text-right">
                <div>
                  <span className="text-xs font-medium font-mono block leading-none">{field.name}</span>
                  <span className="text-[10px] text-slate-500 font-mono uppercase mt-1 block">
                    {field.type}
                  </span>
                </div>
                <Icon className={`w-4 h-4 ${isConnected ? 'text-cyan-400' : 'text-slate-500'}`} />
                <GripVertical className="w-3.5 h-3.5 text-slate-600 group-hover:text-cyan-400 transition-colors" />
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
