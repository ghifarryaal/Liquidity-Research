'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

const GRADE = (wr) => {
  if (wr >= 0.65) return { label: 'A', color: '#00FFB2', bg: 'rgba(0,255,178,0.1)', description: 'Excellent' };
  if (wr >= 0.55) return { label: 'B+', color: '#84cc16', bg: 'rgba(132,204,22,0.1)', description: 'Very Good' };
  if (wr >= 0.50) return { label: 'B', color: '#fbbf24', bg: 'rgba(251,191,36,0.1)', description: 'Good' };
  if (wr >= 0.45) return { label: 'C+', color: '#f97316', bg: 'rgba(249,115,22,0.1)', description: 'Fair' };
  if (wr >= 0.40) return { label: 'C', color: '#f97316', bg: 'rgba(249,115,22,0.1)', description: 'Below Average' };
  return { label: 'D', color: '#ef4444', bg: 'rgba(239,68,68,0.1)', description: 'Poor' };
};

const ACCURACY_INTERPRETATION = (wr) => {
  if (wr >= 0.65) return '✓ Strategi menunjukkan akurasi tinggi dengan konsistensi yang baik';
  if (wr >= 0.55) return '✓ Strategi cukup andal dengan tingkat keberhasilan di atas rata-rata';
  if (wr >= 0.50) return '✓ Strategi seimbang dengan tingkat keberhasilan yang wajar';
  if (wr >= 0.45) return '⚠ Strategi masih layak namun perlu optimasi lebih lanjut';
  if (wr >= 0.40) return '⚠ Strategi memerlukan perbaikan untuk meningkatkan akurasi';
  return '✗ Strategi perlu evaluasi ulang dan penyesuaian parameter';
};

