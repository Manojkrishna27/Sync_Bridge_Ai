import React from 'react';
import {
  Upload,
  Sparkles,
  CheckCircle2,
  Play,
  Download,
  RotateCcw,
  RotateCw,
  Search,
  Maximize2,
  HelpCircle,
  Code2,
  Layers,
  Zap,
  Check
} from 'lucide-react';

export default function HeaderBar({
  mappingName,
  setMappingName,
  onOpenSourceModal,
  onOpenTargetModal,
  onGenerateAiMapping,
  onValidate,
  onPreview,
  onExport,
  onUndo,
  onRedo,
  onStartTour,
  isAnalyzing,
  isValidating,
  validationStatus,
  searchTerm,
  setSearchTerm
}) {
  return (
    <header className="w-full bg-slate-950/90 backdrop-blur-xl border-b border-slate-800/80 px-6 py-3 sticky top-0 z-30 shadow-xl">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Left: Title & Mapping Info */}
        <div className="flex items-center gap-3 min-w-[280px]">
          <div className="flex items-center justify-center w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 text-white shadow-lg shadow-indigo-500/25 border border-indigo-400/30">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={mappingName}
                onChange={(e) => setMappingName(e.target.value)}
                className="bg-transparent text-sm font-bold text-slate-100 hover:bg-slate-800/60 focus:bg-slate-900 border border-transparent hover:border-slate-700 focus:border-cyan-500 rounded-lg px-1.5 py-0.5 transition-all focus:outline-none"
              />
              <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 font-mono border border-cyan-500/30">
                v2.4 Active
              </span>
            </div>
            <p className="text-xs text-slate-400 flex items-center gap-1.5 mt-0.5">
              <span>SOAP (XML)</span>
              <span className="text-slate-600">➔</span>
              <span>RESTful (JSON)</span>
            </p>
          </div>
        </div>

        {/* Center: Search & History Controls */}
        <div className="flex items-center gap-2 flex-1 max-w-sm">
          <div className="relative w-full">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search fields (e.g. email, customer_id)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-900/90 border border-slate-800 hover:border-slate-700 focus:border-indigo-500 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none transition-all"
            />
          </div>

          <div className="flex items-center bg-slate-900 border border-slate-800 rounded-xl p-1 shrink-0">
            <button
              onClick={onUndo}
              title="Undo mapping change"
              className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={onRedo}
              title="Redo mapping change"
              className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
            >
              <RotateCw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2.5">
          {/* Upload Schemas */}
          <div className="flex items-center bg-slate-900 border border-slate-800 rounded-xl p-1">
            <button
              onClick={onOpenSourceModal}
              className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold text-slate-300 hover:text-white rounded-lg hover:bg-slate-800 transition-all"
            >
              <Upload className="w-3.5 h-3.5 text-indigo-400" />
              Source Schema
            </button>
            <div className="w-[1px] h-4 bg-slate-800" />
            <button
              onClick={onOpenTargetModal}
              className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold text-slate-300 hover:text-white rounded-lg hover:bg-slate-800 transition-all"
            >
              <Upload className="w-3.5 h-3.5 text-cyan-400" />
              Target Schema
            </button>
          </div>

          {/* AI Generate Mapping */}
          <button
            onClick={onGenerateAiMapping}
            disabled={isAnalyzing}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-white text-xs font-semibold shadow-lg shadow-indigo-500/25 transition-all hover:scale-105 disabled:opacity-50"
          >
            <Sparkles className="w-3.5 h-3.5 animate-spin text-cyan-200" />
            <span>Generate AI Mapping</span>
          </button>

          {/* Validate Button */}
          <button
            onClick={onValidate}
            disabled={isValidating}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-semibold transition-all hover:scale-105 ${
              validationStatus === 'success'
                ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400'
                : validationStatus === 'error'
                ? 'bg-rose-500/10 border-rose-500/40 text-rose-400'
                : 'bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Validate</span>
          </button>

          {/* Preview & Export */}
          <button
            onClick={onPreview}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 text-xs font-semibold transition-all"
          >
            <Code2 className="w-3.5 h-3.5 text-cyan-400" />
            <span>Preview</span>
          </button>

          <button
            onClick={onExport}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 text-xs font-semibold transition-all"
          >
            <Download className="w-3.5 h-3.5 text-slate-400" />
            <span>Export</span>
          </button>

          {/* Tour Button */}
          <button
            onClick={onStartTour}
            title="Start Interactive Guided Tour"
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <HelpCircle className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
