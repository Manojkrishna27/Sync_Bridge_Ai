import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Workflow, Cpu, Activity, MessageSquare, Users, Shield, BookOpen, ArrowRight } from 'lucide-react';

export default function CommandPalette({ isOpen, onClose }) {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const navigate = useNavigate();

  const commands = [
    { id: 'dashboard', title: 'Go to Executive Dashboard', category: 'Navigation', icon: Activity, path: '/dashboard' },
    { id: 'integrations', title: 'View All Integration Pipelines', category: 'Navigation', icon: Workflow, path: '/integrations' },
    { id: 'studio', title: 'Open AI Visual Mapping Studio', category: 'Studio', icon: Cpu, path: '/integrations/studio' },
    { id: 'copilot', title: 'Ask AI Copilot Assistant', category: 'AI', icon: MessageSquare, path: '/copilot' },
    { id: 'monitoring', title: 'View Real-Time Telemetry & Monitoring', category: 'Monitoring', icon: Activity, path: '/monitoring' },
    { id: 'clients', title: 'Manage Clients & Multi-Tenant Keys', category: 'Management', icon: Users, path: '/clients' },
    { id: 'admin', title: 'Admin & Role Security Console', category: 'Security', icon: Shield, path: '/admin' }
  ];

  const filteredCommands = commands.filter((cmd) =>
    cmd.title.toLowerCase().includes(query.toLowerCase()) ||
    cmd.category.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % Math.max(filteredCommands.length, 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filteredCommands.length) % Math.max(filteredCommands.length, 1));
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (filteredCommands[selectedIndex]) {
          navigate(filteredCommands[selectedIndex].path);
          onClose();
        }
      } else if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, selectedIndex, filteredCommands, navigate, onClose]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4 bg-slate-950/80 backdrop-blur-md">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: -10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: -10 }}
          className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl overflow-hidden text-white"
        >
          {/* Search Header */}
          <div className="relative flex items-center px-4 border-b border-slate-800">
            <Search className="w-4 h-4 text-slate-400 mr-3" />
            <input
              type="text"
              autoFocus
              placeholder="Type a command or search (e.g. Studio, Copilot, Dashboard)..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full py-4 bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none"
            />
            <kbd className="px-2 py-0.5 text-[10px] font-mono text-slate-400 bg-slate-800 border border-slate-700 rounded-md">
              ESC
            </kbd>
          </div>

          {/* Results List */}
          <div className="max-h-80 overflow-y-auto p-2">
            {filteredCommands.length === 0 ? (
              <div className="p-6 text-center text-xs text-slate-500 font-mono">
                No matching actions found.
              </div>
            ) : (
              filteredCommands.map((cmd, idx) => {
                const Icon = cmd.icon;
                const isSelected = idx === selectedIndex;

                return (
                  <div
                    key={cmd.id}
                    onClick={() => {
                      navigate(cmd.path);
                      onClose();
                    }}
                    onMouseEnter={() => setSelectedIndex(idx)}
                    className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl cursor-pointer transition-colors ${
                      isSelected ? 'bg-blue-600/20 text-white border border-blue-500/40' : 'text-slate-300 hover:bg-slate-800/60'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${isSelected ? 'bg-blue-500 text-white' : 'bg-slate-800 text-slate-400'}`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div>
                        <span className="text-xs font-semibold block">{cmd.title}</span>
                        <span className="text-[10px] text-slate-500 uppercase tracking-wider font-mono">{cmd.category}</span>
                      </div>
                    </div>
                    <ArrowRight className={`w-4 h-4 transition-transform ${isSelected ? 'translate-x-1 text-blue-400' : 'opacity-0'}`} />
                  </div>
                );
              })
            )}
          </div>

          {/* Footer Shortcuts */}
          <div className="flex items-center justify-between px-4 py-2 bg-slate-950/60 border-t border-slate-800/80 text-[10px] text-slate-500 font-mono">
            <span>Use ↑ ↓ to navigate</span>
            <span>Press ↵ to select</span>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
