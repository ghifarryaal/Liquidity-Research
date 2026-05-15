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
    <div className="flex flex-col gap-2 md:gap-3 p-2 md:p-3 bg-surface-container rounded-lg border border-outline-variant/50">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5 md:gap-2">
          <span className="material-symbols-outlined text-[14px] md:text-[16px]" style={{ color: barColor }}>
            insights
          </span>
          <span className="text-[9px] md:text-[10px] font-black uppercase tracking-widest text-on-surface-variant">
            XGBoost Confidence Score
          </span>
        </div>
        <div className="flex items-center gap-1.5 md:gap-2">
          {isHighConviction && (
            <motion.span
              className="inline-flex items-center gap-0.5 md:gap-1 text-[8px] md:text-[9px] font-black uppercase tracking-widest px-1.5 md:px-2 py-0.5 rounded"
              style={{ background: 'rgba(0,255,178,0.12)', color: '#00FFB2', border: '1px solid rgba(0,255,178,0.3)' }}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ type: 'spring', stiffness: 300 }}
            >
              <span className="material-symbols-outlined text-[10px] md:text-[12px]">verified</span>
              <span className="hidden sm:inline">High Conviction Setup</span>
              <span className="sm:hidden">High Conv.</span>
            </motion.span>
          )}
          <span
            className="text-lg md:text-xl font-black font-mono tabular-nums"
            style={{ color: labelColor }}
          >
            {pct}%
          </span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="w-full h-2 md:h-2.5 bg-white/5 rounded-full overflow-hidden relative">
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
        <span className="text-[8px] md:text-[9px] text-white/30 font-mono">
          P(+5% gain in 5 days)
        </span>
        <div className="flex items-center gap-0.5 md:gap-1">
          <div
            className="w-1 md:w-1.5 h-1 md:h-1.5 rounded-full"
            style={{ background: labelColor, boxShadow: `0 0 4px ${labelColor}` }}
          />
          <span className="text-[8px] md:text-[9px] font-black uppercase tracking-wider" style={{ color: labelColor }}>
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
    <div className="flex flex-col gap-3 md:gap-4 mt-3 md:mt-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <h3 className="font-heading-table text-xs md:text-sm text-on-surface uppercase tracking-wider flex items-center gap-1.5 md:gap-2">
          <span className="material-symbols-outlined text-primary text-[18px] md:text-[20px]">assignment</span>
          <span className="hidden sm:inline">Ringkasan Trade Plan ({ticker.replace('.JK', '')})</span>
          <span className="sm:hidden">Trade Plan ({ticker.replace('.JK', '')})</span>
        </h3>
        <span className={`px-2 py-0.5 rounded text-[9px] md:text-[10px] font-bold uppercase ${getStatusColor(plan.status)} w-fit`}>
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
        {/* Desktop Table */}
        <div className="hidden md:block overflow-x-auto">
          <table className="w-full text-left text-[11px] md:text-[12px]">
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
        </div>

        {/* Mobile Cards */}
        <div className="md:hidden p-3 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="flex flex-col gap-1">
              <span className="text-[9px] text-on-surface-variant uppercase font-bold">Entry Zone</span>
              <span className="text-[11px] font-data-mono text-on-surface">{plan.entry_range}</span>
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-[9px] text-on-surface-variant uppercase font-bold">Risk/Reward</span>
              <span className="text-[11px] font-data-mono text-on-surface">{plan.rr_ratio}</span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 gap-2">
            <div className="flex justify-between items-center p-2 bg-surface-container-high rounded">
              <span className="text-[9px] text-on-surface-variant uppercase font-bold">Stop Loss</span>
              <span className="text-[11px] font-data-mono text-semantic-bearish font-bold">{formatPrice(plan.stop_loss)}</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-surface-container-high rounded">
              <span className="text-[9px] text-semantic-bullish uppercase font-bold">TP1 (Fib 0.618)</span>
              <span className="text-[11px] font-data-mono text-semantic-bullish font-bold">{formatPrice(plan.take_profit_1)}</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-surface-container-high rounded">
              <span className="text-[9px] text-semantic-bullish uppercase font-bold">TP2 (Fib 1.618)</span>
              <span className="text-[11px] font-data-mono text-semantic-bullish">{formatPrice(plan.take_profit_2)}</span>
            </div>
          </div>
        </div>
        
        <div className="bg-surface-container p-2 md:p-3 border-t border-outline-variant">
          <div className="flex items-start gap-1.5 md:gap-2">
            <span className="material-symbols-outlined text-on-surface-variant text-[14px] md:text-[16px] mt-0.5">info</span>
            <p className="text-[10px] md:text-[11px] text-on-surface-variant leading-relaxed">
              <span className="font-bold text-on-surface">Strategi Cicil:</span> {plan.scaling_strategy}
            </p>
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <button 
          onClick={() => setShowLogic(!showLogic)}
          className="flex items-center gap-1 md:gap-1.5 text-[10px] md:text-[11px] font-bold text-primary hover:underline w-fit"
        >
          <span className="material-symbols-outlined text-[14px] md:text-[16px]">
            {showLogic ? 'expand_less' : 'psychology'}
          </span>
          {showLogic ? 'Sembunyikan Analisis' : 'Lihat Analisis Logika'}
        </button>

        {showLogic && (
          <div className="p-2 md:p-3 bg-surface-container-highest rounded border border-primary/20 text-[11px] md:text-[12px] text-on-surface leading-relaxed animate-in fade-in slide-in-from-top-1 duration-200">
            {plan.logic_explanation}
            {plan.is_confirmed && (
              <div className="mt-2 flex items-center gap-1 md:gap-1.5 text-semantic-bullish font-bold uppercase text-[9px] md:text-[10px]">
                <span className="material-symbols-outlined text-[12px] md:text-[14px]">verified</span>
                Konfirmasi Tren: EMA & RSI Valid
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
