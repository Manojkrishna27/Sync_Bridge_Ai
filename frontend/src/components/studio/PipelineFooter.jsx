import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Globe, FileCode, ShieldCheck, Cpu, RefreshCw, FileText, ArrowRight, Play, CheckCircle2 } from 'lucide-react';

export default function PipelineFooter({ isExecuting, onRunPipeline }) {
  const [activeStage, setActiveStage] = useState(-1);

  const stages = [
    { id: 'rest', name: 'REST / XML', icon: Globe, color: 'from-blue-500 to-indigo-500' },
    { id: 'parser', name: 'Parser', icon: FileCode, color: 'from-indigo-500 to-cyan-500' },
    { id: 'validator', name: 'Validator', icon: ShieldCheck, color: 'from-cyan-500 to-emerald-500' },
    { id: 'mapping', name: 'Mapping Engine', icon: Cpu, color: 'from-emerald-500 to-amber-500' },
    { id: 'transformer', name: 'Transformer', icon: RefreshCw, color: 'from-amber-500 to-purple-500' },
    { id: 'json', name: 'JSON Output', icon: FileText, color: 'from-purple-500 to-pink-500' }
  ];

  useEffect(() => {
    if (isExecuting) {
      setActiveStage(0);
      const interval = setInterval(() => {
        setActiveStage((prev) => {
          if (prev >= stages.length - 1) {
            clearInterval(interval);
            return stages.length - 1;
          }
          return prev + 1;
        });
      }, 400);

      return () => clearInterval(interval);
    } else {
      setActiveStage(-1);
    }
  }, [isExecuting]);

  return (
    <div className="w-full bg-slate-950/90 backdrop-blur-xl border-t border-slate-800/80 px-6 py-3 shadow-2xl">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Title */}
        <div className="flex items-center gap-3 min-w-[180px]">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-indigo-400">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-semibold text-slate-200">Live Integration Pipeline</h4>
            <span className="text-[10px] text-slate-400 font-mono">Real-time Stream Execution</span>
          </div>
        </div>

        {/* Stages */}
        <div className="flex-1 flex items-center justify-center gap-2 overflow-x-auto py-1">
          {stages.map((stage, idx) => {
            const Icon = stage.icon;
            const isActive = activeStage === idx;
            const isDone = activeStage > idx;

            return (
              <React.Fragment key={stage.id}>
                {/* Stage Box */}
                <motion.div
                  animate={{
                    scale: isActive ? 1.05 : 1,
                    borderColor: isActive ? '#38bdf8' : isDone ? '#10b981' : '#334155'
                  }}
                  transition={{ duration: 0.2 }}
                  className={`relative flex items-center gap-2.5 px-3 py-2 rounded-xl border backdrop-blur-md transition-all ${
                    isActive
                      ? 'bg-slate-900 border-cyan-400 shadow-lg shadow-cyan-500/20 text-white'
                      : isDone
                      ? 'bg-slate-900/80 border-emerald-500/40 text-emerald-300'
                      : 'bg-slate-900/40 border-slate-800 text-slate-400'
                  }`}
                >
                  <div
                    className={`flex items-center justify-center w-7 h-7 rounded-lg bg-gradient-to-tr ${stage.color} text-white shadow-md text-xs`}
                  >
                    <Icon className={`w-3.5 h-3.5 ${isActive ? 'animate-spin' : ''}`} />
                  </div>
                  <span className="text-xs font-medium font-mono whitespace-nowrap">{stage.name}</span>

                  {isDone && (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 ml-1 shrink-0" />
                  )}

                  {/* Active Indicator Glow */}
                  {isActive && (
                    <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
                    </span>
                  )}
                </motion.div>

                {/* Connecting Arrow & Data Flow Pulse */}
                {idx < stages.length - 1 && (
                  <div className="relative flex items-center justify-center w-8 text-slate-600">
                    <ArrowRight className={`w-4 h-4 transition-colors ${isDone ? 'text-emerald-400' : 'text-slate-700'}`} />
                    {isActive && (
                      <motion.div
                        className="absolute w-2 h-2 rounded-full bg-cyan-400 shadow-lg shadow-cyan-400"
                        initial={{ x: -12 }}
                        animate={{ x: 12 }}
                        transition={{ repeat: Infinity, duration: 0.4 }}
                      />
                    )}
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>

        {/* Pipeline Trigger Button */}
        <button
          onClick={onRunPipeline}
          disabled={isExecuting}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white text-xs font-semibold shadow-lg shadow-emerald-600/30 transition-all hover:scale-105 disabled:opacity-50"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>{isExecuting ? 'Simulating...' : 'Run Pipeline'}</span>
        </button>
      </div>
    </div>
  );
}
