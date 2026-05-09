'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { formatPrice } from '@/lib/formatters';

/**
 * TradePlanTable — Trade Plan summary with Confidence Score progress bar.
 *
 * Props:
 *   plan             : TradePlan object from API
 *   ticker           : stock ticker string
 *   confidenceScore  : XGBoost probability (0.0–1.0)
 *   isHighConviction : boolean — true if confidenceScore > 0.75
 */

function ConfidenceBar({ score, isHighConviction }) {
  const pct = Math.round((score ?? 0.5) * 100);

  let barColor, labelColor, label;
  if (pct >= 75) {
    barColor  = '#00FFB2';
    labelColor = '#00FFB2';
    label     = 'High Conviction';
  } else if (pct >= 50) {
    barColor  = '#3b82f6';
    labelColor = '#3b82f6';
    label     = 'Moderate';
  } else {
    barColor  = '#f59e0b';
    labelColor = '#f59e0b';
    label     = 'Low Conviction';
  }

  return (
    <div className="flex flex-col gap-2 p-3 bg-surface-container rounded-lg border border-outline-variant/50">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[16px]" style={{ color: barColor }}>
            insights
          </span>
          <span className="text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
            XGBoost Confidence Score
          </span>
        </div>
        <div className="flex items-center gap-2">
          {isHighConviction && (
            <motion.span
              className="inline-flex items-center gap-1 text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded"
              style={{ background: 'rgba(0,255,178,0.12)', color: '#00FFB2', border: '1px solid rgba(0,255,178,0.3)' }}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ type: 'spring', stiffness: 300 }}
            >
              <span className="material-symbols-outlined text-[12px]">verified</span>
              High Conviction Setup
            </motion.span>
          )}
          <span
            className="text-xl font-black font-mono tabular-nums"
            style={{ color: labelColor }}
          >
            {pct}%
          </span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-full h-2.5 bg-white/5 rounded-full overflow-hidden relative">
        {/* Threshold marker at 75% */}
        <div className="absolute top-0 bottom-0 w-px bg-white/20" style={{ left: '75%' }} />
        <motion.div
          className="h-full rounded-full"
          style={{
            background: `linear-gradient(90deg, ${barColor}80, ${barColor})`,
            boxShadow: `0 0 8px ${barColor}60`,
          }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.9, ease: 'easeOut' }}
        />
      </div>

      <div className="flex justify-between items-center">
        <span className="text-[9px] text-white/30 font-mono">
          P(+5% gain in 5 days)
        </span>
        <div className="flex items-center gap-1">
          <div
            className="w-1.5 h-1.5 rounded-full"
            style={{ background: labelColor, boxShadow: `0 0 4px ${labelColor}` }}
          />
          <span className="text-[9px] font-black uppercase tracking-wider" style={{ color: labelColor }}>
            {label}
          </span>
        </div>
      </div>
    </div>
  );
}

export default function TradePlanTable({ plan, ticker, confidenceScore, isHighConviction }) {
  const [showLogic, setShowLogic] = useState(false);

  if (!plan) return null;

  const getStatusColor = (status) => {
    switch (status) {
      case 'Strong Buy': return 'bg-semantic-bullish text-black';
      case 'Speculative': return 'bg-primary text-black';
      case 'High Risk': return 'bg-semantic-bearish text-white';
      default: return 'bg-surface-variant text-on-surface-variant';
    }
  };

  return (
    <div className="flex flex-col gap-4 mt-4">
      <div className="flex items-center justify-between">
        <h3 className="font-heading-table text-heading-table text-on-surface uppercase tracking-wider flex items-center gap-2">
          <span className="material-symbols-outlined text-primary text-[20px]">assignment</span>
          Ringkasan Trade Plan ({ticker.replace('.JK', '')})
        </h3>
        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${getStatusColor(plan.status)}`}>
          {plan.status}
        </span>
      </div>

      {/* ── XGBoost Confidence Score Bar ──────────────────────────────── */}
      <ConfidenceBar
        score={confidenceScore}
        isHighConviction={isHighConviction}
      />

      {/* ── Trade Plan Table ──────────────────────────────────────────── */}
      <div className="border border-outline-variant rounded-lg overflow-hidden bg-surface">
        <table className="w-full text-left text-[12px]">
          <thead>
            <tr className="bg-surface-container-high border-b border-outline-variant">
              <th className="py-2 px-3 font-heading-table text-on-surface-variant uppercase">Entry Zone</th>
              <th className="py-2 px-3 font-heading-table text-on-surface-variant uppercase">Stop Loss</th>
              <th className="py-2 px-3 font-heading-table text-on-surface-variant uppercase text-semantic-bullish">TP1 (Fib 0.618)</th>
              <th className="py-2 px-3 font-heading-table text-on-surface-variant uppercase text-semantic-bullish">TP2 (Fib 1.618)</th>
              <th className="py-2 px-3 font-heading-table text-on-surface-variant uppercase text-right">Risk/Reward</th>
            </tr>
          </thead>
          <tbody>
            <tr className="font-data-mono">
              <td className="py-3 px-3 text-on-surface">{plan.entry_range}</td>
              <td className="py-3 px-3 text-semantic-bearish font-bold">{formatPrice(plan.stop_loss)}</td>
              <td className="py-3 px-3 text-semantic-bullish font-bold">{formatPrice(plan.take_profit_1)}</td>
              <td className="py-3 px-3 text-semantic-bullish">{formatPrice(plan.take_profit_2)}</td>
              <td className="py-3 px-3 text-on-surface text-right">{plan.rr_ratio}</td>
            </tr>
          </tbody>
        </table>
        
        <div className="bg-surface-container p-3 border-t border-outline-variant">
          <div className="flex items-start gap-2">
            <span className="material-symbols-outlined text-on-surface-variant text-[16px] mt-0.5">info</span>
            <p className="text-[11px] text-on-surface-variant leading-relaxed">
              <span className="font-bold text-on-surface">Strategi Cicil:</span> {plan.scaling_strategy}
            </p>
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <button 
          onClick={() => setShowLogic(!showLogic)}
          className="flex items-center gap-1.5 text-[11px] font-bold text-primary hover:underline w-fit"
        >
          <span className="material-symbols-outlined text-[16px]">
            {showLogic ? 'expand_less' : 'psychology'}
          </span>
          {showLogic ? 'Sembunyikan Analisis' : 'Lihat Analisis Logika'}
        </button>

        {showLogic && (
          <div className="p-3 bg-surface-container-highest rounded border border-primary/20 text-[12px] text-on-surface leading-relaxed animate-in fade-in slide-in-from-top-1 duration-200">
            {plan.logic_explanation}
            {plan.is_confirmed && (
              <div className="mt-2 flex items-center gap-1.5 text-semantic-bullish font-bold uppercase text-[10px]">
                <span className="material-symbols-outlined text-[14px]">verified</span>
                Konfirmasi Tren: EMA & RSI Valid
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
