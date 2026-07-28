import React, { useRef, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ZoomIn, ZoomOut, Maximize2, Sparkles, AlertCircle, RefreshCw } from 'lucide-react';

export default function MappingCanvas({
  connections,
  hoveredField,
  setHoveredField,
  selectedEdge,
  setSelectedEdge,
  onOpenTransformation,
  onConnectFields,
  isConnecting,
  validationDiagnostics
}) {
  const containerRef = useRef(null);
  const [zoom, setZoom] = useState(1);

  // Helper to determine confidence color & label
  const getConfidenceBadge = (confidence) => {
    if (confidence >= 90) {
      return {
        bgColor: 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300',
        dotColor: 'bg-emerald-400',
        label: `${confidence}% High`
      };
    } else if (confidence >= 75) {
      return {
        bgColor: 'bg-amber-500/20 border-amber-500/50 text-amber-300',
        dotColor: 'bg-amber-400',
        label: `${confidence}% Med`
      };
    } else {
      return {
        bgColor: 'bg-rose-500/20 border-rose-500/50 text-rose-300',
        dotColor: 'bg-rose-400',
        label: `${confidence}% Low`
      };
    }
  };

  return (
    <div
      ref={containerRef}
      className="relative flex-1 bg-slate-950/60 rounded-3xl border border-slate-800/80 overflow-hidden shadow-2xl flex items-center justify-center select-none"
    >
      {/* Background Animated Grid & Ambient Glow */}
      <div className="absolute inset-0 bg-[radial-gradient(#334155_1px,transparent_1px)] [background-size:24px_24px] opacity-25 pointer-events-none" />
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* SVG Canvas for Edges */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none z-10">
        <defs>
          {/* Linear Gradients for Edges */}
          <linearGradient id="edge-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#6366f1" />
            <stop offset="50%" stopColor="#38bdf8" />
            <stop offset="100%" stopColor="#10b981" />
          </linearGradient>

          <linearGradient id="edge-gradient-hover" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#818cf8" />
            <stop offset="100%" stopColor="#34d399" />
          </linearGradient>

          {/* Glow filter */}
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {connections.map((conn, idx) => {
          // Source & Target coordinates based on vertical spacing
          const totalConns = connections.length || 1;
          const ySpacing = 340 / (totalConns + 1);
          const yPos = (idx + 1) * ySpacing + 40;

          const startX = 20;
          const startY = yPos;
          const endX = 580;
          const endY = yPos;

          // Bezier curve path calculation
          const controlDist = 180;
          const pathD = `M ${startX} ${startY} C ${startX + controlDist} ${startY}, ${endX - controlDist} ${endY}, ${endX} ${endY}`;
          const midX = (startX + endX) / 2;
          const midY = (startY + endY) / 2;

          const isHovered =
            hoveredField === conn.source ||
            hoveredField === conn.target ||
            selectedEdge === conn.id;

          const isOtherHovered = hoveredField && !isHovered;
          const confidenceBadge = getConfidenceBadge(conn.confidence || 95);

          return (
            <g key={conn.id} className="pointer-events-auto cursor-pointer">
              {/* Base SVG Edge line */}
              <motion.path
                d={pathD}
                fill="none"
                stroke={isHovered ? 'url(#edge-gradient-hover)' : 'url(#edge-gradient)'}
                strokeWidth={isHovered ? 4 : 2}
                strokeOpacity={isOtherHovered ? 0.2 : 0.85}
                filter={isHovered ? 'url(#glow)' : undefined}
                initial={{ pathLength: 0, strokeDashoffset: 100 }}
                animate={{ pathLength: 1, strokeDashoffset: 0 }}
                transition={{ duration: 0.8, delay: idx * 0.15, ease: 'easeOut' }}
                onMouseEnter={() => setHoveredField(conn.source)}
                onMouseLeave={() => setHoveredField(null)}
                onClick={() => {
                  setSelectedEdge(conn.id);
                  onOpenTransformation(conn);
                }}
              />

              {/* Flowing Data Packet Dots (Continuous Motion) */}
              {!isOtherHovered && (
                <motion.circle
                  r={isHovered ? 5 : 3.5}
                  fill="#ffffff"
                  className="shadow-lg"
                  animate={{
                    cx: [startX, midX, endX],
                    cy: [startY, midY, endY]
                  }}
                  transition={{
                    repeat: Infinity,
                    duration: 2.2 + idx * 0.3,
                    ease: 'linear'
                  }}
                />
              )}

              {/* Animated Confidence Badge at Edge Midpoint */}
              <foreignObject
                x={midX - 45}
                y={midY - 14}
                width="90"
                height="28"
                className="overflow-visible pointer-events-none"
              >
                <motion.div
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: isOtherHovered ? 0.3 : 1 }}
                  transition={{ type: 'spring', stiffness: 300, damping: 20, delay: idx * 0.15 }}
                  onClick={(e) => {
                    e.stopPropagation();
                    onOpenTransformation(conn);
                  }}
                  className={`pointer-events-auto flex items-center justify-center gap-1.5 px-2 py-0.5 rounded-full border text-[10px] font-mono font-bold shadow-lg backdrop-blur-md cursor-pointer transition-transform hover:scale-110 ${confidenceBadge.bgColor}`}
                >
                  <span className={`w-1.5 h-1.5 rounded-full ${confidenceBadge.dotColor}`} />
                  <span>{confidenceBadge.label}</span>
                </motion.div>
              </foreignObject>
            </g>
          );
        })}
      </svg>

      {/* Empty State / Instructional Overlay if no connections */}
      {connections.length === 0 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center p-6 max-w-sm z-20"
        >
          <div className="flex items-center justify-center w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 mx-auto mb-3">
            <Sparkles className="w-6 h-6 animate-pulse" />
          </div>
          <h4 className="text-sm font-bold text-slate-200">No Active Field Connections</h4>
          <p className="text-xs text-slate-400 mt-1">
            Click <span className="text-cyan-400 font-semibold">"Generate AI Mapping"</span> or drag fields from Source to Target to begin mapping.
          </p>
        </motion.div>
      )}

      {/* Canvas Zoom Controls (Bottom Left) */}
      <div className="absolute bottom-4 left-4 z-20 flex items-center gap-1 bg-slate-900/90 border border-slate-800 rounded-2xl p-1.5 shadow-xl backdrop-blur-md">
        <button
          onClick={() => setZoom((z) => Math.min(z + 0.1, 1.5))}
          title="Zoom In"
          className="p-1.5 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition-colors"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={() => setZoom((z) => Math.max(z - 0.1, 0.7))}
          title="Zoom Out"
          className="p-1.5 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition-colors"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={() => setZoom(1)}
          title="Fit View"
          className="p-1.5 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition-colors"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
        <span className="text-[10px] font-mono text-slate-500 px-2 border-l border-slate-800">
          {Math.round(zoom * 100)}%
        </span>
      </div>
    </div>
  );
}
