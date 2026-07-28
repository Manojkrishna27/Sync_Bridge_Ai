import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, Sparkles, MessageSquare, X, ChevronRight, Zap, CheckCircle2 } from 'lucide-react';

export default function AiAssistantWidget({ status, onApplySuggestion, onAutoMap, totalConnections }) {
  const [isOpen, setIsOpen] = useState(true);
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);

  const messages = [
    "I'm ready! Click 'Generate AI Mapping' to auto-connect fields.",
    `I found high-confidence matches for your schema fields.`,
    "Confidence score is 98% for CustomerID → customer_id.",
    "Do you want me to automatically map Address → location?",
    "Tip: Drag any field from Left to Right to create custom connections."
  ];

  useEffect(() => {
    if (totalConnections > 0) {
      setCurrentMessageIndex(1);
    }
  }, [totalConnections]);

  const handleNextMessage = () => {
    setCurrentMessageIndex((prev) => (prev + 1) % messages.length);
  };

  return (
    <div className="fixed bottom-20 right-6 z-40 flex flex-col items-end gap-3 pointer-events-none">
      {/* Speech Bubble */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 10 }}
            className="pointer-events-auto max-w-xs bg-slate-900/95 backdrop-blur-xl border border-indigo-500/40 rounded-2xl p-4 shadow-2xl shadow-indigo-950/80 text-white"
          >
            <div className="flex items-center justify-between gap-2 pb-2 mb-2 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <span className="flex h-2 w-2 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="text-xs font-semibold text-indigo-300">SyncBridge AI Copilot</span>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-slate-400 hover:text-white transition-colors p-1 rounded-lg hover:bg-slate-800"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>

            <p className="text-xs text-slate-200 leading-relaxed font-sans min-h-[36px] flex items-center">
              "{messages[currentMessageIndex]}"
            </p>

            {/* Quick Action Chips */}
            <div className="mt-3 pt-2 border-t border-slate-800/80 flex flex-wrap gap-1.5">
              <button
                onClick={onAutoMap}
                className="text-[10px] px-2.5 py-1 rounded-lg bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-200 border border-indigo-500/40 flex items-center gap-1 transition-all hover:scale-105"
              >
                <Zap className="w-3 h-3 text-cyan-400" />
                Auto-Map Fields
              </button>

              <button
                onClick={handleNextMessage}
                className="text-[10px] px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center gap-1 transition-all"
              >
                Next Tip
                <ChevronRight className="w-3 h-3" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Robot Avatar Button */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        whileHover={{ scale: 1.08 }}
        whileTap={{ scale: 0.95 }}
        className="pointer-events-auto relative group flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 text-white shadow-xl shadow-indigo-500/30 border border-indigo-400/40 focus:outline-none"
      >
        <motion.div
          animate={status === 'thinking' ? { rotate: [0, 10, -10, 0] } : { y: [0, -3, 0] }}
          transition={{ repeat: Infinity, duration: status === 'thinking' ? 0.6 : 3 }}
        >
          <Bot className="w-7 h-7 text-white" />
        </motion.div>

        {/* Glow Ring */}
        <span className="absolute inset-0 rounded-2xl bg-cyan-400/20 animate-pulse pointer-events-none" />

        <span className="absolute -top-1 -right-1 flex h-4 w-4">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-4 w-4 bg-cyan-500 text-[9px] font-bold text-slate-950 items-center justify-center">
            AI
          </span>
        </span>
      </motion.button>
    </div>
  );
}