export default function BacktestScorecard({ backtest, ticker }) {
  const [open, setOpen] = useState(false);
  const [chartUrl, setChartUrl] = useState(null);
  const [chartLoading, setChartLoading] = useState(false);
  const [chartError, setChartError] = useState(null);

  if (!backtest || backtest.total_trades === 0) return null;

  const { win_rate, winning_trades, total_trades, avg_rr_achieved, best_trade_pct, worst_trade_pct, max_drawdown_pct } = backtest;
  const grade = GRADE(win_rate);
  const winPct = Math.round(win_rate * 100);
  const lossRate = Math.round((1 - win_rate) * 100);
  const profitFactor = avg_rr_achieved > 0 ? (avg_rr_achieved * win_rate) / ((1 - win_rate) || 0.01) : 0;
  const expectancy = (win_rate * best_trade_pct) + ((1 - win_rate) * worst_trade_pct);

  const handleGenerateChart = async () => {
    if (!ticker || chartLoading) return;
    setChartLoading(true);
    setChartError(null);
    try {
      const res = await fetch(`${API_URL}/api/cluster/backtest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticker: ticker.replace('.JK', ''),
          backtest_months: 6,
          initial_capital: 100_000_000,
          generate_chart: true,
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (data.chart_url) {
        setChartUrl(`${API_URL}${data.chart_url}`);
      } else {
        setChartError('Chart tidak tersedia untuk saham ini.');
      }
    } catch (e) {
      setChartError('Gagal generate chart. Coba lagi.');
    } finally {
      setChartLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="mt-3 md:mt-4 border border-outline-variant rounded-xl overflow-hidden bg-surface-container"
    >
      {/* Header toggle */}
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-3 md:px-4 py-3 md:py-4 bg-surface-container hover:bg-surface-container-high transition-colors"
      >
        <div className="flex items-center gap-2 md:gap-3 flex-1">
          <div
            className="w-8 h-8 md:w-10 md:h-10 rounded-lg flex items-center justify-center text-xs md:text-sm font-black border-2"
            style={{ background: grade.bg, color: grade.color, borderColor: grade.color }}
          >
            {grade.label}
          </div>
          <div className="text-left">
            <p className="text-[11px] md:text-xs font-bold text-on-surface">Backtest Scorecard</p>
            <p className="text-[9px] md:text-[10px] text-on-surface-variant">{grade.description} · {total_trades} trades simulasi</p>
          </div>
        </div>
        <div className="flex items-center gap-2 md:gap-4">
          <div className="text-right">
            <div className="text-lg md:text-2xl font-mono font-bold" style={{ color: grade.color }}>{winPct}%</div>
            <span className="text-[8px] md:text-[9px] text-on-surface-variant uppercase tracking-wider">Win Rate</span>
          </div>
          <span
            className="material-symbols-outlined text-on-surface-variant text-[18px] md:text-[20px] transition-transform"
            style={{ transform: open ? 'rotate(180deg)' : 'rotate(0deg)' }}
          >
            expand_more
          </span>
        </div>
      </button>

      {/* Expanded detail */}
      {open && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.3 }}
          className="px-3 md:px-4 pb-4 md:pb-6 pt-3 md:pt-4 bg-surface flex flex-col gap-4 md:gap-6 border-t border-outline-variant"
        >
          {/* Accuracy Interpretation */}
          <div className="p-3 md:p-4 rounded-lg border border-outline-variant/40 bg-background/40">
            <p className="text-xs md:text-sm text-on-surface leading-relaxed">
              {ACCURACY_INTERPRETATION(win_rate)}
            </p>
          </div>

          {/* Win/Loss Rate Bars */}
          <div className="space-y-3 md:space-y-4">
            <div>
              <div className="flex justify-between text-[10px] md:text-[11px] text-on-surface-variant mb-2">
                <span className="font-bold">Win Rate</span>
                <span className="font-mono font-bold" style={{ color: grade.color }}>
                  {winning_trades}/{total_trades} ({winPct}%)
                </span>
              </div>
              <div className="h-2 md:h-2.5 bg-surface-container-highest rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${winPct}%` }}
                  transition={{ duration: 1, ease: 'easeOut' }}
                  className="h-full rounded-full"
                  style={{ background: grade.color }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-[10px] md:text-[11px] text-on-surface-variant mb-2">
                <span className="font-bold">Loss Rate</span>
                <span className="font-mono font-bold text-semantic-bearish">
                  {total_trades - winning_trades}/{total_trades} ({lossRate}%)
                </span>
              </div>
              <div className="h-2 md:h-2.5 bg-surface-container-highest rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${lossRate}%` }}
                  transition={{ duration: 1, ease: 'easeOut' }}
                  className="h-full rounded-full bg-semantic-bearish"
                />
              </div>
            </div>
          </div>

          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2 md:gap-3">
            <StatBox label="Avg R:R" value={`1:${avg_rr_achieved.toFixed(2)}`} icon="trending_up" color="#60a5fa" />
            <StatBox label="Best Trade" value={`+${best_trade_pct.toFixed(1)}%`} icon="arrow_upward" color="#00FFB2" />
            <StatBox label="Worst Trade" value={`${worst_trade_pct.toFixed(1)}%`} icon="arrow_downward" color="#ef4444" />
            <StatBox label="Max Drawdown" value={`${max_drawdown_pct.toFixed(1)}%`} icon="trending_down" color="#f59e0b" />
            <StatBox
              label="Profit Factor"
              value={profitFactor.toFixed(2)}
              icon="calculate"
              color={profitFactor > 1.5 ? '#00FFB2' : profitFactor > 1.0 ? '#fbbf24' : '#ef4444'}
            />
            <StatBox
              label="Expectancy"
              value={`${expectancy.toFixed(2)}%`}
              icon="analytics"
              color={expectancy > 0 ? '#00FFB2' : '#ef4444'}
            />
          </div>

          {/* Backtest Chart Section */}
          <div className="flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <h4 className="text-[10px] md:text-xs font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[16px]">bar_chart</span>
                Visualisasi Backtest
              </h4>
              {!chartUrl && (
                <button
                  onClick={handleGenerateChart}
                  disabled={chartLoading}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-bold bg-primary/10 border border-primary/40 text-primary hover:bg-primary/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {chartLoading ? (
                    <>
                      <div className="w-3 h-3 rounded-full border-2 border-primary border-t-transparent animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined text-[14px]">auto_graph</span>
                      Generate Chart
                    </>
                  )}
                </button>
              )}
              {chartUrl && (
                <button
                  onClick={() => { setChartUrl(null); setChartError(null); }}
                  className="text-[10px] text-on-surface-variant hover:text-on-surface transition-colors flex items-center gap-1"
                >
                  <span className="material-symbols-outlined text-[13px]">refresh</span>
                  Regenerate
                </button>
              )}
            </div>

            {chartError && (
              <div className="p-3 rounded-lg bg-semantic-bearish/10 border border-semantic-bearish/30 text-[10px] text-semantic-bearish">
                {chartError}
              </div>
            )}

            {chartUrl && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-xl overflow-hidden border border-outline-variant/40"
              >
                <img
                  src={chartUrl}
                  alt={`Backtest chart for ${ticker}`}
                  className="w-full h-auto"
                  onError={() => setChartError('Gagal memuat gambar chart.')}
                />
              </motion.div>
            )}

            {!chartUrl && !chartError && (
              <p className="text-[10px] text-on-surface-variant/60 italic">
                Klik &quot;Generate Chart&quot; untuk melihat visualisasi price action dan equity curve dari simulasi backtest.
              </p>
            )}
          </div>

          {/* Detailed Explanation */}
          <div className="space-y-3 md:space-y-4 p-3 md:p-4 rounded-lg bg-background/40 border border-outline-variant/30">
            <h4 className="text-[10px] md:text-xs font-bold text-on-surface-variant uppercase tracking-wider mb-2">Penjelasan Metrik</h4>
            <ul className="space-y-1.5 md:space-y-2 text-[9px] md:text-[10px] text-on-surface-variant leading-relaxed">
              <li className="flex gap-2"><span className="text-primary font-bold">•</span><span><strong>Win Rate:</strong> Persentase sinyal yang mencapai target profit</span></li>
              <li className="flex gap-2"><span className="text-primary font-bold">•</span><span><strong>Avg R:R:</strong> Rata-rata risk/reward ratio yang dicapai</span></li>
              <li className="flex gap-2"><span className="text-primary font-bold">•</span><span><strong>Max Drawdown:</strong> Kerugian maksimal dalam satu trade</span></li>
              <li className="flex gap-2"><span className="text-primary font-bold">•</span><span><strong>Profit Factor:</strong> Rasio profit terhadap loss (nilai ideal: 1.5+)</span></li>
              <li className="flex gap-2"><span className="text-primary font-bold">•</span><span><strong>Expectancy:</strong> Rata-rata profit/loss per trade</span></li>
            </ul>
          </div>

          {/* Disclaimer */}
          <div className="p-3 md:p-4 rounded-lg bg-semantic-warning/10 border border-semantic-warning/30 text-[9px] md:text-[10px] text-on-surface-variant leading-relaxed">
            <span className="font-bold text-semantic-warning">⚠ Penting:</span>
            {' '}Backtest adalah simulasi historis berdasarkan data 6 bulan terakhir. Hasil masa lalu tidak menjamin performa masa depan. Selalu gunakan stop-loss dan manajemen risiko yang ketat.
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

function StatBox({ label, value, icon, color }) {
  return (
    <motion.div
      whileHover={{ y: -2 }}
      className="flex flex-col gap-1.5 md:gap-2 p-2 md:p-3 rounded-lg bg-surface-container-highest border border-outline-variant/40 hover:border-outline-variant/60 transition-colors"
    >
      <div className="flex items-center gap-1.5 md:gap-2">
        <span className="material-symbols-outlined text-[14px] md:text-[16px]" style={{ color }}>{icon}</span>
        <span className="text-[8px] md:text-[9px] text-on-surface-variant uppercase tracking-wider font-bold">{label}</span>
      </div>
      <span className="text-xs md:text-sm font-bold font-mono" style={{ color }}>{value}</span>
    </motion.div>
  );
}
