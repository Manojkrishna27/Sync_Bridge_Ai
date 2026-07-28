import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown } from 'lucide-react';

export default function StatCard({
  title,
  value,
  trend,
  isPositive = true,
  icon: Icon,
  sparklineData = [10, 25, 18, 40, 32, 55, 48, 62],
  isLoading = false
}) {
  if (isLoading) {
    return (
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-sm animate-pulse">
        <div className="flex items-center justify-between mb-4">
          <div className="w-24 h-4 bg-slate-800 rounded-md" />
          <div className="w-8 h-8 bg-slate-800 rounded-xl" />
        </div>
        <div className="w-32 h-8 bg-slate-800 rounded-lg mb-2" />
        <div className="w-20 h-3 bg-slate-800 rounded-md" />
      </div>
    );
  }

  // Normalize sparkline values to SVG points
  const max = Math.max(...sparklineData, 1);
  const min = Math.min(...sparklineData, 0);
  const points = sparklineData
    .map((val, idx) => {
      const x = (idx / (sparklineData.length - 1)) * 100;
      const y = 30 - ((val - min) / (max - min || 1)) * 24;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <motion.div
      whileHover={{ y: -3, transition: { duration: 0.2 } }}
      className="bg-slate-900/80 backdrop-blur-xl border border-slate-800 hover:border-slate-700/80 rounded-2xl p-5 shadow-sm hover:shadow-lg transition-all duration-200 flex flex-col justify-between"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            {title}
          </span>
          <h3 className="text-2xl font-bold text-slate-100 font-mono tracking-tight">{value}</h3>
        </div>
        {Icon && (
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-slate-800/60 mt-2">
        {/* Trend Indicator */}
        <div className="flex items-center gap-1.5">
          <span
            className={`inline-flex items-center gap-1 text-xs font-semibold font-mono px-2 py-0.5 rounded-full border ${
              isPositive
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                : 'bg-red-500/10 border-red-500/30 text-red-400'
            }`}
          >
            {isPositive ? (
              <TrendingUp className="w-3 h-3 text-emerald-400" />
            ) : (
              <TrendingDown className="w-3 h-3 text-red-400" />
            )}
            {trend}
          </span>
          <span className="text-[10px] text-slate-500">vs last 7d</span>
        </div>

        {/* Sparkline SVG */}
        <svg className="w-20 h-8 overflow-visible">
          <polyline
            fill="none"
            stroke={isPositive ? '#10b981' : '#ef4444'}
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            points={points}
          />
        </svg>
      </div>
    </motion.div>
  );
}
