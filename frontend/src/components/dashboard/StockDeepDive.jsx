'use client';

import { motion } from 'framer-motion';
import { useStockDetail } from '@/hooks/useStockDetail';
import CandlestickChart from '@/components/charts/CandlestickChart';
import { formatPrice, formatPct, rsiLabel } from '@/lib/formatters';
import TradePlanTable from './TradePlanTable';
import BacktestScorecard from './BacktestScorecard';
import { useMentor } from '@/lib/mentorContext';

export default function StockDeepDive({ stock, onClose }) {
  // Fetch detailed data for chart
  const { ohlcv, ema20, ema50, bbUpper, bbMiddle, bbLower, isLoading: chartLoading } =
    useStockDetail(stock?.ticker);
  const { askAboutTerm } = useMentor();

  if (!stock) return null;

  const rsi = rsiLabel(stock.indicators?.rsi);
  const macdBull = stock.indicators?.macd != null &&
    stock.indicators?.macd_signal != null &&
    stock.indicators.macd > stock.indicators.macd_signal;
    
  const volRatio = stock.indicators?.volume_ratio || 0;
  const ticker = stock.ticker.replace('.JK', '');

  // Build page context for the Mentor
  const mentorCtx = {
    ticker: stock.ticker,
    cluster_label: stock.cluster_label,
    indicators: stock.indicators,
    trade_plan: stock.trade_plan,
  };

  /** Render a clickable technical term that opens the Mentor */
  const Term = ({ label }) => (
    <button
      type="button"
      className="mentor-term"
      onClick={() => askAboutTerm(label, ticker, mentorCtx)}
      title={`Tanya Mentor tentang ${label}`}
    >
      {label}
      <span className="material-symbols-outlined mentor-term-icon">help</span>
    </button>
  );

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm"
      onClick={onClose}
    >
      <motion.div 
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        className="w-full max-w-5xl bg-surface-container rounded-lg border border-outline-variant flex flex-col gap-component-gap-md p-6 max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Top: Header / Summary */}
        <header className="flex justify-between items-start border-b border-outline-variant pb-4">
          <div className="flex flex-col gap-1">
            <div className="flex items-baseline gap-3">
              <h1 className="font-ticker-lg text-ticker-lg text-primary uppercase tracking-tight">{stock.ticker.replace('.JK', '')}</h1>
              <span className="font-heading-table text-heading-table text-on-surface-variant">{stock.name}</span>
            </div>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="font-display-sm text-display-sm text-on-surface">{formatPrice(stock.current_price)}</span>
              <span className={`font-data-mono text-data-mono flex items-center ${stock.price_change_pct > 0 ? 'text-semantic-bullish' : stock.price_change_pct < 0 ? 'text-semantic-bearish' : 'text-on-surface-variant'}`}>
                {stock.price_change_pct > 0 ? (
                  <span className="material-symbols-outlined text-[14px]">arrow_upward</span>
                ) : stock.price_change_pct < 0 ? (
                  <span className="material-symbols-outlined text-[14px]">arrow_downward</span>
                ) : null}
                {formatPct(stock.price_change_pct)} (1H)
              </span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={onClose} className="flex items-center justify-center w-8 h-8 rounded border border-outline-variant text-on-surface-variant hover:bg-surface-variant transition-colors">
              <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>close</span>
            </button>
          </div>
        </header>

        {/* Main Section: Two Columns */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-gutter">
          {/* Left Column: Chart Area (Span 2) */}
          <div className="lg:col-span-2 bg-surface rounded border border-outline-variant p-4 flex flex-col gap-3 min-h-[350px]">
            <div className="flex justify-between items-center">
              <h3 className="font-heading-table text-heading-table text-on-surface uppercase">Price Action</h3>
              <div className="flex gap-2">
                <span className="font-data-mono text-data-mono text-primary text-xs px-2 py-1 bg-surface-container-highest rounded border border-primary/30">180D</span>
              </div>
            </div>

            {/* Chart Legend / Overlays */}
            <div className="flex gap-4 font-data-mono text-data-mono text-xs">
              <span className="text-[#06b6d4] flex items-center gap-1"><div className="w-2 h-0.5 bg-[#06b6d4]"></div> EMA(20)</span>
              <span className="text-[#a855f7] flex items-center gap-1"><div className="w-2 h-0.5 bg-[#a855f7]"></div> EMA(50)</span>
              <span className="text-orange-400 flex items-center gap-1"><div className="w-2 h-0.5 bg-orange-400 border-dashed border-b"></div> BB</span>
            </div>

            {/* Chart Canvas */}
            <div className="flex-1 w-full bg-[#020817] rounded border border-outline-variant/50 relative overflow-hidden flex items-center justify-center">
              {chartLoading ? (
                <div className="flex items-center justify-center h-full text-on-surface-variant">
                  <div className="w-6 h-6 rounded-full border-2 border-primary border-t-transparent animate-spin mr-3" />
                  <span>Loading chart data...</span>
                </div>
              ) : (
                <CandlestickChart
                  ohlcv={ohlcv}
                  ema20={ema20}
                  ema50={ema50}
                  bbUpper={bbUpper}
                  bbMiddle={bbMiddle}
                  bbLower={bbLower}
                />
              )}
            </div>
          </div>

          {/* Right Column: Technical Snapshot */}
          <div className="lg:col-span-1 bg-surface rounded border border-outline-variant p-4 flex flex-col gap-4">
            <h3 className="font-heading-table text-heading-table text-on-surface uppercase border-b border-outline-variant pb-2">Technical Snapshot</h3>
            <div className="flex flex-col gap-3">
              
              {/* RSI */}
              <div className="flex justify-between items-center group p-2 hover:bg-surface-variant/50 rounded transition-colors">
                <div className="relative">
                  <Term label="RSI (14)" />
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-data-mono text-data-mono text-on-surface">{stock.indicators?.rsi?.toFixed(1) || '—'}</span>
                  <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${rsi.zone === 'positive' ? 'text-semantic-bullish bg-semantic-bullish/10' : rsi.zone === 'negative' ? 'text-semantic-bearish bg-semantic-bearish/10' : 'text-on-surface-variant bg-surface-variant'}`}>
                    {rsi.zone === 'positive' ? 'Oversold' : rsi.zone === 'negative' ? 'Overbought' : 'Neutral'}
                  </span>
                </div>
              </div>

              {/* MACD */}
              <div className="flex justify-between items-center group p-2 hover:bg-surface-variant/50 rounded transition-colors">
                <div className="relative">
                  <Term label="MACD" />
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-data-mono text-data-mono text-on-surface">{stock.indicators?.macd?.toFixed(1) || '—'}</span>
                  <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${macdBull ? 'text-semantic-bullish bg-semantic-bullish/10' : 'text-semantic-bearish bg-semantic-bearish/10'}`}>
                    {macdBull ? 'Bullish' : 'Bearish'}
                  </span>
                </div>
              </div>

              {/* Volume Ratio */}
              <div className="flex justify-between items-center group p-2 hover:bg-surface-variant/50 rounded transition-colors">
                <div className="relative">
                  <Term label="Volume Ratio" />
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-data-mono text-data-mono text-on-surface">{volRatio.toFixed(1)}x</span>
                  <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${volRatio > 1.5 ? 'text-tertiary bg-tertiary/10' : 'text-on-surface-variant bg-surface-variant'}`}>
                    {volRatio > 1.5 ? 'Elevated' : 'Normal'}
                  </span>
                </div>
              </div>

              {/* ATR */}
              <div className="flex justify-between items-center group p-2 hover:bg-surface-variant/50 rounded transition-colors">
                <div className="relative">
                  <Term label="ATR (14)" />
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-data-mono text-data-mono text-on-surface">{stock.indicators?.atr ? Math.round(stock.indicators.atr) : '—'}</span>
                  <span className="text-[10px] uppercase font-bold text-on-surface-variant bg-surface-variant px-1.5 py-0.5 rounded">IDR</span>
                </div>
              </div>

            </div>
          </div>
        </div>

        {/* Bottom: Analyst Desk Brief */}
        <div className="bg-surface rounded border border-outline-variant p-5 flex flex-col gap-4 mt-2">
          <div className="flex justify-between items-center border-b border-outline-variant pb-2">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-primary" style={{ fontSize: '20px' }}>psychology</span>
              <h3 className="font-heading-table text-heading-table text-on-surface uppercase tracking-wider">Analyst Desk Briefing</h3>
            </div>
            <div className="flex items-center gap-3">
              <span className="font-heading-table text-heading-table text-on-surface-variant hidden sm:inline">AI Confidence</span>
              <div className="flex items-center gap-2">
                <div className="w-24 h-[6px] bg-outline-variant rounded-full overflow-hidden">
                  <div className="h-full bg-primary" style={{ width: `${Math.round(stock.confidence * 100)}%` }}></div>
                </div>
                <span className="font-data-mono text-data-mono text-primary text-xs">{Math.round(stock.confidence * 100)}%</span>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="md:col-span-1 flex flex-col gap-4">
              <div>
                <span className="font-heading-table text-heading-table text-on-surface-variant uppercase block mb-2">Strategy</span>
                <div className="inline-flex items-center justify-center w-full px-3 py-2 bg-primary/10 border border-primary text-primary font-bold tracking-widest uppercase rounded text-[10px] text-center">
                  {stock.cluster_label}
                </div>
              </div>
              <div>
                <span className="font-heading-table text-heading-table text-on-surface-variant uppercase block mb-2">Trading Style</span>
                <div className="text-on-surface font-semibold text-sm flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-[18px]">timer</span>
                  {stock.trading_style}
                </div>
              </div>
            </div>
            
            <div className="md:col-span-3 flex flex-col gap-4">
              <div className="flex flex-col gap-2">
                <span className="font-heading-table text-heading-table text-on-surface-variant uppercase">Rationale & Analisis</span>
                <p className="font-body-standard text-body-standard text-on-surface leading-relaxed text-sm bg-surface-container-high/30 p-4 rounded-lg border border-outline-variant/30">
                  {stock.reasoning}
                  <span className="block mt-2 text-[11px] text-on-surface-variant italic">
                    💡 Catatan: {(stock.cluster_label === 'High Risk' || stock.cluster_label === 'High Risk / Avoid') ? 'Waspadai volatilitas tinggi. Disarankan untuk wait and see.' : 'Gunakan strategi cicil bertahap (scaling-in) untuk mendapatkan harga rata-rata yang optimal.'}
                  </span>
                </p>
              </div>
            </div>
          </div>

          {/* Trade Plan Table */}
          {stock.trade_plan ? (
            <TradePlanTable
              plan={stock.trade_plan}
              ticker={stock.ticker}
              confidenceScore={stock.confidence_score}
              isHighConviction={stock.is_high_conviction}
            />
          ) : (
            <div className="mt-4 p-4 border border-dashed border-outline-variant rounded-lg text-center text-on-surface-variant text-xs">
              Trade Plan sedang dikalkulasi ulang untuk emiten ini...
            </div>
          )}

          {/* Backtest Scorecard */}
          <BacktestScorecard backtest={stock.backtest} />
        </div>
      </motion.div>
    </motion.div>
  );
}
