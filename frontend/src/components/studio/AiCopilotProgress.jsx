import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, Sparkles, CheckCircle2, Loader2, ArrowRight } from 'lucide-react';

export default function AiCopilotProgress({ isAnalyzing, currentStage, stageProgress, onComplete }) {
  if (!isAnalyzing) return null;

  const stages = [
    { title: 'Analyzing schema structure...', percent: 35 },
    { title: 'Finding field relationships & semantics...', percent: 70 },
    { title: 'Generating transformation pipelines...', percent: 95 },
    { title: 'Complete! Mappings synthesized.', percent: 100 }
  ];

  const stageIndex = Math.min(currentStage, stages.length - 1);
  const stageInfo = stages[stageIndex];

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -20, scale: 0.95 }}
        className="absolute top-4 left-1/2 -translate-x-1/2 z-50 w-full max-w-xl px-4"
      >
        <div className="bg-slate-900/90 backdrop-blur-xl border border-indigo-500/30 rounded-2xl p-4 shadow-2xl shadow-indigo-500/20 text-white">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-500 text-white shadow-lg shadow-indigo-500/30">
                <Bot className="w-5 h-5 animate-pulse" />
                <span className="absolute -top-1 -right-1 flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
                </span>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-sm bg-gradient-to-r from-cyan-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
                    🤖 AI Copilot Engine
                  </span>
                  <span className="text-[10px] uppercase tracking-widest px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-mono border border-indigo-500/30">
                    Active
                  </span>
                </div>
                <p className="text-xs text-slate-300 flex items-center gap-1.5 mt-0.5">
                  {stageProgress < 100 ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                  ) : (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  )}
                  {stageInfo.title}
                </p>
              </div>
            </div>
            <div className="text-right">
              <span className="text-xl font-bold font-mono text-cyan-400">{Math.round(stageProgress)}%</span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="relative w-full h-2.5 bg-slate-800 rounded-full overflow-hidden border border-slate-700/50">
            <motion.div
              className="h-full bg-gradient-to-r from-indigo-500 via-cyan-400 to-emerald-400 rounded-full shadow-lg shadow-cyan-500/50"
              initial={{ width: '0%' }}
              animate={{ width: `${stageProgress}%` }}
              transition={{ ease: 'easeInOut', duration: 0.3 }}
            />
          </div>

          {/* Sub steps */}
          <div className="grid grid-cols-3 gap-2 mt-3 text-[11px]">
            <div className={`flex items-center gap-1 font-mono transition-colors ${currentStage >= 0 ? 'text-indigo-300' : 'text-slate-500'}`}>
              <Sparkles className="w-3 h-3" />
              <span>Analyzing</span>
            </div>
            <div className={`flex items-center justify-center gap-1 font-mono transition-colors ${currentStage >= 1 ? 'text-cyan-300' : 'text-slate-500'}`}>
              <Sparkles className="w-3 h-3" />
              <span>Relationships</span>
            </div>
            <div className={`flex items-center justify-end gap-1 font-mono transition-colors ${currentStage >= 2 ? 'text-emerald-300' : 'text-slate-500'}`}>
              <Sparkles className="w-3 h-3" />
              <span>Synthesizing</span>
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
