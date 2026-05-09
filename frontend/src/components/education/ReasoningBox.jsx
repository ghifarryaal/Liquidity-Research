'use client';

import { motion } from 'framer-motion';
import { CLUSTER_CONFIG } from '@/constants/clusterConfig';

/**
 * ReasoningBox — "Why this recommendation?" educational panel.
 */
export default function ReasoningBox({ stock }) {
  const cfg = CLUSTER_CONFIG[stock.cluster_label] ?? CLUSTER_CONFIG['Hold / Sideways'];

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.15, duration: 0.4 }}
      className="reasoning-box mt-4"
      style={{
        background: `rgba(${hexToRgb(cfg.color)}, 0.05)`,
        borderColor: cfg.borderColor,
      }}
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <span className="text-base">{cfg.icon}</span>
        <span
          className="text-xs font-semibold tracking-wide uppercase"
          style={{ color: cfg.color }}
        >
          Mengapa Rekomendasi Ini?
        </span>
      </div>

      {/* Strategy */}
      <div className="flex flex-col gap-1 mb-3">
        <p className="text-sm font-semibold text-slate-100">
          🎯 {stock.strategy}
        </p>
        <div className="flex items-center gap-1.5 text-[10px] text-primary font-bold uppercase tracking-wider">
          <span className="material-symbols-outlined text-[14px]">timer</span>
          {stock.trading_style}
        </div>
      </div>

      {/* Reasoning paragraph */}
      <p className="text-sm text-slate-300 leading-relaxed">
        {stock.reasoning}
      </p>

      {/* Confidence bar */}
      <div className="mt-4">
        <div className="flex justify-between items-center mb-1.5">
          <span className="text-xs text-slate-500">Tingkat Keyakinan AI</span>
          <span className="text-xs font-mono font-semibold" style={{ color: cfg.color }}>
            {Math.round(stock.confidence * 100)}%
          </span>
        </div>
        <div className="h-1.5 rounded-full bg-navy-500 overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${stock.confidence * 100}%` }}
            transition={{ delay: 0.3, duration: 0.8, ease: 'easeOut' }}
            className="h-full rounded-full"
            style={{ background: `linear-gradient(90deg, ${cfg.color}88, ${cfg.color})` }}
          />
        </div>
      </div>

      {/* Macro note */}
      {stock.macro && (
        <div className="mt-3 pt-3 border-t border-white/5">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">Sentimen Makro Global:</span>
            <MacroRegimeBadge regime={stock.macro.macro_regime} />
          </div>
        </div>
      )}
    </motion.div>
  );
}

function MacroRegimeBadge({ regime }) {
  const configs = {
    'Risk-On':  { color: '#00FFB2', bg: 'rgba(0,255,178,0.1)',  label: '📈 Risk On'  },
    'Neutral':  { color: '#fbbf24', bg: 'rgba(245,158,11,0.1)', label: '⚖️ Netral'   },
    'Risk-Off': { color: '#f87171', bg: 'rgba(239,68,68,0.1)',  label: '🛡️ Risk Off' },
  };
  const cfg = configs[regime] ?? configs['Neutral'];
  return (
    <span
      className="text-xs px-2 py-0.5 rounded-full font-medium"
      style={{ background: cfg.bg, color: cfg.color, border: `1px solid ${cfg.color}33` }}
    >
      {cfg.label}
    </span>
  );
}

/** Convert hex color to "r,g,b" string for rgba() usage */
function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) return '6,182,212';
  return `${parseInt(result[1], 16)},${parseInt(result[2], 16)},${parseInt(result[3], 16)}`;
}
