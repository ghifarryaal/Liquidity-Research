'use client';

import { useState } from 'react';

const GRADE = (wr) => {
  if (wr >= 0.65) return { label: 'A', color: '#00FFB2', bg: 'rgba(0,255,178,0.1)' };
  if (wr >= 0.50) return { label: 'B', color: '#fbbf24', bg: 'rgba(251,191,36,0.1)' };
  if (wr >= 0.40) return { label: 'C', color: '#f97316', bg: 'rgba(249,115,22,0.1)' };
  return { label: 'D', color: '#ef4444', bg: 'rgba(239,68,68,0.1)' };
};

export default function BacktestScorecard({ backtest }) {
  const [open, setOpen] = useState(false);

  if (!backtest || backtest.total_trades === 0) return null;

  const { win_rate, winning_trades, total_trades, avg_rr_achieved, best_trade_pct, worst_trade_pct } = backtest;
  const grade = GRADE(win_rate);
  const winPct = Math.round(win_rate * 100);

  return (
    <div className="mt-3 md:mt-4 border border-outline-variant rounded-xl overflow-hidden">
      {/* Header toggle */}
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-3 md:px-4 py-2.5 md:py-3 bg-surface-container hover:bg-surface-container-high transition-colors"
      >
        <div className="flex items-center gap-2 md:gap-3">
          <span
            className="w-7 h-7 md:w-8 md:h-8 rounded-lg flex items-center justify-center text-xs md:text-sm font-black"
            style={{ background: grade.bg, color: grade.color }}
          >
            {grade.label}
          </span>
          <div className="text-left">
            <p className="text-[11px] md:text-xs font-bold text-on-surface">Backtest Scorecard</p>
            <p className="text-[9px] md:text-[10px] text-on-surface-variant hidden sm:block">Simulasi strategi 6 bulan historis</p>
          </div>
        </div>
        <div className="flex items-center gap-2 md:gap-3">
          <div className="text-right">
            <span className="text-base md:text-lg font-mono font-bold" style={{ color: grade.color }}>{winPct}%</span>
            <span className="text-[9px] md:text-[10px] text-on-surface-variant ml-1">win rate</span>
          </div>
          <span className="material-symbols-outlined text-on-surface-variant text-[16px] md:text-[18px]">
            {open ? 'expand_less' : 'expand_more'}
          </span>
        </div>
      </button>

      {/* Expanded detail */}
      {open && (
        <div className="px-3 md:px-4 pb-3 md:pb-4 pt-2 bg-surface flex flex-col gap-3 md:gap-4 border-t border-outline-variant">

          {/* Win-rate bar */}
          <div>
            <div className="flex justify-between text-[10px] md:text-[11px] text-on-surface-variant mb-1">
              <span>Win Rate</span>
              <span className="font-mono font-bold" style={{ color: grade.color }}>
                {winning_trades}/{total_trades} trades
              </span>
            </div>
            <div className="h-1.5 md:h-2 bg-surface-container-highest rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{ width: `${winPct}%`, background: grade.color }}
              />
            </div>
          </div>

          {/* Stats grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 md:gap-3">
            <StatBox label="Avg R:R Dicapai" value={`1:${avg_rr_achieved.toFixed(1)}`} />
            <StatBox
              label="Trade Terbaik"
              value={`+${best_trade_pct.toFixed(1)}%`}
              color="#00FFB2"
            />
            <StatBox
              label="Trade Terburuk"
              value={`${worst_trade_pct.toFixed(1)}%`}
              color="#ef4444"
            />
          </div>

          {/* Learning note */}
          <div className="p-2 md:p-3 rounded-lg bg-surface-container text-[10px] md:text-[11px] text-on-surface-variant leading-relaxed">
            <span className="font-bold text-on-surface">💡 Apa artinya?</span>
            {' '}Win rate {winPct}% berarti dari setiap 10 sinyal yang dihasilkan AI di masa lalu,
            sekitar {Math.round(win_rate * 10)} sinyal berhasil mencapai target. Ini adalah simulasi
            historis — bukan jaminan hasil ke depan.
          </div>
        </div>
      )}
    </div>
  );
}

function StatBox({ label, value, color }) {
  return (
    <div className="flex flex-col gap-0.5 p-1.5 md:p-2 rounded-lg bg-surface-container-highest">
      <span className="text-[8px] md:text-[9px] text-on-surface-variant uppercase tracking-wider">{label}</span>
      <span className="text-xs md:text-sm font-bold font-mono" style={{ color: color ?? '#94a3b8' }}>{value}</span>
    </div>
  );
}
